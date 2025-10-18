# YouTube Video Summarizer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/) [![Streamlit](https://img.shields.io/badge/Streamlit-Latest-red.svg)](https://streamlit.io/) [![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

AI-powered YouTube video summarization with semantic search and enhanced Q&A (RAG) using a clean, modular architecture.

---

## Key Features
- **Summaries:** Short (2–3 sentences) and detailed paragraph-level summaries using Gemini.
- **Rich Q&A (Enhanced RAG):** Multi-query retrieval, larger context window, and improved prompting for comprehensive answers.
- **Transcript Processing:** yt-dlp for captions/metadata, cleaning, chunking, vectorization.
- **Semantic Search:** FAISS + Sentence-Transformers for fast and relevant retrieval.
- **User Accounts:** Login/Signup with bcrypt hashing, per-user history (videos, summaries, Q&A).
- **Local Persistence:** SQLite database; FAISS index saved locally.

---

## Architecture
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
Enhanced Retriever → Comprehensive Context Builder
      │
      ▼
Summariser (Gemini 2.0 Flash) → Summaries & Q&A
      │
      ▼
SQLite DB (users, videos, summaries, qa_history)
```

---

## Tech Stack
- **Frontend:** Streamlit
- **LLM:** Google Gemini 2.0 Flash (configurable)
- **Embeddings:** Sentence-Transformers (all-MiniLM-L6-v2)
- **Vector DB:** FAISS (CPU)
- **Video:** yt-dlp (captions + metadata)
- **Database:** SQLite3
- **Auth:** bcrypt + session state

---

## Quick Start
```bash
git clone https://github.com/TheSkyBiz/yt-video-summariser.git
cd yt-video-summariser
pip install -r requirements.txt
cp .env.example .env   # add your GOOGLE_API_KEY
streamlit run run.py
```

---

## Configuration
Edit `src/config.py` to tune behavior.

```python
# Model
GENAI_MODEL_NAME = "gemini-2.0-flash"  # change if needed
MAX_TOKENS = 8192
TEMPERATURE = 0.3

# Embeddings / Vector store
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"
INDEX_DIR = "faiss_index"

# RAG Enhancements
RAG_CHUNK_RETRIEVAL = 8        # number of chunks retrieved
RAG_MAX_CONTEXT_LENGTH = 8000  # characters combined into context
RAG_MIN_SIMILARITY = 0.3       # similarity cutoff for filtering
```

Environment (.env):
```env
GOOGLE_API_KEY=your_key_here
```

---

## Project Structure
```
yt-video-summariser/
├── src/
│   ├── main.py              # Streamlit app + pages
│   ├── config.py            # Constants & settings (incl. RAG knobs)
│   ├── auth.py              # Authentication/session
│   ├── video_handler.py     # yt-dlp processing (captions + metadata)
│   ├── text_processor.py    # Cleaning & chunking
│   ├── embedding_store.py   # Embeddings + FAISS + enhanced retrieval
│   ├── summariser.py        # Gemini prompts, summaries, Q&A
│   └── db_utils.py          # SQLite schema & queries
├── requirements.txt
├── run.py                   # App entry point
├── .env.example
├── LICENSE
└── README.md
```

---

## Usage
1. **Login/Signup** to enable saving history.
2. **Paste YouTube URL** and click “Process Video”.
3. Review **Short** and **Detailed** summaries.
4. Ask **Questions** about the video; the app retrieves a comprehensive context and generates detailed answers.
5. Browse your **History** (videos, summaries, Q&A) anytime.

---

## What’s Implemented (as of now)
- End-to-end pipeline: URL → transcript → chunks → FAISS → summaries → Q&A → DB.
- Enhanced RAG: multi-query expansion, top‑k with similarity filtering, large context building, deduplication.
- Safer yt-dlp handling with None-safe metadata defaults and demo transcript fallback.
- Robust Streamlit UI with metrics (response time, context size), and full-context expander.
- Strong auth + SQLite schema (users, videos, summaries, qa_history).
- Configurable model and RAG knobs via `config.py`.

---

## Known Limitations
- **Captions Availability:** If YouTube captions are missing/blocked, the app will fall back to a demo transcript, which reduces Q&A quality.
- **Subtitle Parsing:** Current implementation does not fully parse and download VTT/SRT files—can be improved for more accurate transcripts.
- **Long Videos:** Very long videos may exceed the maximum combined context window; answers are only as good as retrieved segments.

---

## Roadmap / Improvements
- **Reliable Caption Ingestion**
  - Download .vtt/.srt with yt-dlp and parse to plain text (timestamps → sentences).
  - Optional ASR fallback (e.g., Whisper) when captions are unavailable.
- **Richer Retrieval**
  - Adjacent-chunk stitching (windowed retrieval around top hits).
  - Query re-writing (hyDE / LLM-guided queries) for better recall.
  - Per-video vector stores with metadata filters (speaker/section).
- **Citations & Explainability**
  - Inline citations with timestamps and quote spans.
  - “Jump to moment” links using YouTube timecodes.
- **Multi-turn Chat**
  - Conversational memory (carry context over turns) with re-ranking.
  - Follow-up question suggestions.
- **Analytics & Export**
  - Export summaries/Q&A as Markdown/PDF.
  - Per-video analytics (topic clouds, sentiment, named entities).
- **Deployment**
  - Dockerfile and one-click deploy (Streamlit Cloud / Hugging Face / Fly.io).
  - Caching layer for repeated queries.
- **Security & DX**
  - Rate limiting and API key validation on boot.
  - Add unit tests for chunking/retrieval and a small integration test.

---

## Troubleshooting
- "404 model not found": set `GENAI_MODEL_NAME` to a model you see in `genai.list_models()` (e.g., `gemini-2.0-flash` or `gemini-1.5-pro`).
- Poor Q&A quality: make sure real captions were ingested (not the demo fallback). Increase `RAG_CHUNK_RETRIEVAL` and `RAG_MAX_CONTEXT_LENGTH`.
- Import errors: confirm `src/__init__.py` exists and run `streamlit run run.py` from project root.

---

## License
MIT — see `LICENSE` for details.

## Author
**Aakash Biswas** — https://github.com/TheSkyBiz
