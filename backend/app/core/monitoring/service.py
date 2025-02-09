from typing import Dict, List, Optional
from decimal import Decimal
import logging
from datetime import datetime, timedelta
import asyncio
from ..notifications.service import NotificationService, NotificationType, NotificationPriority
from ..trading.position_manager import PositionManager
from ..price_feed.coingecko import CoinGeckoPriceFeed
from ..db.service import DatabaseService

logger = logging.getLogger(__name__)

class MonitoringService:
    def __init__(
        self,
        notification_service: NotificationService,
        position_manager: PositionManager,
        price_feed: CoinGeckoPriceFeed,
        db_service: DatabaseService
    ):
        self.notification_service = notification_service
        self.position_manager = position_manager
        self.price_feed = price_feed
        self.db_service = db_service
        self.price_alerts: Dict[str, List[Dict]] = {}  # wallet -> list of price alerts
        self.monitoring_tasks: Dict[str, asyncio.Task] = {}
        self.system_health = {
            "last_price_update": None,
            "last_position_check": None,
            "errors": []
        }

    async def start_monitoring(self, wallet_address: str) -> Dict:
        """Start monitoring for a specific wallet."""
        try:
            if wallet_address in self.monitoring_tasks:
                return {
                    "status": "error",
                    "error": "Monitoring already active for this wallet"
                }

            # Create monitoring task
            self.monitoring_tasks[wallet_address] = asyncio.create_task(
                self._monitor_wallet(wallet_address)
            )

            return {
                "status": "success",
                "message": "Monitoring started successfully"
            }

        except Exception as e:
            logger.error(f"Failed to start monitoring: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def stop_monitoring(self, wallet_address: str) -> Dict:
        """Stop monitoring for a specific wallet."""
        try:
            if wallet_address not in self.monitoring_tasks:
                return {
                    "status": "error",
                    "error": "No active monitoring for this wallet"
                }

            # Cancel monitoring task
            self.monitoring_tasks[wallet_address].cancel()
            del self.monitoring_tasks[wallet_address]

            return {
                "status": "success",
                "message": "Monitoring stopped successfully"
            }

        except Exception as e:
            logger.error(f"Failed to stop monitoring: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def add_price_alert(
        self,
        wallet_address: str,
        price_level: Decimal,
        alert_type: str,  # 'above' or 'below'
        expiry: Optional[datetime] = None
    ) -> Dict:
        """Add a price alert for a wallet."""
        try:
            if wallet_address not in self.price_alerts:
                self.price_alerts[wallet_address] = []

            alert = {
                "id": f"alert_{datetime.utcnow().timestamp()}",
                "price_level": price_level,
                "type": alert_type,
                "created_at": datetime.utcnow(),
                "expiry": expiry,
                "triggered": False
            }

            self.price_alerts[wallet_address].append(alert)

            return {
                "status": "success",
                "alert": alert
            }

        except Exception as e:
            logger.error(f"Failed to add price alert: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def remove_price_alert(self, wallet_address: str, alert_id: str) -> Dict:
        """Remove a price alert."""
        try:
            if wallet_address not in self.price_alerts:
                return {
                    "status": "error",
                    "error": "No alerts found for this wallet"
                }

            self.price_alerts[wallet_address] = [
                alert for alert in self.price_alerts[wallet_address]
                if alert['id'] != alert_id
            ]

            return {
                "status": "success",
                "message": "Alert removed successfully"
            }

        except Exception as e:
            logger.error(f"Failed to remove price alert: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _monitor_wallet(self, wallet_address: str) -> None:
        """Background task to monitor a wallet's positions and alerts."""
        try:
            while True:
                try:
                    # Update system health
                    self.system_health["last_position_check"] = datetime.utcnow()

                    # Check positions
                    await self._check_positions(wallet_address)

                    # Check price alerts
                    await self._check_price_alerts(wallet_address)

                    # Check funding rates
                    await self._check_funding_rates(wallet_address)

                    # Sleep for monitoring interval
                    await asyncio.sleep(30)  # 30 seconds interval

                except asyncio.CancelledError:
                    logger.info(f"Monitoring cancelled for wallet {wallet_address}")
                    break
                except Exception as e:
                    logger.error(f"Error in monitoring loop: {str(e)}")
                    self.system_health["errors"].append({
                        "timestamp": datetime.utcnow(),
                        "error": str(e)
                    })
                    await asyncio.sleep(5)  # Short sleep on error

        except Exception as e:
            logger.error(f"Monitoring task failed: {str(e)}")

    async def _check_positions(self, wallet_address: str) -> None:
        """Check positions for liquidation risks and significant PnL changes."""
        try:
            # Get active positions
            positions = await self.position_manager.get_active_positions(wallet_address)
            if positions["status"] != "success":
                return

            # Check liquidation risks
            risks = await self.position_manager.monitor_liquidation_risks(wallet_address)
            if risks["status"] == "success":
                for pos_type, risk in risks["risks"].items():
                    if risk["risk_level"] in ["HIGH", "CRITICAL"]:
                        await self.notification_service.notify_liquidation_risk(
                            wallet_address,
                            {
                                "position_type": pos_type,
                                "distance_to_liquidation_percent": risk["distance_to_liquidation_percent"]
                            }
                        )

            # Check PnL changes
            for pos_type, position in positions["positions"].items():
                if abs(float(position["pnl"]["amount"])) >= 1000:  # $1000 threshold
                    await self.notification_service.notify_position_update(
                        wallet_address,
                        position
                    )

        except Exception as e:
            logger.error(f"Failed to check positions: {str(e)}")

    async def _check_price_alerts(self, wallet_address: str) -> None:
        """Check and trigger price alerts."""
        try:
            if wallet_address not in self.price_alerts:
                return

            current_price = await self.price_feed.get_token_price("AVAX")
            if not current_price:
                return

            # Update system health
            self.system_health["last_price_update"] = datetime.utcnow()

            for alert in self.price_alerts[wallet_address]:
                if alert["triggered"]:
                    continue

                if alert["expiry"] and datetime.utcnow() > alert["expiry"]:
                    alert["triggered"] = True
                    continue

                price_level = float(alert["price_level"])
                if (
                    (alert["type"] == "above" and current_price >= price_level) or
                    (alert["type"] == "below" and current_price <= price_level)
                ):
                    alert["triggered"] = True
                    await self.notification_service.notify(
                        wallet_address,
                        NotificationType.SYSTEM_ALERT,
                        f"Price Alert: AVAX price {alert['type']} ${price_level}",
                        NotificationPriority.HIGH,
                        {"current_price": current_price, "alert": alert}
                    )

        except Exception as e:
            logger.error(f"Failed to check price alerts: {str(e)}")

    async def _check_funding_rates(self, wallet_address: str) -> None:
        """Monitor funding rates and notify if significant changes."""
        try:
            # This is a placeholder for actual funding rate checks
            # In a real implementation, you would:
            # 1. Fetch funding rates from the exchange
            # 2. Compare with historical rates
            # 3. Notify if significant changes
            pass

        except Exception as e:
            logger.error(f"Failed to check funding rates: {str(e)}")

    def get_system_health(self) -> Dict:
        """Get system health status."""
        try:
            now = datetime.utcnow()
            price_update_age = None
            position_check_age = None

            if self.system_health["last_price_update"]:
                price_update_age = (now - self.system_health["last_price_update"]).total_seconds()

            if self.system_health["last_position_check"]:
                position_check_age = (now - self.system_health["last_position_check"]).total_seconds()

            return {
                "status": "success",
                "health": {
                    "price_feed": "healthy" if price_update_age and price_update_age < 60 else "warning",
                    "position_monitoring": "healthy" if position_check_age and position_check_age < 60 else "warning",
                    "active_monitors": len(self.monitoring_tasks),
                    "recent_errors": self.system_health["errors"][-5:],  # Last 5 errors
                    "last_price_update": self.system_health["last_price_update"],
                    "last_position_check": self.system_health["last_position_check"]
                }
            }

        except Exception as e:
            logger.error(f"Failed to get system health: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            } 