import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


class LLMService:
    """
    Service class responsible for initializing and providing
    the Large Language Model (LLM).
    """

    def __init__(
        self,
        model_name: str = "llama3-8b-8192",
        temperature: float = 0.2,
    ):
        self.model_name = model_name
        self.temperature = temperature
        self.api_key = os.getenv("GROQ_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GROQ_API_KEY not found. Please add it to your .env file."
            )

        self.llm = ChatGroq(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key,
        )

    def get_llm(self):
        """
        Returns the initialized LLM instance.
        """
        return self.llm


import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq

load_dotenv()


class LLMService:

    # Supported models
    AVAILABLE_MODELS = {
        "llama8b": "llama3-8b-8192",
        "llama70b": "llama-3.3-70b-versatile",
        "deepseek": "deepseek-r1-distill-llama-70b",
        "gemma": "gemma2-9b-it",
        "mixtral": "mixtral-8x7b-32768",
    }

    @classmethod
    def get_llm(
        cls,
        model_name: str = "llama8b",
        temperature: float = 0.2,
    ):
        api_key = os.getenv("GROQ_API_KEY")

        if not api_key:
            raise ValueError("GROQ_API_KEY not found.")

        if model_name not in cls.AVAILABLE_MODELS:
            raise ValueError(
                f"Model '{model_name}' is not supported.\n"
                f"Available models: {list(cls.AVAILABLE_MODELS.keys())}"
            )

        return ChatGroq(
            model=cls.AVAILABLE_MODELS[model_name],
            temperature=temperature,
            api_key=api_key,
        )

    @classmethod
    def list_models(cls):
        return cls.AVAILABLE_MODELS