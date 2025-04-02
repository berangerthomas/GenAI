import logging
import os

import requests
from fastapi import FastAPI
from pydantic import BaseModel

# Configuration du logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

# Récupérer l'URL du backend depuis les variables d'environnement
BACKEND_URL = os.getenv("BACKEND_URL", "http://backend:11434")
logger.info(f"Using backend URL: {BACKEND_URL}")

# Modèle Ollama à utiliser
OLLAMA_MODEL = "tinyllama"


class ChatRequest(BaseModel):
    messages: list
    model: str = OLLAMA_MODEL


class ChatResponse(BaseModel):
    model: str
    message: dict


@app.get("/")
async def root():
    return {"message": "Please use the /chat/completions endpoint to get chat response"}


@app.post("/api/chat")
async def api_chat(request: ChatRequest):
    try:
        # Convertir les messages au format Ollama
        ollama_messages = [
            {"role": msg["role"], "content": msg["content"]} for msg in request.messages
        ]

        logger.info(f"Using model: {OLLAMA_MODEL} (requested model: {request.model})")
        logger.info(f"Sending request to Ollama with messages: {ollama_messages}")

        response = requests.post(
            f"{BACKEND_URL}/api/chat",
            json={
                "model": OLLAMA_MODEL,  # Forcer l'utilisation de notre modèle
                "messages": ollama_messages,
                "stream": False,
            },
        )

        logger.info(f"Ollama response status: {response.status_code}")
        logger.info(f"Ollama response: {response.text}")

        if response.status_code != 200:
            logger.error(f"Error from Ollama: {response.text}")
            # Return a properly formatted error response
            return ChatResponse(
                model=OLLAMA_MODEL,
                message={"role": "assistant", "content": f"Error: {response.text}"},
            )

        # Return the response in a format compatible with LlamaIndex
        ollama_response = response.json()
        return ChatResponse(
            model=OLLAMA_MODEL,
            message=ollama_response.get(
                "message", {"role": "assistant", "content": "No response from model"}
            ),
        )
    except Exception as e:
        logger.error(f"Error in api_chat: {str(e)}")
        # Return a properly formatted error response
        return ChatResponse(
            model=OLLAMA_MODEL,
            message={"role": "assistant", "content": f"Error: {str(e)}"},
        )
