import os
from langchain_community.document_loaders import (
    DirectoryLoader,
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings

# --- Constants ---
CURRICULUM_PATH = "Curriculum/"
VECTORSTORE_PATH = "./chroma_db"
EMBEDDING_MODEL = "nomic-embed-text"

def get_vectorstore(rebuild: bool = False):
    """
    Loads or creates a vector store from all documents in the Curriculum directory.

    Args:
        rebuild (bool): If True, forces recreation of the vector store.

    Returns:
        A Chroma vector store instance.
    """
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    if os.path.exists(VECTORSTORE_PATH) and not rebuild:
        print("Loading existing vector store.")
        return Chroma(persist_directory=VECTORSTORE_PATH, embedding_function=embeddings)

    print(f"Building new vector store from directory: {CURRICULUM_PATH}")
    if not os.path.exists(CURRICULUM_PATH):
        raise FileNotFoundError(f"The curriculum directory was not found at: {CURRICULUM_PATH}")

    # Use DirectoryLoader to handle multiple file types
    loader = DirectoryLoader(
        CURRICULUM_PATH,
        glob="**/*.*",  # Scan all subdirectories and files
        use_multithreading=True,
        show_progress=True,
        loader_map={
            ".pdf": PyPDFLoader,
            ".md": UnstructuredMarkdownLoader,
            ".txt": TextLoader,
        },
    )

    documents = loader.load()
    if not documents:
        raise ValueError(f"No documents could be loaded from {CURRICULUM_PATH}. Check the directory and file permissions.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(documents)

    print(f"Creating vector store from {len(chunks)} chunks...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=VECTORSTORE_PATH
    )
    print("Vector store created successfully.")
    return vectorstore

def get_parsed_curriculum_content():
    """
    Loads all documents from the curriculum and returns a concatenated string for display.
    """
    if not os.path.exists(CURRICULUM_PATH):
        return "Curriculum directory not found."

    # This uses a simple text loader for display purposes to show raw content
    display_loader = DirectoryLoader(CURRICULUM_PATH, glob="**/*.*", loader_cls=TextLoader)
    documents = display_loader.load()

    content = ""
    for doc in documents:
        source_path = os.path.relpath(doc.metadata['source'], CURRICULUM_PATH)
        content += f"--- Source: {source_path} ---\n"
        content += doc.page_content[:1000] + "\n\n" # Preview first 1000 chars
    return content if content else "No text documents found to display."

