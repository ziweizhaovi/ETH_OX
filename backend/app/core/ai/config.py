from pydantic_settings import BaseSettings
from typing import Optional

class AIConfig(BaseSettings):
    OPENAI_API_KEY: str
    MODEL_NAME: str = "gpt-4-turbo-preview"
    MAX_TOKENS: int = 4000
    TEMPERATURE: float = 0.7
    SYSTEM_PROMPT: str = """You are an AI assistant for the ETH_OX DeFi Position Management Platform. 
    Your role is to help users with:
    1. Understanding their DeFi positions
    2. Analyzing market conditions
    3. Providing trading suggestions
    4. Explaining DeFi concepts and strategies
    Always prioritize user's risk management and provide clear, actionable insights."""
    
    class Config:
        env_file = ".env"

ai_config = AIConfig() 