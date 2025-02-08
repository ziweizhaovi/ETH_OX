"use client"

import { useState, useEffect } from "react"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

interface Recommendation {
  id: string
  asset: string
  stopLoss: number
  takeProfit: number
  riskLevel: "High" | "Medium" | "Low"
  reasoning: string
}

export function AIRecommendations() {
  const [recommendations, setRecommendations] = useState<Recommendation[]>([])

  useEffect(() => {
    // TODO: Fetch real AI recommendations
    const mockRecommendations: Recommendation[] = [
      {
        id: "1",
        asset: "AVAX",
        stopLoss: 14.5,
        takeProfit: 17.5,
        riskLevel: "Medium",
        reasoning:
          "Based on recent market trends and volatility analysis, AVAX shows potential for growth but with moderate risk.",
      },
      {
        id: "2",
        asset: "USDC",
        stopLoss: 0.99,
        takeProfit: 1.01,
        riskLevel: "Low",
        reasoning:
          "USDC is a stablecoin with minimal price fluctuations, making it a low-risk option for capital preservation.",
      },
    ]
    setRecommendations(mockRecommendations)
  }, [])

  return (
    <Card>
      <CardHeader>
        <CardTitle>AI Recommendations</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="space-y-4">
          {recommendations.map((rec) => (
            <Card key={rec.id}>
              <CardHeader>
                <CardTitle>{rec.asset}</CardTitle>
              </CardHeader>
              <CardContent>
                <p>Recommended Stop-Loss: ${rec.stopLoss.toFixed(2)}</p>
                <p>Take Profit: ${rec.takeProfit.toFixed(2)}</p>
                <p
                  className={`font-bold ${
                    rec.riskLevel === "High"
                      ? "text-red-400"
                      : rec.riskLevel === "Medium"
                        ? "text-yellow-400"
                        : "text-green-400"
                  }`}
                >
                  Risk Level: {rec.riskLevel}
                </p>
                <p className="mt-2 text-sm text-gray-400">{rec.reasoning}</p>
              </CardContent>
            </Card>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

