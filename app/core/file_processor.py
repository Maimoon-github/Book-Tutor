import os
import tempfile
from typing import List, Optional
from langchain_community.document_loaders import (
    PyPDFLoader,
    TextLoader,
    UnstructuredMarkdownLoader,
)
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import OllamaEmbeddings
from streamlit.runtime.uploaded_file_manager import UploadedFile

# --- Constants ---
EMBEDDING_MODEL = "nomic-embed-text"

def process_uploaded_files(uploaded_files: List[UploadedFile]) -> Optional[Chroma]:
    """
    Processes a list of user-uploaded files in a temporary directory,
    creates an in-memory vector store, and returns it.

    Args:
        uploaded_files: A list of files from st.file_uploader.

    Returns:
        A Chroma vector store instance or None if no files are processed.
    """
    if not uploaded_files:
        return None

    all_documents = []
    with tempfile.TemporaryDirectory() as temp_dir:
        for uploaded_file in uploaded_files:
            temp_path = os.path.join(temp_dir, uploaded_file.name)
            with open(temp_path, "wb") as f:
                f.write(uploaded_file.getvalue())

            try:
                if uploaded_file.name.lower().endswith(".pdf"):
                    loader = PyPDFLoader(temp_path)
                elif uploaded_file.name.lower().endswith(".md"):
                    loader = UnstructuredMarkdownLoader(temp_path)
                elif uploaded_file.name.lower().endswith(".txt"):
                    loader = TextLoader(temp_path)
                else:
                    continue

                all_documents.extend(loader.load())
            except Exception as e:
                print(f"Error loading file {uploaded_file.name}: {e}")
                continue

    if not all_documents:
        raise ValueError("None of the uploaded files could be processed. Please check file formats (.pdf, .txt, .md) and content.")

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    chunks = text_splitter.split_documents(all_documents)

    print(f"Creating in-memory vector store from {len(chunks)} chunks...")
    embeddings = OllamaEmbeddings(model=EMBEDDING_MODEL)
    vectorstore = Chroma.from_documents(documents=chunks, embedding=embeddings)
    print("Vector store created successfully.")

    return vectorstore
