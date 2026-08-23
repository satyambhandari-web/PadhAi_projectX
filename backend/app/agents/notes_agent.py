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
def get_notes_content(query: str):
    """
    Retrieves relevant educational content from the vector database
    using Retrieval-Augmented Generation (RAG), to be used as the
    basis for generating structured study notes.
    """

    rag_service = RAGService()
    retriever = rag_service.get_retriever()

    documents = retriever.invoke(query)

    return documents


# ============================================================
# NOTES AGENT
# ============================================================

class NotesAgent:

    def __init__(self):

        # Initialize LLM
        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.1,
            max_tokens=2048,
            api_key=os.getenv("GROQ_API_KEY")
        )

        # Register tool
        self.tools = [
            get_notes_content
        ]

        # Tool lookup
        self.tools_by_names = {
            tool.name: tool
            for tool in self.tools
        }

        # Bind tools
        self.llm_with_tools = self.llm.bind_tools(
            self.tools
        )

    # ========================================================
    # STEP 1: LLM decides to retrieve content
    # ========================================================

    def agent_node(self, state: dict) -> dict:

        messages = state["messages"]

        system_prompt = SystemMessage(
            content=(
                "You are an expert professor creating "
                "exam-ready study notes for an engineering student.\n\n"

                "Follow these instructions strictly:\n\n"

                "1. ALWAYS use the get_notes_content tool to "
                "retrieve relevant study material before generating notes.\n"

                "2. Base the notes strictly on the retrieved "
                "educational content.\n"

                "3. Do not invent information that is not present "
                "in the retrieved content.\n"

                "4. Organize the notes using clear headings "
                "and subheadings.\n"

                "5. Include important definitions, concepts, "
                "properties, explanations and key points.\n"

                "6. Include code examples or algorithms when "
                "they are present in the retrieved material.\n"

                "7. Explain code logic clearly when relevant.\n"

                "8. Highlight important points useful for "
                "engineering university examinations.\n"

                "9. Keep the notes comprehensive but easy to study.\n"

                "10. Do not include apologies, conversational text, "
                "or introductory filler such as 'Here are your notes'.\n\n"

                "Use a structure similar to:\n\n"

                "# Topic Name\n\n"

                "## Definition\n"
                "- Important definition\n\n"

                "## Key Concepts\n"
                "- Concept 1\n"
                "- Concept 2\n\n"

                "## Explanation\n"
                "Detailed explanation based on the source material.\n\n"

                "## Example / Code\n"
                "Include examples or code when present in the source.\n\n"

                "## Important Points for Exam\n"
                "- Important point 1\n"
                "- Important point 2\n"
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
    # STEP 2: Execute RAG tool
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
    # STEP 3: Generate final notes
    # ========================================================

    def generate_final_notes(
        self,
        original_messages,
        agent_response,
        tool_response
    ):

        final_messages = (
            original_messages
            + agent_response["messages"]
            + tool_response["messages"]
        )

        # Normal LLM call.
        # We already retrieved the required content.
        final_response = self.llm.invoke(
            final_messages
        )

        return final_response


# ============================================================
# TEST NOTES AGENT
# ============================================================

if __name__ == "__main__":

    print("\n========================================")
    print("          NOTES AGENT STARTED")
    print("========================================\n")

    agent = NotesAgent()

    state = {
        "messages": [
            HumanMessage(
                content=(
                    "Give me detailed exam-ready study notes "
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
        # STEP 3: Generate final notes
        # ----------------------------------------------------

        final_response = agent.generate_final_notes(
            state["messages"],
            response,
            tool_response
        )

        print("\n========================================")
        print("             FINAL NOTES")
        print("========================================\n")

        print(final_response.content)

    else:

        print(
            "\nERROR: The LLM did not call the RAG tool."
        )