import os

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage
from langchain_core.tools import tool
from app.services.rag_service import RAGService
from dotenv import load_dotenv

load_dotenv()


# ============================================================
# TOOL: Retrieve educational content from RAG / ChromaDB
# ============================================================

@tool
def get_flashcard_content(query: str):
    """
    Retrieves relevant educational content from the vector database
    using RAG. The retrieved content is used to generate flashcards.
    """

    rag_service = RAGService()
    retriever = rag_service.get_retriever()

    documents = retriever.invoke(query)

    return documents


# ============================================================
# FLASHCARD AGENT
# ============================================================

class FlashcardAgent:

    def __init__(self):

        # Initialize LLM
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.2,
            max_tokens=2048,
            api_key=os.getenv("GROQ_API_KEY")
        )

        # Register tools
        self.tools = [
            get_flashcard_content
        ]

        # Create tool lookup
        self.tools_by_names = {
            tool.name: tool
            for tool in self.tools
        }

        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(
            self.tools
        )

    # ========================================================
    # STEP 1: LLM decides which tool to use
    # ========================================================

    def agent_node(self, state: dict) -> dict:

        messages = state["messages"]

        system_prompt = SystemMessage(
            content=(
                "You are an expert engineering tutor who creates "
                "high-quality study flashcards.\n\n"

                "Follow these instructions strictly:\n"

                "1. ALWAYS use the get_flashcard_content tool "
                "before generating flashcards.\n"

                "2. Retrieve educational content relevant to "
                "the user's requested topic.\n"

                "3. Generate EXACTLY 10 flashcards unless the "
                "user explicitly requests another number.\n"

                "4. Flashcards must be based ONLY on the retrieved "
                "educational content.\n"

                "5. Do not invent information that is not present "
                "in the retrieved content.\n"

                "6. Keep questions clear and useful for examination "
                "preparation.\n"

                "7. Keep answers short, accurate and easy to memorize.\n"

                "8. Do not include introductory text, explanations, "
                "apologies or conclusions.\n\n"

                "Use this exact format:\n\n"

                "*Flashcard 1*\n"
                "*Question:* [question]\n"
                "*Answer:* [answer]\n\n"

                "*Flashcard 2*\n"
                "*Question:* [question]\n"
                "*Answer:* [answer]\n\n"

                "Continue until exactly 10 flashcards are generated."
            )
        )

        full_message = [
            system_prompt
        ] + messages

        response = self.llm_with_tools.invoke(
            full_message
        )

        return {
            "messages": [response]
        }

    # ========================================================
    # STEP 2: Execute tool calls
    # ========================================================

    def tool_node(self, state: dict) -> dict:

        messages = state["messages"]

        last_message = messages[-1]

        tool_outputs = []

        if hasattr(last_message, "tool_calls"):

            for tool_call in last_message.tool_calls:

                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                tool_id = tool_call["id"]

                tool_function = self.tools_by_names.get(
                    tool_name
                )

                if tool_function:

                    tool_result = tool_function.invoke(
                        tool_args
                    )

                else:

                    tool_result = (
                        f"Error: Tool {tool_name} not found"
                    )

                tool_outputs.append(
                    ToolMessage(
                        content=str(tool_result),
                        tool_call_id=tool_id,
                        name=tool_name
                    )
                )

        return {
            "messages": tool_outputs
        }

    # ========================================================
    # STEP 3: Generate final flashcards
    # ========================================================

    def generate_final_flashcards(
        self,
        original_messages,
        agent_response,
        tool_response
    ):

        # Combine the conversation history
        final_messages = (
            original_messages
            + agent_response["messages"]
            + tool_response["messages"]
        )

        # IMPORTANT:
        # Use normal LLM, not llm_with_tools.
        # We already retrieved the content.
        final_response = self.llm.invoke(
            final_messages
        )

        return final_response


# ============================================================
# TEST THE FLASHCARD AGENT
# ============================================================

if __name__ == "__main__":

    print("\n========================================")
    print("       FLASHCARD AGENT STARTED")
    print("========================================\n")

    agent = FlashcardAgent()

    # User request
    state = {
        "messages": [
            HumanMessage(
                content=(
                    "Give me exactly 10 flashcards "
                    "on Python Unit 1."
                )
            )
        ]
    }

    # --------------------------------------------------------
    # STEP 1: Ask LLM to retrieve content
    # --------------------------------------------------------

    response = agent.agent_node(
        state
    )

    print("===== AGENT RESPONSE =====")
    print(response)

    # --------------------------------------------------------
    # STEP 2: Execute RAG tool
    # --------------------------------------------------------

    if response["messages"][0].tool_calls:

        tool_response = agent.tool_node(
            response
        )

        print("\n===== TOOL RESPONSE =====")
        print(tool_response)

        # ----------------------------------------------------
        # STEP 3: Generate final flashcards
        # ----------------------------------------------------

        final_response = agent.generate_final_flashcards(
            state["messages"],
            response,
            tool_response
        )

        print("\n========================================")
        print("          FINAL FLASHCARDS")
        print("========================================\n")

        print(final_response.content)

    else:

        print("\nERROR: The LLM did not call the RAG tool.")