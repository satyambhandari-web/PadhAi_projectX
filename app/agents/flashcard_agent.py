import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from app.services.rag_service import RAGService
from dotenv import load_dotenv

load_dotenv()

@tool
def get_flashcard_content(query: str):
    """Retrieves relevant educational content from the vector
     database using Retrieval-Augmented Generation (RAG), 
     to be used as the basis for generating flashcards. """
     
     rag_service = RAGService()
     retriver =rag_service.get_retriver()

     response = retriver.invoke(query)

     return response 

class FlashcardAgent:

    def __init__(self):

        llm = ChatGroq(
            model="openai/gpt-oss-120b",
            temperature=0.1,
            max_tokens=1024,
            api_key=os.getenv("GROQ_API_KEY")
        )

        self.tools = [get_flashcard_content]

        self.tools_by_name ={
            t.name :t for t in self.tools
        }

        self.llm_with