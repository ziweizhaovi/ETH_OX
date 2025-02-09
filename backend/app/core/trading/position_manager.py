from typing import Dict, List, Optional
from decimal import Decimal
import logging
from datetime import datetime
from ..gmx.client import GMXClient
from ..gmx.config import gmx_config

logger = logging.getLogger(__name__)

class PositionManager:
    def __init__(self):
        self.gmx = GMXClient()

    async def get_active_positions(self, wallet_address: str) -> Dict:
        """Get all active positions for a wallet."""
        try:
            # Get both long and short positions
            long_position = await self.gmx.get_position_info(
                wallet_address,
                gmx_config.TOKEN_ADDRESSES['USDC'],
                gmx_config.TOKEN_ADDRESSES['AVAX'],
                True
            )
            
            short_position = await self.gmx.get_position_info(
                wallet_address,
                gmx_config.TOKEN_ADDRESSES['USDC'],
                gmx_config.TOKEN_ADDRESSES['AVAX'],
                False
            )
            
            # Calculate additional metrics
            positions = {}
            
            if long_position['size'] > 0:
                positions['long'] = await self._enrich_position_data(
                    wallet_address,
                    long_position,
                    True
                )
                
            if short_position['size'] > 0:
                positions['short'] = await self._enrich_position_data(
                    wallet_address,
                    short_position,
                    False
                )
            
            return {
                "status": "success",
                "positions": positions
            }
            
        except Exception as e:
            logger.error(f"Failed to get active positions: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _enrich_position_data(
        self,
        wallet_address: str,
        position: Dict,
        is_long: bool
    ) -> Dict:
        """Add additional metrics to position data."""
        try:
            # Calculate PnL
            has_profit, delta = await self.gmx.calculate_position_delta(
                wallet_address,
                position['size'],
                position['average_price'],
                is_long,
                gmx_config.TOKEN_ADDRESSES['AVAX']
            )
            
            # Calculate leverage
            leverage = self.gmx.get_position_leverage(
                position['size'],
                position['collateral'],
                position['average_price']
            )
            
            # Calculate liquidation price
            liquidation_price = self.gmx.get_liquidation_price(
                position['size'],
                position['collateral'],
                position['average_price'],
                is_long
            )
            
            return {
                **position,
                "pnl": {
                    "has_profit": has_profit,
                    "amount": str(Decimal(delta) / 10**30)
                },
                "leverage": str(leverage),
                "liquidation_price": str(liquidation_price),
                "position_type": "long" if is_long else "short",
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to enrich position data: {str(e)}")
            return position

    async def check_risk_limits(
        self,
        wallet_address: str,
        position_size: Decimal,
        leverage: Decimal
    ) -> Dict:
        """Check if position meets risk management criteria."""
        try:
            # Get current positions
            positions = await self.get_active_positions(wallet_address)
            
            # Define risk limits
            MAX_LEVERAGE = Decimal('50')
            MAX_POSITION_SIZE = Decimal('100000')  # $100k
            MAX_TOTAL_POSITIONS = Decimal('200000')  # $200k
            
            # Calculate total position size
            total_size = Decimal('0')
            if positions['status'] == 'success':
                for pos in positions['positions'].values():
                    total_size += Decimal(pos['size']) / 10**30
            
            # Add new position size
            total_size += position_size
            
            # Check limits
            checks = {
                "leverage_within_limit": leverage <= MAX_LEVERAGE,
                "position_size_within_limit": position_size <= MAX_POSITION_SIZE,
                "total_size_within_limit": total_size <= MAX_TOTAL_POSITIONS
            }
            
            return {
                "status": "success",
                "passed_all_checks": all(checks.values()),
                "checks": checks,
                "current_total_size": str(total_size),
                "limits": {
                    "max_leverage": str(MAX_LEVERAGE),
                    "max_position_size": str(MAX_POSITION_SIZE),
                    "max_total_positions": str(MAX_TOTAL_POSITIONS)
                }
            }
            
        except Exception as e:
            logger.error(f"Failed to check risk limits: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def monitor_liquidation_risks(self, wallet_address: str) -> Dict:
        """Monitor positions for liquidation risks."""
        try:
            positions = await self.get_active_positions(wallet_address)
            if positions['status'] != 'success':
                return positions
            
            risks = {}
            for pos_type, position in positions['positions'].items():
                # Calculate distance to liquidation
                current_price = Decimal(position['average_price']) / 10**30
                liquidation_price = Decimal(position['liquidation_price'])
                
                if current_price > 0 and liquidation_price > 0:
                    distance_to_liq = abs(current_price - liquidation_price) / current_price * 100
                    
                    risks[pos_type] = {
                        "distance_to_liquidation_percent": str(distance_to_liq),
                        "risk_level": (
                            "HIGH" if distance_to_liq < 5 else
                            "MEDIUM" if distance_to_liq < 10 else
                            "LOW"
                        )
                    }
            
            return {
                "status": "success",
                "risks": risks
            }
            
        except Exception as e:
            logger.error(f"Failed to monitor liquidation risks: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            } 