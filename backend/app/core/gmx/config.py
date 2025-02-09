from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import Dict

class GMXConfig(BaseSettings):
    # Network Configuration
    AVALANCHE_RPC_URL: str = "https://api.avax.network/ext/bc/C/rpc"
    CHAIN_ID: int = 43114  # Avalanche C-Chain

    # GMX Contract Addresses (Avalanche Mainnet)
    ROUTER_ADDRESS: str = "0x5F719c2F1095F7B9fc68a68e35B51194f4b6abe8"
    POSITION_ROUTER_ADDRESS: str = "0xb87a436B93fFE9D75c5cFA7bAcFff96430b09868"
    READER_ADDRESS: str = "0x67b789D48c926006F5132BFCe4e976F0A7A63d5D"
    VAULT_ADDRESS: str = "0x9ab2De34A33fB459b538c43f251eB825645e8595"
    
    # Default Settings
    DEFAULT_SLIPPAGE_BPS: int = 30  # 0.3%
    DEFAULT_EXECUTION_FEE: int = 300000  # in wei
    REFERRAL_CODE: str = "0x0000000000000000000000000000000000000000000000000000000000000000"
    
    # Token Addresses
    TOKEN_ADDRESSES: Dict[str, str] = {
        "AVAX": "0xB31f66AA3C1e785363F0875A1B74E27b85FD66c7",  # WAVAX
        "USDC": "0xB97EF9Ef8734C71904D8002F8b6Bc66Dd9c48a6E"
    }
    
    # Timeouts and Confirmations
    TRANSACTION_TIMEOUT: int = 60  # seconds
    REQUIRED_CONFIRMATIONS: int = 3
    
    model_config = ConfigDict(
        env_file=".env",
        extra="allow"
    )

gmx_config = GMXConfig() 