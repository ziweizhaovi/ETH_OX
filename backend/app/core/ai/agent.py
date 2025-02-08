from typing import List, Dict, Optional, Tuple
import openai
import re
from decimal import Decimal
from .config import ai_config
import logging
import sys

# Configure logging to write to both file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chat_debug.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}

class AIAgent:
    def __init__(self):
        self.client = None
        self.conversation_history: List[Message] = [
            Message("system", ai_config.SYSTEM_PROMPT)
        ]
        logger.info("System prompt loaded")

    @classmethod
    async def create(cls):
        instance = cls()
        await instance.initialize()
        return instance

    async def initialize(self):
        logger.info("Initializing AI Agent...")
        if not ai_config.OPENAI_API_KEY:
            logger.error("OpenAI API key is not set!")
            raise ValueError("OpenAI API key is not configured")
        
        logger.info(f"Using OpenAI API key: {ai_config.OPENAI_API_KEY[:8]}...")
        try:
            self.client = openai.AsyncOpenAI(
                api_key=ai_config.OPENAI_API_KEY,
                base_url="https://api.openai.com/v1"
            )
            # Test the client
            await self.client.models.list()
            logger.info("OpenAI client initialized and tested successfully")
        except Exception as e:
            logger.error(f"Failed to initialize OpenAI client: {str(e)}")
            raise

    def parse_trade_message(self, message: str) -> Optional[Dict]:
        """Parse natural language message to extract trading information."""
        # Common patterns for buy/sell operations
        buy_patterns = [
            r'(?i)(?:buy|purchase|get)\s+(?:(\d+(?:\.\d+)?)\s+)?AVAX(?:\s+(?:with|for|using)\s+(\d+(?:\.\d+)?)\s*USDC)?',
            r'(?i)(?:spend|use)\s+(\d+(?:\.\d+)?)\s*USDC(?:\s+(?:on|for|to get)\s+(?:(\d+(?:\.\d+)?)\s+)?AVAX)?'
        ]
        
        sell_patterns = [
            r'(?i)(?:sell|convert)\s+(?:(\d+(?:\.\d+)?)\s+)?AVAX(?:\s+(?:for|to)\s+(?:(\d+(?:\.\d+)?)\s+)?USDC)?',
            r'(?i)(?:get|want)\s+(\d+(?:\.\d+)?)\s*USDC(?:\s+(?:for|from)\s+(?:(\d+(?:\.\d+)?)\s+)?AVAX)?'
        ]

        # Check buy patterns
        for pattern in buy_patterns:
            match = re.search(pattern, message)
            if match:
                groups = match.groups()
                return {
                    "operation_type": "buy",
                    "token_pair": "AVAX/USDC",
                    "amount": groups[1] if groups[1] else groups[0],  # USDC amount if specified
                    "target_amount": groups[0] if groups[1] else None  # AVAX amount if specified
                }

        # Check sell patterns
        for pattern in sell_patterns:
            match = re.search(pattern, message)
            if match:
                groups = match.groups()
                return {
                    "operation_type": "sell",
                    "token_pair": "AVAX/USDC",
                    "amount": groups[0],  # AVAX amount
                    "target_amount": groups[1]  # USDC amount if specified
                }

        # If no specific trade operation is found, treat as analysis
        if any(word in message.lower() for word in ["price", "analysis", "market", "trend", "chart"]):
            return {
                "operation_type": "analyze",
                "token_pair": "AVAX/USDC"
            }

        return None

    async def process_message(self, user_message: str, context: Optional[Dict] = None) -> str:
        logger.info(f"Processing message: {user_message[:50]}...")
        # Try to parse trading information from the message if no context is provided
        if not context:
            parsed_context = self.parse_trade_message(user_message)
            if parsed_context:
                context = parsed_context
                logger.info(f"Parsed context: {context}")
                # Add parsed information to the message for clarity
                user_message += f"\n[Detected Operation: {parsed_context['operation_type'].upper()}]"
                if parsed_context.get('amount'):
                    user_message += f"\n[Amount: {parsed_context['amount']}]"

        # Add user message to conversation history
        self.conversation_history.append(Message("user", user_message))
        
        # If context is provided, add it to the message
        if context:
            context_str = "\nContext:\n" + "\n".join(f"{k}: {v}" for k, v in context.items())
            self.conversation_history[-1].content += context_str

        try:
            # Create message list for API call
            messages = [msg.to_dict() for msg in self.conversation_history]
            logger.info("Sending request to OpenAI...")
            
            # Get response from OpenAI
            completion = await self.client.chat.completions.create(
                model=ai_config.MODEL_NAME,
                messages=messages,
                max_tokens=ai_config.MAX_TOKENS,
                temperature=ai_config.TEMPERATURE
            )
            
            # Extract and store assistant's response
            assistant_message = completion.choices[0].message.content
            logger.info("Received response from OpenAI")
            self.conversation_history.append(Message("assistant", assistant_message))
            
            return assistant_message

        except Exception as e:
            logger.error(f"Error in process_message: {str(e)}")
            error_msg = f"Error processing message: {str(e)}"
            self.conversation_history.append(Message("system", error_msg))
            raise Exception(error_msg)

    def clear_history(self):
        """Clear conversation history except for the system prompt"""
        self.conversation_history = [self.conversation_history[0]]

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history"""
        return [msg.to_dict() for msg in self.conversation_history] 