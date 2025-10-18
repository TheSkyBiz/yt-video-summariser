"""
YouTube video processing using yt-dlp
"""
from typing import Dict, Optional
import yt_dlp
import re
import logging
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
        """
        Extract YouTube video ID from various URL formats
        """
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
    
    def _extract_subtitle_text(self, subtitles_data: list) -> str:
        """
        Extract text from subtitle entries.
        Note: Implement VTT/SRT fetch + parse if needed. This returns empty string
        when not available and the app will fall back to a demo transcript.
        """
        if not subtitles_data:
            return ""
        # Choose first available subtitle URL (prefer vtt)
        subtitle_url = None
        for sub in subtitles_data:
            if sub.get('ext') in ['vtt', 'srv3', 'srt']:
                subtitle_url = sub.get('url')
                break
        if not subtitle_url and subtitles_data:
            subtitle_url = subtitles_data[0].get('url')
        if not subtitle_url:
            return ""
        # For now, we do not download; return empty so app uses fallback
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
                info = ydl.extract_info(url, download=False)
                if not info:
                    raise ValueError("Could not extract video information")
                
                # Safe metadata extraction with None-handling
                title = info.get('title') or 'Unknown Title'
                duration = info.get('duration') or 0
                description = info.get('description') or ''
                uploader = info.get('uploader') or 'Unknown'
                upload_date = info.get('upload_date') or ''
                view_count = info.get('view_count') or 0
                
                # Duration check
                if duration and duration > MAX_VIDEO_DURATION:
                    raise ValueError(f"Video too long ({duration}s). Maximum allowed: {MAX_VIDEO_DURATION}s")
                
                # Transcript extraction
                transcript_text = ""
                subtitles = info.get('subtitles', {})
                auto_captions = info.get('automatic_captions', {})
                
                # Priority: manual EN > auto EN > other manual > other auto
                for lang in [DEFAULT_LANGUAGE] + SUPPORTED_LANGUAGES:
                    if lang in subtitles:
                        transcript_text = self._extract_subtitle_text(subtitles[lang])
                        if transcript_text:
                            break
                if not transcript_text:
                    for lang in [DEFAULT_LANGUAGE] + SUPPORTED_LANGUAGES:
                        if lang in auto_captions:
                            transcript_text = self._extract_subtitle_text(auto_captions[lang])
                            if transcript_text:
                                break
                
                # Fallback transcript for demo
                if not transcript_text:
                    title_safe = title or "this video"
                    transcript_text = (
                        f"This is a demo transcript for the video: {title_safe}\n\n"
                        f"The video appears to be about {title_safe.lower()} and was uploaded by {uploader}. "
                        f"The video is {duration} seconds long and has received {view_count} views.\n\n"
                        "This transcript would normally contain the actual spoken content from the video, "
                        "extracted from YouTube's subtitles or generated via speech-to-text."
                    )
                
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
                    'title': info.get('title') or 'Unknown Title',
                    'duration': info.get('duration') or 0,
                    'uploader': info.get('uploader') or 'Unknown',
                    'view_count': info.get('view_count') or 0
                }
        except Exception as e:
            logger.error(f"Error getting video info for {url}: {e}")
            return None

# Global video processor instance
video_processor = VideoProcessor()
