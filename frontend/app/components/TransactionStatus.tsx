import { CheckCircle, Clock, AlertTriangle } from "lucide-react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export type TransactionState = "initiated" | "in_progress" | "completed" | "failed"

interface TransactionStatusProps {
  state: TransactionState
  asset: string
  amount: string
  timestamp: string
}

export function TransactionStatus({ state, asset, amount, timestamp }: TransactionStatusProps) {
  const getStatusColor = (state: TransactionState) => {
    switch (state) {
      case "initiated":
        return "text-blue-400"
      case "in_progress":
        return "text-yellow-400"
      case "completed":
        return "text-green-400"
      case "failed":
        return "text-red-400"
      default:
        return "text-gray-400"
    }
  }

  const getStatusIcon = (state: TransactionState) => {
    switch (state) {
      case "initiated":
        return <Clock className="h-6 w-6" />
      case "in_progress":
        return <Clock className="h-6 w-6 animate-spin" />
      case "completed":
        return <CheckCircle className="h-6 w-6" />
      case "failed":
        return <AlertTriangle className="h-6 w-6" />
      default:
        return null
    }
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <span>Transaction Status</span>
          <span className={`flex items-center ${getStatusColor(state)}`}>
            {getStatusIcon(state)}
            <span className="ml-2 capitalize">{state.replace("_", " ")}</span>
          </span>
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p>
          <strong>Asset:</strong> {asset}
        </p>
        <p>
          <strong>Amount:</strong> {amount}
        </p>
        <p>
          <strong>Timestamp:</strong> {timestamp}
        </p>
      </CardContent>
    </Card>
  )
}

