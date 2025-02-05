# app/routers/deepseek.py

import os
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from typing import List

router = APIRouter(
    prefix="/deepseek",
    tags=["deepseek"]
)

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    messages: List[ChatMessage]  # Se espera el historial completo de la conversación

class ChatResponse(BaseModel):
    content: str

@router.post("/chat", response_model=ChatResponse)
def chat_with_deepseek(payload: ChatRequest):
    """
    Envía la conversación completa a la API de DeepSeek y retorna la respuesta del modelo.
    """
    try:
        # 1. Cargamos la API key desde variable de entorno
        api_key = os.getenv("DEEPSEEK_API_KEY")
        if not api_key:
            raise HTTPException(status_code=500, detail="Falta la DeepSeek API Key")

        # 2. Inicializamos el cliente de la API de DeepSeek
        client = OpenAI(
            api_key=api_key,
            base_url="https://api.deepseek.com"
        )

        # 3. Convertimos los mensajes (modelos de Pydantic) a diccionarios
        conversation = [msg.dict() for msg in payload.messages]

        # 4. Verificamos si ya se ha incluido un mensaje del sistema; de lo contrario, lo agregamos al inicio.
        if not conversation or conversation[0].get("role") != "system":
            system_message = {
                "role": "system",
                "content": (
                    "Eres un asistente de un adulto mayor. "
                    "Procura siempre ser amistoso y respetuoso. "
                    "Responde brevemente y humanamente (no estructurado). "
                    "Vas a recordarle sus rutinas de salud "
                    "como medicación, citas médicas, ejercicios"
                    "Cuando haya hecho eso, busca mantener conversación"
                    "Inducir memorias, reflexiones, acompañarlo."
                )
            }
            conversation.insert(0, system_message)

        # 5. Llamamos a la API enviando el historial completo
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=conversation,
            stream=False
        )

        # 6. Extraemos la respuesta del asistente
        content = response.choices[0].message.content
        return ChatResponse(content=content)

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
