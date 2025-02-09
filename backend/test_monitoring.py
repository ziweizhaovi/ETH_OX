import asyncio
from decimal import Decimal
from datetime import datetime, timedelta
from app.core.monitoring.service import MonitoringService
from app.core.notifications.service import NotificationService, NotificationType, NotificationPriority
from app.core.trading.position_manager import PositionManager
from app.core.price_feed.coingecko import CoinGeckoPriceFeed
from app.core.db.service import DatabaseService
from app.core.gmx.client import GMXClient

# Use SQLite for testing
DATABASE_URL = "sqlite:///./test.db"

async def setup_test_data(db_service: DatabaseService, wallet_address: str):
    """Set up test trading data."""
    # Create some test positions
    positions = [
        {
            "position_type": "long",
            "size": "2500",
            "collateral": "500",
            "leverage": "5",
            "average_price": "24.50",
            "liquidation_price": "20.00",
            "status": "OPEN"
        },
        {
            "position_type": "short",
            "size": "2000",
            "collateral": "400",
            "leverage": "5",
            "average_price": "25.50",
            "liquidation_price": "30.00",
            "status": "OPEN"
        }
    ]
    
    for position_data in positions:
        await db_service.store_position(wallet_address, position_data)

class TestNotificationHandler:
    def __init__(self):
        self.notifications = []

    async def handle_notification(self, wallet_address: str, notification: dict):
        self.notifications.append({
            "wallet": wallet_address,
            "type": notification["type"],
            "message": notification["message"],
            "priority": notification["priority"],
            "data": notification.get("data", {}),
            "timestamp": datetime.utcnow()
        })
        print(f"\nNotification received: {notification['message']}")
        print(f"Priority: {notification['priority']}")
        print(f"Data: {notification.get('data', {})}\n")

async def test_monitoring():
    # Initialize services
    db_service = DatabaseService(DATABASE_URL)
    notification_service = NotificationService()
    position_manager = PositionManager()
    price_feed = CoinGeckoPriceFeed()
    monitoring_service = MonitoringService(
        notification_service,
        position_manager,
        price_feed,
        db_service
    )
    
    # Test wallet address
    test_wallet = "0x1234567890123456789012345678901234567890"
    
    print("\nTesting Monitoring Service:\n")

    # Set up test data and notification handler
    print("Setting up test data...")
    await setup_test_data(db_service, test_wallet)
    notification_handler = TestNotificationHandler()
    
    # Subscribe to all notification types
    for notification_type in NotificationType:
        notification_service.subscribe(notification_type, notification_handler.handle_notification)

    # 1. Test Price Alerts
    print("\n1. Testing Price Alerts:")
    alert_response = await monitoring_service.add_price_alert(
        test_wallet,
        Decimal("25.00"),
        "above",
        datetime.utcnow() + timedelta(hours=1)
    )
    print(f"Added price alert: {alert_response}")

    # 2. Test Position Monitoring
    print("\n2. Testing Position Monitoring:")
    monitor_response = await monitoring_service.start_monitoring(test_wallet)
    print(f"Started monitoring: {monitor_response}")

    # Wait for some monitoring cycles
    print("\nWaiting for monitoring cycles (30 seconds)...")
    await asyncio.sleep(30)

    # 3. Test System Health
    print("\n3. Testing System Health:")
    health = monitoring_service.get_system_health()
    print("\nSystem Health Status:")
    print(f"Price Feed: {health['health']['price_feed']}")
    print(f"Position Monitoring: {health['health']['position_monitoring']}")
    print(f"Active Monitors: {health['health']['active_monitors']}")
    if health['health']['recent_errors']:
        print("\nRecent Errors:")
        for error in health['health']['recent_errors']:
            print(f"- {error['timestamp']}: {error['error']}")

    # 4. Test Alert Removal
    print("\n4. Testing Alert Removal:")
    if alert_response["status"] == "success":
        remove_response = await monitoring_service.remove_price_alert(
            test_wallet,
            alert_response["alert"]["id"]
        )
        print(f"Removed price alert: {remove_response}")

    # Stop monitoring
    print("\n5. Testing Monitoring Stop:")
    stop_response = await monitoring_service.stop_monitoring(test_wallet)
    print(f"Stopped monitoring: {stop_response}")

    # Print received notifications
    print("\nReceived Notifications:")
    for notification in notification_handler.notifications:
        print(f"\nType: {notification['type']}")
        print(f"Message: {notification['message']}")
        print(f"Priority: {notification['priority']}")
        print(f"Timestamp: {notification['timestamp']}")

if __name__ == "__main__":
    asyncio.run(test_monitoring()) 