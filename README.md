# 📚 PadhAI - AI Powered Student Learning Assistant

<p align="center">

<img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python">
<img src="https://img.shields.io/badge/Framework-Flask-black?logo=flask">
<img src="https://img.shields.io/badge/AI-LangChain-green">
<img src="https://img.shields.io/badge/LLM-Groq-orange">
<img src="https://img.shields.io/badge/RAG-ChromaDB-purple">

</p>

<p align="center">
<b>Learn Smarter. Generate Faster. Study Better.</b>
</p>


## 📌 About PadhAI

**PadhAI** is an AI-powered educational assistant that converts students' PDF study materials into intelligent learning resources.

Using **Retrieval-Augmented Generation (RAG)** and **Large Language Models (LLMs)**, PadhAI automatically generates:

- 📝 Summaries
- 📚 Study Notes
- ❓ Practice Quizzes
- 🧠 Flashcards


The goal of PadhAI is to help students save time and improve their learning experience with AI.


---

# ✨ Features

## 📄 PDF Based Learning

✅ Upload study PDFs  
✅ Extract document content  
✅ Create AI knowledge base  
✅ Generate learning material from uploaded documents  


## 🤖 AI Content Generation

| Feature | Description |
|---|---|
| 📝 Summary Generator | Creates concise summaries |
| 📚 Notes Generator | Generates structured notes |
| ❓ Quiz Generator | Creates practice questions |
| 🧠 Flashcards | Generates revision cards |


## 🔍 RAG Based AI System

PadhAI uses Retrieval-Augmented Generation to provide accurate answers from uploaded documents.


```
PDF Upload
     |
     ↓
PDF Processing
     |
     ↓
Text Chunking
     |
     ↓
Gemini Embeddings
     |
     ↓
Chroma Vector Database
     |
     ↓
RAG Retrieval
     |
     ↓
Groq LLM
     |
     ↓
Generated Learning Content
```

---

# 🏗️ Project Architecture


```
                 User
                  |
                  ↓
          HTML + CSS Interface
                  |
                  ↓
              Flask Backend
                  |
        ----------------------
        |                    |
        ↓                    ↓
 PDF Processing          AI Agents
        |                    |
        ↓                    ↓
     ChromaDB            Groq LLM
        |
        ↓
 Gemini Embeddings

```


---

# 🛠️ Tech Stack


## Frontend

- HTML5
- CSS3


## Backend

- Python
- Flask


## AI / ML

- LangChain
- LangChain Community
- Groq API
- Google Gemini Embeddings
- Retrieval-Augmented Generation


## Database

- ChromaDB


## PDF Processing

- PyPDFLoader
- RecursiveCharacterTextSplitter


---

# 📂 Project Structure


```
PadhAI/
│
├── app/
│   ├── agents/
│   │   ├── summary_agent.py
│   │   ├── notes_agent.py
│   │   ├── quiz_agent.py
│   │   └── flashcard_agent.py
│   │
│   ├── services/
│   │   ├── rag_service.py
│   │   └── pdf_service.py
│   │
│   ├── workflows/
│   │   └── workflow.py
│   │
│   └── main.py
│
├── frontend/
│   ├── templates/
│   └── static/
│
├── uploads/
├── generated/
├── rag_chroma_db/
├── requirements.txt
└── README.md

```

---

# ⚙️ Installation


### Clone Repository

```bash
git clone https://github.com/yourusername/PadhAI.git
```


### Navigate Project

```bash
cd PadhAI
```


### Create Virtual Environment

```bash
python -m venv venv
```


### Activate Environment

Windows:

```bash
venv\Scripts\activate
```


Linux/macOS:

```bash
source venv/bin/activate
```


### Install Dependencies

```bash
pip install -r requirements.txt
```


---

# 🔑 Environment Variables


Create `.env` file:

```env
GOOGLE_API_KEY=your_google_api_key

GROQ_API_KEY=your_groq_api_key
```


---

# ▶️ Run Application


```bash
python app/main.py
```


Open:

```
http://127.0.0.1:5000
```


---

# 📊 Development Status


| Component | Status |
|---|---|
| Flask Backend | ✅ |
| Frontend UI | ✅ |
| PDF Upload | ✅ |
| PDF Processing | ✅ |
| RAG Pipeline | ✅ |
| ChromaDB | ✅ |
| Gemini Embeddings | ✅ |
| Summary Agent | ✅ |
| Notes Agent | 🚧 |
| Quiz Agent | 🚧 |
| Flashcard Agent | 🚧 |
| Multi-Agent Workflow | 🚧 |


---

# 📸 Screenshots


Add your screenshots here:


```
screenshots/

├── home.png
├── upload.png
├── summary.png
├── quiz.png

```


---

# 🚀 Future Roadmap


### 📚 Learning Features

- Chat with PDF
- Multi-language support
- Voice learning assistant
- Personalized study recommendations


### ⚡ Platform Improvements

- User authentication
- Cloud deployment
- Multiple PDF support
- Download notes as PDF/DOCX
- Student progress tracking


### 🤖 AI Improvements

- Advanced Agentic Workflow
- AI Tutor Mode
- Memory-based learning assistant


---

# 👨‍💻 Team


### Team Capable

Developed by:

- Satyam
- Om
- Ritesh


B.Tech Computer Science Engineering  
Agentic AI Project


---

# 🤝 Contribution


Contributions are welcome!


1. Fork this repository
2. Create a new branch
3. Commit changes
4. Create Pull Request


---

# 📄 License


This project is created for educational purposes.


---

<p align="center">

Made with ❤️ using Python, LangChain, RAG & Generative AI

</p>