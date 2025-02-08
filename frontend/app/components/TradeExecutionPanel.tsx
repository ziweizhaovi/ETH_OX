"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import type { Transaction } from "./TransactionHistory"

interface TradeExecutionPanelProps {
  onTradeExecuted: (transaction: Transaction) => void
}

export function TradeExecutionPanel({ onTradeExecuted }: TradeExecutionPanelProps) {
  const [asset, setAsset] = useState("AVAX")
  const [amount, setAmount] = useState("")
  const [stopLoss, setStopLoss] = useState("")
  const [aiAssisted, setAiAssisted] = useState(false)
  let newTransaction: Transaction // Declare newTransaction here

  async function executeTrade() {
    try {
      newTransaction = {
        // Assign value to newTransaction
        id: Date.now().toString(),
        state: "initiated",
        asset,
        amount,
        timestamp: new Date().toISOString(),
      }
      onTradeExecuted(newTransaction)

      // Simulate trade execution process
      await new Promise((resolve) => setTimeout(resolve, 2000))
      onTradeExecuted({ ...newTransaction, state: "in_progress" })

      if (aiAssisted) {
        // TODO: Implement AI-assisted trade execution
        console.log("Executing AI-assisted trade:", { asset, amount, stopLoss })
      } else {
        // TODO: Implement manual trade execution logic using ethers.js
        console.log("Executing manual trade:", { asset, amount, stopLoss })
      }

      // Simulate trade completion
      await new Promise((resolve) => setTimeout(resolve, 3000))
      onTradeExecuted({ ...newTransaction, state: "completed" })
    } catch (error) {
      console.error("Error executing trade:", error)
      onTradeExecuted({ ...newTransaction, state: "failed" })
    }
  }

  return (
    <Card>
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
            <Label htmlFor="asset">Asset</Label>
            <Select value={asset} onValueChange={setAsset}>
              <SelectTrigger id="asset">
                <SelectValue placeholder="Select asset" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="AVAX">AVAX</SelectItem>
                <SelectItem value="USDC">USDC</SelectItem>
              </SelectContent>
            </Select>
          </div>
          <div className="space-y-2">
            <Label htmlFor="amount">Amount</Label>
            <Input
              type="number"
              id="amount"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
              placeholder="Enter amount"
              required
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
        <Button onClick={executeTrade} className="w-full">
          {aiAssisted ? "Execute AI-Assisted Trade" : "Execute Manual Trade"}
        </Button>
      </CardFooter>
    </Card>
  )
}

