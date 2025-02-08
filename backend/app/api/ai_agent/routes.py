from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Optional, List
from pydantic import BaseModel
from ...core.ai.agent import AIAgent

router = APIRouter()
ai_agent = AIAgent()

class MessageRequest(BaseModel):
    message: str
    context: Optional[Dict] = None

class MessageResponse(BaseModel):
    response: str

class ConversationHistory(BaseModel):
    history: List[Dict[str, str]]

@router.post("/chat", response_model=MessageResponse)
async def chat_with_agent(request: MessageRequest):
    try:
        response = await ai_agent.process_message(request.message, request.context)
        return MessageResponse(response=response)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=ConversationHistory)
async def get_chat_history():
    try:
        history = ai_agent.get_conversation_history()
        return ConversationHistory(history=history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear")
async def clear_chat_history():
    try:
        ai_agent.clear_history()
        return {"message": "Conversation history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 