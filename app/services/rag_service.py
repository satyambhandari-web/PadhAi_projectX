import os

from langchain_groq import ChatGroq
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain_community.vectorstores import Chroma
from langchain_classic.chains import RetrievalQA

from dotenv import load_dotenv

load_dotenv()


class RAGService:

    def __init__(self):
        self.pdf_path = "./uploads/PYTHON U1 NOTES.pdf"
        self.persist_directory = "rag_chroma_db"
        self.collection_name = "Python_Unit1"

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
            max_tokens=max_tokens
        )

        response = llm.invoke(prompt)

        print(response.content)

    def process_pdf(self):

        loader = PyPDFLoader(self.pdf_path)

        pages = loader.load()

        splitter = RecursiveCharacterTextSplitter(
            chunk_size=1000,
            chunk_overlap=200
        )

        splits = splitter.split_documents(pages)

        print(f"The document has been split into {len(splits)} chunks.")

        return splits

    def generate_and_store_embeddings(self):

        splits = self.process_pdf()

        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

        vector_store = Chroma(
            embedding_function=embeddings,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name
        )

        vector_store.add_documents(splits)

        print("Embeddings stored successfully.")

    def create_retriever(self):

        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=os.getenv("GEMINI_API_KEY")
        )

        vector_store = Chroma(
            embedding_function=embeddings,
            persist_directory=self.persist_directory,
            collection_name=self.collection_name
        )

        return vector_store.as_retriever(
            search_kwargs={"k": 4}
        )

    def get_retriever(self):
        return self.create_retriever()

    def get_llm(self, model="openai/gpt-oss-20b"):

        llm = ChatGroq(
            model=model,
            temperature=0.3,
            max_tokens=256
        )

        return llm

    def create_rag_chain(self, prompt: str):

        llm = self.get_llm()

        retriever = self.create_retriever()

        rag_chain = RetrievalQA.from_chain_type(
            llm=llm,
            retriever=retriever,
            return_source_documents=True
        )

        response = rag_chain.invoke(
            {"query": prompt}
        )

        return response


if __name__ == "__main__":

    rag_service = RAGService()
     
    rag_service.generate_and_store_embeddings()

    result = rag_service.create_rag_chain(
        "Give me a detailed summary of this Python Unit 1."
    )

    print(result)