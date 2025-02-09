from typing import Dict, List, Optional
from decimal import Decimal
import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.sql import func
from .models import Base, Position, Order, TradingStats, PositionStatus, OrderStatus

logger = logging.getLogger(__name__)

class DatabaseService:
    def __init__(self, database_url: str):
        self.engine = create_engine(database_url)
        Base.metadata.create_all(self.engine)
        self.SessionLocal = sessionmaker(bind=self.engine)

    def get_db(self) -> Session:
        """Get database session."""
        return self.SessionLocal()

    async def store_position(self, wallet_address: str, position_data: Dict) -> Position:
        """Store a new position in the database."""
        try:
            with self.get_db() as db:
                position = Position(
                    wallet_address=wallet_address,
                    position_type=position_data['position_type'],
                    size=float(position_data['size']),
                    collateral=float(position_data['collateral']),
                    leverage=float(position_data['leverage']),
                    entry_price=float(position_data['average_price']),
                    liquidation_price=float(position_data['liquidation_price']),
                    status=PositionStatus.OPEN
                )
                db.add(position)
                db.commit()
                db.refresh(position)
                return position
                
        except Exception as e:
            logger.error(f"Failed to store position: {str(e)}")
            raise

    async def update_position(self, position_id: int, update_data: Dict) -> Position:
        """Update an existing position."""
        try:
            with self.get_db() as db:
                position = db.query(Position).filter(Position.id == position_id).first()
                if not position:
                    raise ValueError(f"Position {position_id} not found")
                
                for key, value in update_data.items():
                    if hasattr(position, key):
                        setattr(position, key, value)
                
                if update_data.get('status') == PositionStatus.CLOSED:
                    position.closed_at = datetime.utcnow()
                
                db.commit()
                db.refresh(position)
                return position
                
        except Exception as e:
            logger.error(f"Failed to update position: {str(e)}")
            raise

    async def store_order(self, wallet_address: str, order_data: Dict) -> Order:
        """Store a new order in the database."""
        try:
            with self.get_db() as db:
                order = Order(
                    order_id=order_data['order_id'],
                    wallet_address=wallet_address,
                    position_id=order_data.get('position_id'),
                    order_type=order_data['type'],
                    size=float(order_data['size']),
                    target_price=float(order_data['target_price']),
                    leverage=float(order_data.get('leverage', 1)),
                    status=OrderStatus.PENDING
                )
                db.add(order)
                db.commit()
                db.refresh(order)
                return order
                
        except Exception as e:
            logger.error(f"Failed to store order: {str(e)}")
            raise

    async def update_order(self, order_id: str, update_data: Dict) -> Order:
        """Update an existing order."""
        try:
            with self.get_db() as db:
                order = db.query(Order).filter(Order.order_id == order_id).first()
                if not order:
                    raise ValueError(f"Order {order_id} not found")
                
                for key, value in update_data.items():
                    if hasattr(order, key):
                        setattr(order, key, value)
                
                if update_data.get('status') == OrderStatus.EXECUTED:
                    order.executed_at = datetime.utcnow()
                elif update_data.get('status') == OrderStatus.CANCELLED:
                    order.cancelled_at = datetime.utcnow()
                
                db.commit()
                db.refresh(order)
                return order
                
        except Exception as e:
            logger.error(f"Failed to update order: {str(e)}")
            raise

    async def update_trading_stats(self, wallet_address: str, trade_result: Dict) -> TradingStats:
        """Update trading statistics for a wallet."""
        try:
            with self.get_db() as db:
                stats = db.query(TradingStats).filter(
                    TradingStats.wallet_address == wallet_address
                ).first()
                
                if not stats:
                    # Initialize new stats with default values
                    stats = TradingStats(
                        wallet_address=wallet_address,
                        total_trades=0,
                        winning_trades=0,
                        total_pnl=0.0,
                        best_trade=float('-inf'),
                        worst_trade=float('inf'),
                        average_leverage=0.0
                    )
                    db.add(stats)
                
                # Update stats
                stats.total_trades += 1
                pnl = float(trade_result.get('pnl', 0))
                
                if pnl > 0:
                    stats.winning_trades += 1
                
                stats.total_pnl += pnl
                stats.best_trade = max(stats.best_trade, pnl)
                stats.worst_trade = min(stats.worst_trade, pnl)
                
                # Update average leverage
                current_leverage = float(trade_result.get('leverage', 1))
                stats.average_leverage = (
                    (stats.average_leverage * (stats.total_trades - 1) + current_leverage) / 
                    stats.total_trades
                )
                
                stats.last_updated = datetime.utcnow()
                
                db.commit()
                db.refresh(stats)
                return stats
                
        except Exception as e:
            logger.error(f"Failed to update trading stats: {str(e)}")
            raise

    async def get_position_history(
        self,
        wallet_address: str,
        status: Optional[PositionStatus] = None
    ) -> List[Position]:
        """Get position history for a wallet."""
        try:
            with self.get_db() as db:
                query = db.query(Position).filter(Position.wallet_address == wallet_address)
                if status:
                    query = query.filter(Position.status == status)
                return query.order_by(Position.created_at.desc()).all()
                
        except Exception as e:
            logger.error(f"Failed to get position history: {str(e)}")
            raise

    async def get_order_history(
        self,
        wallet_address: str,
        status: Optional[OrderStatus] = None
    ) -> List[Order]:
        """Get order history for a wallet."""
        try:
            with self.get_db() as db:
                query = db.query(Order).filter(Order.wallet_address == wallet_address)
                if status:
                    query = query.filter(Order.status == status)
                return query.order_by(Order.created_at.desc()).all()
                
        except Exception as e:
            logger.error(f"Failed to get order history: {str(e)}")
            raise

    async def get_trading_stats(self, wallet_address: str) -> Optional[TradingStats]:
        """Get trading statistics for a wallet."""
        try:
            with self.get_db() as db:
                return db.query(TradingStats).filter(
                    TradingStats.wallet_address == wallet_address
                ).first()
                
        except Exception as e:
            logger.error(f"Failed to get trading stats: {str(e)}")
            raise 