from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Optional, List, Literal
from pydantic import BaseModel, Field, validator
from ...core.ai.agent import AIAgent
from decimal import Decimal
from ...core.trading.service import TradingService

router = APIRouter()
ai_agent = None

async def get_ai_agent():
    global ai_agent
    if ai_agent is None:
        ai_agent = await AIAgent.create()
    return ai_agent

class TradeContext(BaseModel):
    operation_type: Literal["buy", "sell", "analyze"] = Field(..., description="Type of trading operation")
    amount: Optional[Decimal] = Field(None, description="Amount of tokens to trade")
    token_pair: Literal["AVAX/USDC"] = Field(default="AVAX/USDC", description="Trading pair")
    slippage_tolerance: Optional[float] = Field(None, ge=0, le=100, description="Slippage tolerance in percentage")

class MessageRequest(BaseModel):
    message: str
    context: Optional[TradeContext] = None
    wallet_address: Optional[str] = None

    @validator('message')
    def validate_message_content(cls, v):
        # Ensure message is not empty and is reasonable length
        if not v.strip():
            raise ValueError("Message cannot be empty")
        if len(v) > 1000:
            raise ValueError("Message is too long. Please keep it under 1000 characters")
        return v.strip()

class MessageResponse(BaseModel):
    response: str
    trade_details: Optional[Dict] = None

class ConversationHistory(BaseModel):
    history: List[Dict[str, str]]

@router.post("/chat", response_model=MessageResponse)
async def chat_with_agent(request: MessageRequest):
    try:
        print("Received chat request:", request)  # Debug print
        agent = await get_ai_agent()
        context = {}
        if request.context:
            context = {
                "operation_type": request.context.operation_type,
                "token_pair": request.context.token_pair,
                "amount": str(request.context.amount) if request.context.amount else None,
                "slippage_tolerance": request.context.slippage_tolerance
            }
            print("Request context:", context)  # Debug print
        
        print(f"Processing message: {request.message}")  # Debug print
        response = await agent.process_message(request.message, context)
        print(f"Got response: {response}")  # Debug print
        
        if not response:
            print("Empty response from AI agent")  # Debug print
            raise ValueError("Empty response from AI agent")
            
        response_obj = MessageResponse(response=response)
        print("Sending response:", response_obj)  # Debug print
        return response_obj
    
    except ValueError as ve:
        print(f"ValueError in chat endpoint: {str(ve)}")  # Debug print
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        print(f"Unexpected error in chat endpoint: {str(e)}")  # Debug print
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history", response_model=ConversationHistory)
async def get_chat_history():
    try:
        agent = await get_ai_agent()
        history = agent.get_conversation_history()
        return ConversationHistory(history=history)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/clear")
async def clear_chat_history():
    try:
        agent = await get_ai_agent()
        agent.clear_history()
        return {"message": "Conversation history cleared successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/execute-trade")
async def execute_trade(request: MessageRequest):
    try:
        agent = await get_ai_agent()
        parsed_trade = agent.parse_trade_message(request.message)
        
        if not parsed_trade:
            raise HTTPException(status_code=400, detail="Could not parse trade command")
            
        # Initialize trading service
        trading_service = TradingService()
        
        # Execute the trade
        result = await trading_service.execute_trade(
            parsed_trade,
            request.wallet_address or "default_wallet"
        )
        
        if result["status"] == "error":
            raise HTTPException(status_code=400, detail=result["error"])
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 