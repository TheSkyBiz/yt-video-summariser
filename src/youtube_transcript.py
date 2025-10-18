from urllib.parse import urlparse, parse_qs
from youtube_transcript_api import YouTubeTranscriptApi
import streamlit as st

def extract_video_id(url: str) -> str:
    """
    Extracts the YouTube video ID from different types of YouTube URLs.
    """
    parsed = urlparse(url)
    if parsed.hostname == 'youtu.be':
        return parsed.path[1:]
    if parsed.hostname in ('www.youtube.com', 'youtube.com'):
        if parsed.path == '/watch':
            return parse_qs(parsed.query).get('v', [None])[0]
        if parsed.path.startswith('/embed/'):
            return parsed.path.split('/')[2]
        if parsed.path.startswith('/v/'):
            return parsed.path.split('/')[2]
    return None

def transcribe_video(video_id: str):
    """
    Fetches and translates the transcript of a YouTube video.
    Returns a dictionary with translated, original transcript and language info.
    """
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
        transcript = transcript_list.find_transcript(['en'])  # try English first
        translated = transcript.translate('en').fetch()
        return {
            'translated': ' '.join([i['text'] for i in translated]),
            'original': ' '.join([i['text'] for i in transcript.fetch()]),
            'language': transcript.language
        }

    except:
        try:
            # fallback: pick first available transcript and translate
            transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)
            transcript = transcript_list.find_transcript([t.language_code for t in transcript_list])
            translated = transcript.translate('en').fetch()
            return {
                'translated': ' '.join([i['text'] for i in translated]),
                'original': ' '.join([i['text'] for i in transcript.fetch()]),
                'language': transcript.language
            }

        except Exception as e:
            st.error("🚨 Transcript is not available for the given video.")
            return None
