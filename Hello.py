from llama_index.llms.ollama import Ollama
from llama_index.embeddings.ollama import OllamaEmbedding
from llama_index.core import VectorStoreIndex, SimpleDirectoryReader
from llama_index.core import Settings
from llama_index.core.memory import ChatMemoryBuffer
import streamlit as st
import pandas as pd


system_prompt = f"""
You are a multilingual expert system with real-time knowledge. Your goal is to always be helpful by answering questions to the best of your ability. If you don't know the answer, clearly state that you DON'T KNOW.

Respond to all questions in English.
You are a study assistant for students, helping them prepare for exams based on the given material. Follow these interaction guidelines:

Question Creation:

YOU ASK THE QUESTIONS.
All questions must be directly related to the given material.
Avoid asking questions outside the scope of the document or introducing irrelevant information.
DO NOT PROVIDE ANY HELP before the user answers.
If the user is ready, directly provide the first question.
Answer Evaluation:

When the student answers, analyze their response.
Provide a clear explanation of whether their answer is correct or incorrect.
If there are errors, provide corrections and explanations of the correct answer.
After the discussion, ask the student to summarize the correct answer to reinforce understanding.
DON'T CONTINUE IF the student haven't successfully summarizes the correct answer
CITE THE PROVIDED DOCUMENT when explaining.

Continue with Questions:

Conversation so far:
"""

Settings.llm = Ollama(model="llama3.1:latest", base_url="http://127.0.0.1:11434", system_prompt=system_prompt) 
Settings.embed_model = OllamaEmbedding(base_url="http://127.0.0.1:11434", model_name="mxbai-embed-large:latest") 

docs = SimpleDirectoryReader("docs").load_data()
index = VectorStoreIndex.from_documents(docs)

st.title("Quiz Netdef")
# st.write("Lorem ipsum dolor sit amet")

if "messages_docs" not in st.session_state:
    st.session_state.messages_docs = [
        {"role": "assistant",
         "content": "Hello, are you ready?"}
    ]

if "chat_engine_docs" not in st.session_state:

    memory = ChatMemoryBuffer.from_defaults(token_limit=50384)
    st.session_state.chat_engine_docs = index.as_chat_engine(
    chat_mode="context",
    memory=memory,
    system_prompt= system_prompt,
    verbose=True
)

# Display chat messages from history on app rerun
for message in st.session_state.messages_docs:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

print("A user connected")

# Accept user input
if prompt:= st.chat_input("What is up?"):
    # Add user message to chat history
    st.session_state.messages_docs.append({"role": "user", "content": prompt})
    # Display user message in chat message container
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response_stream = st.session_state.chat_engine_docs.chat(prompt)
            st.markdown(response_stream)

    # Add user message to chat history
    st.session_state.messages_docs.append({"role": "assistant", "content": response_stream})