"use client"

import { useState } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"

interface Position {
  id: string
  asset: string
  type: "LONG" | "SHORT"
  size: number
  entryPrice: number
  leverage: number
  pnl: number
  pnlPercentage: number
  liquidationPrice: number
}

const mockPositions: Position[] = [
  {
    id: "1",
    asset: "AVAX-USDC",
    type: "LONG",
    size: 1000,
    entryPrice: 35.5,
    leverage: 2,
    pnl: 150.25,
    pnlPercentage: 15.025,
    liquidationPrice: 17.75,
  },
  {
    id: "2",
    asset: "ETH-USDC",
    type: "SHORT",
    size: 2000,
    entryPrice: 3500,
    leverage: 3,
    pnl: -75.50,
    pnlPercentage: -3.775,
    liquidationPrice: 4375,
  },
]

export function DefiPosition() {
  const [positions] = useState<Position[]>(mockPositions)

  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>Active Positions</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {positions.map((position) => (
            <Card key={position.id} className="p-4 hover:bg-gray-50 transition-colors">
              <div className="flex justify-between items-start">
                <div>
                  <div className="flex items-center gap-2">
                    <h3 className="font-semibold text-lg">{position.asset}</h3>
                    <Badge variant={position.type === "LONG" ? "default" : "destructive"}>
                      {position.type}
                    </Badge>
                    <Badge variant="outline">{position.leverage}x</Badge>
                  </div>
                  <div className="mt-2 text-sm text-gray-600">
                    <div>Size: ${position.size.toLocaleString()}</div>
                    <div>Entry Price: ${position.entryPrice.toLocaleString()}</div>
                    <div>Liquidation Price: ${position.liquidationPrice.toLocaleString()}</div>
                  </div>
                </div>
                <div className={`text-right ${position.pnl >= 0 ? 'text-green-600' : 'text-red-600'}`}>
                  <div className="font-bold">${Math.abs(position.pnl).toLocaleString()}</div>
                  <div className="text-sm">{position.pnlPercentage.toFixed(2)}%</div>
                </div>
              </div>
            </Card>
          ))}
          {positions.length === 0 && (
            <div className="text-center text-gray-500 py-8">
              No active positions
            </div>
          )}
        </div>
      </CardContent>
    </Card>
  )
} 