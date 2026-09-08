import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
    ToolMessage,
)
from langchain_core.tools import tool

from app.services.rag_service import RAGService


load_dotenv()


# ============================================================
# TOOL: RETRIEVE RELEVANT STUDY MATERIAL
# ============================================================

@tool
def get_quiz_content(query: str) -> str:
    """
    Retrieve relevant educational content from the PadhAi
    RAG/vector database for generating quiz questions.
    """

    rag_service = RAGService()

    retriever = rag_service.get_retriever()

    documents = retriever.invoke(query)

    if not documents:
        return "No relevant educational material was found."

    content = []

    for doc in documents:
        if hasattr(doc, "page_content") and doc.page_content:
            content.append(doc.page_content)

    return "\n\n".join(content)


class QuizAgent:

    def __init__(self):

        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.2,
            max_tokens=2048,
            api_key=os.getenv("GROQ_API_KEY"),
        )

        self.tools = [
            get_quiz_content
        ]

        self.tools_by_names = {
            tool_function.name: tool_function
            for tool_function in self.tools
        }

        self.llm_with_tools = self.llm.bind_tools(
            self.tools
        )


    def agent_node(self, state: dict) -> dict:
        """
        Ask the LLM to decide whether educational content
        needs to be retrieved.
        """

        messages = state["messages"]

        system_prompt = SystemMessage(
            content="""
You are PadhAi's Quiz Agent.

You are an expert university professor who creates
exam-oriented quizzes for engineering students.

Your job at this stage is ONLY to retrieve the relevant
educational material.

IMPORTANT RULES:

1. ALWAYS call get_quiz_content before generating a quiz.
2. Retrieve material relevant to the user's requested topic.
3. Do not generate the final quiz in this node.
4. Do not use outside knowledge.
5. The final quiz will be generated after retrieval.
"""
        )

        full_messages = [
            system_prompt
        ] + messages

        response = self.llm_with_tools.invoke(
            full_messages
        )

        return {
            "messages": [response]
        }


   
    def tool_node(self, state: dict) -> dict:
        """
        Execute the requested tool and return the result
        as a LangGraph state update.

        IMPORTANT:
        LangGraph nodes MUST return dictionaries.
        """

        messages = state["messages"]

        last_message = messages[-1]

        if not getattr(last_message, "tool_calls", None):

            return {
                "messages": []
            }


        tool_call = last_message.tool_calls[0]

        tool_name = tool_call["name"]

        tool_args = tool_call.get(
            "args",
            {}
        )

        tool_function = self.tools_by_names.get(
            tool_name
        )

        
        if tool_function is None:

            tool_message = ToolMessage(
                content=f"Tool '{tool_name}' was not found.",
                tool_call_id=tool_call["id"],
                name=tool_name,
            )

            return {
                "messages": [
                    tool_message
                ]
            }

     
        try:

            result = tool_function.invoke(
                tool_args
            )

            result = str(result)

        except Exception as error:

            result = (
                f"Error while retrieving quiz content: "
                f"{str(error)}"
            )



        tool_message = ToolMessage(
            content=result,
            tool_call_id=tool_call["id"],
            name=tool_name,
        )

       

        return {
            "messages": [
                tool_message
            ]
        }


    def generate_final_quiz(
        self,
        topic: str,
        retrieved_content: str,
        number_of_questions: int = 10,
    ) -> str:

       

        if number_of_questions < 1:
            number_of_questions = 1

        if number_of_questions > 20:
            number_of_questions = 20


        max_chars = 6500

        if len(retrieved_content) > max_chars:

            retrieved_content = (
                retrieved_content[:max_chars]
            )

       

        system_prompt = SystemMessage(
            content=f"""
You are PadhAi's Quiz Generator.

You are an expert university professor creating an
exam-oriented quiz for engineering students.

Create EXACTLY {number_of_questions} multiple-choice
questions about:

{topic}

Use ONLY the educational material provided below.

STRICT RULES:

1. Use ONLY the supplied educational material.
2. Do NOT use outside knowledge.
3. Do NOT invent facts.
4. Every question must be related to the requested topic.
5. Create exactly {number_of_questions} questions.
6. Each question must have exactly four options.
7. Options must be A, B, C and D.
8. There must be exactly one correct answer.
9. Provide the correct answer.
10. Provide a short explanation.
11. Avoid duplicate questions.
12. Focus on important exam-relevant concepts.
13. Mix conceptual and application-based questions when
    the source material supports them.
14. Keep the questions appropriate for an engineering student.
15. Do not mention RAG.
16. Do not mention vector databases.
17. Do not mention tools.
18. Do not mention internal processing.
19. Do not add conversational introduction or conclusion.

IMPORTANT:

Every question must be answerable using ONLY the provided
educational material.

FORMAT:

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

Continue until exactly {number_of_questions}
questions are generated.
"""
        )

        user_message = HumanMessage(
            content=f"""
Topic:
{topic}

Educational Material:
----------------------------------------

{retrieved_content}

----------------------------------------

Generate the final quiz now.
"""
        )

    

        response = self.llm.invoke(
            [
                system_prompt,
                user_message,
            ]
        )

        return response.content



if __name__ == "__main__":

    print()
    print("=" * 60)
    print("                 PADHAI QUIZ AGENT")
    print("=" * 60)
    print()

    agent = QuizAgent()

    topic = "Python Unit 1"

    state = {
        "messages": [
            HumanMessage(
                content=f"""
Create a quiz on {topic}.
"""
            )
        ]
    }


    print("===== STEP 1: QUIZ AGENT =====")
    print()

    response = agent.agent_node(
        state
    )

    print("Agent response generated.")

    if response["messages"]:

        assistant_message = response["messages"][0]

        if getattr(
            assistant_message,
            "tool_calls",
            None,
        ):

            print()
            print("===== STEP 2: RETRIEVING EDUCATIONAL CONTENT =====")
            print()

            tool_result = agent.tool_node(
                {
                    "messages": response["messages"]
                }
            )


            if tool_result["messages"]:

                retrieved_content = (
                    tool_result["messages"][0].content
                )

            else:

                retrieved_content = ""

            if retrieved_content:

                print(
                    "Educational content retrieved successfully."
                )

            else:

                print(
                    "WARNING: No educational content retrieved."
                )


            print()
            print("=" * 60)
            print("                    FINAL QUIZ")
            print("=" * 60)
            print()

            final_quiz = agent.generate_final_quiz(
                topic=topic,
                retrieved_content=retrieved_content,
                number_of_questions=10,
            )

            print(final_quiz)

        else:

            print()
            print(
                "ERROR: Quiz retrieval tool was not called."
            )

    else:

        print()
        print(
            "ERROR: Quiz agent returned no messages."
        )