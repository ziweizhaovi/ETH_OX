import asyncio
from decimal import Decimal
from datetime import datetime
from app.core.db.service import DatabaseService
from app.core.db.models import PositionStatus, OrderStatus

# Use SQLite for testing
DATABASE_URL = "sqlite:///./test.db"

async def test_database():
    db_service = DatabaseService(DATABASE_URL)
    
    # Test wallet address
    test_wallet = "0x1234567890123456789012345678901234567890"
    
    print("\nTesting Database Integration:\n")

    # 1. Test Position Storage
    print("1. Testing Position Storage:")
    
    # Store a new position
    position_data = {
        "position_type": "long",
        "size": "1000",
        "collateral": "200",
        "leverage": "5",
        "average_price": "24.50",
        "liquidation_price": "20.00"
    }
    
    position = await db_service.store_position(test_wallet, position_data)
    print("\nStored Position:")
    print(f"ID: {position.id}")
    print(f"Type: {position.position_type}")
    print(f"Size: ${position.size}")
    print(f"Status: {position.status}")
    
    # Update position
    update_data = {
        "pnl": 50.0,
        "status": PositionStatus.CLOSED
    }
    
    updated_position = await db_service.update_position(position.id, update_data)
    print("\nUpdated Position:")
    print(f"Status: {updated_position.status}")
    print(f"PnL: ${updated_position.pnl}")
    print(f"Closed At: {updated_position.closed_at}")

    # 2. Test Order Storage
    print("\n2. Testing Order Storage:")
    
    # Store a new order
    order_data = {
        "order_id": f"limit_{test_wallet}_{datetime.utcnow().timestamp()}",
        "type": "limit",
        "size": "100",
        "target_price": "25.00",
        "leverage": "5"
    }
    
    order = await db_service.store_order(test_wallet, order_data)
    print("\nStored Order:")
    print(f"Order ID: {order.order_id}")
    print(f"Type: {order.order_type}")
    print(f"Status: {order.status}")
    
    # Update order
    order_update = {
        "status": OrderStatus.EXECUTED,
        "execution_price": 25.00
    }
    
    updated_order = await db_service.update_order(order.order_id, order_update)
    print("\nUpdated Order:")
    print(f"Status: {updated_order.status}")
    print(f"Execution Price: ${updated_order.execution_price}")
    print(f"Executed At: {updated_order.executed_at}")

    # 3. Test Trading Stats
    print("\n3. Testing Trading Stats:")
    
    # Update trading stats with a winning trade
    trade_result = {
        "pnl": 50.0,
        "leverage": 5.0
    }
    
    stats = await db_service.update_trading_stats(test_wallet, trade_result)
    print("\nTrading Stats:")
    print(f"Total Trades: {stats.total_trades}")
    print(f"Winning Trades: {stats.winning_trades}")
    print(f"Total PnL: ${stats.total_pnl}")
    print(f"Best Trade: ${stats.best_trade}")
    print(f"Average Leverage: {stats.average_leverage}x")

    # 4. Test History Retrieval
    print("\n4. Testing History Retrieval:")
    
    # Get position history
    positions = await db_service.get_position_history(test_wallet)
    print("\nPosition History:")
    for pos in positions:
        print(f"Position {pos.id}: {pos.position_type} - {pos.status}")
    
    # Get order history
    orders = await db_service.get_order_history(test_wallet)
    print("\nOrder History:")
    for ord in orders:
        print(f"Order {ord.order_id}: {ord.order_type} - {ord.status}")
    
    # Get trading stats
    final_stats = await db_service.get_trading_stats(test_wallet)
    print("\nFinal Trading Stats:")
    print(f"Win Rate: {(final_stats.winning_trades / final_stats.total_trades * 100):.2f}%")
    print(f"Total PnL: ${final_stats.total_pnl}")

if __name__ == "__main__":
    asyncio.run(test_database()) 