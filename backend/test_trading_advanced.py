import asyncio
from decimal import Decimal
from app.core.trading.position_manager import PositionManager
from app.core.trading.order_manager import OrderManager

async def test_advanced_trading():
    position_manager = PositionManager()
    order_manager = OrderManager()
    
    # Test wallet address (replace with actual wallet when testing)
    test_wallet = "0x1234567890123456789012345678901234567890"
    
    print("\nTesting Advanced Trading Features:\n")

    # 1. Test Position Management
    print("1. Testing Position Management:")
    
    # Check active positions
    positions = await position_manager.get_active_positions(test_wallet)
    print("\nActive Positions:")
    print(positions)
    
    # Check risk limits for a new position
    risk_check = await position_manager.check_risk_limits(
        test_wallet,
        Decimal('1000'),  # $1000 position
        Decimal('5')      # 5x leverage
    )
    print("\nRisk Check Results:")
    print(risk_check)
    
    # Monitor liquidation risks
    liquidation_risks = await position_manager.monitor_liquidation_risks(test_wallet)
    print("\nLiquidation Risks:")
    print(liquidation_risks)

    # 2. Test Order Management
    print("\n2. Testing Order Management:")
    
    # Create a limit order
    limit_order = await order_manager.create_limit_order(
        test_wallet,
        "long",
        Decimal('100'),   # $100 USDC
        Decimal('20'),    # Target price $20
        Decimal('5')      # 5x leverage
    )
    print("\nLimit Order Created:")
    print(limit_order)
    
    # Create a stop loss
    stop_loss = await order_manager.create_stop_loss(
        test_wallet,
        "long",
        Decimal('19')     # Trigger at $19
    )
    print("\nStop Loss Created:")
    print(stop_loss)
    
    # Create a take profit
    take_profit = await order_manager.create_take_profit(
        test_wallet,
        "long",
        Decimal('25')     # Trigger at $25
    )
    print("\nTake Profit Created:")
    print(take_profit)
    
    # Check pending orders
    pending_orders = order_manager.get_pending_orders(test_wallet)
    print("\nPending Orders:")
    print(pending_orders)
    
    # Check for order execution
    execution_check = await order_manager.check_and_execute_orders()
    print("\nOrder Execution Check:")
    print(execution_check)
    
    # Cancel an order (using the limit order ID)
    if limit_order['status'] == 'success':
        cancellation = order_manager.cancel_order(
            limit_order['order_id'],
            test_wallet
        )
        print("\nOrder Cancellation:")
        print(cancellation)

if __name__ == "__main__":
    asyncio.run(test_advanced_trading()) 