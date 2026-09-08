import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_chroma import Chroma
from langchain_classic.chains import RetrievalQA

load_dotenv()


class RAGService:

    def __init__(self):
        # backend/
        self.base_dir = Path(__file__).resolve().parent.parent.parent

        # backend/uploads/
        self.upload_dir = self.base_dir / "uploads"

        # backend/rag_chroma_db/
        self.persist_directory = self.base_dir / "rag_chroma_db"

        # Chroma collection
        self.collection_name = "PadhAi_Materials"

    def run_llm(
        self,
        prompt: str,
        model="llama3-8b-8192",
        temperature=0.1,
        max_tokens=1024,
    ):
        llm = ChatGroq(
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )

        response = llm.invoke(prompt)

        print(response.content)

        return response.content

    def process_pdf(self, pdf_path, material_id):
        """
        Load and split one selected PDF.

        pdf_path:
            Full path of the selected PDF.

        material_id:
            Unique ID identifying the selected PDF.
        """

        pdf_path = Path(pdf_path)

        if not pdf_path.exists():
            raise FileNotFoundError(
                f"PDF file not found: {pdf_path}"
            )

        if pdf_path.suffix.lower() != ".pdf":
            raise ValueError(
                f"Selected file is not a PDF: {pdf_path.name}"
            )

        loader = PyPDFLoader(str(pdf_path))

        pages = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200,
        )

        splits = splitter.split_documents(pages)

        # Add information that identifies the source PDF.
        for doc in splits:
            doc.metadata["material_id"] = material_id
            doc.metadata["filename"] = pdf_path.name

        print(
            f"{pdf_path.name} has been split into "
            f"{len(splits)} chunks."
        )

        return splits

    def has_material(self, material_id: str) -> bool:
        """
        Check if Chroma vector store already contains documents for material_id.
        """
        if not material_id:
            return False
        try:
            embeddings = GoogleGenerativeAIEmbeddings(
                model="models/gemini-embedding-001",
                google_api_key=os.getenv("GEMINI_API_KEY"),
            )
            vector_store = Chroma(
                embedding_function=embeddings,
                persist_directory=str(self.persist_directory),
                collection_name=self.collection_name,
            )
            results = vector_store.get(where={"material_id": material_id}, limit=1)
            return len(results.get("ids", [])) > 0
        except Exception:
            return False

    def generate_and_store_embeddings(
        self,
        pdf_path,
        material_id,
    ):
        """
        Create embeddings for the selected PDF
        and store them in Chroma.
        """

        splits = self.process_pdf(
            pdf_path=pdf_path,
            material_id=material_id,
        )

        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=os.getenv("GEMINI_API_KEY"),
        )

        vector_store = Chroma(
            embedding_function=embeddings,
            persist_directory=str(self.persist_directory),
            collection_name=self.collection_name,
        )

        vector_store.add_documents(splits)

        print(
            f"Embeddings stored successfully for: "
            f"{Path(pdf_path).name}"
        )

        return len(splits)

    def get_material_content(
        self,
        query: str,
        material_id: str | None = None,
        max_chars: int = 6000,
    ) -> str:
        """
        Robustly retrieve educational content for a query and material_id.
        Tries ChromaDB vector search first. If ChromaDB returns no content,
        auto-indexes or loads text directly from the PDF file in uploads/.
        """
        content_parts = []

        # Auto-detect material_id from query if material_id is None
        if not material_id and query and self.upload_dir.exists():
            for pdf_file in self.upload_dir.iterdir():
                if pdf_file.is_file() and pdf_file.suffix.lower() == ".pdf":
                    if pdf_file.name.lower() in query.lower() or pdf_file.stem.lower() in query.lower():
                        material_id = pdf_file.name
                        break

        if material_id:
            pdf_path = self.upload_dir / Path(material_id).name
            if pdf_path.exists() and not self.has_material(material_id):
                try:
                    self.generate_and_store_embeddings(
                        pdf_path=str(pdf_path),
                        material_id=material_id,
                    )
                except Exception as e:
                    print(f"[RAG AUTO-INDEX WARNING] {e}")

        # Try ChromaDB retrieval
        try:
            retriever = self.get_retriever(material_id=material_id)
            docs = retriever.invoke(query or "key topics concepts definitions")
            for doc in docs:
                if hasattr(doc, "page_content") and doc.page_content and doc.page_content.strip():
                    content_parts.append(doc.page_content.strip())
        except Exception as e:
            print(f"[RAG RETRIEVAL ERROR] {e}")

        # Fallback to direct PDF text if ChromaDB returned empty content
        if not content_parts:
            if material_id:
                pdf_path = self.upload_dir / Path(material_id).name
                if pdf_path.exists():
                    try:
                        from app.services.pdf_service import extract_text_from_pdf
                        pdf_text = extract_text_from_pdf(str(pdf_path))
                        if pdf_text and pdf_text.strip():
                            content_parts.append(pdf_text.strip())
                    except Exception as e:
                        print(f"[PDF FALLBACK ERROR] {e}")

            # If still empty or material_id was not found, search all PDFs in uploads
            if not content_parts and self.upload_dir.exists():
                for pdf_file in self.upload_dir.glob("*.pdf"):
                    try:
                        from app.services.pdf_service import extract_text_from_pdf
                        pdf_text = extract_text_from_pdf(str(pdf_file))
                        if pdf_text and pdf_text.strip():
                            content_parts.append(f"--- {pdf_file.name} ---\n" + pdf_text.strip())
                            break
                    except Exception as e:
                        print(f"[PDF FALLBACK ALL ERROR] {e}")

        full_content = "\n\n".join(content_parts).strip()
        if len(full_content) > max_chars:
            full_content = full_content[:max_chars]

        if not full_content:
            return "No relevant educational material was found for the selected topic."

        return full_content

    def create_retriever(self, material_id=None):
        """
        Create a retriever.

        If material_id is provided, retrieval should
        be restricted to that selected material.
        """

        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=os.getenv("GEMINI_API_KEY"),
        )

        vector_store = Chroma(
            embedding_function=embeddings,
            persist_directory=str(self.persist_directory),
            collection_name=self.collection_name,
        )

        search_kwargs = {
            "k": 8,
            "fetch_k": 20,
        }

        # Restrict retrieval to the selected PDF.
        if material_id:
            search_kwargs["filter"] = {
                "material_id": material_id
            }

        return vector_store.as_retriever(
            search_type="mmr",
            search_kwargs=search_kwargs,
        )

    def get_retriever(self, material_id=None):
        return self.create_retriever(
            material_id=material_id
        )

    def get_llm(self, model="openai/gpt-oss-20b"):

        llm = ChatGroq(
            model=model,
            temperature=0.3,
            max_tokens=1024,
        )

        return llm

    def create_rag_chain(
        self,
        prompt: str,
        material_id=None,
    ):
        """
        Create a RAG chain for the selected material.
        """

        llm = self.get_llm()

        retriever = self.create_retriever(
            material_id=material_id
        )

        rag_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True,
        )

        response = rag_chain.invoke(
            {
                "query": prompt
            }
        )

        return response


if __name__ == "__main__":

    rag_service = RAGService()

    # Example PDF from backend/uploads/
    pdf_path = (
        rag_service.upload_dir
        / "PYTHON U1 NOTES.pdf"
    )

    material_id = "python-u1"

    rag_service.generate_and_store_embeddings(
        pdf_path=pdf_path,
        material_id=material_id,
    )

    result = rag_service.create_rag_chain(
        prompt="Give me a detailed summary of this Python Unit 1.",
        material_id=material_id,
    )

    print(result)