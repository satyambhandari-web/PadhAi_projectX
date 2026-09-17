# 📚 PadhAi - AI Powered Student Learning Assistant

<p align="center">

<img src="https://img.shields.io/badge/Python-3.12+-blue?logo=python">
<img src="https://img.shields.io/badge/Framework-FastAPI-009688?logo=fastapi">
<img src="https://img.shields.io/badge/AI-LangGraph-orange">
<img src="https://img.shields.io/badge/LLM-Groq-black?logo=groq">
<img src="https://img.shields.io/badge/RAG-ChromaDB-purple">
<img src="https://img.shields.io/badge/TTS-gTTS-green">

</p>

<p align="center">

<b>Learn Smarter. Generate Faster. Study Better.</b>

</p>

---

# 📌 About PadhAi

**PadhAi** is an AI-powered student learning assistant that converts PDF study materials into intelligent and interactive learning resources.

Students can upload their study material and use AI to generate:

* 📝 Summaries
* 📚 Study Notes
* ❓ Practice Quizzes / MCQs
* 🧠 Flashcards
* 📖 Educational Content
* 💬 AI-powered questions and answers
* 🔊 Text-to-Speech learning content

PadhAi combines **Retrieval-Augmented Generation (RAG)**, **Large Language Models (LLMs)**, **Vector Databases**, and **Agentic AI workflows** to create a personalized learning experience.

---

# ✨ Features

## 📄 PDF Based Learning

✅ Upload study PDFs
✅ Extract content from documents
✅ Process and chunk PDF text
✅ Create a searchable AI knowledge base
✅ Generate learning resources from uploaded material

---

## 🤖 AI Content Generation

| Feature              | Description                                   |
| -------------------- | --------------------------------------------- |
| 📝 Summary Generator | Creates concise summaries from study material |
| 📚 Notes Generator   | Generates structured and exam-oriented notes  |
| ❓ Quiz Generator     | Creates practice questions and MCQs           |
| 🧠 Flashcards        | Generates quick revision flashcards           |
| 📖 Content Generator | Generates educational explanations            |
| 💬 AI Chat           | Answers questions using study material        |

---

## 🔍 RAG Based AI System

PadhAi uses **Retrieval-Augmented Generation (RAG)** to retrieve relevant information from uploaded study materials before generating AI responses.

```text
PDF Upload
     |
     ↓
PDF Text Extraction
     |
     ↓
Text Chunking
     |
     ↓
Gemini Embeddings
     |
     ↓
ChromaDB Vector Database
     |
     ↓
Relevant Context Retrieval
     |
     ↓
Groq LLM
     |
     ↓
AI Generated Learning Content
```

---

# 🤖 Agentic AI Workflow

PadhAi uses **LangGraph** to organize AI tasks into specialized agents.

```text
                    User Request
                         |
                         ↓
                  LangGraph Workflow
                         |
        --------------------------------
        |        |        |       |     |
        ↓        ↓        ↓       ↓     ↓
     Summary    Notes    Quiz  Flashcard Content
      Agent     Agent   Agent    Agent    Agent
        |        |        |       |       |
        --------------------------------
                         |
                         ↓
                   Generated Output
```

The system includes specialized agents for:

* 📝 Summary
* 📚 Notes
* ❓ Quiz
* 🧠 Flashcards
* 📖 Educational Content

---

# 🏗️ Project Architecture

```text
                       User
                         |
                         ↓
                 HTML/CSS/JavaScript
                         |
                         ↓
                    FastAPI
                    Backend
                         |
              ---------------------
              |                   |
              ↓                   ↓
        PDF Processing       AI Workflow
              |                   |
              ↓                   ↓
          Text Chunks        LangGraph
              |                   |
              ↓          -------------------
          Embeddings      |    |    |    |
              |           ↓    ↓    ↓    ↓
              ↓        Notes Quiz Summary
          ChromaDB          Flashcards
              |                   |
              ---------------------
                         |
                         ↓
                      Groq LLM
                         |
                         ↓
                 Generated Content
                         |
                         ↓
                       gTTS
                         |
                         ↓
                  Voice Learning
```

---

# 🛠️ Tech Stack

## Frontend

* HTML5
* CSS3
* JavaScript

## Backend

* Python
* FastAPI
* Uvicorn
* Pydantic

## AI / ML

* LangChain
* LangGraph
* Groq API
* Google Gemini Embeddings
* Retrieval-Augmented Generation (RAG)

## Database

* ChromaDB

## PDF Processing

* PyPDF
* PDF text extraction
* Text chunking

## Text-to-Speech

* gTTS (Google Text-to-Speech)

---

# 📂 Project Structure

```text
PadhAi/
│
├── backend/
│   │
│   ├── app/
│   │   ├── agents/
│   │   │   ├── summary_agent.py
│   │   │   ├── notes_agent.py
│   │   │   ├── quiz_agent.py
│   │   │   ├── flashcard_agent.py
│   │   │   └── content_generator_agent.py
│   │   │
│   │   ├── services/
│   │   │   ├── rag_service.py
│   │   │   ├── pdf_service.py
│   │   │   ├── llm_service.py
│   │   │   ├── embeddings.py
│   │   │   └── tts_service.py
│   │   │
│   │   ├── workflows/
│   │   │   └── workflow.py
│   │   │
│   │   └── main.py
│   │
│   ├── materials/
│   ├── generated/
│   ├── audio/
│   └── requirements.txt
│
├── frontend/
│   │
│   ├── assets/
│   ├── css/
│   │   └── style.css
│   │
│   ├── js/
│   │   └── script.js
│   │
│   └── index.html
│
├── rag_chroma_db/
│
├── .gitignore
└── README.md
```

---

# ⚙️ Installation

## Clone Repository

```bash
git clone https://github.com/yourusername/PadhAi.git
```

## Navigate Project

```bash
cd PadhAi
```

## Create Virtual Environment

```bash
py -3.12 -m venv .venv
```

## Activate Environment

Windows:

```powershell
.venv\Scripts\activate
```

Linux/macOS:

```bash
source .venv/bin/activate
```

## Install Dependencies

```bash
pip install -r backend/requirements.txt
```

---

# 🔑 Environment Variables

Create a `.env` file and add your API keys:

```env
GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key
```

⚠️ **Never upload your `.env` file or API keys to GitHub.**

---

# ▶️ Run Application

## Start Backend

Navigate to the backend:

```bash
cd backend
```

Run FastAPI:

```bash
uvicorn app.main:app --reload
```

Backend will run at:

```text
http://127.0.0.1:8000
```

API documentation:

```text
http://127.0.0.1:8000/docs
```

---

## Start Frontend

Open another terminal:

```bash
cd frontend
```

Run the frontend server:

```bash
python -m http.server 5500
```

Open:

```text
http://localhost:5500
```

---

# 🔌 API Endpoints

| Endpoint             | Method   | Purpose                       |
| -------------------- | -------- | ----------------------------- |
| `/upload`            | POST     | Upload PDF                    |
| `/api/uploads`       | GET      | Get uploaded materials        |
| `/api/materials`     | GET      | Get available study materials |
| `/api/chat`          | POST     | Chat with study material      |
| `/api/workflow`      | POST     | Run AI workflow               |
| `/api/analyze`       | POST     | Analyze study material        |
| `/api/notes`         | GET/POST | Generate notes                |
| `/api/summary`       | GET/POST | Generate summaries            |
| `/api/quiz`          | GET/POST | Generate quizzes              |
| `/api/flashcards`    | GET/POST | Generate flashcards           |
| `/api/content`       | GET/POST | Generate educational content  |
| `/api/tts`           | POST     | Generate speech               |
| `/api/tts/languages` | GET      | Get available TTS languages   |

For the complete API specification, open:

```text
http://127.0.0.1:8000/docs
```

---

# 🔄 How PadhAi Works

### 1️⃣ Upload

Student uploads a PDF containing study material.

### 2️⃣ Process

The backend extracts text from the uploaded document.

### 3️⃣ Chunk

The extracted text is divided into smaller chunks.

### 4️⃣ Embed

The chunks are converted into vector embeddings using Gemini embeddings.

### 5️⃣ Store

The embeddings are stored inside ChromaDB.

### 6️⃣ Retrieve

Relevant information is retrieved from the vector database when the student asks a question or requests learning content.

### 7️⃣ Generate

The retrieved context is passed to the AI workflow and Groq LLM.

### 8️⃣ Learn

The generated output is displayed as:

```text
Summary
Notes
Quiz
Flashcards
Educational Content
```

### 9️⃣ Listen

Text can also be converted into speech using gTTS.

---

# 📊 Development Status

| Component               | Status |
| ----------------------- | ------ |
| FastAPI Backend         | ✅      |
| Frontend UI             | ✅      |
| PDF Upload              | ✅      |
| PDF Processing          | ✅      |
| RAG Pipeline            | ✅      |
| ChromaDB                | ✅      |
| Gemini Embeddings       | ✅      |
| Groq LLM                | ✅      |
| Summary Agent           | ✅      |
| Notes Agent             | ✅      |
| Quiz Agent              | ✅      |
| Flashcard Agent         | ✅      |
| Content Generator Agent | ✅      |
| Text-to-Speech          | ✅      |


---

# 📸 Screenshots

Add your project screenshots here:

```text
screenshots/
│
├── dashboard.png
├── upload.png
├── summary.png
├── notes.png
├── quiz.png
├── flashcards.png
└── chat.png
```

Example:

```markdown
![PadhAi Dashboard](screenshots/dashboard.png)
```

---

# 🚀 Future Roadmap

## 📚 Learning Features

* [ ] Chat with multiple PDFs
* [ ] Personalized study plans
* [ ] AI Tutor Mode
* [ ] Difficulty-based quizzes
* [ ] Student progress tracking
* [ ] Score history
* [ ] Personalized revision recommendations

## 🌐 Accessibility & Language

* [ ] Multi-language AI responses
* [ ] More TTS languages
* [ ] Voice-based learning assistant
* [ ] Improved accessibility

## 📤 Export

* [ ] Export notes as PDF
* [ ] Export notes as DOCX
* [ ] Download quizzes
* [ ] Download flashcards

## ☁️ Platform Improvements

* [ ] User authentication
* [ ] Cloud deployment
* [ ] Cloud vector database
* [ ] Persistent student profiles
* [ ] Usage analytics

---

# 👨‍💻 Team

### Team PadhAi

Developed by:

* **Satyam**
* **Om**
* **Ritesh**

**B.Tech Computer Science Engineering**

**Agentic AI Project**

---

# 🤝 Contribution

Contributions are welcome!

1. Fork this repository
2. Create a new branch

```bash
git checkout -b feature/new-feature
```

3. Make your changes
4. Commit your changes

```bash
git commit -m "Add new feature"
```

5. Push your branch

```bash
git push origin feature/new-feature
```

6. Create a Pull Request

---

# 📄 License

This project is created for **educational and academic purposes**.

---

<p align="center">

Made with ❤️ using Python, FastAPI, LangGraph, RAG, ChromaDB & Generative AI

</p>
