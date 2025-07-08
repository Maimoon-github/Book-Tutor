System Overview

This document outlines the development requirements for a voice-interactive AI tutoring system. The system is designed to take user voice input, understand the user's intent, and respond by either fetching a pre-defined exercise, generating a response using a Retrieval-Augmented Generation (RAG) pipeline, or recalling previous context. It maintains a memory of the conversation and delivers its response as synthesized audio.

Module 1: UI Layer & Input Processing

1.1. User Voice Input & Streaming

Objective: Capture audio from the user's microphone and stream it for real-time processing.

Inputs: Raw audio stream from the device's microphone.

Outputs: A continuous stream of audio data chunks.

Core Logic:

Request microphone access from the user.

Once access is granted, begin capturing audio.

Use a library like MediaRecorder (in a browser) or a platform-specific audio API.

Encode the audio into a suitable format (e.g., PCM, WAV, or Opus).

Break the audio into small chunks and send them to the ASR Transcription service over a WebSocket or similar streaming connection.

Dependencies: Web Audio API, WebSocket client.

1.2. ASR (Automatic Speech Recognition) Transcription

Objective: Convert the incoming audio stream into a live text transcription.

Inputs: The audio data stream from the User Voice Input module.

Outputs: A string of transcribed text.

Core Logic:

Receive the audio chunks.

Use a real-time ASR service (e.g., Google Speech-to-Text, AssemblyAI, Deepgram) to perform transcription.

As the user speaks, the service should provide intermediate and final transcription results.

Once the user pauses or stops speaking (end-of-speech detection), finalize the transcription.

Pass the final, complete text string to the Memory System (Reasoner Decision).

Dependencies: ASR service API/SDK.

Module 2: Memory System

2.1. Reasoner Decision

Objective: Act as the central router. Analyze the user's transcribed input and decide which primary workflow to trigger.

Inputs:

transcribed_text: The string from the ASR Transcription module.

conversation_history: The output from the Recall Context function.

Outputs: A decision that routes to one of the following:

LangChain Node: Exercise

LangChain Node: Generate

LangChain Node: Simple Reply

LangChain Node: Question

Core Logic:

Receive the user's latest input text.

Fetch the recent conversation history using the Recall Context function.

Use a powerful language model (LLM) as the "reasoner."

Create a prompt for the LLM that includes the user's input, the conversation history, and a set of instructions to classify the user's intent into one of the available paths (Exercise, Generate, Simple Reply, Question).

Example Logic:

If the input contains keywords like "start an exercise," "give me a quiz," -> Route to Exercise.

If the input is a question like "what is...?" or "explain...?" -> Route to Question.

If the input is a direct command or statement that requires a generated, thoughtful response -> Route to Generate.

If the input is a simple conversational turn like "hello," "thank you," -> Route to Simple Reply.

Based on the LLM's classification, trigger the corresponding function in the Control Flow.

2.2. LangChain Memory (Integration)

Objective: This is not a single function but an underlying component used by other parts of the system. It's responsible for managing the conversation's state.

Components:

Recall Context:

Input: A trigger signal (e.g., from the Reasoner Decision).

Output: The recent conversation history.

Logic: Fetch the last N turns of the conversation from the Memory Store. Format it suitably for the Reasoner Decision's prompt.

Store History:

Input: The final user input and the AI's final audio response.

Output: A confirmation of storage.

Logic: After a full turn is complete (user speaks, AI responds), create a new entry containing both the user's query and the AI's response. Save this entry to the Memory Store.

Memory Store:

Logic: This is the database or data structure holding the conversation log. It could be a simple array of objects in memory for short sessions or a connection to a database (like Redis or a simple JSON file) for persistence. Each entry should be structured, e.g., { role: 'user', content: '...' }, { role: 'assistant', content: '...' }.

Module 3: Control Flow

This module executes the decision made by the Reasoner.

3.1. Fetch Exercise Flow

Triggered by: Reasoner Decision -> LangChain Node: Exercise

Sub-modules:

Fetch Pre-Written/Pool Questions:

Objective: Retrieve an exercise or a set of questions from a database.

Logic: Connect to a database (e.g., a JSON file, a NoSQL DB) where exercises are stored. Select an exercise, perhaps based on user level or topic, and load it.

Prepare Exercise:

Objective: Format the fetched exercise for the user.

Logic: Take the raw exercise data and format it into a clear, spoken prompt. For example, "Okay, let's start with your exercise. Question 1: What is the powerhouse of the cell?"

Output: A formatted string to be passed to the Formulate Response module.

3.2. Generate Response / RAG Search Flow

Triggered by: Reasoner Decision -> LangChain Node: Question or Generate.

Sub-modules:

RAG Search:

Objective: Search the knowledge base for information relevant to the user's query.

Input: The user's transcribed text.

Logic:

Take the user's text and convert it into a vector embedding using a sentence-transformer model.

Query the Textbook Vector DB with this embedding to find the most similar/relevant chunks of text.

Return the top K results as the "retrieved context."

Textbook Vector DB:

Objective: A specialized database (e.g., Pinecone, ChromaDB, FAISS) that stores pre-processed and vectorized content from a textbook or knowledge base. This should be prepared offline.

Retrieve Context:

Objective: A simple function that takes the results from the RAG Search and formats them.

Output: A string containing the combined relevant text chunks.

Generate Answer:

Objective: Use an LLM to synthesize an answer based on the retrieved context.

Input: The user's original query and the retrieved_context string.

Logic:

Create a prompt for an LLM. The prompt should be structured like: "Using the following context, please answer the user's question. Context: [retrieved_context]. Question: [user_query]."

Send this prompt to the LLM and get the generated answer.

Output: The generated text answer, to be passed to the Formulate Response module.

Module 4: Response Formulation & Delivery

4.1. Formulate Response

Objective: A central point to gather the text from different flows before converting it to speech.

Inputs: A text string from either Prepare Exercise or Generate Answer.

Outputs: The final text string to be synthesized.

Core Logic:

This can be a simple pass-through function.

Optionally, you can add final formatting here, like adding conversational filler ("Alright, here's the answer...") or logging the final text before synthesis.

4.2. TTS (Text-to-Speech) Conversion

Objective: Convert the final text response into audio.

Inputs: The final text string from Formulate Response.

Outputs: An audio stream or audio file (e.g., MP3, WAV).

Core Logic:

Use a TTS service (e.g., ElevenLabs, Google TTS, Amazon Polly).

Send the text to the service.

Choose a voice and configure any other settings (speed, emotion).

Receive the audio data back. For best user experience, this should be a stream.

4.3. Audio Response & Streaming

Objective: Play the synthesized audio back to the user.

Inputs: The audio stream from the TTS Conversion module.

Outputs: Sound played through the user's speakers.

Core Logic:

Receive the audio chunks from the TTS service.

Use the Web Audio API or a similar library to buffer and play the audio chunks as they arrive. This ensures the response starts playing quickly without waiting for the full audio file to be generated.

While the audio is playing, update the UI to show that the AI is "speaking."

Once the audio stream finishes, the response part of the turn is complete.

Module 5: Session Management

5.1. Continue Session?

Objective: Decide whether to end the interaction or loop back to listen for the next user input.

Inputs: A signal indicating the Audio Response has finished playing.

Outputs: A decision to either:

Loop back to the UI Layer (User Voice Input).

End Session.

Core Logic:

This is the main application loop.

After the AI's audio response is complete, the system should immediately go back into a "listening" state, activating the User Voice Input module again.

The loop is only broken if:

The user says a specific "end" command (e.g., "goodbye," "end session"). This would be detected in the Reasoner Decision.

A timeout occurs (the user doesn't say anything for X seconds).

The user closes the browser tab or application.

If the decision is to continue, the flow restarts from the top. If not, the application cleans up and terminates.
