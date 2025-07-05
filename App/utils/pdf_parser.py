import os
from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
# Corrected import path to use langchain_community as the stable entry point
from langchain_community.embeddings import OllamaEmbeddings

# --- Constants ---
PDF_PATH = "Curriculum/thiswayEnglishBook-5-2020 - Punjab -20.01.22.pdf"
VECTORSTORE_PATH = "./chroma_db"
# Use the specified embedding model
EMBEDDING_MODEL = "nomic-embed-text"

def get_vectorstore(rebuild: bool = False):
    """
    Loads or creates a vector store from the PDF curriculum using the specified
    Ollama embedding model.

    Args:
        rebuild (bool): If True, forces the recreation of the vector store.

    Returns:
        A Chroma vector store instance.
    """
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    if os.path.exists(VECTORSTORE_PATH) and not rebuild:
        print("Loading existing vector store.")
        return Chroma(persist_directory=VECTORSTORE_PATH, embedding_function=embeddings)

    print(f"Building new vector store with '{EMBEDDING_MODEL}' embeddings...")
    if not os.path.exists(PDF_PATH):
        raise FileNotFoundError(f"The curriculum PDF was not found at: {PDF_PATH}")

    loader = PyPDFLoader(PDF_PATH)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    if not chunks:
        raise ValueError("The PDF could not be split into chunks. Check the PDF content.")

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
    # Limit to first 5 pages for a streamlined display
    for i, page in enumerate(documents[:5]):
        content += f"--- Page {i+1} ---\n"
        content += page.page_content
        content += "\n\n"
    return content
