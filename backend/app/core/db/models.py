from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()

class PositionStatus(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    LIQUIDATED = "liquidated"

class OrderStatus(enum.Enum):
    PENDING = "pending"
    EXECUTED = "executed"
    CANCELLED = "cancelled"
    FAILED = "failed"

class Position(Base):
    __tablename__ = 'positions'
    
    id = Column(Integer, primary_key=True)
    wallet_address = Column(String, index=True)
    position_type = Column(String)  # 'long' or 'short'
    size = Column(Float)
    collateral = Column(Float)
    leverage = Column(Float)
    entry_price = Column(Float)
    liquidation_price = Column(Float)
    status = Column(Enum(PositionStatus))
    pnl = Column(Float, nullable=True)
    funding_fee = Column(Float, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    closed_at = Column(DateTime, nullable=True)
    
    # Relationships
    orders = relationship("Order", back_populates="position")

class Order(Base):
    __tablename__ = 'orders'
    
    id = Column(Integer, primary_key=True)
    order_id = Column(String, unique=True)  # External order ID
    wallet_address = Column(String, index=True)
    position_id = Column(Integer, ForeignKey('positions.id'), nullable=True)
    order_type = Column(String)  # 'limit', 'stop_loss', 'take_profit'
    size = Column(Float)
    target_price = Column(Float)
    leverage = Column(Float, nullable=True)
    status = Column(Enum(OrderStatus))
    execution_price = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    executed_at = Column(DateTime, nullable=True)
    cancelled_at = Column(DateTime, nullable=True)
    
    # Relationships
    position = relationship("Position", back_populates="orders")

class TradingStats(Base):
    __tablename__ = 'trading_stats'
    
    id = Column(Integer, primary_key=True)
    wallet_address = Column(String, unique=True)
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    total_pnl = Column(Float, default=0)
    best_trade = Column(Float, default=0)
    worst_trade = Column(Float, default=0)
    average_leverage = Column(Float, default=0)
    last_updated = Column(DateTime, default=datetime.utcnow) 