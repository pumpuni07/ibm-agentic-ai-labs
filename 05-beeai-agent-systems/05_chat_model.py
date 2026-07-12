"""Step 5 — Constructing a ChatModel backend handle (env-var credentials)."""
import os
from beeai_framework.backend import ChatModel

MODEL_ID = os.environ.get("BEEAI_MODEL", "ollama:granite3.3:8b")

def make_chat_model() -> ChatModel:
    return ChatModel.from_name(MODEL_ID)

if __name__ == "__main__":
    print(type(make_chat_model()).__name__)
