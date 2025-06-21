# Book AI Tutor

## Executive Summary

This document lays out a blueprint for transforming your existing Django front‑end into a **retrieval‑augmented, agent‑driven AI tutor** for a single textbook.  It covers (1) a production‑ready RAG data pipeline, (2) the design of an agent that can reason over student context, and (3) the wiring that glues LangChain / LangGraph to Django.  Where possible, examples and code snippets are linked to current best‑practice tutorials and real‑world reference implementations.  Follow the sections in order; together they amount to roughly a 3–4 page implementation notebook.

---

## 1. System Architecture Overview

### 1.1  High‑Level Flow

1. **Ingestion (offline)** – PDF ➞ chunk ➞ embed ➞ vector store.
2. **Query (online)** – user question ➞ embed ➞ similarity search ➞ prompt assembly ➞ LLM generation ➞ answer.
3. **Agentic loop (optional)** – the answer step can instead be delegated to a stateful agent orchestrated by LangGraph, allowing multiple tool calls and self‑reflection before finalising a reply.

A concise diagram of this flow appears in most modern RAG tutorials ([python.langchain.com](https://python.langchain.com/docs/tutorials/rag/)).

### 1.2  Django Project Layout

```
ai_tutor/
 ├─ ai_tutor/          # Django settings, URLs, ASGI
 ├─ tutor_app/
 │   ├─ models.py      # Session, Chat, Document, Page
 │   ├─ views.py       # chat_view, upload_view, agent_api
 │   ├─ tasks.py       # Celery / Django‑Q workers for embedding & indexing
 │   └─ services/
 │       ├─ rag.py     # retrieval chain
 │       └─ agent.py   # LangGraph agent wrapper
 └─ requirements.txt
```

This folder skeleton is adapted from a public demo that marries Django, LangChain and React ([medium.com](https://medium.com/%40galihlprakoso/rapidly-build-a-powerful-rag-application-with-django-langchain-react-and-elasticsearch-efcae57755de)).

---

## 2. Retrieval‑Augmented Generation (RAG) Module

### 2.1  Document Ingestion

* **Loader** – `PyPDFLoader` (or `pymupdf4llm` for markdown conversion).
* **Splitter** – `RecursiveCharacterTextSplitter` at \~1 000 tokens with 10‑20 % overlap to preserve context ([medium.com](https://medium.com/%40alexrodriguesj/retrieval-augmented-generation-rag-with-langchain-and-faiss-a3997f95b551)).
* **Embeddings** – `OpenAIEmbeddings` (or local model via `OllamaEmbeddings`).
* **Vector Store** – start with FAISS for local prototypes; graduate to Chroma or ElasticSearch for production scale ([medium.com](https://medium.com/%40alexrodriguesj/retrieval-augmented-generation-rag-with-langchain-and-faiss-a3997f95b551), [realpython.com](https://realpython.com/chromadb-vector-database/)).

### 2.2  Chunk Metadata

Store `page`, `chapter`, and a stable `doc_id` in the metadata field; this lets the tutor cite exact pages in its answers and power features like **“jump‑to‑page”** in the UI.

### 2.3  Retrieval Chain

```python
retriever = vector_store.as_retriever(search_type="similarity", k=6)
prompt = hub.pull("langchain-ai/retrieval-qa-chat")
chain = create_retrieval_chain(retriever, prompt)
```

Code identical to the minimal RAG example in the LangChain docs ([python.langchain.com](https://python.langchain.com/docs/tutorials/rag/)).

### 2.4  Prompt Fusion

A three‑part template works well:

1. **System‑level role** ("You are an AI tutor for <Book Title>")
2. **Context block** – injected documents in quoted form
3. **User question**

### 2.5  Post‑processing

* **Source highlighting** – return the top‑k pages with answer.
* **Fallback handling** – if retrieval score < τ, respond “I don’t know – let’s search the glossary...”.

---

## 3. Agentic Mode with LangGraph

LangGraph gives you a graph‑native way to coordinate loops of **Thought → Action → Observation** while persisting state across turns ([langchain-ai.github.io](https://langchain-ai.github.io/langgraph/)).

### 3.1  Observability

* **Fully Observable** – the agent consumes chat history **and** the student’s profile (grade, learning objective, recent mistakes).
* **Partially Observable** – if privacy settings restrict access, only the current question and limited metadata are provided.  The theoretical underpinnings come from RL literature on POMDPs ([ai.stackexchange.com](https://ai.stackexchange.com/questions/27913/what-exactly-are-partially-observable-environments)).

### 3.2  State & Action Spaces

* **State** ≈ `TutorState(messages: List[ChatMessage], memory: Dict, context: Dict)` – **continuous** because embeddings and scores are float tensors.
* **Actions** – discrete tool invocations (`search_book`, `explain`, `quiz_me`, `show_example`), but the policy may emit parameters in continuous space (e.g. temperature).

### 3.3  Learning Agent Pattern

Implement policy improvement with **offline RL‑style evaluation**: track reward = (helpfulness – latency – hallucination\_penalty) and periodically fine‑tune a policy head using LangSmith evals ([langchain.com](https://www.langchain.com/langsmith?utm_source=chatgpt.com), [medium.com](https://medium.com/towards-agi/how-to-use-langsmith-for-monitoring-langchain-applications-ffea867515fb?utm_source=chatgpt.com)).

### 3.4  Core Components Mapping

| Component          | Concrete Implementation                                                                                                                                                       |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Percepts**       | incoming JSON {question, session\_id, client\_meta}                                                                                                                           |
| **Internal State** | LangGraph memory node (Redis or SQLite)                                                                                                                                       |
| **Policy**         | LLM + ReAct loop (`create_react_agent`) ([medium.com](https://medium.com/%40piyushkashyap045/a-comprehensive-guide-to-understanding-langchain-agents-and-tools-43a187414f4c)) |
| **Tools**          | `search_book`, `summarise`, `code_exec`, external web search                                                                                                                  |
| **Goals**          | maximise correctness & pedagogical clarity; minimise tokens                                                                                                                   |

### 3.5  Skeleton Graph

```python
from langgraph.graph import StateGraph, END
from tutor_app.tools import search_book, quiz

graph = StateGraph("Tutor")
state = {
    "messages": [],
    "memory": {},
}
node_policy = create_react_agent(llm, tools=[search_book, quiz])

# Define edges
graph.add_node("policy", node_policy)
graph.add_edge("policy", END)
agent = graph.compile(state)
```

---

## 4. Integrating LangChain / LangGraph With Django

### 4.1  Dependencies

```bash
pip install django langchain langgraph langchain-openai faiss-cpu chromadb django-q redis
```

### 4.2  Async Invocation Path

* **Upload PDF** → `upload_view` saves file and queues `index_pdf.delay(doc_id)`
* **Chat POST /api/chat** → `agent_api` puts question into LangGraph agent, streams tokens via Django Channels (WebSocket).

Practical notes on Django + async + OpenAI embeddings are discussed in community threads ([reddit.com](https://www.reddit.com/r/django/comments/1h54cve/django_djangoninja_async_for_openai_assistants/?utm_source=chatgpt.com)).

### 4.3  Background Tasks

Use **Celery** or **Django‑Q** for long‑running embedding jobs, mirroring the Medium reference implementation ([medium.com](https://medium.com/%40galihlprakoso/rapidly-build-a-powerful-rag-application-with-django-langchain-react-and-elasticsearch-efcae57755de)).

### 4.4  Persistence Layer

* Chat + Session tables already exist.
* Add `VectorIndex` table pointing to external FAISS/Chroma file and re‑compute hashes when the book is updated.

---

## 5. Evaluation, Monitoring & Observability

* Enable LangSmith tracing via `LANGSMITH_TRACING=true` and project env vars ([python.langchain.com](https://python.langchain.com/docs/tutorials/rag/), [docs.smith.langchain.com](https://docs.smith.langchain.com/observability/how_to_guides?utm_source=chatgpt.com)).
* Capture **OpenTelemetry** traces automatically (supported since March 2025) ([blog.langchain.dev](https://blog.langchain.dev/end-to-end-opentelemetry-langsmith/?utm_source=chatgpt.com)).
* Define custom callbacks to log reward metrics and store them in Postgres for offline policy tuning.

---

## 6. Security, Cost & Scalability

* **Token usage** – embed once, reuse; compress memory via `gguf` local embeddings when idle ([medium.com](https://medium.com/%40alexrodriguesj/retrieval-augmented-generation-rag-with-langchain-and-faiss-a3997f95b551)).
* **Rate limiting** – wrap LLM calls with exponential back‑off & caching (see LangChain how‑to on rate‑limits) ([python.langchain.com](https://python.langchain.com/docs/tutorials/rag/)).
* **Data privacy** – keep raw PDF only on‑prem; send chunks to OpenAI under **data‑protection agreements**.

---

## 7. Roadmap & Next Steps

1. Add **quiz‑generator** tool that writes multiple‑choice questions from book pages.
2. Experiment with **contextual compression retrievers** to shrink prompt windows.
3. Use **LangGraph breakpoints** for human‑in‑the‑loop grading of answers.
4. Auto‑fine‑tune a small local model with anonymised transcripts once enough feedback is collected.

---

### Appendix – Key Resources

* LangChain RAG tutorial (Parts 1‑2) ([python.langchain.com](https://python.langchain.com/docs/tutorials/rag/))
* Django‑based RAG demo ([medium.com](https://medium.com/%40galihlprakoso/rapidly-build-a-powerful-rag-application-with-django-langchain-react-and-elasticsearch-efcae57755de))
* FAISS implementation notes ([medium.com](https://medium.com/%40alexrodriguesj/retrieval-augmented-generation-rag-with-langchain-and-faiss-a3997f95b551))
* Chroma vector DB guide ([realpython.com](https://realpython.com/chromadb-vector-database/))
* LangGraph docs ([langchain-ai.github.io](https://langchain-ai.github.io/langgraph/))
* LangChain agents and tools deep‑dive ([medium.com](https://medium.com/%40piyushkashyap045/a-comprehensive-guide-to-understanding-langchain-agents-and-tools-43a187414f4c))
* Observability with LangSmith ([langchain.com](https://www.langchain.com/langsmith?utm_source=chatgpt.com))
* POMDP definition thread ([ai.stackexchange.com](https://ai.stackexchange.com/questions/27913/what-exactly-are-partially-observable-environments))

---

*Prepared June 20 2025 for Shehran.*

***
---
---
***


Based on the README.md blueprint, I understand you're building a Django-based AI tutor system with RAG and agentic capabilities. Here's my technical interpretation:

### Core Architecture Components
1. **RAG Pipeline**
   - **Offline Processing**: PDF → PyPDFLoader → RecursiveCharacterTextSplitter (1K tokens, 10-20% overlap) → OpenAIEmbeddings → FAISS/Chroma
   - **Metadata Strategy**: `{page, chapter, doc_id}` for citations and UI navigation
   - **Retrieval**: Similarity search (k=6) with fallback mechanism when confidence < τ

2. **Agent System**
   - **Framework**: LangGraph for stateful agent orchestration
   - **State Design**: `TutorState(messages, memory, context)` with POMDP-style observability
   - **Tools**: `search_book`, `summarise`, `code_exec`, `quiz_me` with ReAct policy
   - **Learning**: Reward = (helpfulness - latency - hallucination_penalty) tracked via LangSmith

3. **Django Integration**
   - **Async Flow**: 
     ```mermaid
     graph LR
     A[PDF Upload] --> B[Background Embedding Task]
     C[Chat API] --> D[LangGraph Agent]
     D --> E[WebSocket Streaming]
     ```
   - **Key Dependencies**: `django-q`, `langgraph`, `faiss-cpu`, `chromadb`
   - **Persistence**: Redis for agent state + Postgres for chat history

### Critical Implementation Notes
1. **Vector DB Migration Path**
   ```python
   # Prototype vs Production
   if DEBUG:
       vector_store = FAISS.from_documents(chunks, embeddings)
   else:
       vector_store = Chroma.from_documents(chunks, embeddings, persist_dir=PERSIST_PATH)
   ```

2. **Agent Security Considerations**
   - PDF processing on-premises only
   - OpenAI data processing agreement for embeddings
   - Token compression via `gguf` during idle periods

3. **Performance Optimizations**
   - Contextual compression retrievers for prompt shrinking
   - Exponential backoff with Redis caching for LLM calls
   - LangGraph breakpoints for human-in-loop validation

### Immediate Next Steps
1. **Scaffold Django Services**:
   ```bash
   mkdir -p tutor_app/services
   touch tutor_app/services/rag.py tutor_app/services/agent.py
   ```
2. **Implement Priority Tools**:
   - `search_book` (RAG core)
   - `quiz_me` (roadmap item #1)
3. **Configure Observability**:
   ```python
   # settings.py
   import os
   os.environ["LANGSMITH_TRACING"] = "true"
   os.environ["LANGCHAIN_PROJECT"] = "ai_tutor_prod"Based on the README.md blueprint, I understand you're building a Django-based AI tutor system with RAG and agentic capabilities. Here's my technical interpretation:

### Core Architecture Components
1. **RAG Pipeline**
   - **Offline Processing**: PDF → PyPDFLoader → RecursiveCharacterTextSplitter (1K tokens, 10-20% overlap) → OpenAIEmbeddings → FAISS/Chroma
   - **Metadata Strategy**: `{page, chapter, doc_id}` for citations and UI navigation
   - **Retrieval**: Similarity search (k=6) with fallback mechanism when confidence < τ

2. **Agent System**
   - **Framework**: LangGraph for stateful agent orchestration
   - **State Design**: `TutorState(messages, memory, context)` with POMDP-style observability
   - **Tools**: `search_book`, `summarise`, `code_exec`, `quiz_me` with ReAct policy
   - **Learning**: Reward = (helpfulness - latency - hallucination_penalty) tracked via LangSmith

3. **Django Integration**
   - **Async Flow**: 
     ```mermaid
     graph LR
     A[PDF Upload] --> B[Background Embedding Task]
     C[Chat API] --> D[LangGraph Agent]
     D --> E[WebSocket Streaming]
     ```
   - **Key Dependencies**: `django-q`, `langgraph`, `faiss-cpu`, `chromadb`
   - **Persistence**: Redis for agent state + Postgres for chat history

### Critical Implementation Notes
1. **Vector DB Migration Path**
   ```python
   # Prototype vs Production
   if DEBUG:
       vector_store = FAISS.from_documents(chunks, embeddings)
   else:
       vector_store = Chroma.from_documents(chunks, embeddings, persist_dir=PERSIST_PATH)
   ```

2. **Agent Security Considerations**
   - PDF processing on-premises only
   - OpenAI data processing agreement for embeddings
   - Token compression via `gguf` during idle periods

3. **Performance Optimizations**
   - Contextual compression retrievers for prompt shrinking
   - Exponential backoff with Redis caching for LLM calls
   - LangGraph breakpoints for human-in-loop validation

### Immediate Next Steps
1. **Scaffold Django Services**:
   ```bash
   mkdir -p tutor_app/services
   touch tutor_app/services/rag.py tutor_app/services/agent.py
   ```
2. **Implement Priority Tools**:
   - `search_book` (RAG core)
   - `quiz_me` (roadmap item #1)
3. **Configure Observability**:
   ```python
   # settings.py
   import os
   os.environ["LANGSMITH_TRACING"] = "true"
   os.environ["LANGCHAIN_PROJECT"] = "ai_tutor_prod"
   ```

The architecture provides a solid foundation - I recommend starting with Section 2 (RAG module) before tackling the LangGraph integration. The linked resources (especially the Medium Django-RAG tutorial) are crucial for implementation specifics.
   ```

The architecture provides a solid foundation - I recommend starting with Section 2 (RAG module) before tackling the LangGraph integration. The linked resources (especially the Medium Django-RAG tutorial) are crucial for implementation specifics.