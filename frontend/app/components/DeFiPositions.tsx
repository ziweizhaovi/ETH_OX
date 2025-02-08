"use client"

import { useState, useEffect } from "react"

interface Position {
  id: string
  asset: string
  entryPrice: number
  currentPrice: number
  pnl: number
  leverage: number
}

export function DeFiPositions() {
  const [positions, setPositions] = useState<Position[]>([])

  useEffect(() => {
    // TODO: Fetch real data from GMX & Dexalot
    const mockPositions: Position[] = [
      { id: "1", asset: "AVAX", entryPrice: 15.5, currentPrice: 16.2, pnl: 4.52, leverage: 2 },
      { id: "2", asset: "USDC", entryPrice: 1, currentPrice: 1, pnl: 0, leverage: 1 },
    ]
    setPositions(mockPositions)
  }, [])

  return (
    <div>
      <h2 className="text-2xl font-semibold mb-4">DeFi Positions</h2>
      <div className="overflow-x-auto">
        <table className="min-w-full bg-gray-800 rounded-lg overflow-hidden">
          <thead className="bg-gray-700">
            <tr>
              <th className="px-4 py-2">Asset</th>
              <th className="px-4 py-2">Entry Price</th>
              <th className="px-4 py-2">Current Price</th>
              <th className="px-4 py-2">P&L</th>
              <th className="px-4 py-2">Leverage</th>
            </tr>
          </thead>
          <tbody>
            {positions.map((position) => (
              <tr key={position.id} className="border-b border-gray-700">
                <td className="px-4 py-2">{position.asset}</td>
                <td className="px-4 py-2">${position.entryPrice.toFixed(2)}</td>
                <td className="px-4 py-2">${position.currentPrice.toFixed(2)}</td>
                <td className={`px-4 py-2 ${position.pnl >= 0 ? "text-green-400" : "text-red-400"}`}>
                  {position.pnl.toFixed(2)}%
                </td>
                <td className="px-4 py-2">{position.leverage}x</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

