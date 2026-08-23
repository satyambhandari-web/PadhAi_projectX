from pathlib import Path
from langchain_community.document_loaders import PyPDFLoader


def load_pdf(pdf_path: str):
    """
    Load a PDF and return its pages as LangChain Documents.
    """

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {pdf_path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported.")

    loader = PyPDFLoader(str(path))
    documents = loader.load()

    return documents


def extract_text_from_pdf(pdf_path: str) -> str:
    """
    Extract all text from a PDF into a single string.
    """

    documents = load_pdf(pdf_path)

    text = "\n\n".join(
        document.page_content
        for document in documents
        if document.page_content.strip()
    )

    return text


def get_pdf_page_count(pdf_path: str) -> int:
    """
    Return the number of pages in a PDF.
    """

    documents = load_pdf(pdf_path)
    return len(documents)


if __name__ == "__main__":
    pdf_path = "./uploads/PYTHON U1 NOTES.pdf"

    try:
        documents = load_pdf(pdf_path)

        print("=" * 60)
        print("PDF SERVICE TEST")
        print("=" * 60)

        print(f"Pages: {len(documents)}")
        print(f"Characters: {len(extract_text_from_pdf(pdf_path))}")

        print("\nFirst page preview:")
        print(documents[0].page_content[:500])

    except Exception as e:
        print(f"Error: {e}")