import asyncio
from app.core.notifications.service import (
    NotificationService,
    NotificationType,
    NotificationPriority
)

async def notification_callback(wallet_address: str, notification: dict):
    """Example callback for notifications."""
    print(f"\nCallback received for {wallet_address}:")
    print(f"Type: {notification['type']}")
    print(f"Message: {notification['message']}")

async def test_notifications():
    notification_service = NotificationService()
    
    # Test wallet address
    test_wallet = "0x1234567890123456789012345678901234567890"
    
    print("\nTesting Notification System:\n")

    # 1. Test Basic Notification
    print("1. Testing Basic Notification:")
    
    # Subscribe to notifications
    notification_service.subscribe(
        NotificationType.POSITION_UPDATE,
        notification_callback
    )
    
    # Send a test notification
    result = await notification_service.notify(
        test_wallet,
        NotificationType.POSITION_UPDATE,
        "Test notification",
        NotificationPriority.MEDIUM,
        {"test": "data"}
    )
    print("\nNotification Result:")
    print(result)

    # 2. Test Position Update Notification
    print("\n2. Testing Position Update Notification:")
    
    # Simulate position update
    position_data = {
        "status": "open",
        "pnl": "1500.50",
        "position_type": "long",
        "size": "10000",
        "leverage": "5"
    }
    
    result = await notification_service.notify_position_update(
        test_wallet,
        position_data
    )
    print("\nPosition Update Notification:")
    print(result)

    # 3. Test Order Execution Notification
    print("\n3. Testing Order Execution Notification:")
    
    # Simulate order execution
    order_data = {
        "order_type": "limit",
        "execution_price": "25.50",
        "size": "1000",
        "leverage": "5"
    }
    
    result = await notification_service.notify_order_execution(
        test_wallet,
        order_data
    )
    print("\nOrder Execution Notification:")
    print(result)

    # 4. Test Liquidation Risk Notification
    print("\n4. Testing Liquidation Risk Notification:")
    
    # Simulate liquidation risk
    risk_data = {
        "distance_to_liquidation_percent": "4.5",
        "position_type": "long",
        "current_price": "24.50",
        "liquidation_price": "23.40"
    }
    
    result = await notification_service.notify_liquidation_risk(
        test_wallet,
        risk_data
    )
    print("\nLiquidation Risk Notification:")
    print(result)

    # 5. Test Notification Retrieval
    print("\n5. Testing Notification Retrieval:")
    
    # Get all notifications
    notifications = await notification_service.get_notifications(test_wallet)
    print("\nAll Notifications:")
    print(f"Total: {len(notifications['notifications'])}")
    for notification in notifications['notifications']:
        print(f"\nType: {notification['type']}")
        print(f"Priority: {notification['priority']}")
        print(f"Message: {notification['message']}")
        print(f"Read: {notification['read']}")

    # 6. Test Mark as Read
    print("\n6. Testing Mark as Read:")
    
    # Mark specific notification as read
    first_notification_id = notifications['notifications'][0]['id']
    mark_result = await notification_service.mark_as_read(
        test_wallet,
        first_notification_id
    )
    print("\nMark as Read Result:")
    print(mark_result)
    
    # Get unread notifications
    unread = await notification_service.get_notifications(
        test_wallet,
        unread_only=True
    )
    print("\nUnread Notifications:")
    print(f"Count: {len(unread['notifications'])}")

if __name__ == "__main__":
    asyncio.run(test_notifications()) 