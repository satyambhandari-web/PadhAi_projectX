# 📚 PadhAI – Smart Student Educational Content Generator

PadhAI is an AI-powered educational assistant that helps students learn more efficiently by generating summaries, notes, quizzes, and flashcards from uploaded PDF documents using Retrieval-Augmented Generation (RAG) and Large Language Models (LLMs).

---

## 🚀 Features

- 📄 Upload PDF study materials
- 📝 AI-generated summaries
- 📚 Automatic study notes
- ❓ Quiz generation
- 🧠 Flashcard generation
- 🔍 Retrieval-Augmented Generation (RAG)
- 🤖 Powered by Gemini Embeddings and Groq LLM
- 🌐 Web interface using HTML & CSS
- 🐍 Flask backend

---

## 🛠️ Tech Stack

### Frontend
- HTML5
- CSS3

### Backend
- Python
- Flask

### AI & RAG
- LangChain
- LangChain Community
- ChromaDB
- Google Gemini Embeddings
- Groq API
- PyPDFLoader

### Environment
- Python Virtual Environment (venv)

---

## 📂 Project Structure

```text
PadhAI/
│
├── app/
│   ├── agents/
│   ├── services/
│   ├── workflows/
│   ├── utils/
│   └── main.py
│
├── frontend/
│   ├── templates/
│   │   ├── index.html
│   │   ├── upload.html
│   │   ├── summary.html
│   │   ├── notes.html
│   │   ├── quiz.html
│   │   └── flashcards.html
│   │
│   └── static/
│       ├── css/
│       └── images/
│
├── uploads/
├── generated/
├── rag_chroma_db/
├── .env
├── requirements.txt
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/PadhAI.git
```

### 2. Move into the project

```bash
cd PadhAI
```

### 3. Create a virtual environment

```bash
python -m venv venv
```

### 4. Activate the virtual environment

Windows

```bash
venv\Scripts\activate
```

Linux/macOS

```bash
source venv/bin/activate
```

### 5. Install dependencies

```bash
pip install -r requirements.txt
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root.

```env
GOOGLE_API_KEY=your_google_api_key
GROQ_API_KEY=your_groq_api_key
```

---

## ▶️ Run the Application

```bash
python app/main.py
```

Open your browser:

```
http://127.0.0.1:5000
```

---

## 📖 How It Works

1. Upload a PDF document.
2. The PDF is processed using PyPDFLoader.
3. The document is split into chunks.
4. Gemini Embeddings generate vector embeddings.
5. ChromaDB stores the embeddings.
6. RAG retrieves relevant document chunks.
7. Groq LLM generates:
   - Summary
   - Notes
   - Quiz
   - Flashcards
8. Results are displayed in the web interface.

---

## 📌 Current Progress

- ✅ Backend project structure
- ✅ Virtual environment setup
- ✅ Requirements file
- ✅ Flask application
- ✅ HTML & CSS frontend
- ✅ PDF processing
- ✅ RAG pipeline
- ✅ Chroma vector database
- ✅ Summary Agent
- 🚧 Notes Agent
- 🚧 Quiz Agent
- 🚧 Flashcards Agent

---

## 📷 Screenshots

Add screenshots here after completing the UI.

Example:

```
screenshots/
    home.png
    upload.png
    summary.png
```

---

## 🔮 Future Enhancements

- User authentication
- Multiple PDF support
- Download generated notes
- MCQ evaluation
- Dark mode
- Voice-based learning assistant
- Chat with uploaded PDF
- Multi-agent workflow

---

## 👨‍💻 Author

**Satyam**

B.Tech Student

Agentic AI Project – PadhAI

---

## 📄 License

This project is developed for educational purposes.