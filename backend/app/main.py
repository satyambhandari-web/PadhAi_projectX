import os
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Literal, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
from starlette.concurrency import run_in_threadpool

from langchain_core.messages import HumanMessage

from app.workflows.workflow import workflow
from app.services.tts_service import TTSService
from app.services.pdf_service import load_pdf
from app.services.rag_service import RAGService


APP_NAME = "PadhAi"
APP_VERSION = "1.0.0"

BASE_DIR = Path(__file__).resolve().parent.parent

UPLOAD_DIR = BASE_DIR / "uploads"
GENERATED_AUDIO_DIR = BASE_DIR / "generated_audio"
GENERATED_DIR = BASE_DIR / "generated"

UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
GENERATED_AUDIO_DIR.mkdir(parents=True, exist_ok=True)
GENERATED_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_SIZE = 50 * 1024 * 1024


MAX_PDF_TEXT = 60000


@asynccontextmanager
async def lifespan(app: FastAPI):
    print()
    print("=" * 60)
    print("                 PADHAI API")
    print("=" * 60)
    print()

    print(f"Application:  {APP_NAME}")
    print(f"Version:      {APP_VERSION}")
    print()
    print("Backend:      FastAPI")
    print("Workflow:     LangGraph")
    print("Agents:       Notes / Quiz / Content / Flashcards / Summary")
    print("RAG:          Chroma")
    print("TTS:          gTTS")
    print()
    print(f"Uploads:      {UPLOAD_DIR}")
    print(f"Audio:        {GENERATED_AUDIO_DIR}")
    print()
    print("API running successfully.")
    print("Docs: http://127.0.0.1:8000/docs")
    print("=" * 60)
    print()

    yield

    print()
    print("PadhAi API shutting down...")


app = FastAPI(
    title="PadhAi API",
    description=(
        "AI-powered educational platform with "
        "Notes, Quiz, Content, Flashcards, "
        "Summary, RAG and Text-to-Speech."
    ),
    version=APP_VERSION,
    lifespan=lifespan,
)

# Configurable CORS
default_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5500",
    "http://127.0.0.1:5500",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
]

env_cors = os.getenv("CORS_ORIGINS")
if env_cors:
    custom_origins = [origin.strip() for origin in env_cors.split(",") if origin.strip()]
    cors_origins = list(dict.fromkeys(default_origins + custom_origins))
else:
    cors_origins = default_origins

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



app.mount(
    "/audio",
    StaticFiles(
        directory=str(GENERATED_AUDIO_DIR)
    ),
    name="audio",
)



class WorkflowRequest(BaseModel):

    task: Literal[
        "content",
        "content_generator",
        "notes",
        "note",
        "flashcard",
        "flashcards",
        "quiz",
        "quizzes",
        "mcq",
        "mcqs",
        "summary",
        "summarize",
    ]

    query: str = Field(
        ...,
        min_length=1,
    )

    material_id: Optional[str] = None

class TTSRequest(BaseModel):

    text: str = Field(
        ...,
        min_length=1,
    )

    language: str = "en"


class AgentRequest(BaseModel):

    query: Optional[str] = ""

    text: Optional[str] = ""

    filename: Optional[str] = None

    material: Optional[str] = None

    topic: Optional[str] = None


class ProfileRequest(BaseModel):

    name: Optional[str] = None

    email: Optional[str] = None

    avatar: Optional[str] = None


class ChatRequest(BaseModel):

    message: str = Field(
        ...,
        min_length=1,
    )

    filename: Optional[str] = None

    material_id: Optional[str] = None

    history: Optional[list] = None


def get_uploaded_pdf_files():

    if not UPLOAD_DIR.exists():
        return []

    files = [
        file
        for file in UPLOAD_DIR.iterdir()
        if file.is_file()
        and file.suffix.lower() == ".pdf"
    ]

    files.sort(
        key=lambda x: x.name.lower()
    )

    return files



def find_pdf(filename: str) -> Path:

    if not filename:

        raise HTTPException(
            status_code=400,
            detail="No PDF filename was provided.",
        )

    safe_filename = Path(
        filename
    ).name.strip()

    if not safe_filename:

        raise HTTPException(
            status_code=400,
            detail="Invalid PDF filename.",
        )

    if safe_filename.lower() == "undefined":

        raise HTTPException(
            status_code=400,
            detail=(
                "No PDF was selected. "
                "Please select a material first."
            ),
        )

    if not safe_filename.lower().endswith(".pdf"):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    pdf_path = UPLOAD_DIR / safe_filename

    if not pdf_path.exists():

        raise HTTPException(
            status_code=404,
            detail=(
                f"PDF '{safe_filename}' "
                "was not found in uploads."
            ),
        )

    return pdf_path

def extract_pdf_text(
    pdf_path: Path,
) -> str:

    try:

        documents = load_pdf(
            str(pdf_path)
        )

    except Exception as exc:

        print(
            f"[PDF LOAD ERROR] "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=400,
            detail=(
                "Could not read the selected PDF. "
                "Make sure it is a valid PDF."
            ),
        ) from exc

    if not documents:

        raise HTTPException(
            status_code=400,
            detail=(
                "The selected PDF contains no readable text."
            ),
        )

    text_parts = []

    for document in documents:

        content = getattr(
            document,
            "page_content",
            None,
        )

        if content:

            text_parts.append(
                str(content)
            )

    full_text = "\n\n".join(
        text_parts
    ).strip()

    if not full_text:

        raise HTTPException(
            status_code=400,
            detail=(
                "No readable text was found "
                "inside the selected PDF."
            ),
        )

    # Prevent extremely large prompts.
    if len(full_text) > MAX_PDF_TEXT:

        full_text = full_text[
            :MAX_PDF_TEXT
        ]

        full_text += (
            "\n\n[PDF TEXT TRUNCATED "
            "FOR PROCESSING]"
        )

    return full_text



def get_workflow_output(result) -> str:

    if not result:

        return (
            "The workflow returned no result."
        )

    if isinstance(result, dict):

        # Most common output
        output = result.get(
            "output"
        )

        if output:

            return str(output)

        # Some LangGraph workflows
        # return messages.
        messages = result.get(
            "messages",
            [],
        )

        if messages:

            last_message = messages[-1]

            if isinstance(
                last_message,
                dict,
            ):

                content = last_message.get(
                    "content"
                )

                if content:

                    return str(content)

            content = getattr(
                last_message,
                "content",
                "",
            )

            if content:

                return str(content)

    return (
        "The workflow completed "
        "but produced no output."
    )


def normalize_task(
    task: str,
) -> str:

    task = task.strip().lower()

    aliases = {

        "content_generator": "content",

        "note": "notes",

        "notes": "notes",

        "flashcard": "flashcards",

        "flashcards": "flashcards",

        "quiz": "quiz",

        "quizzes": "quiz",

        "mcq": "quiz",

        "mcqs": "quiz",

        "summary": "summary",

        "summarize": "summary",

    }

    return aliases.get(
        task,
        task,
    )



def execute_workflow(
    task: str,
    query: str,
    pdf_path: Optional[Path] = None,
    material_id: Optional[str] = None,
) -> str:

    task = normalize_task(
        task
    )

    query = query.strip()

    if not query:

        raise HTTPException(
            status_code=400,
            detail="Query cannot be empty.",
        )

    if not pdf_path and UPLOAD_DIR.exists():
        for uploaded_file in UPLOAD_DIR.iterdir():
            if uploaded_file.is_file() and uploaded_file.suffix.lower() == ".pdf":
                if uploaded_file.name.lower() in query.lower() or uploaded_file.stem.lower() in query.lower():
                    pdf_path = uploaded_file
                    break

    effective_material_id = material_id or (pdf_path.name if pdf_path else None)

    if pdf_path and effective_material_id:
        try:
            rag_service = RAGService()
            if not rag_service.has_material(effective_material_id):
                rag_service.generate_and_store_embeddings(
                    pdf_path=str(pdf_path),
                    material_id=effective_material_id,
                )
        except Exception as exc:
            print(f"[RAG INDEX ERROR] Could not ensure embeddings: {exc}")

        workflow_query = f"""
You are working inside PadhAi.

TASK:
{task}

SELECTED STUDY MATERIAL:
{pdf_path.name}

USER REQUEST:
{query}

Generate the requested educational content by retrieving relevant information from the selected study material.
""".strip()

    else:

        workflow_query = f"""
You are working inside PadhAi.

TASK:
{task}

USER REQUEST:
{query}

Generate the requested educational content.
""".strip()

    print()
    print("-" * 60)
    print("WORKFLOW REQUEST")
    print("-" * 60)
    print(f"Task: {task}")

    if pdf_path:
        print(
            f"PDF:  {pdf_path.name}"
        )

    print(
        f"Query: {query}"
    )

    print("-" * 60)


    try:

        result = workflow.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=workflow_query
                    )
                ],

                "task": task,

                "query": workflow_query,

                "material_id": effective_material_id,

                "output": "",
            }
        )

        output = get_workflow_output(
            result
        )

        print()
        print("-" * 60)
        print("WORKFLOW COMPLETED")
        print("-" * 60)
        try:
            print(output)
        except Exception:
            print(output.encode("ascii", "replace").decode("ascii"))
        print("-" * 60)

        return output

    except ValueError as exc:

        print(
            f"[WORKFLOW VALUE ERROR] "
            f"{exc}"
        )

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        print(
            f"[WORKFLOW ERROR] "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                f"{task} workflow failed."
            ),
        ) from exc


@app.get("/")
async def root():

    return {

        "success": True,

        "message":
            "PadhAi API is running.",

        "application":
            APP_NAME,

        "version":
            APP_VERSION,

        "docs":
            "/docs",

        "health":
            "/health",
    }


@app.get("/health")
async def health():

    return {

        "success": True,

        "status":
            "healthy",

        "application":
            APP_NAME,

        "version":
            APP_VERSION,
    }



@app.get("/api/test")
async def api_test():

    return {

        "success": True,

        "message":
            "Frontend and backend are connected successfully.",
    }



@app.get("/api")
async def api_info():

    return {

        "application":
            APP_NAME,

        "version":
            APP_VERSION,

        "agents": [
            "notes",
            "quiz",
            "content",
            "flashcards",
            "summary",
        ],

        "endpoints": {

            "materials":
                "GET /api/materials",

            "upload":
                "POST /api/upload",

            "workflow":
                "POST /api/workflow",

            "summary":
                "POST /api/summary/{filename}",

            "notes":
                "POST /api/notes/{filename}",

            "quiz":
                "POST /api/quiz/{filename}",

            "flashcards":
                "POST /api/flashcards/{filename}",

            "content":
                "POST /api/content/{filename}",

            "chat":
                "POST /api/chat",

            "tts":
                "POST /api/tts",

            "profile":
                "PUT /profile",

            "process_pdf":
                "POST /api/process-pdf",
        },
    }


def get_materials_sync():
    files = get_uploaded_pdf_files()

    materials = []

    for file in files:

        try:

            size = file.stat().st_size

        except Exception:

            size = 0

        pages = 0

        try:

            documents = load_pdf(
                str(file)
            )

            pages = len(
                documents
            )

        except Exception:

            pages = 0

        try:

            uploaded_at = (
                file.stat()
                .st_mtime
            )

        except Exception:

            uploaded_at = None

        from datetime import datetime

        uploaded_at_iso = None

        if uploaded_at:

            uploaded_at_iso = (
                datetime.fromtimestamp(
                    uploaded_at
                ).isoformat()
            )

        materials.append(
            {

                "id":
                    file.name,

                "name":
                    file.name,

                "filename":
                    file.name,

                "size":
                    size,

                "sizeKb":
                    round(
                        size / 1024,
                        2,
                    ),

                "pages":
                    pages,

                "type":
                    "pdf",

                "uploadedAt":
                    uploaded_at_iso,
            }
        )

    return materials


@app.get("/materials")
@app.get("/api/materials")
async def get_materials():
    return await run_in_threadpool(get_materials_sync)


async def save_uploaded_pdf(
    file: UploadFile,
):

    if not file.filename:

        raise HTTPException(
            status_code=400,
            detail="No file was selected.",
        )

    filename = Path(
        file.filename
    ).name

    if not filename:

        raise HTTPException(
            status_code=400,
            detail="Invalid filename.",
        )

    if not filename.lower().endswith(
        ".pdf"
    ):

        raise HTTPException(
            status_code=400,
            detail="Only PDF files are supported.",
        )

    destination = (
        UPLOAD_DIR /
        filename
    )

    try:

        content = await file.read()

        if not content:

            raise HTTPException(
                status_code=400,
                detail="Uploaded file is empty.",
            )

        if len(content) > MAX_UPLOAD_SIZE:

            raise HTTPException(
                status_code=413,
                detail=(
                    "PDF is too large. "
                    "Maximum size is 50 MB."
                ),
            )

        destination.write_bytes(
            content
        )

        # Validate that it can actually be read.
        try:

            documents = load_pdf(
                str(destination)
            )

            pages = len(
                documents
            )

        except Exception:

            if destination.exists():

                destination.unlink()

            raise HTTPException(
                status_code=400,
                detail=(
                    "The uploaded file is not "
                    "a readable PDF."
                ),
            )

        return {

            "success":
                True,

            "message":
                "PDF uploaded successfully.",

            "id":
                filename,

            "filename":
                filename,

            "name":
                filename,

            "size":
                len(content),

            "sizeKb":
                round(
                    len(content) / 1024,
                    2,
                ),

            "pages":
                pages,

            "type":
                "pdf",

            "location":
                "uploads",
        }

    except HTTPException:

        raise

    except Exception as exc:

        print(
            f"[UPLOAD ERROR] "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to upload the PDF."
            ),
        ) from exc


@app.post("/upload")
@app.post("/api/upload")
async def upload_file(
    file: UploadFile = File(...)
):

    return await save_uploaded_pdf(
        file
    )



@app.post("/api/upload-pdf")
async def upload_pdf(
    file: UploadFile = File(...)
):

    return await save_uploaded_pdf(
        file
    )

@app.post("/api/workflow")
async def run_workflow(
    request: WorkflowRequest
):

    task = normalize_task(
        request.task
    )

    pdf_path = None

    if request.material_id:
        pdf_path = find_pdf(
            request.material_id
        )

    output = await run_in_threadpool(
        execute_workflow,
        task=task,
        query=request.query,
        pdf_path=pdf_path,
        material_id=request.material_id,
    )

    return {
        "success": True,
        "task": task,
        "query": request.query,
        "material_id": request.material_id,
        "filename": (
            pdf_path.name
            if pdf_path
            else None
        ),
        "output": output,
        "content": output,
    }


async def run_material_agent(
    task: str,
    filename: str,
    request: Optional[AgentRequest] = None,
):

    pdf_path = find_pdf(
        filename
    )

    query = ""

    if request:

        values = [

            request.query,

            request.text,

            request.topic,

            request.material,

        ]

        for value in values:

            if value and value.strip():

                query = value.strip()

                break

    if not query:

        default_queries = {

            "summary":
                "Create a clear and detailed summary of the selected study material.",

            "notes":
                "Create structured, detailed, exam-ready notes from the selected study material.",

            "quiz":
                "Create a quiz based on the selected study material with useful questions and answers.",

            "flashcards":
                "Create useful flashcards from the selected study material.",

            "content":
                "Generate useful educational content from the selected study material.",
        }

        query = default_queries.get(
            task,
            "Generate useful educational content from the selected study material.",
        )

    output = await run_in_threadpool(
        execute_workflow,
        task=task,
        query=query,
        pdf_path=pdf_path,
        material_id=pdf_path.name,
    )

    return {

        "success":
            True,

        "task":
            task,

        "filename":
            pdf_path.name,

        "query":
            query,

        "output":
            output,

        "content":
            output,
    }


@app.post("/api/summary/{filename}")
@app.post("/summary/{filename}")
async def summary_filename(
    filename: str,
    request: Optional[AgentRequest] = None,
):

    return await run_material_agent(
        "summary",
        filename,
        request,
    )



@app.post("/api/notes/{filename}")
@app.post("/notes/{filename}")
async def notes_filename(
    filename: str,
    request: Optional[AgentRequest] = None,
):

    return await run_material_agent(
        "notes",
        filename,
        request,
    )


@app.post("/api/quiz/{filename}")
@app.post("/quiz/{filename}")
async def quiz_filename(
    filename: str,
    request: Optional[AgentRequest] = None,
):

    return await run_material_agent(
        "quiz",
        filename,
        request,
    )



@app.post("/api/flashcards/{filename}")
@app.post("/flashcards/{filename}")
async def flashcards_filename(
    filename: str,
    request: Optional[AgentRequest] = None,
):

    return await run_material_agent(
        "flashcards",
        filename,
        request,
    )



@app.post("/api/content/{filename}")
@app.post("/content/{filename}")
async def content_filename(
    filename: str,
    request: Optional[AgentRequest] = None,
):

    return await run_material_agent(
        "content",
        filename,
        request,
    )


@app.post("/api/summary")
async def summary_without_material(
    request: AgentRequest,
):

    query = (
        request.query
        or request.text
        or request.topic
        or request.material
        or ""
    ).strip()

    if not query:

        raise HTTPException(
            status_code=400,
            detail="Please provide a topic or query.",
        )

    output = await run_in_threadpool(
        execute_workflow,
        task="summary",
        query=query,
    )

    return {

        "success":
            True,

        "task":
            "summary",

        "query":
            query,

        "output":
            output,

        "content":
            output,
    }


@app.post("/api/notes")
async def notes_without_material(
    request: AgentRequest,
):

    query = (
        request.query
        or request.text
        or request.topic
        or request.material
        or ""
    ).strip()

    if not query:

        raise HTTPException(
            status_code=400,
            detail="Please provide a topic or query.",
        )

    output = await run_in_threadpool(
        execute_workflow,
        task="notes",
        query=query,
    )

    return {

        "success":
            True,

        "task":
            "notes",

        "query":
            query,

        "output":
            output,

        "content":
            output,
    }


@app.post("/api/quiz")
async def quiz_without_material(
    request: AgentRequest,
):

    query = (
        request.query
        or request.text
        or request.topic
        or request.material
        or ""
    ).strip()

    if not query:

        raise HTTPException(
            status_code=400,
            detail="Please provide a topic or query.",
        )

    output = await run_in_threadpool(
        execute_workflow,
        task="quiz",
        query=query,
    )

    return {

        "success":
            True,

        "task":
            "quiz",

        "query":
            query,

        "output":
            output,

        "content":
            output,
    }


@app.post("/api/flashcards")
async def flashcards_without_material(
    request: AgentRequest,
):

    query = (
        request.query
        or request.text
        or request.topic
        or request.material
        or ""
    ).strip()

    if not query:

        raise HTTPException(
            status_code=400,
            detail="Please provide a topic or query.",
        )

    output = await run_in_threadpool(
        execute_workflow,
        task="flashcards",
        query=query,
    )

    return {

        "success":
            True,

        "task":
            "flashcards",

        "query":
            query,

        "output":
            output,

        "content":
            output,
    }


@app.post("/api/content")
async def content_without_material(
    request: AgentRequest,
):

    query = (
        request.query
        or request.text
        or request.topic
        or request.material
        or ""
    ).strip()

    if not query:

        raise HTTPException(
            status_code=400,
            detail="Please provide a topic or query.",
        )

    output = await run_in_threadpool(
        execute_workflow,
        task="content",
        query=query,
    )

    return {

        "success":
            True,

        "task":
            "content",

        "query":
            query,

        "output":
            output,

        "content":
            output,
    }


@app.post("/chat")
@app.post("/api/chat")
async def chat(
    request: ChatRequest,
):

    message = request.message.strip()

    if not message:

        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    pdf_path = None


    selected_filename = (
        request.filename
        or request.material_id
    )

    if selected_filename:

        try:

            pdf_path = find_pdf(
                selected_filename
            )

        except HTTPException:

            pdf_path = None

    output = await run_in_threadpool(
        execute_workflow,
        task="content",
        query=message,
        pdf_path=pdf_path,
        material_id=(
            pdf_path.name
            if pdf_path
            else None
        ),
    )

    return {

        "success":
            True,

        "message":
            message,

        "response":
            output,

        "reply":
            output,

        "output":
            output,
    }

@app.put("/profile")
@app.put("/api/profile")
async def update_profile(
    request: ProfileRequest,
):

    return {

        "success":
            True,

        "message":
            "Profile updated successfully.",

        "profile":
            request.model_dump(),
    }



@app.post("/api/tts")
async def generate_tts(
    request: TTSRequest,
):

    text = request.text.strip()

    language = (
        request.language
        .lower()
        .strip()
    )

    if not text:

        raise HTTPException(
            status_code=400,
            detail="Text is required.",
        )

    try:

        tts_service = TTSService(
            output_dir=str(
                GENERATED_AUDIO_DIR
            )
        )

        audio_path = await run_in_threadpool(
            tts_service.generate_audio,
            text=text,
            language=language,
        )

        filename = Path(
            audio_path
        ).name

        return {

            "success":
                True,

            "filename":
                filename,

            "audio_url":
                f"/audio/{filename}",
        }

    except ValueError as exc:

        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc

    except Exception as exc:

        print(
            f"[TTS ERROR] "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail="Failed to generate audio.",
        ) from exc



@app.get("/api/tts/languages")
async def get_tts_languages():

    try:

        service = TTSService(
            output_dir=str(
                GENERATED_AUDIO_DIR
            )
        )

        return {

            "success":
                True,

            "languages":
                service.get_supported_languages(),
        }

    except Exception as exc:

        print(
            f"[TTS LANGUAGES ERROR] "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to get TTS languages."
            ),
        ) from exc


@app.post("/api/process-pdf")
async def process_pdf(
    filename: str,
):

    pdf_path = find_pdf(
        filename
    )

    try:

        rag_service = RAGService()

        material_id = pdf_path.name

        chunks = await run_in_threadpool(
            rag_service.generate_and_store_embeddings,
            pdf_path=str(pdf_path),
            material_id=material_id,
        )

        return {
            "success": True,
            "message": "PDF processed successfully.",
            "filename": pdf_path.name,
            "material_id": material_id,
            "chunks": chunks,
        }

    except Exception as exc:

        print(
            f"[RAG ERROR] "
            f"{type(exc).__name__}: {exc}"
        )

        raise HTTPException(
            status_code=500,
            detail=(
                "Failed to process the PDF "
                "and create embeddings."
            ),
        ) from exc

def get_stats_sync():
    pdf_files = get_uploaded_pdf_files()
    audio_files = [
        file
        for file in GENERATED_AUDIO_DIR.iterdir()
        if file.is_file() and file.suffix.lower() == ".mp3"
    ] if GENERATED_AUDIO_DIR.exists() else []

    total_pages = 0
    for pdf_file in pdf_files:
        try:
            docs = load_pdf(str(pdf_file))
            total_pages += len(docs)
        except Exception:
            pass

    return {
        "success": True,
        "stats": {
            "total_materials": len(pdf_files),
            "total_audio": len(audio_files),
            "total_pages": total_pages,
            "active_agents": 5,
            "system_status": "Operational",
        },
    }


@app.get("/stats")
@app.get("/api/stats")
async def get_stats():
    return await run_in_threadpool(get_stats_sync)