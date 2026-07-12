from flask import Flask, render_template

app = Flask(
    __name__,
    template_folder="../frontend/templates",
    static_folder="../frontend/static"
)

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/upload")
def upload():
    return render_template("upload.html")


@app.route("/summary")
def summary():
    summary_text = """
Artificial Intelligence (AI) is the simulation of human intelligence by machines.
Machine Learning is a subset of AI that enables systems to learn from data.
Deep Learning uses neural networks to solve complex problems.
"""

    return render_template(
        "summary.html",
        summary=summary_text
    )


@app.route("/notes")
def notes():
    notes_text = """
• Artificial Intelligence (AI)
• Machine Learning (ML)
• Deep Learning (DL)
• Applications of AI
• Advantages and Challenges
"""

    return render_template(
        "notes.html",
        notes=notes_text
    )


@app.route("/quiz")
def quiz():
    quiz_text = """
1. What does AI stand for?

A. Artificial Intelligence
B. Automated Internet
C. Advanced Interface
D. Artificial Internet

Answer: A
"""

    return render_template(
        "quiz.html",
        quiz=quiz_text
    )


@app.route("/flashcards")
def flashcards():
    flashcards_text = """
Flashcard 1

Question:
What is AI?

Answer:
Artificial Intelligence is the simulation of human intelligence by machines.
"""

    return render_template(
        "flashcards.html",
        flashcards=flashcards_text
    )


if __name__ == "__main__":
    app.run(debug=True)