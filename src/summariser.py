"""
Gemini API integration for text summarization
"""
import time
import logging
from typing import Dict, Optional, List 
import google.generativeai as genai
from .config import GENAI_MODEL_NAME, MAX_TOKENS, TEMPERATURE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Summarizer:
    def __init__(self, api_key: str):
        genai.configure(api_key=api_key)
        generation_config = {
            'max_output_tokens': MAX_TOKENS,
            'temperature': TEMPERATURE
        }
        self.model = genai.GenerativeModel(
            GENAI_MODEL_NAME,
            generation_config=generation_config
        )
    
    def generate_short_summary(self, transcript: str, max_sentences: int = 3) -> str:
        prompt = f"""
        Summarize the following video transcript in exactly {max_sentences} clear, concise sentences.
        Focus on the main points and key takeaways.
        
        Transcript:
        {transcript[:4000]}
        
        Summary:
        """
        try:
            start_time = time.time()
            response = self.model.generate_content(prompt)
            end_time = time.time()
            summary = response.text.strip()
            logger.info(f"Short summary generated in {end_time - start_time:.2f}s")
            return summary
        except Exception as e:
            logger.error(f"Error generating short summary: {e}")
            return f"Error generating summary: {str(e)}"
    
    def generate_detailed_summary(self, transcript: str) -> str:
        prompt = f"""
        Create a detailed summary of the following video transcript. Structure your response as follows:

        **Main Topic:** [Brief description of what the video is about]

        **Key Points:**
        • [First major point discussed]
        • [Second major point discussed]  
        • [Third major point discussed]
        • [Additional points as needed]

        **Important Details:**
        [Elaborate on significant details, examples, or explanations provided]

        **Conclusion:**
        [Summarize the main takeaway or conclusion]

        Transcript:
        {transcript[:6000]}
        
        Detailed Summary:
        """
        try:
            start_time = time.time()
            response = self.model.generate_content(prompt)
            end_time = time.time()
            summary = response.text.strip()
            logger.info(f"Detailed summary generated in {end_time - start_time:.2f}s")
            return summary
        except Exception as e:
            logger.error(f"Error generating detailed summary: {e}")
            return f"Error generating detailed summary: {str(e)}"
    
    def answer_question(self, context: str, question: str) -> Dict:
        """Enhanced Q&A with comprehensive context analysis"""
        prompt = f"""
        You are an expert analyst helping users understand video content in detail.
        
        CONTEXT FROM VIDEO:
        {context}
        
        USER QUESTION: {question}
        
        INSTRUCTIONS:
        1. Analyze the provided context thoroughly
        2. Give a comprehensive, detailed answer (aim for 3-5 paragraphs)
        3. Include specific details, examples, and quotes when available
        4. If the speaker mentioned specific points, elaborate on them
        5. Provide context and background when relevant
        6. If information is limited, explain what IS available rather than what isn't
        7. Use a conversational, informative tone
        
        ANSWER:
        """
        try:
            start_time = time.time()
            response = self.model.generate_content(prompt)
            end_time = time.time()
            answer = response.text.strip()
            response_time = end_time - start_time
            logger.info(f"Enhanced Q&A answered in {response_time:.2f}s")
            return {
                'answer': answer,
                'response_time': response_time,
                'context_used': len(context.split()),
                'success': True
            }
        except Exception as e:
            logger.error(f"Error in enhanced Q&A: {e}")
            return {
                'answer': f"I encountered an issue processing your question: {str(e)}",
                'response_time': 0,
                'context_used': 0,
                'success': False
            }
    
    def generate_key_insights(self, transcript: str) -> str:
        prompt = f"""
        Analyze the following video transcript and extract key insights, learning points, or actionable takeaways.
        Present them as a bulleted list of the most valuable information someone could learn from this video.
        
        Transcript:
        {transcript[:5000]}
        
        Key Insights:
        """
        try:
            response = self.model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"Error generating insights: {e}")
            return f"Error generating insights: {str(e)}"
    
    def generate_transcript_topics(self, transcript: str) -> List[str]:
        prompt = f"""
        Identify the main topics or themes discussed in this video transcript.
        Return only a simple list of topics, one per line, without numbers or bullets.
        Limit to the 5 most important topics.
        
        Transcript:
        {transcript[:3000]}
        
        Topics:
        """
        try:
            response = self.model.generate_content(prompt)
            topics = [topic.strip() for topic in response.text.strip().split('\n') if topic.strip()]
            return topics[:5]
        except Exception as e:
            logger.error(f"Error generating topics: {e}")
            return ["Error identifying topics"]

def create_summarizer(api_key: str) -> Optional[Summarizer]:
    try:
        return Summarizer(api_key)
    except Exception as e:
        logger.error(f"Failed to create summarizer: {e}")
        return None
