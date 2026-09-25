import os
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv
from google.genai import errors

from utils.llm import generate_response
from utils.rag import load_knowledge_base, parse_upload, retrieve
from utils.tools import TOOLS

st.set_page_config(
    page_title="Digital Twin Assistant",
    page_icon="🤖",
    layout="centered",
)

KNOWLEDGE_BASE = Path(__file__).parent / "data" / "knowledge_base.json"


def get_api_key():
    """Get API key from Streamlit secrets, .env, or user input."""
    # Method 1: Streamlit secrets (Streamlit Community Cloud, or .streamlit/secrets.toml locally)
    try:
        return st.secrets["GEMINI_API_KEY"]
    except (FileNotFoundError, KeyError):
        pass

    # Method 2: Environment variables (.env for local development)
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    if api_key:
        return api_key

    # Fall back to user input
    st.sidebar.warning("⚠️ API key not configured")
    api_key = st.sidebar.text_input(
        "Enter your Gemini API key:",
        type="password",
        help="Get your free key from aistudio.google.com/apikey",
    )
    if not api_key:
        st.error("Please provide an API key to continue")
        st.stop()
    return api_key


@st.cache_data
def load_entries():
    return load_knowledge_base(KNOWLEDGE_BASE)


# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hello! I'm your Digital Twin. Ask me about your week, "
                   "or ask me to do a quick calculation.",
        "timestamp": datetime.now(),
    }]
if "user_name" not in st.session_state:
    st.session_state.user_name = ""

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")

    st.subheader("Profile")
    st.session_state.user_name = st.text_input("Your Name:", st.session_state.user_name)

    st.subheader("Model")
    model = st.selectbox("Model", ["gemini-3.5-flash-lite", "gemini-3.8-flash"])
    temperature = st.slider("Temperature", 0.0, 1.0, 0.7, help="Higher = more creative")
    persona = st.text_area(
        "Twin persona",
        "You are the user's friendly digital twin. Keep answers short and clear. "
        "Use plain text.",
    )

    st.subheader("Features")
    use_knowledge = st.toggle("📚 Use knowledge base (RAG)", value=True)
    use_tools = st.toggle("🛠️ Use tools (time, calculator)", value=True)
    uploaded = st.file_uploader(
        "Add more knowledge", type=["json", "txt"],
        help="A .json file in the same format as data/knowledge_base.json, "
             "or a .txt file with paragraphs separated by blank lines",
    )

    st.divider()

    st.subheader("📊 Stats")
    col1, col2 = st.columns(2)
    col1.metric("Messages", len(st.session_state.messages))
    col2.metric("Yours", len([m for m in st.session_state.messages if m["role"] == "user"]))

    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

api_key = get_api_key()

entries = list(load_entries())
if uploaded:
    try:
        entries += parse_upload(uploaded.name, uploaded.getvalue())
    except (ValueError, KeyError):
        st.sidebar.error("Couldn't read that file. Check it matches the knowledge base format.")

# Main chat interface
st.title("🤖 Digital Twin Assistant")
if st.session_state.user_name:
    st.write(f"Chatting as: **{st.session_state.user_name}**")
st.caption(f"📚 {len(entries)} entries in the knowledge base")

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])
        details = message["timestamp"].strftime("%H:%M:%S")
        if message.get("tools"):
            details += " · 🛠️ " + ", ".join(message["tools"])
        st.caption(details)
        if message.get("sources"):
            with st.expander("📚 Sources"):
                for source in message["sources"]:
                    st.caption(source)

user_input = st.chat_input("Ask your twin...")

if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input, "timestamp": datetime.now()})

    sources = retrieve(user_input, entries) if use_knowledge else []

    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                response, tools_used = generate_response(
                    st.session_state.messages, api_key, model, temperature,
                    persona, sources, TOOLS if use_tools else [])
            except errors.APIError as e:
                response, tools_used, sources = f"Sorry, something went wrong: {e.message}", [], []

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "timestamp": datetime.now(),
        "sources": sources,
        "tools": tools_used,
    })
    st.rerun()
