PadhAi --- Smart Student Educational Content Generator

<p align="center">

<strong>{=html}Learn Smarter. Revise Faster. Perform
Better.</strong>{=html}

</p>

<p align="center">

An AI-powered learning platform that transforms PDF study material into
summaries, exam-ready notes, quizzes, flashcards, educational content,
and voice output.

</p>

<p align="center">

<img src="https://img.shields.io/badge/Python-3.10%2B-blue?logo=python" alt="Python">{=html}
<img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi" alt="FastAPI">{=html}
<img src="https://img.shields.io/badge/LangGraph-Agentic%20Workflow-orange" alt="LangGraph">{=html}
<img src="https://img.shields.io/badge/RAG-ChromaDB-purple" alt="RAG">{=html}
<img src="https://img.shields.io/badge/LLM-Groq-black" alt="Groq">{=html}
<img src="https://img.shields.io/badge/Embeddings-Google%20Gemini-blue" alt="Gemini">{=html}

</p>

🚀 Overview

PadhAi is a student-focused AI learning assistant designed to turn
ordinary study PDFs into interactive learning resources.

Instead of manually reading large documents and preparing revision
material, students can upload a PDF and use AI-powered workflows to
generate:

📝 Concise summaries

📚 Detailed exam-ready notes

❓ Practice quizzes / MCQs

🧠 Flashcards

📖 Educational explanations and learning content

💬 Questions and answers based on study material

🔊 Text-to-speech audio

The application combines Retrieval-Augmented Generation (RAG),
vector search, Large Language Models, and an agentic workflow
powered by LangGraph.

🎯 Problem

Students often spend significant time converting lengthy PDFs, lecture
notes, and reference material into useful revision resources.

PadhAi aims to reduce this effort by providing a single platform where
students can:

Upload their study material.

Process the PDF automatically.

Retrieve relevant information from the material.

Generate different types of learning content.

Revise using summaries, notes, quizzes, and flashcards.

Listen to generated content using text-to-speech.

✨ Key Features

📄 PDF Upload & Processing

Upload PDF study material through the web interface.

Extract text from uploaded PDFs.

Store uploaded materials for later use.

Process documents for AI-powered content generation.

🧠 Retrieval-Augmented Generation

PadhAi uses RAG to ground AI responses in uploaded study material.

The pipeline is:

PDF
 ↓
PDF Text Extraction
 ↓
Text Chunking
 ↓
Google Gemini Embeddings
 ↓
ChromaDB Vector Store
 ↓
Semantic Retrieval
 ↓
Groq LLM
 ↓
Context-Aware Response

This allows the system to retrieve relevant document content before
generating an answer.

🤖 Agentic AI Workflow

PadhAi uses LangGraph to route requests to specialized AI agents.

                    User Request
                         │
                         ▼
                  LangGraph Router
                         │
       ┌─────────┬───────┼───────┬──────────┐
       ▼         ▼       ▼       ▼          ▼
   Summary     Notes    Quiz  Flashcards  Content
     Agent      Agent   Agent    Agent      Agent
       └─────────┴───────┼───────┴──────────┘
                         ▼
                    Generated Output

Specialized agents include:

SummaryAgent

NotesAgent

QuizAgent

FlashcardAgent

ContentGeneratorAgent

💬 Study Material Chat

Students can ask questions about selected study material and receive
AI-generated answers using the available document context.

🔊 Text-to-Speech

Generated text can be converted into audio using gTTS, allowing
students to listen to learning content.

🎨 Student-Friendly Interface

The frontend provides:

Dashboard

Uploaded material management

Learning content generation

Chat interface

Settings

Light/dark appearance

Golden/white and charcoal/gold visual design

🛠️ Technology Stack

Frontend

HTML5

CSS3

JavaScript

XMLHttpRequest / Fetch API

Backend

Python

FastAPI

Uvicorn

Pydantic

Python-dotenv

Python Multipart

AI & Agentic Layer

LangChain

LangGraph

Groq LLM

Google Gemini Embeddings

RAG & Vector Database

ChromaDB

Recursive Character Text Splitter

PyPDF / PyPDFLoader

Semantic vector retrieval

Text-to-Speech

Google Text-to-Speech (gTTS)

📂 Project Structure

PadhAi/
│
├── backend/
│   ├── app/
│   │   ├── agents/
│   │   │   ├── content_generator_agent.py
│   │   │   ├── flashcard_agent.py
│   │   │   ├── notes_agent.py
│   │   │   ├── quiz_agent.py
│   │   │   └── summary_agent.py
│   │   │
│   │   ├── services/
│   │   │   ├── embeddings.py
│   │   │   ├── llm_service.py
│   │   │   ├── pdf_service.py
│   │   │   ├── rag_service.py
│   │   │   └── tts_service.py
│   │   │
│   │   ├── workflows/
│   │   │   └── workflow.py
│   │   │
│   │   └── main.py
│   │
│   ├── generated/
│   ├── generated_audio/
│   └── uploads/
│
├── frontend/
│   ├── css/
│   │   └── style.css
│   ├── js/
│   │   └── script.js
│   └── index.html
│
├── rag_chroma_db/
├── requirements.txt
├── .gitignore
└── README.md

Important: Do not commit .env, uploaded PDFs, generated files,
local virtual environments, or the Chroma database to a public
repository. The included .gitignore is intended to keep these local
resources out of Git.

⚙️ Installation

1. Clone the Repository

git clone https://github.com/YOUR_USERNAME/PadhAi.git
cd PadhAi

2. Create a Python Virtual Environment

Windows:

py -3.12 -m venv .venv
.venv\Scripts\activate

Linux/macOS:

python3 -m venv .venv
source .venv/bin/activate

3. Install Dependencies

pip install -r requirements.txt

🔑 Environment Variables

Create a .env file in the project root/backend environment expected by
your configuration.

Example:

GROQ_API_KEY=your_groq_api_key
GOOGLE_API_KEY=your_google_api_key

Never publish real API keys to GitHub.

▶️ Run the Backend

From the backend directory:

cd backend
uvicorn app.main:app --reload

The FastAPI backend will normally be available at:

http://127.0.0.1:8000

FastAPI's interactive API documentation is available at:

http://127.0.0.1:8000/docs

▶️ Run the Frontend

The frontend is a static HTML/CSS/JavaScript application.

From the frontend directory:

cd frontend
python -m http.server 5500

Then open:

http://localhost:5500

Make sure the backend is running on port 8000 while using the
frontend.

🔌 API Overview

The backend exposes APIs for the main learning workflows.

Endpoint               Method     Purpose

/api/upload          POST       Upload a PDF
/api/materials       GET        List available study materials
/api/workflow        POST       Run an AI learning workflow
/api/chat            POST       Ask questions about study material
/api/tts             POST       Convert generated text to audio
/api/tts/languages   GET        Get supported TTS languages
/api/notes           POST/GET   Notes-related operations
/api/summary         POST/GET   Summary-related operations
/api/quiz            POST/GET   Quiz-related operations
/api/flashcards      POST/GET   Flashcard-related operations
/api/content         POST/GET   Educational content operations

The exact available routes can be inspected through the FastAPI Swagger
documentation at /docs.

🔄 How PadhAi Works

Step 1 --- Upload

The student uploads a study PDF.

Step 2 --- Extract

The backend extracts readable text from the PDF.

Step 3 --- Chunk & Embed

The document is divided into smaller chunks and converted into vector
embeddings using Google Gemini embeddings.

Step 4 --- Store

The embeddings are stored in ChromaDB for semantic retrieval.

Step 5 --- Retrieve

When the student requests content or asks a question, relevant document
information can be retrieved from the vector store.

Step 6 --- Agent Routing

LangGraph routes the request to the appropriate specialized agent:

Summary → Summary Agent
Notes → Notes Agent
Quiz → Quiz Agent
Flashcards → Flashcard Agent
Content → Content Generator Agent

Step 7 --- Generate

The selected agent uses the LLM to generate the requested educational
content.

Step 8 --- Optional Voice Output

Generated content can be converted into speech using gTTS.

🧪 Example Workflow

Student
   │
   │ Upload Python Notes.pdf
   ▼
PadhAi Backend
   │
   ├── Extract PDF text
   ├── Split into chunks
   ├── Generate embeddings
   └── Store in ChromaDB
             │
             ▼
       Student selects
       "Generate Quiz"
             │
             ▼
       LangGraph Router
             │
             ▼
          Quiz Agent
             │
             ▼
          Groq LLM
             │
             ▼
       Practice Quiz

📸 Screenshots

Add screenshots of the application here:

screenshots/
├── dashboard.png
├── upload.png
├── notes.png
├── summary.png
├── quiz.png
├── flashcards.png
└── chat.png

Example:

![PadhAi Dashboard](screenshots/dashboard.png)

🔒 Security Notes

Store API keys only in environment variables.

Do not commit .env files.

Do not upload private student documents to a public repository.

Do not commit .venv/, __pycache__/, generated audio, or local
vector databases.

Review CORS settings before production deployment.

Add authentication and authorization before deploying for multiple
users.

🚧 Future Roadmap

📚 Learning

Multiple PDF support

Improved multi-document chat

Personalized study plans

Difficulty-based quizzes

Progress and score tracking

Better revision recommendations

🌐 Accessibility & Language

More TTS languages

Multilingual AI responses

Improved voice-learning experience

Accessibility improvements

📤 Export

Export notes as PDF

Export notes as DOCX

Download generated quizzes

Download flashcards

☁️ Platform

User authentication

Cloud database/vector storage

Production deployment

Persistent user profiles

Usage monitoring

👥 Team

PadhAi was developed as a collaborative academic project by:

Satyam

Om

Ritesh

B.Tech --- Computer Science Engineering

🤝 Contributing

Contributions and suggestions are welcome.

Fork the repository.

Create a feature branch.

git checkout -b feature/your-feature

Make your changes.

Commit your changes.

git commit -m "Add your feature"

Push the branch.

git push origin feature/your-feature

Open a Pull Request.

📄 License

This project is developed for educational and academic purposes.

If you plan to distribute or deploy PadhAi publicly, add an appropriate
open-source license such as MIT and update this section accordingly.

⭐ Project Vision

PadhAi --- turning study material into an intelligent learning
experience.

The long-term vision is to build an AI-powered personal study assistant
that understands a student's learning material and helps them learn,
revise, practice, and listen from one platform.

<p align="center">

Made with ❤️ by the PadhAi Team

</p>