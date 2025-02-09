"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"

interface Transaction {
  id: string
  state: "initiated" | "in_progress" | "completed" | "failed"
  asset: string
  amount: string
  timestamp: string
  type: "LONG" | "SHORT"
}

interface TradeExecutionPanelProps {
  onTradeExecuted: (transaction: Transaction) => void
}

export function TradeExecutionPanel({ onTradeExecuted }: TradeExecutionPanelProps) {
  const [asset, setAsset] = useState("AVAX")
  const [amount, setAmount] = useState("")
  const [stopLoss, setStopLoss] = useState("")
  const [aiAssisted, setAiAssisted] = useState(false)
  const [isLoading, setIsLoading] = useState(false)
  const [tradeType, setTradeType] = useState<"LONG" | "SHORT">("LONG")
  let newTransaction: Transaction

  async function executeTrade() {
    try {
      setIsLoading(true)
      newTransaction = {
        id: Date.now().toString(),
        state: "initiated",
        asset,
        amount,
        timestamp: new Date().toISOString(),
        type: tradeType,
      }
      onTradeExecuted(newTransaction)

      // Simulate API call to backend
      const response = await fetch('/api/trade', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          asset,
          amount: parseFloat(amount),
          stopLoss: parseFloat(stopLoss),
          isAiAssisted: aiAssisted,
          type: tradeType,
        }),
      });

      if (!response.ok) {
        throw new Error('Trade execution failed');
      }

      onTradeExecuted({ ...newTransaction, state: "completed" })
    } catch (error) {
      console.error("Error executing trade:", error)
      onTradeExecuted({ ...newTransaction, state: "failed" })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <Card className="w-full max-w-md mx-auto">
      <CardHeader>
        <CardTitle>Execute Trade</CardTitle>
      </CardHeader>
      <CardContent>
        <form
          onSubmit={(e) => {
            e.preventDefault()
            executeTrade()
          }}
          className="space-y-4"
        >
          <div className="space-y-2">
            <Label htmlFor="asset">Trading Pair</Label>
            <Select value={asset} onValueChange={setAsset}>
              <SelectTrigger id="asset">
                <SelectValue placeholder="Select trading pair" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="AVAX">AVAX-USDC</SelectItem>
                <SelectItem value="ETH">ETH-USDC</SelectItem>
                <SelectItem value="BTC">BTC-USDC</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="tradeType">Position Type</Label>
            <Select value={tradeType} onValueChange={(value: "LONG" | "SHORT") => setTradeType(value)}>
              <SelectTrigger id="tradeType">
                <SelectValue placeholder="Select position type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="LONG">Long</SelectItem>
                <SelectItem value="SHORT">Short</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div className="space-y-2">
            <Label htmlFor="amount">Size (USDC)</Label>
            <Input
              type="number"
              id="amount"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="Enter position size"
              required
              min="0"
              step="0.01"
            />
          </div>

          <div className="space-y-2">
            <Label htmlFor="stopLoss">Stop-Loss Price</Label>
            <Input
              type="number"
              id="stopLoss"
              value={stopLoss}
              onChange={(e) => setStopLoss(e.target.value)}
              placeholder="Enter stop-loss price"
              required
              min="0"
              step="0.01"
            />
          </div>

          <div className="flex items-center space-x-2">
            <input
              type="checkbox"
              id="aiAssisted"
              checked={aiAssisted}
              onChange={(e) => setAiAssisted(e.target.checked)}
              className="form-checkbox h-4 w-4 text-blue-600"
            />
            <Label htmlFor="aiAssisted">AI-Assisted Execution</Label>
          </div>
        </form>
      </CardContent>
      <CardFooter>
        <Button 
          onClick={executeTrade} 
          className="w-full" 
          disabled={isLoading}
        >
          {isLoading ? "Executing Trade..." : (aiAssisted ? "Execute AI-Assisted Trade" : "Execute Manual Trade")}
        </Button>
      </CardFooter>
    </Card>
  )
}

