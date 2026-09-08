import os
from typing import Optional, Dict, Any

from dotenv import load_dotenv
from langchain_groq import ChatGroq


# Load environment variables from .env
load_dotenv()



GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    raise ValueError(
        "GROQ_API_KEY is not set. "
        "Please add GROQ_API_KEY=your_api_key to your .env file."
    )


llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0.3,
    groq_api_key=GROQ_API_KEY,
)



def generate_response(
    prompt: str,
    temperature: Optional[float] = None,
) -> str:
    """
    Send a prompt to the LLM and return the generated text.

    Args:
        prompt: User/system prompt.
        temperature: Optional temperature override.

    Returns:
        Generated response as a string.
    """

    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    try:
        current_llm = llm

        if temperature is not None:
            current_llm = ChatGroq(
                model="openai/gpt-oss-120b",
                temperature=temperature,
                groq_api_key=GROQ_API_KEY,
            )

        response = current_llm.invoke(prompt)

        return response.content.strip()

    except Exception as e:
        raise RuntimeError(f"LLM generation failed: {str(e)}") from e

EDUCATIONAL_SYSTEM_PROMPT = """
You are PadhAi, an intelligent AI educational assistant.

Your job is to help students understand academic subjects clearly,
accurately, and efficiently.

You should behave like a highly capable teacher and study mentor.

IMPORTANT RULES:

1. Explain concepts in simple and understandable language.
2. Do not unnecessarily use complicated terminology.
3. When a technical term is necessary, explain it first.
4. Prefer structured answers with headings and bullet points.
5. Give examples whenever they improve understanding.
6. Use the provided study material as the primary source when context
   is supplied.
7. Do not invent facts that are not supported by the provided context
   when the task is based on uploaded study material.
8. If the answer cannot be determined from the provided material,
   clearly say that the information is not available in the provided
   material.
9. Maintain academic accuracy.
10. Avoid unnecessary repetition.
11. Match the student's requested difficulty level.
12. For programming questions, provide correct and readable code.
13. For mathematical problems, show the important calculation steps.
14. For exam preparation, emphasize definitions, important points,
    differences, formulas, examples, and likely exam concepts.
15. Do not mention that you are an AI unless specifically asked.
"""


def build_context_prompt(
    context: str,
    query: str,
    task: str,
) -> str:
    """
    Build a structured prompt using retrieved study material.

    Args:
        context: Retrieved text from RAG.
        query: Student's request.
        task: Type of educational content.

    Returns:
        Complete prompt for the LLM.
    """

    if not context or not context.strip():
        context = "No study material was provided."

    return f"""
{EDUCATIONAL_SYSTEM_PROMPT}

TASK TYPE:
{task}

STUDENT REQUEST:
{query}

STUDY MATERIAL:
-------------------------
{context}
-------------------------

Generate the requested educational content using the study material
as the primary source.

Make the response:
- Clear
- Well structured
- Academically useful
- Easy to revise
- Appropriate for a college student

Do not unnecessarily repeat the study material word-for-word.
"""



def generate_educational_content(
    context: str,
    query: str,
    task: str = "general",
) -> str:
    """
    Generate educational content using retrieved context.

    This is the main function that can be called by the RAG pipeline
    or content generator agent.
    """

    prompt = build_context_prompt(
        context=context,
        query=query,
        task=task,
    )

    return generate_response(prompt)



def generate_summary(
    context: str,
    query: str = "Give me a detailed summary of the provided material.",
) -> str:
    """
    Generate a detailed academic summary.
    """

    return generate_educational_content(
        context=context,
        query=query,
        task="Detailed Summary",
    )

def generate_notes(
    context: str,
    query: str = "Create complete study notes from the provided material.",
) -> str:
    """
    Generate structured study notes.
    """

    prompt = f"""
{EDUCATIONAL_SYSTEM_PROMPT}

Create high-quality academic notes from the provided study material.

Organize the notes using:

1. Main concepts
2. Important definitions
3. Key points
4. Explanations
5. Examples
6. Important formulas, if applicable
7. Important differences/comparisons
8. Exam-focused points

STUDENT REQUEST:
{query}

STUDY MATERIAL:
-------------------------
{context}
-------------------------

Make the notes concise enough for revision but detailed enough
to understand the topic properly.
"""

    return generate_response(prompt)



def generate_explanation(
    context: str,
    query: str,
) -> str:
    """
    Explain a concept using the retrieved study material.
    """

    return generate_educational_content(
        context=context,
        query=query,
        task="Concept Explanation",
    )

def generate_quiz(
    context: str,
    number_of_questions: int = 10,
    difficulty: str = "medium",
) -> str:
    """
    Generate a quiz based on the study material.
    """

    prompt = f"""
{EDUCATIONAL_SYSTEM_PROMPT}

Create a quiz using ONLY the provided study material.

Number of questions:
{number_of_questions}

Difficulty:
{difficulty}

For every question:

- Include the question.
- For MCQs, provide 4 options.
- Clearly identify the correct answer.
- Give a short explanation for the answer.

Use a mixture of:
- Conceptual questions
- Definition-based questions
- Application questions
- Understanding questions

STUDY MATERIAL:
-------------------------
{context}
-------------------------

Format:

Question 1:
...

A)
B)
C)
D)

Correct Answer:
...

Explanation:
...
"""

    return generate_response(prompt)


def generate_flashcards(
    context: str,
    number_of_cards: int = 15,
) -> str:
    """
    Generate revision flashcards.
    """

    prompt = f"""
{EDUCATIONAL_SYSTEM_PROMPT}

Create {number_of_cards} useful study flashcards from the provided
material.

Each flashcard must contain:

Flashcard 1
Question:
Answer:

Focus on:
- Definitions
- Important concepts
- Formulas
- Key facts
- Important differences
- Exam-relevant information

STUDY MATERIAL:
-------------------------
{context}
-------------------------
"""

    return generate_response(prompt)


def generate_important_questions(
    context: str,
    number_of_questions: int = 10,
) -> str:
    """
    Generate exam-oriented important questions.
    """

    prompt = f"""
{EDUCATIONAL_SYSTEM_PROMPT}

Analyze the provided study material and create
{number_of_questions} important exam-oriented questions.

Include a mixture of:

- Short-answer questions
- Definition questions
- Conceptual questions
- Long-answer questions
- Application-based questions

For each question, also provide:

- Expected answer points
- Important keywords
- Approximate difficulty

STUDY MATERIAL:
-------------------------
{context}
-------------------------
"""

    return generate_response(prompt)



def answer_question(
    context: str,
    question: str,
) -> str:
    """
    Answer a student's question using the retrieved study material.
    """

    prompt = f"""
{EDUCATIONAL_SYSTEM_PROMPT}

Answer the student's question using the provided study material.

Student Question:
{question}

Study Material:
-------------------------
{context}
-------------------------

Instructions:

- Answer directly.
- Explain the reasoning where necessary.
- Use examples if useful.
- If the answer is not present in the study material,
  clearly state that.
- Do not fabricate information.
"""

    return generate_response(prompt)



def simplify_content(
    context: str,
    query: str = "Explain this material in very simple language.",
) -> str:
    """
    Convert difficult academic material into easier language.
    """

    prompt = f"""
{EDUCATIONAL_SYSTEM_PROMPT}

Rewrite/explain the provided academic material in very simple
student-friendly language.

Student request:
{query}

Use:

- Simple explanations
- Small sections
- Examples
- Analogies where appropriate
- Important keywords

Do not remove important academic concepts.

STUDY MATERIAL:
-------------------------
{context}
-------------------------
"""

    return generate_response(prompt)


def generate_study_plan(
    context: str,
    days: int = 7,
) -> str:
    """
    Generate a study plan based on the provided material.
    """

    prompt = f"""
{EDUCATIONAL_SYSTEM_PROMPT}

Create a {days}-day study plan using the provided study material.

For each day include:

- Topics to study
- Concepts to understand
- Revision activities
- Practice questions
- Quick revision task

Make the plan realistic for a college student.

STUDY MATERIAL:
-------------------------
{context}
-------------------------
"""

    return generate_response(prompt)



def generate_content(
    content_type: str,
    context: str,
    query: str = "",
    **kwargs: Any,
) -> str:
    """
    Universal content-generation function.

    Supported content types:

    - summary
    - notes
    - explanation
    - quiz
    - flashcards
    - questions
    - answer
    - simplify
    - study_plan
    """

    content_type = content_type.lower().strip()

    if content_type == "summary":
        return generate_summary(context, query)

    elif content_type == "notes":
        return generate_notes(context, query)

    elif content_type == "explanation":
        return generate_explanation(context, query)

    elif content_type == "quiz":
        return generate_quiz(
            context,
            number_of_questions=kwargs.get("number_of_questions", 10),
            difficulty=kwargs.get("difficulty", "medium"),
        )

    elif content_type == "flashcards":
        return generate_flashcards(
            context,
            number_of_cards=kwargs.get("number_of_cards", 15),
        )

    elif content_type == "questions":
        return generate_important_questions(
            context,
            number_of_questions=kwargs.get("number_of_questions", 10),
        )

    elif content_type == "answer":
        return answer_question(context, query)

    elif content_type == "simplify":
        return simplify_content(context, query)

    elif content_type == "study_plan":
        return generate_study_plan(
            context,
            days=kwargs.get("days", 7),
        )

    else:
        return generate_educational_content(
            context=context,
            query=query,
            task=content_type,
        )



if __name__ == "__main__":

    print("=" * 60)
    print("PADHAI LLM SERVICE TEST")
    print("=" * 60)

    try:
        test_prompt = """
Explain the concept of an algorithm to a first-year engineering
student in simple language. Give one simple example.
"""

        response = generate_response(test_prompt)

        print("\nLLM RESPONSE:")
        print("-" * 60)
        print(response)
        print("-" * 60)

        print("\nLLM SERVICE WORKING SUCCESSFULLY!")

    except Exception as e:

        print("\nLLM SERVICE ERROR:")
        print("-" * 60)
        print(str(e))
        print("-" * 60)