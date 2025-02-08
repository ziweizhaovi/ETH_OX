"use client"

import { useState } from "react"
import { DeFiPositions } from "./components/DeFiPositions"
import { AIRecommendations } from "./components/AIRecommendations"
import { TradeExecutionPanel } from "./components/TradeExecutionPanel"
import { AIChat } from "./components/AIChat"
import { TransactionHistory, type Transaction } from "./components/TransactionHistory"

export default function Home() {
  const [transactions, setTransactions] = useState<Transaction[]>([])

  const handleTradeExecuted = (newTransaction: Transaction) => {
    setTransactions((prev) => {
      const existingIndex = prev.findIndex((tx) => tx.id === newTransaction.id)
      if (existingIndex !== -1) {
        // Update existing transaction
        const updatedTransactions = [...prev]
        updatedTransactions[existingIndex] = newTransaction
        return updatedTransactions
      } else {
        // Add new transaction
        return [newTransaction, ...prev]
      }
    })
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-8">
          <DeFiPositions />
          <AIRecommendations />
        </div>
        <div className="space-y-8">
          <AIChat />
          <TradeExecutionPanel onTradeExecuted={handleTradeExecuted} />
        </div>
      </div>
      <TransactionHistory transactions={transactions} />
    </div>
  )
}

