from typing import Dict, List, Optional
import logging
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)

class NotificationType(Enum):
    POSITION_UPDATE = "position_update"
    ORDER_EXECUTED = "order_executed"
    ORDER_CANCELLED = "order_cancelled"
    LIQUIDATION_RISK = "liquidation_risk"
    PNL_ALERT = "pnl_alert"
    FUNDING_RATE = "funding_rate"
    SYSTEM_ALERT = "system_alert"

class NotificationPriority(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class NotificationService:
    def __init__(self):
        self.notifications: Dict[str, List[Dict]] = {}  # wallet_address -> notifications
        self.subscribers: Dict[str, List[callable]] = {}  # notification_type -> callbacks

    async def notify(
        self,
        wallet_address: str,
        notification_type: NotificationType,
        message: str,
        priority: NotificationPriority = NotificationPriority.MEDIUM,
        data: Optional[Dict] = None
    ) -> Dict:
        """Send a notification to a wallet."""
        try:
            # Create notification
            notification = {
                "id": f"{notification_type.value}_{datetime.utcnow().timestamp()}",
                "type": notification_type.value,
                "message": message,
                "priority": priority.value,
                "data": data,
                "timestamp": datetime.utcnow().isoformat(),
                "read": False
            }
            
            # Store notification
            if wallet_address not in self.notifications:
                self.notifications[wallet_address] = []
            self.notifications[wallet_address].append(notification)
            
            # Call subscribers
            if notification_type.value in self.subscribers:
                for callback in self.subscribers[notification_type.value]:
                    try:
                        await callback(wallet_address, notification)
                    except Exception as e:
                        logger.error(f"Notification callback failed: {str(e)}")
            
            return {
                "status": "success",
                "notification": notification
            }
            
        except Exception as e:
            logger.error(f"Failed to send notification: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def subscribe(self, notification_type: NotificationType, callback: callable) -> None:
        """Subscribe to notifications of a specific type."""
        if notification_type.value not in self.subscribers:
            self.subscribers[notification_type.value] = []
        self.subscribers[notification_type.value].append(callback)

    def unsubscribe(self, notification_type: NotificationType, callback: callable) -> None:
        """Unsubscribe from notifications of a specific type."""
        if notification_type.value in self.subscribers:
            self.subscribers[notification_type.value].remove(callback)

    async def get_notifications(
        self,
        wallet_address: str,
        notification_type: Optional[NotificationType] = None,
        unread_only: bool = False
    ) -> Dict:
        """Get notifications for a wallet."""
        try:
            if wallet_address not in self.notifications:
                return {
                    "status": "success",
                    "notifications": []
                }
            
            notifications = self.notifications[wallet_address]
            
            # Filter by type if specified
            if notification_type:
                notifications = [
                    n for n in notifications
                    if n['type'] == notification_type.value
                ]
            
            # Filter unread if specified
            if unread_only:
                notifications = [n for n in notifications if not n['read']]
            
            return {
                "status": "success",
                "notifications": sorted(
                    notifications,
                    key=lambda x: x['timestamp'],
                    reverse=True
                )
            }
            
        except Exception as e:
            logger.error(f"Failed to get notifications: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def mark_as_read(
        self,
        wallet_address: str,
        notification_id: Optional[str] = None
    ) -> Dict:
        """Mark notifications as read."""
        try:
            if wallet_address not in self.notifications:
                return {
                    "status": "success",
                    "marked_count": 0
                }
            
            marked_count = 0
            
            # Mark specific notification or all
            if notification_id:
                for notification in self.notifications[wallet_address]:
                    if notification['id'] == notification_id and not notification['read']:
                        notification['read'] = True
                        marked_count += 1
            else:
                for notification in self.notifications[wallet_address]:
                    if not notification['read']:
                        notification['read'] = True
                        marked_count += 1
            
            return {
                "status": "success",
                "marked_count": marked_count
            }
            
        except Exception as e:
            logger.error(f"Failed to mark notifications as read: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def notify_position_update(
        self,
        wallet_address: str,
        position_data: Dict
    ) -> Dict:
        """Send position update notification."""
        try:
            # Determine notification priority based on changes
            priority = NotificationPriority.MEDIUM
            message = "Position Update: "
            
            if position_data.get('status') == 'closed':
                priority = NotificationPriority.HIGH
                message += "Position Closed"
            elif position_data.get('pnl'):
                pnl = float(position_data['pnl'])
                if abs(pnl) >= 1000:  # $1000 PnL change
                    priority = NotificationPriority.HIGH
                message += f"PnL changed by ${pnl:,.2f}"
            else:
                message += "Position parameters updated"
            
            return await self.notify(
                wallet_address,
                NotificationType.POSITION_UPDATE,
                message,
                priority,
                position_data
            )
            
        except Exception as e:
            logger.error(f"Failed to send position update notification: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def notify_order_execution(
        self,
        wallet_address: str,
        order_data: Dict
    ) -> Dict:
        """Send order execution notification."""
        try:
            # Determine notification priority
            priority = NotificationPriority.HIGH
            message = f"Order Executed: {order_data['order_type']} order at ${float(order_data['execution_price']):,.2f}"
            
            return await self.notify(
                wallet_address,
                NotificationType.ORDER_EXECUTED,
                message,
                priority,
                order_data
            )
            
        except Exception as e:
            logger.error(f"Failed to send order execution notification: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def notify_liquidation_risk(
        self,
        wallet_address: str,
        risk_data: Dict
    ) -> Dict:
        """Send liquidation risk notification."""
        try:
            # Determine notification priority based on risk level
            priority = NotificationPriority.MEDIUM
            distance = float(risk_data['distance_to_liquidation_percent'])
            
            if distance <= 5:
                priority = NotificationPriority.CRITICAL
                message = f"CRITICAL: Position near liquidation ({distance:.1f}% away)"
            elif distance <= 10:
                priority = NotificationPriority.HIGH
                message = f"WARNING: Position approaching liquidation ({distance:.1f}% away)"
            else:
                message = f"Position liquidation distance: {distance:.1f}%"
            
            return await self.notify(
                wallet_address,
                NotificationType.LIQUIDATION_RISK,
                message,
                priority,
                risk_data
            )
            
        except Exception as e:
            logger.error(f"Failed to send liquidation risk notification: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            } 