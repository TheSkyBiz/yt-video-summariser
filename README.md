# YouTube Video Summarizer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/) [![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)](https://streamlit.io/) [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

AI-powered YouTube video summarization with semantic search and Q&A using a clean, modular architecture.

## What it does
- Generate short and detailed AI summaries
- Ask questions with context-aware answers (RAG)
- Save user history with secure authentication

## Tech stack
- Frontend: Streamlit
- AI: Google Gemini 1.5 Flash
- Vector search: FAISS + Sentence-Transformers (all-MiniLM-L6-v2)
- Video: yt-dlp (metadata + transcripts)
- Database: SQLite3
- Auth: bcrypt password hashing

## System architecture
```
User (Streamlit UI)
      │
      ▼
Video Handler (yt-dlp) → Transcript/Metadata
      │
      ▼
Text Processor → Cleaning + Chunking
      │
      ▼
Embedding Store (Sentence-Transformers → FAISS)
      │
      ▼
Retriever → Top‑k relevant chunks
      │
      ▼
Summarizer (Gemini 1.5 Flash) → Summaries & Q&A
      │
      ▼
SQLite DB (users, videos, summaries, qa_history)
```

## Quick start
```bash
git clone https://github.com/TheSkyBiz/yt-video-summariser.git
cd yt-video-summariser
pip install -r requirements.txt
cp .env.example .env   # add your GOOGLE_API_KEY
streamlit run run.py
```

## How to use
- Register/Login in the app
- Paste a YouTube URL and click Process
- Read short and detailed summaries
- Ask questions (RAG-based answers)
- Revisit from History anytime

## Project structure
```
yt-video-summariser/
├── src/
│   ├── main.py              # Streamlit app + pages
│   ├── config.py            # Constants & settings
│   ├── auth.py              # Authentication/session
│   ├── video_handler.py     # yt-dlp processing
│   ├── text_processor.py    # Cleaning & chunking
│   ├── embedding_store.py   # Embeddings + FAISS
│   ├── summarizer.py        # Gemini prompts
│   └── db_utils.py          # SQLite models/queries
├── requirements.txt
├── run.py
├── .env.example
├── LICENSE
└── README.md
```

## Requirements
- Python 3.8+
- Google Generative AI API key
- 4GB RAM (8GB recommended)

## Environment
```env
GOOGLE_API_KEY=your_key
GENAI_MODEL=gemini-1.5-flash
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
```

## Supported videos
- Public YouTube videos with transcripts
- Up to ~2 hours
- Multi-language (auto-translated to English)

## License
MIT — see LICENSE for details.

## Author
Aakash Biswas — https://github.com/TheSkyBiz
