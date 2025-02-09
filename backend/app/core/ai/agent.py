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
        # Pattern for position opening with leverage
        position_pattern = r'(?i)(?:open|create|start)\s+(?:a\s+)?(?:(\d+)x\s+)?(long|short)\s+(?:position\s+)?(?:on\s+)?AVAX\s+(?:with|for|using)\s+(\d+(?:\.\d+)?)\s*USDC'
        
        # Pattern for position closing
        close_pattern = r'(?i)(?:close|exit|end)\s+(?:the\s+)?(?:AVAX\s+)?(long|short)?\s*(?:position)?'
        
        # Check position opening pattern
        position_match = re.search(position_pattern, message)
        if position_match:
            leverage, position_type, amount = position_match.groups()
            return {
                "operation_type": "open_position",
                "position_type": position_type.lower(),
                "leverage": int(leverage) if leverage else 1,
                "token_pair": "AVAX/USDC",
                "amount": amount,
                "currency": "USDC"
            }

        # Check position closing pattern
        close_match = re.search(close_pattern, message)
        if close_match:
            position_type = close_match.group(1)
            return {
                "operation_type": "close_position",
                "position_type": position_type.lower() if position_type else None,
                "token_pair": "AVAX/USDC"
            }

        # Common patterns for spot buy/sell operations
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
                    "operation_type": "spot_buy",
                    "token_pair": "AVAX/USDC",
                    "amount": groups[1] if groups[1] else groups[0],  # USDC amount if specified
                    "target_amount": groups[0] if groups[1] else None,  # AVAX amount if specified
                    "currency": "USDC"
                }

        # Check sell patterns
        for pattern in sell_patterns:
            match = re.search(pattern, message)
            if match:
                groups = match.groups()
                return {
                    "operation_type": "spot_sell",
                    "token_pair": "AVAX/USDC",
                    "amount": groups[0],  # AVAX amount
                    "target_amount": groups[1],  # USDC amount if specified
                    "currency": "AVAX"
                }

        # If no specific trade operation is found, treat as analysis
        if any(word in message.lower() for word in ["price", "analysis", "market", "trend", "chart", "position", "liquidation"]):
            return {
                "operation_type": "analyze",
                "token_pair": "AVAX/USDC"
            }

        return None

    async def process_message(self, user_message: str, context: Optional[Dict] = None) -> str:
        logger.info(f"Processing message: {user_message[:50]}...")
        # Try to parse trading information from the message if no context is provided
        parsed_trade = None
        if not context:
            parsed_trade = self.parse_trade_message(user_message)
            if parsed_trade:
                context = parsed_trade
                logger.info(f"Parsed context: {context}")
                
                # Add parsed information to the message for clarity
                trade_info = [f"[Detected Operation: {parsed_trade['operation_type'].upper()}]"]
                
                if parsed_trade.get('position_type'):
                    trade_info.append(f"[Position Type: {parsed_trade['position_type'].upper()}]")
                
                if parsed_trade.get('leverage'):
                    trade_info.append(f"[Leverage: {parsed_trade['leverage']}x]")
                
                if parsed_trade.get('amount'):
                    currency = parsed_trade.get('currency', 'USDC')
                    trade_info.append(f"[Amount: {parsed_trade['amount']} {currency}]")
                
                if parsed_trade.get('target_amount'):
                    target_currency = 'AVAX' if parsed_trade.get('currency') == 'USDC' else 'USDC'
                    trade_info.append(f"[Target Amount: {parsed_trade['target_amount']} {target_currency}]")
                
                user_message += "\n" + "\n".join(trade_info)

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
            
            # If trade was parsed, add confirmation request
            if parsed_trade:
                assistant_message += "\n\nWould you like me to execute this trade? Please confirm with 'yes' to proceed."
                
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