"use client"

import { Button } from "@/components/ui/button"
import { useWallet } from "../contexts/WalletContext"

export function WalletConnect() {
  const { walletAddress, connectWallet, isConnected } = useWallet()

  return (
    <div>
      {isConnected ? (
        <div className="flex items-center gap-2">
          <span className="text-sm text-gray-400">Connected:</span>
          <span className="text-sm font-medium">
            {walletAddress?.slice(0, 6)}...{walletAddress?.slice(-4)}
          </span>
        </div>
      ) : (
        <Button onClick={connectWallet} variant="outline" size="sm">
          Connect Wallet
        </Button>
      )}
    </div>
  )
}

