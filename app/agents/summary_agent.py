import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, ToolMessage, HumanMessage
from langchain_core.tools import tool

from app.services.rag_service import RAGService


load_dotenv()


# ============================================================
# TOOL: Retrieve relevant content from the RAG database
# ============================================================

@tool
def get_summary_content(query: str):
    """
    Retrieves relevant educational content from the vector database
    using RAG for generating a detailed study summary.
    """
    rag_service = RAGService()
    retriever = rag_service.get_retriever()

    response = retriever.invoke(query)

    return response


# ============================================================
# SUMMARY AGENT
# ============================================================

class SummaryAgent:

    # IMPORTANT: __init__ has TWO underscores on both sides
    def __init__(self):

        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.1,
            max_tokens=2048,
            api_key=os.getenv("GROQ_API_KEY")
        )

        # Register tools
        self.tools = [get_summary_content]

        self.tools_by_names = {
            tool.name: tool
            for tool in self.tools
        }

        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(self.tools)


    # ========================================================
    # AGENT NODE
    # ========================================================

    def agent_node(self, state: dict) -> dict:

        messages = state["messages"]

        system_prompt = SystemMessage(
            content=(
                "You are an expert professor creating detailed study summaries "
                "for an engineering student.\n\n"

                "Your instructions are:\n"

                "1. ALWAYS use the get_summary_content tool to retrieve "
                "relevant educational material before creating the summary.\n\n"

                "2. Generate a detailed but easy-to-understand summary "
                "strictly based on the retrieved educational content.\n\n"

                "3. Organize the summary using clear headings and "
                "subheadings.\n\n"

                "4. Include important definitions, concepts, formulas, "
                "algorithms, explanations, and examples when they are "
                "present in the retrieved material.\n\n"

                "5. Include important Python code examples when they are "
                "present in the retrieved material.\n\n"

                "6. Keep the explanation suitable for engineering students "
                "preparing for examinations.\n\n"

                "7. Do not add information that is not supported by the "
                "retrieved educational material.\n\n"

                "8. Do not include unnecessary conversational text such as "
                "'Here is your summary', apologies, or greetings.\n\n"

                "9. Make the final summary well structured and readable.\n\n"

                "10. Base the final answer strictly on the retrieved "
                "educational content."
            )
        )

        full_message = [system_prompt] + messages

        response = self.llm_with_tools.invoke(full_message)

        return {
            "messages": [response]
        }


    # ========================================================
    # TOOL NODE
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

                tool_function = self.tools_by_names.get(tool_name)

                if tool_function:

                    tool_result = tool_function.invoke(tool_args)

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


# ============================================================
# TEST THE SUMMARY AGENT
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 40)
    print("        SUMMARY AGENT STARTED")
    print("=" * 40)

    agent = SummaryAgent()

    state = {
        "messages": [
            HumanMessage(
                content="Give me a detailed summary of Python Unit 1."
            )
        ]
    }

    # First agent call
    response = agent.agent_node(state)

    print()
    print("===== AGENT RESPONSE =====")
    print(response)

    # Check whether the agent requested the RAG tool
    if response["messages"][0].tool_calls:

        tool_response = agent.tool_node(response)

        print()
        print("===== TOOL RESPONSE =====")
        print(tool_response)

        # ----------------------------------------------------
        # Send retrieved content back to LLM
        # so it can generate the actual summary
        # ----------------------------------------------------

        final_state = {
            "messages": [
                HumanMessage(
                    content="Give me a detailed summary of Python Unit 1."
                ),
                response["messages"][0],
                *tool_response["messages"]
            ]
        }

        final_response = agent.agent_node(final_state)

        print()
        print("=" * 40)
        print("             FINAL SUMMARY")
        print("=" * 40)
        print()

        print(final_response["messages"][0].content)

    else:

        print()
        print("=" * 40)
        print("             FINAL SUMMARY")
        print("=" * 40)
        print()

        print(response["messages"][0].content)