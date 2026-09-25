"""LLM interactions with Gemini (Week 1)."""
from google import genai
from google.genai import types


def generate_response(messages, api_key, model, temperature, persona, sources, tools):
    """Send the conversation to Gemini. Returns (reply_text, names_of_tools_used)."""
    client = genai.Client(api_key=api_key)

    # Gemini expects the conversation to start with a user turn
    first_user = next(i for i, m in enumerate(messages) if m["role"] == "user")
    history = [
        types.Content(
            role="user" if m["role"] == "user" else "model",
            parts=[types.Part(text=m["content"])],
        )
        for m in messages[first_user:]
    ]

    instruction = persona
    if sources:
        instruction += (
            "\n\nUse these entries from the user's knowledge base to answer. "
            "If the answer is not in them, say you don't know.\n\n"
            + "\n".join(f"- {s}" for s in sources)
        )

    response = client.models.generate_content(
        model=model,
        contents=history,
        config=types.GenerateContentConfig(
            system_instruction=instruction,
            temperature=temperature,
            tools=tools or None,
        ),
    )

    tools_used = [
        part.function_call.name
        for content in (response.automatic_function_calling_history or [])
        for part in (content.parts or [])
        if part.function_call
    ]
    text = response.text or "Sorry, I couldn't come up with an answer."
    return text, tools_used
