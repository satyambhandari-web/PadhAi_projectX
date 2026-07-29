import os

from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, ToolMessage
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from app.services.rag_service import RAGService
from dotenv import load_dotenv

load_dotenv()


@tool
def get_quiz_content(query: str):
    """
    Retrieves relevant educational content from the vector database
    using Retrieval-Augmented Generation (RAG), to be used as the
    basis for generating quiz questions.
    """

    rag_service = RAGService()
    retriever = rag_service.get_retriever()

    response = retriever.invoke(query)

    return response


class QuizAgent:

    def __init__(self):

        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.1,
            max_tokens=1024,
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.tools = [get_quiz_content]

        self.tools_by_names = {
            t.name: t for t in self.tools
        }

        self.llm_with_tools = llm.bind_tools(self.tools)

    def agent_node(self, state: dict) -> dict:

        messages = state["messages"]

        system_prompt = SystemMessage(
            content=(
                "You are an AI Quiz Generator.\n"
                "Your instructions are:\n"
                "1. Always use the get_quiz_content tool to retrieve relevant study material.\n"
                "2. Do not ask the user for additional information if enough educational content is available.\n"
                "3. Generate clear, accurate and well-structured quiz questions based on the retrieved content.\n"
                "4. Depending on the user's request, generate multiple choice questions, true/false questions, "
                "short answer questions, or a mixed quiz.\n"
                "5. For multiple choice questions, always provide 4 options and clearly indicate the correct answer.\n"
                "6. Number all questions sequentially and include an answer key at the end.\n"
                "7. Base your quiz only on the retrieved educational content."
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

    agent = QuizAgent()

    state = {
        "messages": [
            HumanMessage(
                content="Give me a 5 question multiple choice quiz on Python Unit 1."
            )
        ]
    }
    response = agent.agent_node(state)

    print("===== AGENT RESPONSE =====")
    print(response)

    if response["messages"][0].tool_calls:
        tool_response = agent.tool_node(response)

        print("\n===== TOOL RESPONSE =====")
        print(tool_response)