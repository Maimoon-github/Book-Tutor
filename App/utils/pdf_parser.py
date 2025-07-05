import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# --- Constants ---
PDF_PATH = "/home/maimoon/Documents/Project Repos/Book-Tutor/docs/thiswayEnglishBook-5-2020 - Punjab -20.01.22.pdf"
VECTORSTORE_PATH = "./chroma_db"
OLLAMA_MODEL = "llama3"

def get_vectorstore(rebuild: bool = False):
    """
    Loads or creates a vector store from the PDF curriculum.

    Args:
        rebuild (bool): If True, forces the recreation of the vector store
                        even if it already exists.

    Returns:
        A Chroma vector store instance.
    """
    embeddings = OllamaEmbeddings(model=OLLAMA_MODEL)

    if os.path.exists(VECTORSTORE_PATH) and not rebuild:
        print("Loading existing vector store.")
        return Chroma(persist_directory=VECTORSTORE_PATH, embedding_function=embeddings)

    print("Vector store not found. Building a new one...")
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"The curriculum PDF was not found at: {PDF_PATH}")

    # 1. Load the PDF
    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    # 2. Split the document into chunks
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    if not chunks:
        raise ValueError("The PDF could not be split into chunks. Check the PDF content.")

    # 3. Create and persist the vector store
    print(f"Creating vector store from {len(chunks)} chunks...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_PATH
    )
    print("Vector store created successfully.")
    return vectorstore

def get_parsed_pdf_content():
    """
    Loads the PDF and returns the raw text content of the first few pages for display.
    """
    if not os.path.exists(PDF_PATH):
        return "Curriculum PDF not found."

    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()

    content = ""
    for i, page in enumerate(documents):
        if i < 5: # Limit to first 5 pages for display
            content += f"--- Page {i+1} ---\n"
            content += page.page_content
            content += "\n\n"
    return content

if __name__ == '__main__':
    # Test the vector store creation
    print("Testing the vector store creation...")
    db = get_vectorstore(rebuild=True)
    print(f"Vector store ready. Number of documents: {db._collection.count()}")

    # Test a similarity search
    print("\nTesting similarity search...")
    query = "What is a noun?"
    results = db.similarity_search(query, k=2)
    for doc in results:
        print(f"--- Result --- \n{doc.page_content[:200]}...")
