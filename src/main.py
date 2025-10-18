"""
Main Streamlit application for YouTube Video Summarizer
"""
from typing import Optional, Dict
import os
import time
from dotenv import load_dotenv
import streamlit as st
from streamlit_option_menu import option_menu

from .config import APP_TITLE, APP_LAYOUT, VERSION
from .auth import auth_manager
from .video_handler import video_processor
from .text_processor import text_processor
from .embedding_store import embedding_store
from .summarizer import create_summarizer
from .db_utils import db_manager

load_dotenv()

class YouTubeSummarizerApp:
    def __init__(self):
        self.setup_page_config()
        self.initialize_services()
        auth_manager.initialize_session_state()
    
    def setup_page_config(self):
        st.set_page_config(
            page_title=APP_TITLE,
            page_icon="🎬",
            layout=APP_LAYOUT,
            initial_sidebar_state="expanded"
        )
    
    def initialize_services(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            st.error("⚠️ GOOGLE_API_KEY not found in environment variables")
            st.stop()
        self.summarizer = create_summarizer(api_key)
        if not self.summarizer:
            st.error("❌ Failed to initialize AI summarization service")
            st.stop()
    
    def render_sidebar(self) -> str:
        with st.sidebar:
            if auth_manager.is_authenticated():
                user_data = auth_manager.get_user_data()
                if user_data:
                    st.success(f"👋 Welcome, {user_data['username']}")
                if st.button("🚪 Logout", use_container_width=True):
                    auth_manager.logout_user()
                    st.rerun()
                st.divider()
                selected = option_menu(
                    "Navigation",
                    ["🏠 Home", "🎬 Summarizer", "📚 History", "⚙️ Settings"],
                    icons=["house", "play-circle", "clock-history", "gear"],
                    menu_icon="cast",
                    default_index=0
                )
            else:
                selected = "🔐 Auth"
            st.divider()
            st.caption(f"📱 Version {VERSION}")
            st.caption("🤖 Powered by Gemini AI")
            return selected
    
    def render_auth_page(self):
        st.title("🔐 Authentication")
        tab1, tab2 = st.tabs(["🔑 Login", "📝 Register"])
        self.render_login_form(tab1)
        self.render_register_form(tab2)
    
    def render_login_form(self, tab):
        with tab:
            st.subheader("Login to Your Account")
            with st.form("login_form"):
                username = st.text_input("Username")
                password = st.text_input("Password", type="password")
                submitted = st.form_submit_button("🔑 Login", use_container_width=True)
                if submitted:
                    if username and password:
                        success, message = auth_manager.login_user(username, password)
                        if success:
                            st.success(message)
                            time.sleep(0.8)
                            st.rerun()
                        else:
                            st.error(message)
                    else:
                        st.error("Please fill in all fields")
    
    def render_register_form(self, tab):
        with tab:
            st.subheader("Create New Account")
            with st.form("register_form"):
                username = st.text_input("Choose Username")
                email = st.text_input("Email (optional)")
                password = st.text_input("Choose Password", type="password")
                password_confirm = st.text_input("Confirm Password", type="password")
                submitted = st.form_submit_button("📝 Create Account", use_container_width=True)
                if submitted:
                    if not (username and password and password_confirm):
                        st.error("Please fill in all required fields")
                    elif password != password_confirm:
                        st.error("Passwords do not match")
                    else:
                        success, message = auth_manager.register_user(username, password, email)
                        if success:
                            st.success(message)
                            st.info("Please login with your new account")
                        else:
                            st.error(message)
    
    def render_home_page(self):
        st.title(APP_TITLE)
        col1, col2 = st.columns([2, 1])
        with col1:
            st.markdown("""
            ### 🚀 Transform YouTube Videos into Actionable Insights
            - 📝 Generate summaries
            - 🔍 Ask questions (RAG)
            - 💾 Save your history
            """)
            if st.button("🎬 Start Summarizing", use_container_width=True, type="primary"):
                st.session_state['selected_page'] = "🎬 Summarizer"
                st.rerun()
        with col2:
            st.info("""
            **🛠️ Tech Stack**
            Streamlit • Gemini • FAISS • yt-dlp • SQLite
            """)
        user_data = auth_manager.get_user_data()
        if user_data:
            st.subheader("📊 Recent Activity")
            recent_videos = db_manager.get_user_videos(user_data['user_id'], limit=3)
            if recent_videos:
                for video in recent_videos:
                    with st.expander(f"🎥 {video['title'][:60]}..."):
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.write(f"**Duration:** {video['duration']}s")
                            st.write(f"**Processed:** {video['processed_at']}")
                        with col2:
                            if st.button(f"View", key=f"view_{video['video_id']}"):
                                st.session_state['selected_video'] = video['video_id']
                                st.session_state['selected_page'] = "📚 History"
                                st.rerun()
            else:
                st.info("No videos processed yet. Start by summarizing your first video!")
    
    def render_summarizer_page(self):
        st.header("🎬 YouTube Video Summarizer")
        url = st.text_input("📎 Enter YouTube Video URL", placeholder="https://www.youtube.com/watch?v=...")
        col1, col2 = st.columns([2, 1])
        with col1:
            process_button = st.button("🚀 Process Video", type="primary", disabled=not url)
        with col2:
            quick_info = st.button("ℹ️ Quick Info", disabled=not url)
        if quick_info and url:
            if video_processor.validate_url(url):
                with st.spinner("Fetching video info..."):
                    info = video_processor.get_video_info_quick(url)
                    if info:
                        st.success("✅ Valid YouTube URL")
                        st.json(info)
                    else:
                        st.error("❌ Could not fetch video information")
            else:
                st.error("❌ Invalid YouTube URL format")
        if process_button and url:
            self.process_video(url)
        if 'current_video_db' in st.session_state:
            st.divider()
            self.render_qa_section()
    
    def process_video(self, url: str):
        if not video_processor.validate_url(url):
            st.error("❌ Invalid YouTube URL format")
            return
        progress_bar = st.progress(0)
        status_text = st.empty()
        try:
            status_text.text("📥 Fetching video data...")
            progress_bar.progress(20)
            video_data = video_processor.fetch_video_data(url)
            if not video_data:
                st.error("❌ Could not process video. Please check the URL.")
                return
            status_text.text("📝 Processing transcript...")
            progress_bar.progress(40)
            transcript = video_data['transcript']
            chunks = text_processor.get_chunks(transcript)
            status_text.text("🔍 Building search index...")
            progress_bar.progress(60)
            vector_db = embedding_store.build_vector_store(chunks, video_data['video_id'])
            status_text.text("🤖 Generating AI summaries...")
            progress_bar.progress(80)
            short_summary = self.summarizer.generate_short_summary(transcript)
            detailed_summary = self.summarizer.generate_detailed_summary(transcript)
            status_text.text("💾 Saving results...")
            progress_bar.progress(90)
            user_data = auth_manager.get_user_data()
            if not user_data:
                st.error("You must be logged in to save results.")
                return
            video_id = db_manager.save_video(
                user_data['user_id'],
                video_data['video_id'],
                url,
                video_data['title'],
                video_data['duration'],
                video_data['language']
            )
            db_manager.save_summary(video_id, 'short', short_summary)
            db_manager.save_summary(video_id, 'detailed', detailed_summary)
            progress_bar.progress(100)
            status_text.text("✅ Processing complete!")
            st.session_state['current_video_db'] = vector_db
            st.session_state['current_video_id'] = video_id
            st.session_state['current_transcript'] = transcript
            self.display_video_results(video_data, short_summary, detailed_summary)
        except Exception as e:
            st.error(f"❌ Error processing video: {str(e)}")
        finally:
            progress_bar.empty()
            status_text.empty()
    
    def display_video_results(self, video_data: Dict, short_summary: str, detailed_summary: str):
        st.success("✅ Video processed successfully!")
        st.subheader(f"🎥 {video_data['title']}")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Duration", f"{video_data['duration']}s")
        with col2:
            st.metric("Language", video_data['language'])
        with col3:
            st.metric("Transcript Length", f"{video_data['transcript_length']} chars")
        tab1, tab2, tab3 = st.tabs(["📝 Short Summary", "📄 Detailed Summary", "📊 Transcript"])
        with tab1:
            st.write(short_summary)
        with tab2:
            st.write(detailed_summary)
        with tab3:
            stats = text_processor.get_text_statistics(video_data['transcript'])
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Words", stats['word_count'])
            with col2:
                st.metric("Sentences", stats['sentence_count'])
            with col3:
                st.metric("Reading Time", f"{stats['reading_time_minutes']:.1f} min")
            with col4:
                st.metric("Avg Sentence Length", f"{stats['average_sentence_length']:.1f}")
            st.text_area("Full Transcript", video_data['transcript'], height=300)
    
    def render_qa_section(self):
        st.subheader("❓ Ask Questions About This Video")
        question = st.text_input("💬 Your Question", placeholder="What are the main points discussed in this video?")
        col1, col2 = st.columns([3, 1])
        with col1:
            ask_button = st.button("🤔 Get Answer", disabled=not question)
        with col2:
            st.caption("💡 Powered by RAG")
        if ask_button and question:
            self.answer_question(question)
    
    def answer_question(self, question: str):
        try:
            with st.spinner("🔍 Searching for relevant information..."):
                vector_db = st.session_state.get('current_video_db')
                if vector_db is None:
                    st.error("No processed video found in session.")
                    return
                relevant_chunks = embedding_store.retrieve_similar_chunks(vector_db, question, k=3)
                if not relevant_chunks:
                    st.warning("No relevant information found in the video.")
                    return
                context = " ".join(relevant_chunks)
                result = self.summarizer.answer_question(context, question)
                if result.get('success'):
                    st.success("💡 Answer:")
                    st.write(result['answer'])
                    video_id = st.session_state.get('current_video_id')
                    if video_id:
                        db_manager.save_qa(
                            video_id,
                            question,
                            result['answer'],
                            response_time=result.get('response_time')
                        )
                    with st.expander("📖 Source Context"):
                        for i, chunk in enumerate(relevant_chunks, 1):
                            st.write(f"**Excerpt {i}:**")
                            st.write(chunk[:300] + "...")
                            st.divider()
                else:
                    st.error("❌ Error generating answer")
        except Exception as e:
            st.error(f"❌ Error processing question: {str(e)}")
    
    def render_history_page(self):
        st.header("📚 Your Video History")
        user_data = auth_manager.get_user_data()
        if not user_data:
            st.error("Please log in to view history.")
            return
        videos = db_manager.get_user_videos(user_data['user_id'], limit=20)
        if not videos:
            st.info("📭 No videos processed yet. Start summarizing some videos!")
            if st.button("🎬 Go to Summarizer"):
                st.session_state['selected_page'] = "🎬 Summarizer"
                st.rerun()
            return
        search_term = st.text_input("🔍 Search videos", placeholder="Enter title or keyword...")
        for video in videos:
            if search_term and search_term.lower() not in (video['title'] or '').lower():
                continue
            with st.expander(f"🎥 {video['title']}"):
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.write(f"**URL:** {video['url']}")
                    st.write(f"**Duration:** {video['duration']}s")
                    st.write(f"**Processed:** {video['processed_at']}")
                with col2:
                    if st.button(f"🔄 Reprocess", key=f"reprocess_{video['video_id']}"):
                        st.session_state['reprocess_url'] = video['url']
                        st.session_state['selected_page'] = "🎬 Summarizer"
                        st.rerun()
                summaries = db_manager.get_video_summaries(video['video_id'])
                if summaries:
                    tab1, tab2, tab3 = st.tabs(["📝 Short", "📄 Detailed", "❓ Q&A"])
                    with tab1:
                        if 'short' in summaries:
                            st.write(summaries['short']['content'])
                    with tab2:
                        if 'detailed' in summaries:
                            st.write(summaries['detailed']['content'])
                    with tab3:
                        qa_history = db_manager.get_video_qa_history(video['video_id'])
                        if qa_history:
                            for qa in qa_history:
                                st.write(f"**Q:** {qa['question']}")
                                st.write(f"**A:** {qa['answer']}")
                                st.caption(f"Asked on {qa['created_at']}")
                                st.divider()
                        else:
                            st.info("No questions asked yet for this video.")
    
    def render_settings_page(self):
        st.header("⚙️ Settings")
        tab1, tab2 = st.tabs(["👤 Account", "🛠️ Preferences"])
        with tab1:
            user_data = auth_manager.get_user_data()
            if user_data:
                st.write(f"**Username:** {user_data['username']}")
                st.write(f"**User ID:** {user_data['user_id']}")
        with tab2:
            st.subheader("Processing Preferences")
            st.caption("Preferences UI placeholder")
    
    def run(self):
        if 'selected_page' not in st.session_state:
            st.session_state['selected_page'] = "🏠 Home"
        selected = self.render_sidebar()
        if 'reprocess_url' in st.session_state:
            st.session_state['selected_page'] = "🎬 Summarizer"
        selected = st.session_state.get('selected_page', selected)
        if not auth_manager.is_authenticated():
            self.render_auth_page()
        elif selected == "🏠 Home":
            self.render_home_page()
        elif selected == "🎬 Summarizer":
            self.render_summarizer_page()
        elif selected == "📚 History":
            self.render_history_page()
        elif selected == "⚙️ Settings":
            self.render_settings_page()

def main():
    app = YouTubeSummarizerApp()
    app.run()

if __name__ == "__main__":
    main()