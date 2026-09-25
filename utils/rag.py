"""RAG system: load the knowledge base and retrieve relevant entries (Week 2)."""
import json
import re
from pathlib import Path

STOPWORDS = {
    "a", "an", "the", "i", "me", "my", "you", "your", "did", "do", "does", "what",
    "when", "where", "who", "how", "is", "was", "were", "are", "to", "of", "in",
    "on", "at", "for", "and", "or", "with", "about", "tell", "have", "had",
}


def load_knowledge_base(path: Path) -> list[dict]:
    """Load the entries from a knowledge_base.json file."""
    if not path.exists():
        return []
    return json.loads(path.read_text())["entries"]


def parse_upload(filename: str, content: bytes) -> list[dict]:
    """Turn an uploaded .json (same format as the knowledge base) or .txt file into entries."""
    text = content.decode("utf-8", errors="ignore")
    if filename.endswith(".json"):
        return json.loads(text)["entries"]
    return [
        {"day": "", "time": "", "text": paragraph.strip()}
        for paragraph in text.split("\n\n")
        if paragraph.strip()
    ]


def entry_to_text(entry: dict) -> str:
    """Format an entry as a single line, e.g. 'Monday 7:45am - Had eggs...'."""
    when = " ".join(part for part in (entry.get("day"), entry.get("time")) if part)
    return f"{when} - {entry['text']}" if when else entry["text"]


def _words(text: str) -> set[str]:
    return {w for w in re.findall(r"[a-z0-9]+", text.lower()) if w not in STOPWORDS}


def retrieve(query: str, entries: list[dict], top_k: int = 3) -> list[str]:
    """Return the entries that share the most words with the query."""
    query_words = _words(query)
    texts = [entry_to_text(entry) for entry in entries]
    scored = [(len(query_words & _words(text)), text) for text in texts]
    scored = [item for item in scored if item[0] > 0]
    scored.sort(key=lambda item: item[0], reverse=True)
    return [text for _, text in scored[:top_k]]
