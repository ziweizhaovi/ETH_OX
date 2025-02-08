"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { TransactionStatus, type TransactionState } from "./TransactionStatus"

export interface Transaction {
  id: string
  state: TransactionState
  asset: string
  amount: string
  timestamp: string
}

interface TransactionHistoryProps {
  transactions: Transaction[]
}

export function TransactionHistory({ transactions }: TransactionHistoryProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Transaction History</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {transactions.length === 0 ? (
            <p>No transactions yet.</p>
          ) : (
            transactions.map((tx) => (
              <TransactionStatus
                key={tx.id}
                state={tx.state}
                asset={tx.asset}
                amount={tx.amount}
                timestamp={tx.timestamp}
              />
            ))
          )}
        </div>
      </CardContent>
    </Card>
  )
}

