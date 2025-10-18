import streamlit as st
from streamlit_option_menu import option_menu
from youtube_transcript import fetch_transcript
from chunking import get_chunks
from embedding_store import build_vector_store, retrieve_similar_chunks, embeddings
import google.generativeai as genai
import os
from dotenv import load_dotenv
import sqlite3
from config import DB_NAME

load_dotenv()  # Load .env file

# Get the API key from environment variable
api_key = os.getenv("GOOGLE_API_KEY")

# Configure the Google Generative AI client
genai.configure(api_key=api_key)

# Initialize the Gemini model
gemini = genai.GenerativeModel("gemini-2.0-flash")

# ------------------ Streamlit Setup ------------------
st.set_page_config(page_title="YouTube Video Summarizer", layout="wide")

if 'messages' not in st.session_state:
    st.session_state.messages = {}

# ------------------ Sidebar Menu ------------------
with st.sidebar:
    selected = option_menu(
        "Menu", ["Home", "YouTube Summarizer", "Chat History"],
        icons=["house", "play-circle", "clock-history"],
        menu_icon="cast", default_index=0
    )

# ------------------ Home ------------------
if selected == "Home":
    st.title("🎬 YouTube Video Summarizer")
    st.write("Enter a YouTube URL to generate a summary and ask questions about the video.")

# ------------------ YouTube Summarizer ------------------
elif selected == "YouTube Summarizer":
    st.header("YouTube Summarizer")

    url = st.text_input("Enter YouTube URL")
    
    if st.button("Fetch Transcript & Generate Summaries") and url:
        with st.spinner("Fetching transcript..."):
            transcript = fetch_transcript(url)
        
        if transcript:
            st.subheader("Transcript Preview")
            st.write(transcript[:1000] + "...")  # show first 1000 characters
            
            # Split into chunks
            chunks = get_chunks(transcript)
            st.info(f"Transcript split into {len(chunks)} chunks.")
            
            # Build FAISS vector store
            db = build_vector_store(chunks)
            st.success("Vector store created successfully!")
            
            # ------------------ Short Summary ------------------
            short_prompt = f"Summarize the following transcript in 3-4 sentences:\n{transcript}"
            short_summary = gemini.generate_content(short_prompt).text
            st.subheader("Short Summary")
            st.write(short_summary)
            
            # ------------------ Detailed Summary ------------------
            detailed_prompt = f"Generate a detailed summary of the following transcript:\n{transcript}"
            detailed_summary = gemini.generate_content(detailed_prompt).text
            st.subheader("Detailed Summary")
            st.write(detailed_summary)
            
            # Save to session state
            st.session_state['db'] = db
            st.session_state['transcript'] = transcript

    # ------------------ Q&A ------------------
    st.subheader("Ask Questions about the Video")
    if 'db' in st.session_state:
        user_query = st.text_input("Type your question here")
        if st.button("Get Answer") and user_query:
            db = st.session_state['db']
            relevant_chunks = retrieve_similar_chunks(db, user_query)
            context = " ".join(relevant_chunks)
            
            qa_prompt = f"""
            Context: {context}
            Question: {user_query}
            Answer in a clear, concise manner.
            """
            answer = gemini.generate_content(qa_prompt).text
            st.markdown(f"**Answer:** {answer}")

# ------------------ Chat History ------------------
elif selected == "Chat History":
    st.header("Past Sessions")
    
    if 'user_id' not in st.session_state:
        st.warning("Please login to view your past sessions.")
    else:
        user_id = st.session_state['user_id']
        st.info(f"Showing past sessions for {st.session_state['first_name']} {st.session_state['last_name']}")

        # Connect to SQLite
        conn = sqlite3.connect(DB_NAME)
        cursor = conn.cursor()
        
        # Fetch videos uploaded by the user
        cursor.execute("SELECT video_id, title, url FROM videos WHERE user_id = ?", (user_id,))
        videos = cursor.fetchall()
        
        if not videos:
            st.info("No past sessions found. Start summarizing some videos first!")
        else:
            for vid in videos:
                video_id, title, url = vid
                st.subheader(f"🎬 {title}")
                st.markdown(f"🔗 [YouTube Link]({url})")
                
                # Fetch summaries
                cursor.execute(
                    "SELECT summary_type, content, created_at FROM summaries WHERE video_id = ?",
                    (video_id,)
                )
                summaries = cursor.fetchall()
                
                if summaries:
                    for s_type, content, created_at in summaries:
                        st.markdown(f"**{s_type.capitalize()} Summary ({created_at}):**")
                        st.write(content)
                
                # Fetch Q&A history
                cursor.execute(
                    "SELECT question, answer, created_at FROM qa_history WHERE video_id = ?",
                    (video_id,)
                )
                qas = cursor.fetchall()
                
                if qas:
                    st.markdown("**Q&A History:**")
                    for question, answer, created_at in qas:
                        st.markdown(f"- **Q:** {question}  \n  **A:** {answer}  \n  *(Time: {created_at})*")
        
        conn.close()

