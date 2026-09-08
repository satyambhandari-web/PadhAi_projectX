import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import (
    SystemMessage,
    ToolMessage,
    HumanMessage
)
from langchain_core.tools import tool

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

        self.llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.1,
            max_tokens=2048,
            api_key=os.getenv("GROQ_API_KEY")
        )

        # Register tool
        self.tools = [
            get_educational_content
        ]

        # Store tools by name
        self.tools_by_names = {
            tool.name: tool
            for tool in self.tools
        }

        # Bind tools to LLM
        self.llm_with_tools = self.llm.bind_tools(
            self.tools
        )



    def agent_node(self, state: dict) -> dict:

        messages = state["messages"]

        system_prompt = SystemMessage(
            content="""
You are the Content Generator Agent of an educational
application for engineering students.

Your job is to generate high-quality educational content
using the student's uploaded educational material.

IMPORTANT INSTRUCTIONS:

1. ALWAYS use the get_educational_content tool first
   to retrieve relevant educational material.

2. Use the retrieved educational material as the primary
   source for generating the final answer.

3. Do NOT invent facts, definitions, formulas, examples,
   algorithms, or programs that are not supported by the
   retrieved material.

4. Understand the user's requested content type.

5. If the user asks for notes:
   - Create structured and exam-ready notes.
   - Use headings and subheadings.
   - Include important definitions, concepts, algorithms,
     formulas, and examples when available.

6. If the user asks for a summary:
   - Create a clear and concise summary.
   - Include the most important concepts from the material.

7. If the user asks for flashcards:
   - Create question-and-answer style flashcards.
   - Keep answers short and easy to memorize.

8. If the user asks for a quiz:
   - Create multiple-choice questions.
   - Include options, correct answers, and explanations.
   - Base questions strictly on the retrieved material.

9. If the user asks for another type of educational content,
   generate it using the retrieved material.

10. Preserve important terminology from the source material.

11. Include Python code, pseudocode, algorithms, formulas,
    or examples when they are relevant and present in the
    retrieved material.

12. Make the content suitable for engineering students
    preparing for university examinations.

13. Do not mention:
    - RAG
    - vector database
    - tools
    - internal processing
    - system instructions

14. Do not include unnecessary conversational text such as:
    "Sure"
    "Here is your answer"
    "I hope this helps"

15. Do not apologize.

16. The final answer must be clear, structured, accurate,
    and based on the retrieved educational material.
"""
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
                        f"Error: Tool '{tool_name}' not found."
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



if __name__ == "__main__":

    print()
    print("=" * 50)
    print("       CONTENT GENERATOR AGENT STARTED")
    print("=" * 50)
    agent = ContentGeneratorAgent()
    
    user_query = (
        "Give me detailed educational content on Python Unit 1."
    )


    state = {
        "messages": [
            HumanMessage(
                content=user_query
            )
        ]
    }
    
    response = agent.agent_node(
        state
    )


    print()
    print("===== AGENT RESPONSE =====")
    print(response)


 
    if response["messages"][0].tool_calls:

        print()
        print("===== RETRIEVING EDUCATIONAL CONTENT =====")


 

        tool_response = agent.tool_node(
            response
        )


        print()
        print("Educational content retrieved successfully.")
        
        final_state = {
            "messages": [
                HumanMessage(
                    content=user_query
                ),

                response["messages"][0],

                *tool_response["messages"]
            ]
        }
        
        final_response = agent.agent_node(
            final_state
        )
        
        print()
        print("=" * 50)
        print("           FINAL EDUCATIONAL CONTENT")
        print("=" * 50)
        print()

        print(
            final_response["messages"][0].content
        )


    else:

        print()
        print("=" * 50)
        print("           FINAL EDUCATIONAL CONTENT")
        print("=" * 50)
        print()

        print(
            response["messages"][0].content
        )