from typing import Dict, List, Optional
from decimal import Decimal
import logging
from datetime import datetime
from ..gmx.client import GMXClient
from ..price_feed.coingecko import CoinGeckoPriceFeed

logger = logging.getLogger(__name__)

class OrderManager:
    def __init__(self):
        self.gmx = GMXClient()
        self.price_feed = CoinGeckoPriceFeed()
        self.pending_orders: Dict[str, Dict] = {}  # In-memory storage for pending orders

    async def create_limit_order(
        self,
        wallet_address: str,
        position_type: str,
        size: Decimal,
        target_price: Decimal,
        leverage: Optional[Decimal] = None
    ) -> Dict:
        """Create a limit order to be executed when price conditions are met."""
        try:
            # Generate unique order ID
            order_id = f"limit_{wallet_address}_{datetime.utcnow().timestamp()}"
            
            # Store order details
            self.pending_orders[order_id] = {
                "type": "limit",
                "wallet_address": wallet_address,
                "position_type": position_type,
                "size": str(size),
                "target_price": str(target_price),
                "leverage": str(leverage) if leverage else "1",
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }
            
            return {
                "status": "success",
                "order_id": order_id,
                "order": self.pending_orders[order_id]
            }
            
        except Exception as e:
            logger.error(f"Failed to create limit order: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def create_stop_loss(
        self,
        wallet_address: str,
        position_type: str,
        trigger_price: Decimal
    ) -> Dict:
        """Create a stop loss order for an existing position."""
        try:
            # Generate unique order ID
            order_id = f"stop_{wallet_address}_{datetime.utcnow().timestamp()}"
            
            # Store order details
            self.pending_orders[order_id] = {
                "type": "stop_loss",
                "wallet_address": wallet_address,
                "position_type": position_type,
                "trigger_price": str(trigger_price),
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }
            
            return {
                "status": "success",
                "order_id": order_id,
                "order": self.pending_orders[order_id]
            }
            
        except Exception as e:
            logger.error(f"Failed to create stop loss: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def create_take_profit(
        self,
        wallet_address: str,
        position_type: str,
        trigger_price: Decimal
    ) -> Dict:
        """Create a take profit order for an existing position."""
        try:
            # Generate unique order ID
            order_id = f"profit_{wallet_address}_{datetime.utcnow().timestamp()}"
            
            # Store order details
            self.pending_orders[order_id] = {
                "type": "take_profit",
                "wallet_address": wallet_address,
                "position_type": position_type,
                "trigger_price": str(trigger_price),
                "status": "pending",
                "created_at": datetime.utcnow().isoformat()
            }
            
            return {
                "status": "success",
                "order_id": order_id,
                "order": self.pending_orders[order_id]
            }
            
        except Exception as e:
            logger.error(f"Failed to create take profit: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def check_and_execute_orders(self) -> Dict:
        """Check all pending orders and execute if conditions are met."""
        try:
            current_price = await self.price_feed.get_token_price("AVAX")
            if not current_price:
                raise ValueError("Failed to get current price")
            
            executed_orders = []
            failed_orders = []
            
            for order_id, order in list(self.pending_orders.items()):
                try:
                    if order['status'] != 'pending':
                        continue
                        
                    should_execute = False
                    
                    # Check execution conditions
                    if order['type'] == 'limit':
                        target_price = Decimal(order['target_price'])
                        if (order['position_type'] == 'long' and current_price <= target_price) or \
                           (order['position_type'] == 'short' and current_price >= target_price):
                            should_execute = True
                            
                    elif order['type'] in ['stop_loss', 'take_profit']:
                        trigger_price = Decimal(order['trigger_price'])
                        if (order['position_type'] == 'long' and current_price <= trigger_price) or \
                           (order['position_type'] == 'short' and current_price >= trigger_price):
                            should_execute = True
                    
                    # Execute order if conditions met
                    if should_execute:
                        # Execute based on order type
                        if order['type'] == 'limit':
                            # Open new position
                            size = Decimal(order['size'])
                            leverage = Decimal(order['leverage'])
                            await self.gmx.open_position(
                                order['wallet_address'],
                                size,
                                leverage,
                                order['position_type'] == 'long'
                            )
                        else:
                            # Close existing position
                            await self.gmx.close_position(
                                order['wallet_address'],
                                order['position_type'] == 'long'
                            )
                        
                        # Update order status
                        order['status'] = 'executed'
                        order['executed_at'] = datetime.utcnow().isoformat()
                        order['execution_price'] = str(current_price)
                        executed_orders.append(order_id)
                        
                except Exception as e:
                    logger.error(f"Failed to execute order {order_id}: {str(e)}")
                    failed_orders.append({
                        "order_id": order_id,
                        "error": str(e)
                    })
            
            return {
                "status": "success",
                "executed_orders": executed_orders,
                "failed_orders": failed_orders
            }
            
        except Exception as e:
            logger.error(f"Failed to check and execute orders: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def get_pending_orders(self, wallet_address: str) -> Dict:
        """Get all pending orders for a wallet."""
        try:
            wallet_orders = {
                order_id: order
                for order_id, order in self.pending_orders.items()
                if order['wallet_address'] == wallet_address and order['status'] == 'pending'
            }
            
            return {
                "status": "success",
                "orders": wallet_orders
            }
            
        except Exception as e:
            logger.error(f"Failed to get pending orders: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    def cancel_order(self, order_id: str, wallet_address: str) -> Dict:
        """Cancel a pending order."""
        try:
            if order_id not in self.pending_orders:
                raise ValueError(f"Order {order_id} not found")
                
            order = self.pending_orders[order_id]
            if order['wallet_address'] != wallet_address:
                raise ValueError("Not authorized to cancel this order")
                
            if order['status'] != 'pending':
                raise ValueError(f"Order {order_id} is not pending")
            
            # Update order status
            order['status'] = 'cancelled'
            order['cancelled_at'] = datetime.utcnow().isoformat()
            
            return {
                "status": "success",
                "order": order
            }
            
        except Exception as e:
            logger.error(f"Failed to cancel order: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            } 