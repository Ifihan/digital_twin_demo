# Digital Twin Assistant

An AI-powered personal assistant built with:
- 🧠 Gemini (LLM)
- 📚 RAG over your knowledge base (data/knowledge_base.json)
- 🛠️ Tool use (current time, calculator)
- 🎨 Beautiful Streamlit UI

## Live App
Try it here: https://YOUR-APP-NAME.streamlit.app

## Features
- Natural conversation
- Answers grounded in your knowledge base, with sources
- Memory within a chat session
- Tool integration

## Setup
Add your GEMINI_API_KEY in the app's Secrets settings on Streamlit Community Cloud.

To run locally, copy `.env.example` to `.env`, add your key, then run:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Edit `data/knowledge_base.json` to make the twin yours.

## Project Structure
```
├── app.py                 # Main Streamlit app
├── requirements.txt       # Dependencies
├── README.md              # Project description
├── .streamlit/
│   ├── config.toml        # Theme
│   └── secrets.toml       # Local secrets (never commit!)
├── utils/
│   ├── __init__.py
│   ├── llm.py             # Gemini interactions
│   ├── rag.py             # Knowledge base retrieval
│   └── tools.py           # Tools the LLM can call
├── data/
│   └── knowledge_base.json
└── tests/
    └── test_app.py
```

## Tests
```bash
pip install pytest
python -m pytest
```

## Built With
Part of the LLM Foundations course.
