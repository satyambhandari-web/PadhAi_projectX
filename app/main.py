from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(title="PadhAi")

# Static files
app.mount(
    "/static",
    StaticFiles(directory=BASE_DIR / "frontend" / "static"),
    name="static",
)

# Templates
templates = Jinja2Templates(
    directory=str(BASE_DIR / "frontend" / "templates")
)


@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
    )


@app.get("/login")
async def login(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="login.html",
    )


@app.get("/signup")
async def signup(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="signup.html",
    )


@app.get("/dashboard")
async def dashboard(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
    )


@app.get("/upload")
async def upload(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="upload.html",
    )


@app.get("/processing")
async def processing(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="processing.html",
    )


@app.get("/summary")
async def summary(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="summary.html",
    )


@app.get("/notes")
async def notes(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="notes.html",
    )


@app.get("/quiz")
async def quiz(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="quiz.html",
    )


@app.get("/flashcards")
async def flashcards(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="flashcards.html",
    )


@app.get("/chat")
async def chat(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="chat.html",
    )


@app.get("/history")
async def history(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="history.html",
    )


@app.get("/profile")
async def profile(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="profile.html",
    )


@app.get("/settings")
async def settings(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="settings.html",
    )