import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage
from langchain_core.tools import tool

from app.services.rag_service import RAGService


load_dotenv()


# ============================================================
# CONFIGURATION
# ============================================================

# Keep retrieved context small enough for Groq TPM limits.
MAX_CONTEXT_CHARS = 6500


# ============================================================
# TOOL: RETRIEVE RELEVANT EDUCATIONAL CONTENT
# ============================================================

@tool
def get_summary_content(query: str):
    """
    Retrieves relevant educational content from the vector database
    for generating a study summary.
    """

    rag_service = RAGService()

    retriever = rag_service.get_retriever()

    documents = retriever.invoke(query)

    # Extract only the actual text from the documents.
    # Do not send complete Document objects or metadata to the LLM.
    content = []

    for doc in documents:

        if hasattr(doc, "page_content"):

            text = doc.page_content

            if text and text.strip():
                content.append(text.strip())

    retrieved_content = "\n\n".join(content)

    # --------------------------------------------------------
    # Prevent Groq 413 / TPM errors
    # --------------------------------------------------------

    if len(retrieved_content) > MAX_CONTEXT_CHARS:

        retrieved_content = retrieved_content[:MAX_CONTEXT_CHARS]

        # Try to end at a complete line instead of cutting
        # the educational material in the middle of a sentence.
        last_newline = retrieved_content.rfind("\n")

        if last_newline > 100:
            retrieved_content = retrieved_content[:last_newline]

    if not retrieved_content.strip():

        return "No relevant educational material was found."

    return retrieved_content


# ============================================================
# SUMMARY AGENT
# ============================================================

class SummaryAgent:

    def __init__(self):

        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.1,
            max_tokens=2048,
            api_key=os.getenv("GROQ_API_KEY")
        )

        # ----------------------------------------------------
        # Register tools
        # ----------------------------------------------------

        self.tools = [
            get_summary_content
        ]

        self.tools_by_names = {
            tool.name: tool
            for tool in self.tools
        }

        # ----------------------------------------------------
        # Bind tools to LLM
        # ----------------------------------------------------

        self.llm_with_tools = self.llm.bind_tools(
            self.tools
        )


    # ========================================================
    # AGENT NODE
    # ========================================================

    def agent_node(self, state: dict) -> dict:

        messages = state["messages"]

        if not messages:
            raise ValueError(
                "SummaryAgent received an empty message list."
            )

        system_prompt = SystemMessage(
            content="""
You are an expert university professor creating
high-quality study summaries for engineering students.

IMPORTANT INSTRUCTIONS:

1. ALWAYS use the get_summary_content tool first to retrieve
   relevant educational material.

2. Base the final summary strictly on the retrieved educational
   material.

3. Do NOT use outside knowledge.

4. Do NOT invent facts, definitions, formulas, algorithms,
   examples, or explanations that are not supported by the
   retrieved material.

5. Respect the user's requested level of detail.

   - If the user asks for a concise summary, keep it short
     and focused on the most important points.

   - If the user asks for a detailed summary, provide a
     comprehensive explanation of the important material.

6. Organize the final answer using clear headings and
   subheadings where appropriate.

7. Include important definitions, concepts, algorithms,
   principles, formulas, and examples when they are present
   in the retrieved material.

8. Include Python code examples only when they are present
   or clearly supported by the retrieved educational material.

9. Focus on concepts useful for engineering examinations.

10. Remove unnecessary repetition.

11. Do not mention RAG, vector databases, retrieval,
    tools, LangChain, or internal processing.

12. Do not include conversational introductions such as:
    "Here is your summary", "Sure", "Of course", etc.

13. Return only the educational summary.

IMPORTANT:
For the first response, use the get_summary_content tool.
Do not generate the final educational answer until the
retrieved material has been provided.
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


    # ========================================================
    # TOOL NODE
    # ========================================================

    def tool_node(self, state: dict) -> dict:

        messages = state["messages"]

        if not messages:
            raise ValueError(
                "SummaryAgent tool_node received no messages."
            )

        last_message = messages[-1]

        tool_outputs = []

        tool_calls = getattr(
            last_message,
            "tool_calls",
            []
        )

        # ----------------------------------------------------
        # Execute every requested tool call
        # ----------------------------------------------------

        for tool_call in tool_calls:

            tool_name = tool_call["name"]

            tool_args = tool_call.get(
                "args",
                {}
            )

            tool_id = tool_call["id"]

            tool_function = self.tools_by_names.get(
                tool_name
            )

            if tool_function is None:

                tool_result = (
                    f"Error: Tool '{tool_name}' was not found."
                )

            else:

                try:

                    tool_result = tool_function.invoke(
                        tool_args
                    )

                except Exception as e:

                    tool_result = (
                        f"Error while retrieving educational "
                        f"content: {str(e)}"
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


# ============================================================
# DIRECT SUMMARY AGENT TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("                 SUMMARY AGENT")
    print("=" * 60)

    agent = SummaryAgent()

    topic = (
        "Give me a concise summary of Python algorithms, "
        "statements, and control structures."
    )

    state = {
        "messages": [
            HumanMessage(
                content=topic
            )
        ]
    }

    try:

        # ----------------------------------------------------
        # STEP 1: Ask agent to retrieve material
        # ----------------------------------------------------

        print()
        print("Retrieving educational material...")

        response = agent.agent_node(
            state
        )

        first_message = response["messages"][0]

        # ----------------------------------------------------
        # STEP 2: Execute RAG tool
        # ----------------------------------------------------

        if first_message.tool_calls:

            print(
                "Educational material retrieved successfully."
            )

            tool_response = agent.tool_node(
                response
            )

            # ------------------------------------------------
            # STEP 3: Send retrieved material back to LLM
            # ------------------------------------------------

            final_state = {
                "messages": [
                    HumanMessage(
                        content=topic
                    ),
                    first_message,
                    *tool_response["messages"]
                ]
            }

            print()
            print("=" * 60)
            print("                    SUMMARY")
            print("=" * 60)
            print()

            final_response = agent.agent_node(
                final_state
            )

            final_message = final_response[
                "messages"
            ][0]

            print(
                final_message.content
            )

        else:

            # ------------------------------------------------
            # Fallback
            # ------------------------------------------------

            print()
            print("=" * 60)
            print("                    SUMMARY")
            print("=" * 60)
            print()

            print(
                first_message.content
            )

    except Exception as e:

        print()
        print("=" * 60)
        print("               SUMMARY AGENT ERROR")
        print("=" * 60)

        print(
            type(e).__name__
        )

        print(
            str(e)
        )