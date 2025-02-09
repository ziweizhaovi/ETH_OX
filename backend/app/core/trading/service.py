from typing import Dict, Optional
from decimal import Decimal
import logging
from ..price_feed.coingecko import CoinGeckoPriceFeed
from ..gmx.client import GMXClient
from ..gmx.config import gmx_config

logger = logging.getLogger(__name__)

class TradingService:
    def __init__(self):
        self.price_feed = CoinGeckoPriceFeed()
        self.gmx = GMXClient()

    async def execute_trade(self, parsed_command: Dict, wallet_address: str) -> Dict:
        """
        Execute a trade based on the parsed command from AI.
        Returns the transaction result and relevant information.
        """
        try:
            # Extract operation details
            operation = parsed_command['operation_type']
            
            if operation == 'analyze':
                return await self._handle_analysis(parsed_command)
            
            # Get current market price for AVAX
            avax_price = await self.price_feed.get_token_price("AVAX")
            if not avax_price:
                raise ValueError("Failed to get AVAX price")

            if operation in ['open_position', 'spot_buy', 'spot_sell']:
                return await self._handle_position_open(parsed_command, wallet_address, avax_price)
            elif operation == 'close_position':
                return await self._handle_position_close(parsed_command, wallet_address, avax_price)
            else:
                raise ValueError(f"Unsupported operation: {operation}")

        except Exception as e:
            logger.error(f"Trade execution failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _handle_analysis(self, parsed_command: Dict) -> Dict:
        """Handle market analysis requests."""
        try:
            market_data = await self.price_feed.get_market_data("AVAX")
            current_price = await self.price_feed.get_token_price("AVAX")
            
            return {
                "status": "success",
                "type": "analysis",
                "data": {
                    "current_price": current_price,
                    "24h_change": market_data['price_change_24h'],
                    "24h_volume": market_data['total_volume'].get('usd'),
                    "24h_high": market_data['high_24h'].get('usd'),
                    "24h_low": market_data['low_24h'].get('usd')
                }
            }
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _handle_position_open(self, parsed_command: Dict, wallet_address: str, current_price: float) -> Dict:
        """Handle position opening (both spot and leverage)."""
        try:
            # Extract parameters
            amount = Decimal(parsed_command['amount'])
            is_long = parsed_command.get('position_type', 'long') == 'long'
            leverage = Decimal(parsed_command.get('leverage', '1'))
            
            # Calculate acceptable price with slippage
            slippage_bps = gmx_config.DEFAULT_SLIPPAGE_BPS
            slippage_multiplier = Decimal(1 + slippage_bps / 10000)
            
            acceptable_price = (
                Decimal(current_price) * slippage_multiplier if is_long
                else Decimal(current_price) / slippage_multiplier
            )

            # Check available liquidity
            avax_liquidity = self.gmx.get_available_liquidity("AVAX")
            usdc_liquidity = self.gmx.get_available_liquidity("USDC")
            
            # Convert to readable numbers
            avax_liquidity_readable = Decimal(avax_liquidity) / 10**18
            usdc_liquidity_readable = Decimal(usdc_liquidity) / 10**6
            
            # Basic liquidity validation
            if amount > usdc_liquidity_readable:
                raise ValueError(f"Insufficient USDC liquidity. Available: {usdc_liquidity_readable} USDC")

            # Execute the trade
            if parsed_command['operation_type'] == 'open_position':
                tx_hash = await self.gmx.open_position(
                    account=wallet_address,
                    collateral_token=gmx_config.TOKEN_ADDRESSES['USDC'],
                    index_token=gmx_config.TOKEN_ADDRESSES['AVAX'],
                    size_usd=amount * leverage,
                    is_long=is_long,
                    acceptable_price=acceptable_price
                )
            else:
                # Spot trades not implemented yet
                raise NotImplementedError("Spot trades not implemented yet")

            return {
                "status": "success",
                "type": "position_open",
                "data": {
                    "tx_hash": tx_hash,
                    "amount": str(amount),
                    "leverage": str(leverage),
                    "position_type": "long" if is_long else "short",
                    "entry_price": str(current_price),
                    "acceptable_price": str(acceptable_price)
                }
            }

        except Exception as e:
            logger.error(f"Position opening failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def _handle_position_close(self, parsed_command: Dict, wallet_address: str, current_price: float) -> Dict:
        """Handle position closing."""
        try:
            is_long = parsed_command.get('position_type', 'long') == 'long'
            
            # Calculate acceptable price with slippage
            slippage_bps = gmx_config.DEFAULT_SLIPPAGE_BPS
            slippage_multiplier = Decimal(1 + slippage_bps / 10000)
            
            acceptable_price = (
                Decimal(current_price) / slippage_multiplier if is_long
                else Decimal(current_price) * slippage_multiplier
            )

            # Close the position
            tx_hash = await self.gmx.close_position(
                account=wallet_address,
                collateral_token=gmx_config.TOKEN_ADDRESSES['USDC'],
                index_token=gmx_config.TOKEN_ADDRESSES['AVAX'],
                is_long=is_long,
                acceptable_price=acceptable_price
            )

            return {
                "status": "success",
                "type": "position_close",
                "data": {
                    "tx_hash": tx_hash,
                    "position_type": "long" if is_long else "short",
                    "exit_price": str(current_price),
                    "acceptable_price": str(acceptable_price)
                }
            }

        except Exception as e:
            logger.error(f"Position closing failed: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            }

    async def get_position_status(self, wallet_address: str) -> Dict:
        """Get the current status of all positions for a wallet."""
        try:
            # Get position info for both long and short
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

            return {
                "status": "success",
                "data": {
                    "long_position": long_position,
                    "short_position": short_position
                }
            }

        except Exception as e:
            logger.error(f"Failed to get position status: {str(e)}")
            return {
                "status": "error",
                "error": str(e)
            } 