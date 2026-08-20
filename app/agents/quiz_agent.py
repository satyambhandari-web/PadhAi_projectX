import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langchain_core.tools import tool

from app.services.rag_service import RAGService


load_dotenv()

@tool
def get_quiz_content(query: str):
    """
    Retrieves relevant educational content from the vector database
    for generating quiz questions.
    """

    rag_service = RAGService()

    retriever = rag_service.get_retriever()

    documents = retriever.invoke(query)

    # Return ONLY useful text.
    # Do not return complete Document objects with metadata.
    content = []

    for doc in documents:
        content.append(doc.page_content)

    return "\n\n".join(content)

class QuizAgent:

    def __init__(self):

        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.2,
            max_tokens=2048,
            api_key=os.getenv("GROQ_API_KEY")
        )

        # Tool-enabled LLM
        self.tools = [get_quiz_content]

        self.tools_by_names = {
            t.name: t
            for t in self.tools
        }

        self.llm_with_tools = self.llm.bind_tools(self.tools)


    def agent_node(self, state: dict) -> dict:

        messages = state["messages"]

        system_prompt = SystemMessage(
            content="""
You are an expert university professor.

You are preparing a quiz for an engineering student.

IMPORTANT:

1. ALWAYS use the get_quiz_content tool first.
2. Retrieve educational material relevant to the user's topic.
3. Do not answer the quiz yet.
4. After retrieving the content, the application will generate
   the final quiz separately.
"""
        )

        full_messages = [system_prompt] + messages

        response = self.llm_with_tools.invoke(full_messages)

        return {
            "messages": [response]
        }

    def tool_node(self, state: dict) -> str:

        messages = state["messages"]

        last_message = messages[-1]

        if not last_message.tool_calls:
            return ""

        tool_call = last_message.tool_calls[0]

        tool_name = tool_call["name"]

        tool_args = tool_call["args"]

        tool_function = self.tools_by_names.get(tool_name)

        if not tool_function:
            return f"Error: Tool {tool_name} not found"

        result = tool_function.invoke(tool_args)

        return str(result)

    def generate_final_quiz(
        self,
        topic: str,
        retrieved_content: str,
        number_of_questions: int = 10
    ):
        max_chars = 14000

        if len(retrieved_content) > max_chars:
            retrieved_content = retrieved_content[:max_chars]

        system_prompt = SystemMessage(
            content=f"""
You are an expert university professor creating an
exam-oriented quiz.

Create EXACTLY {number_of_questions} multiple-choice questions
from the educational material provided below.

STRICT RULES:

1. Use ONLY the provided educational material.
2. Do not use outside knowledge.
3. Do not invent information.
4. Every question must be related to the provided material.
5. Each question must have exactly four options.
6. Options must be A, B, C and D.
7. Give the correct answer.
8. Give a short explanation.
9. Avoid duplicate questions.
10. Focus on important exam-relevant concepts.
11. Keep questions clear and easy to understand.
12. Do not mention RAG, tools, vector databases, or internal
    processing.
13. Do not add introductory conversational text.

FORMAT EXACTLY LIKE THIS:

# Quiz - {topic}

## Question 1

**Question:** [question]

**A.** [option]

**B.** [option]

**C.** [option]

**D.** [option]

**Correct Answer:** [A/B/C/D]

**Explanation:** [short explanation]

---

## Question 2

**Question:** [question]

**A.** [option]

**B.** [option]

**C.** [option]

**D.** [option]

**Correct Answer:** [A/B/C/D]

**Explanation:** [short explanation]

Continue until exactly {number_of_questions} questions
are generated.
"""
        )

        user_message = HumanMessage(
            content=f"""
Topic: {topic}

Educational Material:

{retrieved_content}
"""
        )

        response = self.llm.invoke(
            [system_prompt, user_message]
        )

        return response.content

if __name__ == "__main__":

    print()
    print("========================================")
    print("          QUIZ AGENT STARTED")
    print("========================================")
    print()

    agent = QuizAgent()

    topic = "Python Unit 1"

    state = {
        "messages": [
            HumanMessage(
                content=f"Create a quiz on {topic}."
            )
        ]
    }
    response = agent.agent_node(state)

    print("===== AGENT RESPONSE =====")
    print(response)

    if response["messages"][0].tool_calls:

        print()
        print("===== RETRIEVING CONTENT =====")
        print()

        retrieved_content = agent.tool_node(response)

        print("Educational content retrieved successfully.")
        print()
        print("========================================")
        print("             FINAL QUIZ")
        print("========================================")
        print()

        final_quiz = agent.generate_final_quiz(
            topic=topic,
            retrieved_content=retrieved_content,
            number_of_questions=10
        )

        print(final_quiz)

    else:

        print()
        print("ERROR: Quiz content retrieval tool was not called.")