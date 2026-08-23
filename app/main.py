from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


# ============================================================
# PATH CONFIGURATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent.parent

FRONTEND_DIR = BASE_DIR / "frontend"
STATIC_DIR = FRONTEND_DIR / "static"
TEMPLATES_DIR = FRONTEND_DIR / "templates"


# ============================================================
# FASTAPI APPLICATION
# ============================================================

app = FastAPI(
    title="PadhAi",
    description="AI-powered educational content generation platform",
    version="1.0.0",
)


# ============================================================
# STATIC FILES
# ============================================================

app.mount(
    "/static",
    StaticFiles(directory=STATIC_DIR),
    name="static",
)


# ============================================================
# JINJA2 TEMPLATES
# ============================================================

templates = Jinja2Templates(
    directory=str(TEMPLATES_DIR)
)


# ============================================================
# HELPER FUNCTION
# ============================================================

def render_page(request: Request, page: str):
    """
    Render a frontend HTML page.
    """

    return templates.TemplateResponse(
        request=request,
        name=page,
    )


# ============================================================
# MAIN PAGES
# ============================================================

@app.get("/")
async def home(request: Request):
    return render_page(request, "index.html")


@app.get("/login")
async def login(request: Request):
    return render_page(request, "login.html")


@app.get("/signup")
async def signup(request: Request):
    return render_page(request, "signup.html")


@app.get("/dashboard")
async def dashboard(request: Request):
    return render_page(request, "dashboard.html")


# ============================================================
# DOCUMENT / STUDY FLOW
# ============================================================

@app.get("/upload")
async def upload(request: Request):
    return render_page(request, "upload.html")


@app.get("/processing")
async def processing(request: Request):
    return render_page(request, "processing.html")


@app.get("/result")
async def result(request: Request):
    return render_page(request, "result.html")


# ============================================================
# GENERATED CONTENT
# ============================================================

@app.get("/summary")
async def summary(request: Request):
    return render_page(request, "summary.html")


@app.get("/notes")
async def notes(request: Request):
    return render_page(request, "notes.html")


@app.get("/quiz")
async def quiz(request: Request):
    return render_page(request, "quiz.html")


@app.get("/flashcards")
async def flashcards(request: Request):
    return render_page(request, "flashcards.html")


# ============================================================
# OTHER APPLICATION PAGES
# ============================================================

@app.get("/chat")
async def chat(request: Request):
    return render_page(request, "chat.html")


@app.get("/history")
async def history(request: Request):
    return render_page(request, "history.html")


@app.get("/profile")
async def profile(request: Request):
    return render_page(request, "profile.html")


@app.get("/settings")
async def settings(request: Request):
    return render_page(request, "settings.html")


@app.get("/about")
async def about(request: Request):
    return render_page(request, "about.html")


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
async def health():
    return {
        "status": "ok",
        "application": "PadhAi",
    }