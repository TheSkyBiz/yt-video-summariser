# YouTube Video Summarizer 🎬

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.28+-red.svg)](https://streamlit.io/)
[![Gemini AI](https://img.shields.io/badge/Gemini-AI-orange.svg)](https://ai.google.dev/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

> Transform any YouTube video into actionable insights with AI-powered summarization and intelligent Q&A using Retrieval-Augmented Generation (RAG).

## 🌟 Overview

YouTube Video Summarizer is a sophisticated web application that leverages cutting-edge AI technologies to extract, process, and summarize YouTube video content. Built with modern Python frameworks and Google's Gemini AI, it provides users with instant video insights through intelligent summarization and contextual question-answering capabilities.

### 🎯 Key Highlights

- **🤖 AI-Powered**: Integrates Google Gemini 1.5 Flash for state-of-the-art text summarization
- **🔍 Smart Search**: FAISS vector database enables semantic search across video content
- **💬 Interactive Q&A**: Ask questions about any video and get contextually accurate answers
- **🔐 Secure Platform**: Enterprise-grade authentication with encrypted password storage
- **📊 Rich Analytics**: Comprehensive processing metrics and text statistics
- **📱 Modern UI**: Responsive Streamlit interface with intuitive navigation

## 🛠 Technical Architecture

### Core Technologies

| Layer | Technology | Purpose |
|-------|------------|---------|
| **Frontend** | Streamlit | Interactive web interface with real-time updates |
| **AI Engine** | Google Gemini API | Advanced text summarization and content analysis |
| **Vector Store** | FAISS + Sentence Transformers | Semantic similarity search and RAG implementation |
| **Video Processing** | yt-dlp | Robust YouTube transcript extraction |
| **Database** | SQLite3 | Efficient local data persistence |
| **Authentication** | bcrypt + SQLite | Secure user management system |

### System Architecture

```mermaid
graph TB
    A["User Interface<br/><b>Streamlit</b>"]:::ui
    B["Authentication Layer<br/><b>bcrypt + SQLite</b>"]:::auth
    C["Video Processor<br/><b>yt-dlp</b>"]:::video
    D["Text Processor<br/><b>Chunking + Cleaning</b>"]:::text
    E["Vector Store<br/><b>FAISS + Embeddings</b>"]:::vector
    F["AI Engine<br/><b>Gemini API</b>"]:::ai
    G["Database<br/><b>SQLite3</b>"]:::db

    A --> B
    B --> C
    C --> D
    D --> E
    E --> F
    F --> G

    classDef ui fill:#1976d2,stroke:#fff,stroke-width:2,color:#fff
    classDef auth fill:#f44336,stroke:#fff,stroke-width:2,color:#fff
    classDef video fill:#ffd600,stroke:#333,stroke-width:2,color:#333
    classDef text fill:#00c853,stroke:#fff,stroke-width:2,color:#fff
    classDef vector fill:#6a1b9a,stroke:#fff,stroke-width:2,color:#fff
    classDef ai fill:#f57c00,stroke:#fff,stroke-width:2,color:#fff
    classDef db fill:#263238,stroke:#ffe082,stroke-width:2,color:#ffe082

    class A ui
    class B auth
    class C video
    class D text
    class E vector
    class F ai
    class G db

```

## 🚀 Features

### 📹 Video Processing
- **Multi-format Support**: Handles various YouTube URL formats
- **Intelligent Extraction**: Automatic transcript detection and language processing
- **Quality Validation**: Checks video availability and content suitability
- **Metadata Enrichment**: Captures video title, duration, and additional information

### 🧠 AI-Powered Analysis
- **Dual Summarization**: Both concise (2-3 sentences) and detailed summaries
- **Context-Aware Q&A**: RAG-based question answering with source attribution
- **Key Insight Extraction**: Identifies main topics and learning points
- **Statistical Analysis**: Comprehensive text metrics and readability scores

### 👤 User Management
- **Secure Registration**: Password strength validation and secure hashing
- **Session Management**: Persistent login sessions with timeout protection
- **Personal History**: Complete processing history with searchable interface
- **Data Privacy**: User-isolated data storage and processing

### 🔍 Advanced Search
- **Semantic Search**: Vector-based similarity matching for precise results
- **Contextual Retrieval**: Intelligent chunk selection for Q&A responses
- **Score Ranking**: Similarity scores for result relevance assessment
- **Multi-query Support**: Handle complex questions across video content

## 📦 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- Google Generative AI API key ([Get one here](https://makersuite.google.com/app/apikey))
- Minimum 4GB RAM for optimal performance

### Quick Start

1. **Clone Repository**
```bash
git clone https://github.com/TheSkyBiz/yt-video-summariser.git
cd yt-video-summariser
```

2. **Environment Setup**
```bash
# Create virtual environment
python -m venv venv

# Activate environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

3. **Install Dependencies**
```bash
pip install -r requirements.txt
```

4. **Configuration**
```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your API key
echo "GOOGLE_API_KEY=your_api_key_here" > .env
```

5. **Launch Application**
```bash
streamlit run run.py
```

The application will be available at `http://localhost:8501`

## 🎮 Usage Guide

### Getting Started
1. **Account Creation**: Register with username and secure password
2. **Video Processing**: Paste any YouTube URL and click "Process Video"
3. **Review Results**: Explore generated summaries and video insights
4. **Interactive Q&A**: Ask questions about the video content
5. **History Management**: Access and review previously processed videos

### Supported Content
- ✅ Public YouTube videos with available transcripts
- ✅ Videos up to 2 hours in duration
- ✅ Multiple languages (auto-translated to English)
- ✅ Educational, entertainment, and professional content
- ❌ Private, age-restricted, or unavailable videos

### Pro Tips
- Use specific questions for better Q&A results
- Process shorter videos for faster performance
- Review transcript quality before asking detailed questions
- Save frequently accessed videos to your history

## 🏗 Project Structure

```
yt-video-summariser/
├── src/                     # Source code modules
│   ├── main.py             # Main Streamlit application
│   ├── config.py           # Configuration constants
│   ├── auth.py             # Authentication & session management
│   ├── video_handler.py    # YouTube video processing
│   ├── text_processor.py   # Text analysis & chunking
│   ├── embedding_store.py  # Vector operations & FAISS
│   ├── summarizer.py       # Gemini AI integration
│   └── db_utils.py         # Database operations
├── requirements.txt        # Python dependencies
├── run.py                 # Application entry point
├── .env.example           # Environment template
├── .gitignore            # Git ignore rules
└── README.md             # This documentation
```

## 🔧 Configuration Options

### Environment Variables
```env
# Required
GOOGLE_API_KEY=your_google_api_key

# Optional Customization
GENAI_MODEL=gemini-1.5-flash
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2
CHUNK_SIZE=1000
MAX_VIDEO_DURATION=7200
```

### Performance Tuning
- **Chunk Size**: Adjust text chunk size for processing (500-2000 characters)
- **Vector Dimensions**: Modify embedding model for accuracy vs. speed trade-offs
- **Database Path**: Configure custom database location
- **API Limits**: Set rate limiting for API calls

## 📊 Performance Metrics

### Processing Benchmarks
| Video Length | Processing Time | Memory Usage | API Calls |
|--------------|-----------------|--------------|-----------|
| 5 minutes    | ~30 seconds     | 150MB        | 2-3       |
| 15 minutes   | ~45 seconds     | 200MB        | 3-4       |
| 30 minutes   | ~60 seconds     | 300MB        | 4-6       |
| 60 minutes   | ~90 seconds     | 450MB        | 6-8       |

### System Requirements
- **Minimum**: 4GB RAM, 2GB storage
- **Recommended**: 8GB RAM, 5GB storage
- **Network**: Stable internet for API calls and video processing

## 🔒 Security Features

### Data Protection
- **Password Security**: bcrypt hashing with salt
- **SQL Injection Prevention**: Parameterized queries
- **Session Security**: Timeout-based session management
- **Input Validation**: Comprehensive sanitization of user inputs

### Privacy Measures
- **Local Storage**: All data stored locally in SQLite
- **User Isolation**: Complete data separation between users
- **API Security**: Secure API key management
- **No Data Sharing**: No external data transmission except API calls

## 🛣 Roadmap & Future Enhancements

### Phase 1: Current Features ✅
- [x] Core video processing and summarization
- [x] User authentication and session management
- [x] RAG-based Q&A system
- [x] History management and search

### Phase 2: Enhanced Capabilities 🔄
- [ ] **Multi-language Support**: Process non-English videos
- [ ] **Batch Processing**: Handle multiple videos simultaneously
- [ ] **Export Options**: PDF, Word, and JSON export formats
- [ ] **Advanced Analytics**: Usage statistics and insights
- [ ] **API Integration**: RESTful API for external applications

### Phase 3: Enterprise Features 🔮
- [ ] **Team Collaboration**: Shared workspaces and video libraries
- [ ] **Custom Models**: Fine-tuned summarization models
- [ ] **Integration Plugins**: WordPress, Notion, and other platforms
- [ ] **Mobile Application**: iOS and Android native apps
- [ ] **Cloud Deployment**: Scalable cloud infrastructure

## 🤝 Contributing

We welcome contributions from the community! Here's how you can help:

### Development Setup
```bash
# Fork and clone the repository
git clone https://github.com/yourusername/yt-video-summariser.git

# Create feature branch
git checkout -b feature/your-feature-name

# Make changes and commit
git commit -m "Add: your feature description"

# Push and create pull request
git push origin feature/your-feature-name
```

### Contribution Guidelines
- Follow PEP 8 Python style guidelines
- Add comprehensive docstrings and comments
- Include unit tests for new features
- Update documentation for significant changes
- Ensure backward compatibility when possible

### Areas for Contribution
- 🐛 Bug fixes and performance improvements
- 📚 Documentation enhancements
- 🧪 Unit test coverage expansion
- 🎨 UI/UX improvements
- 🔧 New feature development

## 📄 License & Legal

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

### Third-Party Licenses
- **Streamlit**: Apache 2.0 License
- **Google Generative AI**: Google AI Terms of Service
- **FAISS**: MIT License
- **yt-dlp**: Unlicense/Public Domain

## 👨‍💻 About the Developer

**Aakash Biswas** - Full Stack Developer & AI Enthusiast

- 🌐 **Portfolio**: [github.com/TheSkyBiz](https://github.com/TheSkyBiz)
- 💼 **LinkedIn**: Connect for professional opportunities
- 📧 **Email**: Available for collaboration and questions

### Technical Skills Demonstrated
- **Backend Development**: Python, SQLite, API Integration
- **Frontend Development**: Streamlit, Responsive UI Design
- **AI/ML Integration**: LLMs, Vector Databases, RAG Systems
- **DevOps**: Environment Management, Documentation
- **Security**: Authentication, Data Protection, Input Validation

## 🙋‍♂️ Support & FAQ

### Common Issues

**Q: "Invalid API key" error**
A: Ensure your Google AI API key is correctly set in the `.env` file and has proper permissions.

**Q: Video processing fails**
A: Check if the video has available transcripts and is publicly accessible.

**Q: Slow processing times**
A: Consider processing shorter videos or upgrading system RAM for better performance.

**Q: Database errors**
A: Delete the `app.db` file to reset the database (will lose user data).

### Getting Help
- 📖 Check the documentation in this README
- 🐛 Report bugs via GitHub Issues
- 💬 Join discussions in GitHub Discussions
- 📧 Contact the developer for urgent issues

## 🎉 Acknowledgments

Special thanks to:
- **Google AI Team** for the powerful Gemini API
- **Streamlit Community** for the excellent web framework
- **yt-dlp Developers** for robust video processing tools
- **FAISS Team** for efficient vector search capabilities
- **Open Source Community** for continuous inspiration and support

---

<div align="center">

**⭐ If this project helped you, please consider giving it a star!**

[🐛 Report Bug](https://github.com/TheSkyBiz/yt-video-summariser/issues) • [✨ Request Feature](https://github.com/TheSkyBiz/yt-video-summariser/issues) • [🤝 Contribute](https://github.com/TheSkyBiz/yt-video-summariser/pulls)

**Made with ❤️ by Aakash Biswas**

</div>
