import os
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from typing import List

# --- Constants ---
# Use a relative path for better portability
CURRICULUM_PATH = "/home/maimoon/Documents/Project Repos/Book-Tutor/Curriculum"
VECTORSTORE_PATH = "./chroma_db"
EMBEDDING_MODEL = "nomic-embed-text"

def load_all_documents(path: str) -> List:
    """
    Loads all supported documents from a given directory path.
    """
    all_documents = []
    for root, _, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            if file.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
                all_documents.extend(loader.load())
            elif file.endswith(".md"):
                loader = UnstructuredMarkdownLoader(file_path)
                all_documents.extend(loader.load())
            elif file.endswith(".txt"):
                loader = TextLoader(file_path)
                all_documents.extend(loader.load())
    return all_documents


def get_vectorstore(rebuild: bool = False):
    """
    Loads or creates a vector store from all documents in the Curriculum directory.
    """
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)

    if os.path.exists(VECTORSTORE_PATH) and not rebuild:
        print("Loading existing vector store.")
        return Chroma(persist_directory=VECTORSTORE_PATH, embedding_function=embeddings)

    print(f"Building new vector store from directory: {CURRICULUM_PATH}")
    if not os.path.exists(CURRICULUM_PATH):
        raise FileNotFoundError(f"The curriculum directory was not found at: {CURRICULUM_PATH}")

    documents = load_all_documents(CURRICULUM_PATH)
    if not documents:
        raise ValueError(f"No documents could be loaded from {CURRICULUM_PATH}. Check the directory and file types.")

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

    documents = load_all_documents(CURRICULUM_PATH)

    content = ""
    for doc in documents:
        source_path = doc.metadata.get('source', 'Unknown source')
        relative_path = os.path.relpath(source_path, CURRICULUM_PATH)
        content += f"--- Source: {relative_path} ---\n"
        content += doc.page_content[:1000] + "\n...\n\n" # Preview first 1000 chars
    return content if content else "No documents found to display."
