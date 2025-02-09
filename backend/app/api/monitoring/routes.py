from typing import List
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException
from decimal import Decimal
from datetime import datetime
from ...core.monitoring.service import MonitoringService
from ...core.notifications.service import NotificationService, NotificationType
from ...core.trading.position_manager import PositionManager
from ...core.price_feed.coingecko import CoinGeckoPriceFeed
from ...core.db.service import DatabaseService
from ...dependencies import get_db_service

router = APIRouter()

# Store active WebSocket connections
active_connections: dict[str, List[WebSocket]] = {}

class NotificationWebSocket:
    def __init__(self):
        self.connections: dict[str, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, wallet_address: str):
        await websocket.accept()
        if wallet_address not in self.connections:
            self.connections[wallet_address] = []
        self.connections[wallet_address].append(websocket)

    def disconnect(self, websocket: WebSocket, wallet_address: str):
        if wallet_address in self.connections:
            self.connections[wallet_address].remove(websocket)
            if not self.connections[wallet_address]:
                del self.connections[wallet_address]

    async def broadcast(self, wallet_address: str, message: dict):
        if wallet_address in self.connections:
            for connection in self.connections[wallet_address]:
                try:
                    await connection.send_json(message)
                except:
                    continue

notification_ws = NotificationWebSocket()

@router.websocket("/ws/monitor/{wallet_address}")
async def websocket_endpoint(websocket: WebSocket, wallet_address: str):
    await notification_ws.connect(websocket, wallet_address)
    try:
        while True:
            data = await websocket.receive_json()
            # Handle any incoming messages if needed
    except WebSocketDisconnect:
        notification_ws.disconnect(websocket, wallet_address)

@router.post("/monitor/start/{wallet_address}")
async def start_monitoring(
    wallet_address: str,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Start monitoring for a wallet."""
    notification_service = NotificationService()
    position_manager = PositionManager()
    price_feed = CoinGeckoPriceFeed()
    
    monitoring_service = MonitoringService(
        notification_service,
        position_manager,
        price_feed,
        db_service
    )

    # Set up WebSocket notification handler
    async def notification_handler(wallet: str, notification: dict):
        await notification_ws.broadcast(wallet, {
            "type": "notification",
            "data": notification
        })

    # Subscribe to notifications
    for notification_type in NotificationType:
        notification_service.subscribe(notification_type, notification_handler)

    result = await monitoring_service.start_monitoring(wallet_address)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/monitor/stop/{wallet_address}")
async def stop_monitoring(
    wallet_address: str,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Stop monitoring for a wallet."""
    notification_service = NotificationService()
    position_manager = PositionManager()
    price_feed = CoinGeckoPriceFeed()
    
    monitoring_service = MonitoringService(
        notification_service,
        position_manager,
        price_feed,
        db_service
    )

    result = await monitoring_service.stop_monitoring(wallet_address)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.post("/monitor/alerts/add/{wallet_address}")
async def add_price_alert(
    wallet_address: str,
    price_level: float,
    alert_type: str,
    expiry: datetime = None,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Add a price alert for a wallet."""
    notification_service = NotificationService()
    position_manager = PositionManager()
    price_feed = CoinGeckoPriceFeed()
    
    monitoring_service = MonitoringService(
        notification_service,
        position_manager,
        price_feed,
        db_service
    )

    result = await monitoring_service.add_price_alert(
        wallet_address,
        Decimal(str(price_level)),
        alert_type,
        expiry
    )
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.delete("/monitor/alerts/{wallet_address}/{alert_id}")
async def remove_price_alert(
    wallet_address: str,
    alert_id: str,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Remove a price alert."""
    notification_service = NotificationService()
    position_manager = PositionManager()
    price_feed = CoinGeckoPriceFeed()
    
    monitoring_service = MonitoringService(
        notification_service,
        position_manager,
        price_feed,
        db_service
    )

    result = await monitoring_service.remove_price_alert(wallet_address, alert_id)
    if result["status"] == "error":
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@router.get("/monitor/health/{wallet_address}")
async def get_monitoring_health(
    wallet_address: str,
    db_service: DatabaseService = Depends(get_db_service)
):
    """Get monitoring system health status."""
    notification_service = NotificationService()
    position_manager = PositionManager()
    price_feed = CoinGeckoPriceFeed()
    
    monitoring_service = MonitoringService(
        notification_service,
        position_manager,
        price_feed,
        db_service
    )

    return monitoring_service.get_system_health() 