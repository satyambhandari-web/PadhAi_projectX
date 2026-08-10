import os
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langchain_core.messages import HumanMessage
from langchain_core.tools import tool
from app.services.rag_service import RAGService
from dotenv import load_dotenv

load_dotenv()

