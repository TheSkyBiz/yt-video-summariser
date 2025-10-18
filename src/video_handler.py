"""
YouTube video processing using yt-dlp
"""
import yt_dlp
import re
import logging
from typing import Dict, Optional
from urllib.parse import urlparse, parse_qs
from .config import MAX_VIDEO_DURATION, SUPPORTED_LANGUAGES, DEFAULT_LANGUAGE

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VideoProcessor:
    def __init__(self):
        self.ydl_opts = {
            'writesubtitles': True,
            'writeautomaticsub': True,
            'subtitleslangs': SUPPORTED_LANGUAGES,
            'skip_download': True,
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False
        }
    
    def extract_video_id(self, url: str) -> Optional[str]:
        """Extract YouTube video ID from various URL formats"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/|youtube\.com\/v\/)([^&\n?#]+)',
            r'youtube\.com.*[?&]v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, url)
            if match:
                return match.group(1)
        
        return None
    
    def validate_url(self, url: str) -> bool:
        """Validate YouTube URL format"""
        video_id = self.extract_video_id(url)
        return video_id is not None and len(video_id) == 11
    
    def extract_subtitle_text(self, subtitles_data: list) -> str:
        """Extract text from subtitle entries"""
        if not subtitles_data:
            return ""
        
        # Find the best subtitle format (prefer vtt, then srt)
        subtitle_url = None
        for sub in subtitles_data:
            if sub.get('ext') in ['vtt', 'srv3']:
                subtitle_url = sub.get('url')
                break
        
        if not subtitle_url and subtitles_data:
            subtitle_url = subtitles_data[0].get('url')
        
        if not subtitle_url:
            return ""
        
        try:
            # Download and parse subtitle content
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                # This is a simplified approach - in production you'd parse VTT/SRT properly
                return "Subtitle text extraction - Full implementation needed"
        except Exception as e:
            logger.error(f"Error extracting subtitle text: {e}")
            return ""
    
    def fetch_video_data(self, url: str) -> Optional[Dict]:
        """
        Fetch comprehensive video data including metadata and transcript
        """
        try:
            video_id = self.extract_video_id(url)
            if not video_id:
                raise ValueError("Invalid YouTube URL")
            
            with yt_dlp.YoutubeDL(self.ydl_opts) as ydl:
                # Extract video information
                info = ydl.extract_info(url, download=False)
                
                if not info:
                    raise ValueError("Could not extract video information")
                
                # Basic metadata
                title = info.get('title', 'Unknown Title')
                duration = info.get('duration', 0)
                description = info.get('description', '')
                uploader = info.get('uploader', 'Unknown')
                upload_date = info.get('upload_date', '')
                view_count = info.get('view_count', 0)
                
                # Check duration limit
                if duration > MAX_VIDEO_DURATION:
                    raise ValueError(f"Video too long ({duration}s). Maximum allowed: {MAX_VIDEO_DURATION}s")
                
                # Extract transcript
                transcript_text = ""
                subtitles = info.get('subtitles', {})
                auto_captions = info.get('automatic_captions', {})
                
                # Priority order: manual English > auto English > other manual > other auto
                for lang in [DEFAULT_LANGUAGE] + SUPPORTED_LANGUAGES:
                    if lang in subtitles:
                        transcript_text = self.extract_subtitle_text(subtitles[lang])
                        if transcript_text:
                            break
                
                if not transcript_text:
                    for lang in [DEFAULT_LANGUAGE] + SUPPORTED_LANGUAGES:
                        if lang in auto_captions:
                            transcript_text = self.extract_subtitle_text(auto_captions[lang])
                            if transcript_text:
                                break
                
                # Fallback transcript for demo purposes
                if not transcript_text:
                    # In a real implementation, you might use speech-to-text APIs
                    transcript_text = f"""
This is a demo transcript for the video: {title}

The video appears to be about {title.lower()} and was uploaded by {uploader}. 
The video is {duration} seconds long and has received {view_count} views.

This transcript would normally contain the actual spoken content from the video,
extracted from YouTube's subtitle data or generated using speech-to-text technology.

For a production system, you would implement proper subtitle parsing for VTT/SRT formats
or integrate with speech recognition APIs for videos without subtitles.

The video description begins with: {description[:200]}...
                    """.strip()
                
                return {
                    'video_id': video_id,
                    'title': title,
                    'transcript': transcript_text,
                    'duration': duration,
                    'url': url,
                    'description': description,
                    'uploader': uploader,
                    'upload_date': upload_date,
                    'view_count': view_count,
                    'language': DEFAULT_LANGUAGE,
                    'transcript_length': len(transcript_text)
                }
                
        except Exception as e:
            logger.error(f"Error processing video {url}: {e}")
            return None
    
    def get_video_info_quick(self, url: str) -> Optional[Dict]:
        """Get basic video info without transcript (faster)"""
        try:
            opts = {**self.ydl_opts, 'writesubtitles': False, 'writeautomaticsub': False}
            
            with yt_dlp.YoutubeDL(opts) as ydl:
                info = ydl.extract_info(url, download=False)
                
                return {
                    'video_id': self.extract_video_id(url),
                    'title': info.get('title', 'Unknown Title'),
                    'duration': info.get('duration', 0),
                    'uploader': info.get('uploader', 'Unknown'),
                    'view_count': info.get('view_count', 0)
                }
                
        except Exception as e:
            logger.error(f"Error getting video info for {url}: {e}")
            return None

# Global video processor instance
video_processor = VideoProcessor()