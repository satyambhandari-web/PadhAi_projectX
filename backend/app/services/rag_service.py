import os
import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv

from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_classic.chains import RetrievalQA

load_dotenv()

logger = logging.getLogger(__name__)



class RAGService:

    def __init__(self):

        # backend/
        self.base_dir = (
            Path(__file__).resolve().parent.parent.parent
        )

        # backend/uploads/
        self.upload_dir = self.base_dir / "uploads"

        # backend/rag_chroma_db/
        self.persist_directory = (
            self.base_dir / "rag_chroma_db"
        )

        # Chroma collection
        self.collection_name = "PadhAi_Materials"

        # Configurable models
        self.embedding_model = os.getenv(
            "EMBEDDING_MODEL",
            "models/gemini-embedding-001"
        )

        self.llm_model = os.getenv(
            "GROQ_MODEL",
            "openai/gpt-oss-20b"
        )

        # Chunking configuration
        self.chunk_size = int(
            os.getenv("RAG_CHUNK_SIZE", "1000")
        )

        self.chunk_overlap = int(
            os.getenv("RAG_CHUNK_OVERLAP", "200")
        )

        # Retrieval configuration
        self.retrieval_k = int(
            os.getenv("RAG_RETRIEVAL_K", "8")
        )

        self.retrieval_fetch_k = int(
            os.getenv("RAG_RETRIEVAL_FETCH_K", "20")
        )

        # Create required directories
        self.upload_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        self.persist_directory.mkdir(
            parents=True,
            exist_ok=True
        )

        # Validate API keys
        self._validate_environment()

        logger.info("RAGService initialized successfully.")

    def _validate_environment(self):

        required_keys = [
            "GROQ_API_KEY",
            "GEMINI_API_KEY",
        ]

        missing_keys = [
            key
            for key in required_keys
            if not os.getenv(key)
        ]

        if missing_keys:
            raise EnvironmentError(
                "Missing required environment variables: "
                + ", ".join(missing_keys)
            )

    def get_embeddings(self):

        return GoogleGenerativeAIEmbeddings(
            model=self.embedding_model,
            google_api_key=os.getenv("GEMINI_API_KEY"),
        )

    def get_llm(
        self,
        model: Optional[str] = None,
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ):

        return ChatGroq(
            model=model or self.llm_model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

    def run_llm(
        self,
        prompt: str,
        model: Optional[str] = None,
        temperature: float = 0.1,
        max_tokens: int = 1024,
    ):

        if not prompt or not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        llm = self.get_llm(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        response = llm.invoke(prompt)

        return response.content

    def process_pdf(
        self,
        pdf_path,
        material_id: str,
    ) -> List[Any]:
        """
        Load and split one selected PDF.

        material_id uniquely identifies the PDF.
        """

        if not material_id or not material_id.strip():
            raise ValueError(
                "material_id is required."
            )

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {pdf_path}"
            )

        if not pdf_path.is_file():
            raise ValueError(
                f"Selected path is not a file: {pdf_path}"
            )

        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Selected file is not a PDF: "
                f"{pdf_path.name}"
            )

        logger.info(
            "Processing PDF: %s | material_id=%s",
            pdf_path.name,
            material_id,
        )

        loader = PyPDFLoader(str(pdf_path))

        pages = loader.load()

        if not pages:
            raise ValueError(
                "PDF contains no readable pages."
            )

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
        )

        splits = splitter.split_documents(pages)

        if not splits:
            raise ValueError(
                "No text could be extracted from the PDF."
            )

        # Add source metadata
        for index, doc in enumerate(splits):

            doc.metadata.update({
                "material_id": material_id,
                "filename": pdf_path.name,
                "chunk_index": index,
                "source": pdf_path.name,
            })

        logger.info(
            "%s split into %s chunks.",
            pdf_path.name,
            len(splits),
        )

        return splits

    def get_vector_store(self):

        return Chroma(
            embedding_function=self.get_embeddings(),
            persist_directory=str(
                self.persist_directory
            ),
            collection_name=self.collection_name,
        )

    def generate_and_store_embeddings(
        self,
        pdf_path,
        material_id: str,
    ) -> Dict[str, Any]:
        """
        Create embeddings for a PDF and store them.

        Uses unique IDs to prevent duplicate chunks.
        """

        splits = self.process_pdf(
            pdf_path=pdf_path,
            material_id=material_id,
        )

        vector_store = self.get_vector_store()

        # Unique IDs for every chunk
        chunk_ids = [
            f"{material_id}_{index}"
            for index in range(len(splits))
        ]

        # Add only new chunks
        vector_store.add_documents(
            documents=splits,
            ids=chunk_ids,
        )

        logger.info(
            "Stored %s chunks for material_id=%s",
            len(splits),
            material_id,
        )

        return {
            "material_id": material_id,
            "filename": Path(pdf_path).name,
            "chunks_stored": len(splits),
            "status": "success",
        }
    def create_retriever(
        self,
        material_id: Optional[str] = None,
    ):
        """
        Create a retriever restricted to one PDF
        when material_id is provided.
        """

        vector_store = self.get_vector_store()

        search_kwargs = {
            "k": self.retrieval_k,
            "fetch_k": self.retrieval_fetch_k,
        }

        if material_id:

            search_kwargs["filter"] = {
                "material_id": material_id
            }

        return vector_store.as_retriever(
            search_type="mmr",
            search_kwargs=search_kwargs,
        )

    def get_retriever(
        self,
        material_id: Optional[str] = None,
    ):

        return self.create_retriever(
            material_id=material_id
        )

    def create_rag_chain(
        self,
        prompt: str,
        material_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Run RAG for a selected PDF.

        Returns answer + source documents.
        """

        if not prompt or not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        if not material_id:
            raise ValueError(
                "material_id is required for PDF-based RAG."
            )

        retriever = self.create_retriever(
            material_id=material_id
        )

        # Retrieve documents first
        documents = retriever.invoke(prompt)

        if not documents:
            return {
                "answer": (
                    "I couldn't find relevant information "
                    "in the selected PDF."
                ),
                "source_documents": [],
            }

        llm = self.get_llm()

        rag_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True,
        )

        response = rag_chain.invoke({
            "query": prompt
        })

        return {
            "answer": response.get("result", ""),
            "source_documents": response.get(
                "source_documents",
                []
            ),
        }

if __name__ == "__main__":

    rag_service = RAGService()

    pdf_path = (
        rag_service.upload_dir
        / "PYTHON U1 NOTES.pdf"
    )

    material_id = "python-u1"

    result = (
        rag_service.generate_and_store_embeddings(
            pdf_path=pdf_path,
            material_id=material_id,
        )
    )

    print(result)

    response = rag_service.create_rag_chain(
        prompt=(
            "Give me a detailed summary "
            "of Python Unit 1."
        ),
        material_id=material_id,
    )

    print(response["answer"])

    print("\nSources:")

    for doc in response["source_documents"]:

        print({
            "filename": doc.metadata.get("filename"),
            "page": doc.metadata.get("page"),
            "material_id": doc.metadata.get(
                "material_id"
            ),
        })