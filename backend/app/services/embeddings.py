import os

from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAIEmbeddings


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()


# ============================================================
# PADHAI EMBEDDING SERVICE
# ============================================================

class EmbeddingService:
    """
    Embedding service for the PadhAi RAG pipeline.

    Converts educational text into numerical vectors that
    ChromaDB can use for semantic search.
    """

    def __init__(self):

        self.api_key = os.getenv("GEMINI_API_KEY")

        if not self.api_key:
            raise ValueError(
                "GEMINI_API_KEY is not set in the .env file."
            )

        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=self.api_key,
        )

    # ========================================================
    # GET EMBEDDING MODEL
    # ========================================================

    def get_embeddings(self):
        """
        Return the configured embedding model.
        """

        return self.embeddings

    # ========================================================
    # EMBED ONE TEXT
    # ========================================================

    def embed_text(self, text: str):
        """
        Convert one text string into an embedding vector.
        """

        if not text or not text.strip():
            raise ValueError(
                "Text cannot be empty."
            )

        return self.embeddings.embed_query(text)

    # ========================================================
    # EMBED MULTIPLE TEXTS
    # ========================================================

    def embed_documents(self, documents):
        """
        Convert multiple text chunks into embedding vectors.
        """

        if not documents:
            return []

        cleaned_documents = [
            document.strip()
            for document in documents
            if document and document.strip()
        ]

        if not cleaned_documents:
            return []

        return self.embeddings.embed_documents(
            cleaned_documents
        )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    print()
    print("=" * 60)
    print("              PADHAI EMBEDDING SERVICE")
    print("=" * 60)
    print()

    try:

        embedding_service = EmbeddingService()

        test_text = (
            "An algorithm is a step-by-step procedure "
            "used to solve a problem."
        )

        print("Creating embedding...")
        vector = embedding_service.embed_text(test_text)

        print()
        print("Embedding created successfully.")
        print("Vector dimensions:", len(vector))
        print("First 5 values:", vector[:5])

        print()
        print("=" * 60)
        print("             EMBEDDING TEST PASSED")
        print("=" * 60)

    except Exception as e:

        print()
        print("=" * 60)
        print("              EMBEDDING ERROR")
        print("=" * 60)
        print()

        print(type(e).__name__)
        print(str(e))