import requests
import json

OLLAMA_URL = "http://host.docker.internal:11434/api/chat"
MODEL = "phi3:mini"

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "You are NEXVIBE Assistant, a professional AI chatbot for the company NEXVIBE. "
        "NEXVIBE is an IT solutions company that provides web development, application "
        "development, cloud solutions, and technical consulting. "
        "You must always introduce yourself as NEXVIBE Assistant. "
        "You must NEVER say you are developed by Microsoft, OpenAI, Meta, or any other company. "
        "You must respond in a helpful, polite, professional, and business-friendly tone."
    )
}

def ai_generate_response(prompt, history=None):
    if history is None:
        history = []

    messages = [SYSTEM_PROMPT] + history + [
        {"role": "user", "content": prompt}
    ]

    res = requests.post(
    OLLAMA_URL,
    json={
        "model": MODEL,
        "messages": messages,
        "stream": True,
        "options": {
            "temperature": 0.2,   # 🔽 less random
            "top_p": 0.9
        }
    },
    stream=True,
    timeout=300
)


    reply = ""

    for line in res.iter_lines():
        if not line:
            continue

        try:
            data = json.loads(line.decode("utf-8"))
        except json.JSONDecodeError:
            continue

        if "message" in data and "content" in data["message"]:
            reply += data["message"]["content"]

        if data.get("done"):
            break

    history.append({"role": "assistant", "content": reply})
    return reply, history
