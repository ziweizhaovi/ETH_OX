import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from app.core.analytics.service import AnalyticsService
from app.core.db.service import DatabaseService
from app.core.db.models import Position, PositionStatus

# Use SQLite for testing
DATABASE_URL = "sqlite:///./test.db"

async def setup_test_data(db_service: DatabaseService, wallet_address: str):
    """Set up test trading data."""
    # Create some test positions
    positions = [
        {
            "position_type": "long",
            "size": "1000",
            "collateral": "200",
            "leverage": "5",
            "average_price": "24.50",
            "liquidation_price": "20.00",
            "pnl": 50.0,
            "status": PositionStatus.CLOSED,
            "closed_at": datetime.utcnow() - timedelta(days=2)
        },
        {
            "position_type": "short",
            "size": "2000",
            "collateral": "400",
            "leverage": "5",
            "average_price": "25.50",
            "liquidation_price": "30.00",
            "pnl": -30.0,
            "status": PositionStatus.CLOSED,
            "closed_at": datetime.utcnow() - timedelta(days=1)
        },
        {
            "position_type": "long",
            "size": "1500",
            "collateral": "300",
            "leverage": "5",
            "average_price": "23.50",
            "liquidation_price": "19.00",
            "status": PositionStatus.OPEN
        }
    ]
    
    for position_data in positions:
        await db_service.store_position(wallet_address, position_data)

async def test_analytics():
    db_service = DatabaseService(DATABASE_URL)
    analytics_service = AnalyticsService(db_service)
    
    # Test wallet address
    test_wallet = "0x1234567890123456789012345678901234567890"
    
    print("\nTesting Analytics Service:\n")

    # Set up test data
    print("Setting up test data...")
    await setup_test_data(db_service, test_wallet)

    # 1. Test Performance Metrics
    print("\n1. Testing Performance Metrics:")
    performance = await analytics_service.get_performance_metrics(test_wallet)
    if performance['status'] == 'success':
        metrics = performance['metrics']
        print("\nTrading Performance:")
        print(f"Total Trades: {metrics['total_trades']}")
        print(f"Win Rate: {metrics['win_rate']:.2f}%")
        print(f"Total PnL: ${metrics['total_pnl']:.2f}")
        print(f"Average PnL: ${metrics['average_pnl']:.2f}")
        print(f"Best Trade: ${metrics['best_trade']:.2f}")
        print(f"Worst Trade: ${metrics['worst_trade']:.2f}")
        print(f"Average Holding Time: {metrics['average_holding_time']:.2f} hours")
        print(f"Risk/Reward Ratio: {metrics['risk_reward_ratio']:.2f}")

    # 2. Test Risk Exposure Analysis
    print("\n2. Testing Risk Exposure Analysis:")
    risk = await analytics_service.analyze_risk_exposure(test_wallet)
    if risk['status'] == 'success':
        metrics = risk['risk_metrics']
        print("\nRisk Metrics:")
        print(f"Total Exposure: ${metrics['total_exposure']:.2f}")
        print(f"Max Leverage: {metrics['max_leverage']:.2f}x")
        print(f"Weighted Avg Leverage: {metrics['weighted_avg_leverage']:.2f}x")
        print(f"Long Exposure: ${metrics['long_exposure']:.2f}")
        print(f"Short Exposure: ${metrics['short_exposure']:.2f}")
        print(f"Net Exposure: ${metrics['net_exposure']:.2f}")

    # 3. Test Drawdown Analysis
    print("\n3. Testing Drawdown Analysis:")
    drawdown = await analytics_service.calculate_drawdown(test_wallet)
    if drawdown['status'] == 'success':
        metrics = drawdown['drawdown_metrics']
        print("\nDrawdown Metrics:")
        print(f"Max Drawdown: {metrics['max_drawdown']:.2f}%")
        print(f"Current Drawdown: {metrics['current_drawdown']:.2f}%")
        print(f"Max Drawdown Duration: {metrics['max_drawdown_duration']} periods")

    # 4. Test Market Correlation Analysis
    print("\n4. Testing Market Correlation Analysis:")
    correlation = await analytics_service.analyze_market_correlation(test_wallet)
    if correlation['status'] == 'success':
        metrics = correlation['correlation_metrics']
        print("\nCorrelation Metrics:")
        print(f"Market Correlation: {metrics['market_correlation']:.2f}")
        print(f"Volatility Correlation: {metrics['volatility_correlation']:.2f}")
        print(f"Trend Alignment: {metrics['trend_alignment']:.2f}")

if __name__ == "__main__":
    asyncio.run(test_analytics()) 