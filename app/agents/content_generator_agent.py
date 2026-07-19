import os

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_core.tools import tool
from langchain_core.messages import SystemMessage, ToolMessage

from app.services.rag_service import RAGService

load_dotenv()


@tool
def get_educational_content(query: str):
    """
    Retrieves relevant educational content from the vector database
    using Retrieval-Augmented Generation (RAG).
    """

    rag_service = RAGService()
    retriever = rag_service.get_retriever()

    response = retriever.invoke(query)

    return response


class ContentGeneratorAgent:

    def __init__(self):

        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.1,
            max_tokens=1024,
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.tools = [get_educational_content]

        self.tools_by_names = {
            t.name: t for t in self.tools
        }

        self.llm_with_tools = llm.bind_tools(self.tools)

    def agent_node(self, state: dict) -> dict:

        messages = state["messages"]

        system_prompt = SystemMessage(
            content=(
                "You are an AI Educational Content Generator.\n"
                "Your instructions are:\n"
                "1. Always use the get_educational_content tool to retrieve relevant study material.\n"
                "2. Do not ask the user for additional information if enough educational content is available.\n"
                "3. Generate clear, accurate and well-structured educational content.\n"
                "4. Depending on the user's request, generate summaries, detailed notes, quizzes, flashcards or study material.\n"
                "5. Base your answer only on the retrieved educational content."
            )
        )

        full_message = [system_prompt] + messages

        response = self.llm_with_tools.invoke(full_message)

        return {
            "messages": [response]
        }

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
                    tool_result = f"Error: Tool `{tool_name}` not found"

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


from langchain_core.messages import HumanMessage

if __name__ == "__main__":

    agent = ContentGeneratorAgent()

    state = {
        "messages": [
            HumanMessage(
                content="Give me detailed notes on Python Unit 1."
            )
        ]
    }

    # LLM decides whether to call the tool
    response = agent.agent_node(state)

    print("===== AGENT RESPONSE =====")
    print(response)

    # If tool call exists, execute it
    if response["messages"][0].tool_calls:

        tool_response = agent.tool_node(response)

        print("\n===== TOOL RESPONSE =====")
        print(tool_response)
