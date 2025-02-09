import asyncio
import sys
from app.core.ai.agent import AIAgent

async def test_agent():
    agent = await AIAgent.create()
    
    test_messages = [
        'Open a 5x long on AVAX with 100 USDC',
        'Close the AVAX long position',
        'Open a 3x short position on AVAX with 500 USDC',
        'Buy AVAX with 200 USDC',
        'Sell 10 AVAX for USDC',
        'What is the current AVAX price?'
    ]
    
    print('\nTesting trade command parsing:\n')
    for msg in test_messages:
        print(f'\nTest message: {msg}')
        parsed = agent.parse_trade_message(msg)
        print(f'Parsed result: {parsed}')

if __name__ == "__main__":
    asyncio.run(test_agent()) 