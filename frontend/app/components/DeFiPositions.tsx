"use client"

import { usePositions } from "@/hooks/use-positions"
import { Loader2 } from "lucide-react"
import { useWallet } from "../contexts/WalletContext"
import { Button } from "@/components/ui/button"

export function DeFiPositions() {
  const { isConnected } = useWallet()
  const { positions, isLoading, error, refreshPositions, clearPositions } = usePositions()

  if (!isConnected) {
    return (
      <div className="p-4 text-center text-gray-500">
        Connect your wallet to view positions
      </div>
    )
  }

  if (isLoading) {
    return (
      <div className="flex justify-center items-center p-4">
        <Loader2 className="h-6 w-6 animate-spin" />
      </div>
    )
  }

  if (error) {
    return (
      <div className="p-4 text-center text-red-500">
        Error loading positions: {error}
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex justify-end gap-2">
        <Button onClick={refreshPositions} size="sm" variant="outline">
          Refresh
        </Button>
        <Button onClick={clearPositions} size="sm" variant="outline">
          Clear All
        </Button>
      </div>

      {!positions || positions.length === 0 ? (
        <div className="p-4 text-center text-gray-500">
          No active positions
        </div>
      ) : (
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-700">
            <thead>
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Asset</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Entry Price</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Current Price</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">P&L</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-400 uppercase tracking-wider">Leverage</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-700">
              {positions.map((position) => (
                <tr key={position.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{position.asset}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">${position.entryPrice.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">${position.currentPrice.toFixed(2)}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{position.pnl}%</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm">{position.leverage}x</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}

