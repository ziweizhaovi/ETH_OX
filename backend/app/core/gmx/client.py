from typing import Dict, Optional, Tuple
from decimal import Decimal
import logging
from web3 import Web3
from web3.middleware import geth_poa_middleware
from web3.contract import Contract
from web3.types import TxParams, Wei
from eth_typing import Address
from .config import gmx_config
from ..price_feed.coingecko import CoinGeckoPriceFeed

logger = logging.getLogger(__name__)

class GMXClient:
    def __init__(self):
        """Initialize GMX client with Web3 connection and contract interfaces."""
        self.w3 = Web3(Web3.HTTPProvider(gmx_config.AVALANCHE_RPC_URL))
        
        # Add POA middleware for Avalanche
        self.w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        
        self.price_feed = CoinGeckoPriceFeed()
        
        # Load contract ABIs
        self.router: Contract = self._load_contract('router', gmx_config.ROUTER_ADDRESS)
        self.position_router: Contract = self._load_contract('position_router', gmx_config.POSITION_ROUTER_ADDRESS)
        self.reader: Contract = self._load_contract('reader', gmx_config.READER_ADDRESS)
        self.vault: Contract = self._load_contract('vault', gmx_config.VAULT_ADDRESS)
        
        logger.info("GMX client initialized")

    def _load_contract(self, name: str, address: str) -> Contract:
        """Load contract ABI and create contract instance."""
        try:
            with open(f'app/core/gmx/abis/{name}.json', 'r') as f:
                abi = f.read()
            return self.w3.eth.contract(address=address, abi=abi)
        except Exception as e:
            logger.error(f"Failed to load contract {name}: {str(e)}")
            raise

    def _handle_contract_error(self, error: Exception) -> Exception:
        """Handle common contract errors and provide better error messages."""
        error_str = str(error)
        
        if "execution reverted" in error_str:
            if "insufficient balance" in error_str.lower():
                return ValueError("Insufficient balance for transaction")
            elif "insufficient allowance" in error_str.lower():
                return ValueError("Token allowance not granted")
            elif "price impact too high" in error_str.lower():
                return ValueError("Price impact too high, try smaller size")
            elif "insufficient liquidity" in error_str.lower():
                return ValueError("Insufficient liquidity for trade")
            else:
                return ValueError(f"Transaction reverted: {error_str}")
        
        return error

    async def get_position_info(self, account: str, collateral_token: str, index_token: str, is_long: bool) -> Dict:
        """Get detailed information about a specific position."""
        try:
            position = self.reader.functions.getPosition(
                account,
                collateral_token,
                index_token,
                is_long
            ).call()
            
            return {
                "size": position[0],
                "collateral": position[1],
                "average_price": position[2],
                "entry_funding_rate": position[3],
                "reserve_amount": position[4],
                "realized_pnl": position[5],
                "last_increased_time": position[6]
            }
        except Exception as e:
            logger.error(f"Failed to get position info: {str(e)}")
            raise self._handle_contract_error(e)

    async def calculate_position_delta(
        self,
        account: str,
        size: int,
        average_price: int,
        is_long: bool,
        index_token: str
    ) -> Tuple[bool, int]:
        """Calculate the PnL for a position."""
        try:
            result = self.vault.functions.getPositionDelta(
                account,
                index_token,
                is_long,
                size,
                average_price
            ).call()
            return result[0], result[1]  # (hasProfit, delta)
        except Exception as e:
            logger.error(f"Failed to calculate position delta: {str(e)}")
            raise self._handle_contract_error(e)

    async def open_position(
        self,
        account: str,
        collateral_token: str,
        index_token: str,
        size_usd: Decimal,
        is_long: bool,
        acceptable_price: Decimal,
        execution_fee: Optional[int] = None
    ) -> str:
        """Open a new position."""
        try:
            # Convert size to wei (multiply by 1e30 as GMX uses 30 decimals for USD)
            size_wei = Web3.to_wei(size_usd, 'ether') * 10**12
            
            # Get execution fee if not provided
            if execution_fee is None:
                execution_fee = gmx_config.DEFAULT_EXECUTION_FEE
            
            # Create the path for token swaps
            path = [collateral_token]  # USDC -> AVAX for longs, or AVAX -> USDC for shorts
            if is_long and collateral_token != index_token:
                path.append(index_token)
            
            # Prepare transaction parameters
            params = [
                path,  # _path
                index_token,  # _indexToken
                size_wei,  # _amountIn (collateral amount)
                0,  # _minOut (minimum output amount, 0 for now)
                size_wei,  # _sizeDelta (position size)
                is_long,  # _isLong
                Web3.to_wei(acceptable_price, 'ether'),  # _acceptablePrice
                execution_fee,  # _executionFee
                gmx_config.REFERRAL_CODE,  # _referralCode
                "0x0000000000000000000000000000000000000000"  # _callbackTarget (no callback)
            ]
            
            # Create position
            tx = self.position_router.functions.createIncreasePosition(
                *params
            ).transact({
                'from': account,
                'value': execution_fee
            })
            
            logger.info(f"Position opening transaction sent: {tx.hex()}")
            return tx.hex()
            
        except Exception as e:
            logger.error(f"Failed to open position: {str(e)}")
            raise self._handle_contract_error(e)

    async def close_position(
        self,
        account: str,
        collateral_token: str,
        index_token: str,
        is_long: bool,
        acceptable_price: Decimal,
        execution_fee: Optional[int] = None
    ) -> str:
        """Close an existing position."""
        try:
            # Get position info to close entire position
            position = await self.get_position_info(
                account,
                collateral_token,
                index_token,
                is_long
            )
            
            # Verify position exists
            if position['size'] == 0:
                raise ValueError("No active position found to close")
            
            # Get execution fee if not provided
            if execution_fee is None:
                execution_fee = gmx_config.DEFAULT_EXECUTION_FEE
            
            # Create the path for token swaps
            path = [collateral_token]  # USDC -> AVAX for longs, or AVAX -> USDC for shorts
            if is_long and collateral_token != index_token:
                path.append(index_token)
            
            # Prepare transaction parameters
            params = [
                path,  # _path
                index_token,  # _indexToken
                position['collateral'],  # _collateralDelta (full collateral)
                position['size'],  # _sizeDelta (full size)
                is_long,  # _isLong
                account,  # _receiver
                Web3.to_wei(acceptable_price, 'ether'),  # _acceptablePrice
                0,  # _minOut (minimum output amount, 0 for now)
                execution_fee,  # _executionFee
                False,  # _withdrawETH
                "0x0000000000000000000000000000000000000000"  # _callbackTarget (no callback)
            ]
            
            # Create close position transaction
            tx = self.position_router.functions.createDecreasePosition(
                *params
            ).transact({
                'from': account,
                'value': execution_fee
            })
            
            logger.info(f"Position closing transaction sent: {tx.hex()}")
            return tx.hex()
            
        except Exception as e:
            logger.error(f"Failed to close position: {str(e)}")
            raise self._handle_contract_error(e)

    def get_position_leverage(
        self,
        size: int,
        collateral: int,
        avg_price: int
    ) -> Decimal:
        """Calculate the leverage of a position."""
        try:
            if collateral == 0:
                return Decimal('0')
            
            position_value = Decimal(size) / 10**30  # Convert from wei
            collateral_value = Decimal(collateral) / 10**30  # Convert from wei
            
            return position_value / collateral_value
            
        except Exception as e:
            logger.error(f"Failed to calculate leverage: {str(e)}")
            raise

    def get_liquidation_price(
        self,
        size: int,
        collateral: int,
        avg_price: int,
        is_long: bool
    ) -> Decimal:
        """Calculate the liquidation price for a position."""
        try:
            # GMX uses a liquidation threshold of ~1% of the position size
            liquidation_threshold = Decimal('0.01')
            
            if size == 0 or collateral == 0:
                return Decimal('0')
            
            size_usd = Decimal(size) / 10**30
            collateral_usd = Decimal(collateral) / 10**30
            avg_price_usd = Decimal(avg_price) / 10**30
            
            if is_long:
                return avg_price_usd * (Decimal('1') - collateral_usd / size_usd + liquidation_threshold)
            else:
                return avg_price_usd * (Decimal('1') + collateral_usd / size_usd - liquidation_threshold)
            
        except Exception as e:
            logger.error(f"Failed to calculate liquidation price: {str(e)}")
            raise

    def get_available_liquidity(self, token: str) -> int:
        """Get available liquidity for a token in the GMX pool."""
        try:
            token_address = gmx_config.TOKEN_ADDRESSES.get(token.upper())
            if not token_address:
                raise ValueError(f"Unsupported token: {token}")
            
            return self.vault.functions.poolAmounts(token_address).call()
            
        except Exception as e:
            logger.error(f"Failed to get available liquidity: {str(e)}")
            raise self._handle_contract_error(e) 