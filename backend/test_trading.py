import asyncio
from app.core.trading.service import TradingService
from app.core.ai.agent import AIAgent

async def test_trading():
    trading_service = TradingService()
    ai_agent = await AIAgent.create()
    
    # Test wallet address (replace with actual test wallet)
    test_wallet = "0x1234567890123456789012345678901234567890"
    
    print("\nTesting Trading Service:\n")

    # Test cases
    test_commands = [
        "What is the current AVAX price?",
        "Open a 5x long on AVAX with 100 USDC",
        "Close the AVAX long position"
    ]

    for command in test_commands:
        print(f"\nTesting command: {command}")
        
        # Parse command using AI
        parsed = ai_agent.parse_trade_message(command)
        print(f"Parsed command: {parsed}")
        
        if parsed:
            # Execute trade
            result = await trading_service.execute_trade(parsed, test_wallet)
            print(f"Execution result: {result}")
            
            # If position was opened/closed, check position status
            if result['status'] == 'success' and result['type'] in ['position_open', 'position_close']:
                status = await trading_service.get_position_status(test_wallet)
                print(f"Position status: {status}")
        else:
            print("Failed to parse command")

if __name__ == "__main__":
    asyncio.run(test_trading()) 