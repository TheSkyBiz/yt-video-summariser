"""
Text processing and chunking utilities
"""
import re
from typing import List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from .config import CHUNK_SIZE, CHUNK_OVERLAP, MAX_CHUNKS

class TextProcessor:
    def __init__(self):
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHUNK_SIZE,
            chunk_overlap=CHUNK_OVERLAP,
            length_function=len,
            separators=["\n\n", "\n", ". ", "? ", "! ", " ", ""]
        )
    
    def clean_transcript(self, text: str) -> str:
        """Clean and normalize transcript text"""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove timestamp markers (common in subtitles)
        text = re.sub(r'\d{1,2}:\d{2}:\d{2}[.,]\d{3}\s*-->\s*\d{1,2}:\d{2}:\d{2}[.,]\d{3}', '', text)
        
        # Remove subtitle sequence numbers
        text = re.sub(r'^\d+\s*$', '', text, flags=re.MULTILINE)
        
        # Clean up common subtitle artifacts
        text = re.sub(r'\[.*?\]', '', text)  # Remove [music], [applause], etc.
        text = re.sub(r'<.*?>', '', text)   # Remove HTML tags
        
        # Fix common transcription issues
        text = re.sub(r'\b(um|uh|ah|er)\b', '', text, flags=re.IGNORECASE)
        
        # Normalize punctuation
        text = re.sub(r'([.!?])\1+', r'\1', text)  # Remove repeated punctuation
        text = re.sub(r'([.!?])(\w)', r'\1 \2', text)  # Add space after punctuation
        
        return text.strip()
    
    def get_chunks(self, text: str) -> List[str]:
        """Split text into overlapping chunks for processing"""
        # Clean the text first
        cleaned_text = self.clean_transcript(text)
        
        # Split into chunks
        chunks = self.splitter.split_text(cleaned_text)
        
        # Limit number of chunks for performance
        if len(chunks) > MAX_CHUNKS:
            chunks = chunks[:MAX_CHUNKS]
        
        # Filter out very short chunks
        chunks = [chunk for chunk in chunks if len(chunk.strip()) > 50]
        
        return chunks
    
    def extract_key_phrases(self, text: str, max_phrases: int = 10) -> List[str]:
        """Extract key phrases from text (simple implementation)"""
        # Simple keyword extraction - could be enhanced with NLP libraries
        words = re.findall(r'\b[a-zA-Z]{4,}\b', text.lower())
        
        # Count word frequency
        word_freq = {}
        for word in words:
            if word not in ['this', 'that', 'with', 'have', 'will', 'from', 'they', 'been', 'were']:
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency and return top phrases
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, freq in sorted_words[:max_phrases] if freq > 1]
    
    def get_text_statistics(self, text: str) -> dict:
        """Get basic text statistics"""
        sentences = re.split(r'[.!?]+', text)
        words = text.split()
        
        return {
            'character_count': len(text),
            'word_count': len(words),
            'sentence_count': len([s for s in sentences if s.strip()]),
            'average_sentence_length': len(words) / max(len(sentences), 1),
            'reading_time_minutes': len(words) / 200  # Assume 200 WPM reading speed
        }

# Global text processor instance
text_processor = TextProcessor()
