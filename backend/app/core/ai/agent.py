from typing import List, Dict, Optional
import openai
from .config import ai_config

class Message:
    def __init__(self, role: str, content: str):
        self.role = role
        self.content = content

    def to_dict(self) -> Dict[str, str]:
        return {"role": self.role, "content": self.content}

class AIAgent:
    def __init__(self):
        self.client = openai.OpenAI(api_key=ai_config.OPENAI_API_KEY)
        self.conversation_history: List[Message] = [
            Message("system", ai_config.SYSTEM_PROMPT)
        ]

    async def process_message(self, user_message: str, context: Optional[Dict] = None) -> str:
        # Add user message to conversation history
        self.conversation_history.append(Message("user", user_message))
        
        # If context is provided, add it to the message
        if context:
            context_str = "\nContext:\n" + "\n".join(f"{k}: {v}" for k, v in context.items())
            self.conversation_history[-1].content += context_str

        try:
            # Create message list for API call
            messages = [msg.to_dict() for msg in self.conversation_history]
            
            # Get response from OpenAI
            response = await self.client.chat.completions.create(
                model=ai_config.MODEL_NAME,
                messages=messages,
                max_tokens=ai_config.MAX_TOKENS,
                temperature=ai_config.TEMPERATURE,
            )
            
            # Extract and store assistant's response
            assistant_message = response.choices[0].message.content
            self.conversation_history.append(Message("assistant", assistant_message))
            
            return assistant_message

        except Exception as e:
            error_msg = f"Error processing message: {str(e)}"
            self.conversation_history.append(Message("system", error_msg))
            raise Exception(error_msg)

    def clear_history(self):
        """Clear conversation history except for the system prompt"""
        self.conversation_history = [self.conversation_history[0]]

    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get the conversation history"""
        return [msg.to_dict() for msg in self.conversation_history] 