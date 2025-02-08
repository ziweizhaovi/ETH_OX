"use client"

import { useState, useEffect } from "react"

interface Insight {
  id: string
  date: string
  asset: string
  recommendation: string
  riskLevel: "High" | "Medium" | "Low"
}

export default function Insights() {
  const [insights, setInsights] = useState<Insight[]>([])
  const [filter, setFilter] = useState({ asset: "", riskLevel: "", date: "" })

  useEffect(() => {
    // TODO: Fetch real AI insights
    const mockInsights: Insight[] = [
      { id: "1", date: "2023-05-01", asset: "AVAX", recommendation: "Buy", riskLevel: "Medium" },
      { id: "2", date: "2023-05-02", asset: "USDC", recommendation: "Hold", riskLevel: "Low" },
      { id: "3", date: "2023-05-03", asset: "AVAX", recommendation: "Sell", riskLevel: "High" },
    ]
    setInsights(mockInsights)
  }, [])

  const filteredInsights = insights.filter(
    (insight) =>
      (!filter.asset || insight.asset === filter.asset) &&
      (!filter.riskLevel || insight.riskLevel === filter.riskLevel) &&
      (!filter.date || insight.date === filter.date),
  )

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">AI Insights</h1>

      <div className="flex space-x-4">
        <select
          value={filter.asset}
          onChange={(e) => setFilter({ ...filter, asset: e.target.value })}
          className="bg-gray-700 rounded px-3 py-2"
        >
          <option value="">All Assets</option>
          <option value="AVAX">AVAX</option>
          <option value="USDC">USDC</option>
        </select>
        <select
          value={filter.riskLevel}
          onChange={(e) => setFilter({ ...filter, riskLevel: e.target.value })}
          className="bg-gray-700 rounded px-3 py-2"
        >
          <option value="">All Risk Levels</option>
          <option value="High">High</option>
          <option value="Medium">Medium</option>
          <option value="Low">Low</option>
        </select>
        <input
          type="date"
          value={filter.date}
          onChange={(e) => setFilter({ ...filter, date: e.target.value })}
          className="bg-gray-700 rounded px-3 py-2"
        />
      </div>

      <div className="space-y-4">
        {filteredInsights.map((insight) => (
          <div key={insight.id} className="bg-gray-800 p-4 rounded-lg border border-gray-700">
            <p className="text-sm text-gray-400">{insight.date}</p>
            <h3 className="text-xl font-semibold">{insight.asset}</h3>
            <p>Recommendation: {insight.recommendation}</p>
            <p
              className={`font-bold ${
                insight.riskLevel === "High"
                  ? "text-red-400"
                  : insight.riskLevel === "Medium"
                    ? "text-yellow-400"
                    : "text-green-400"
              }`}
            >
              Risk Level: {insight.riskLevel}
            </p>
          </div>
        ))}
      </div>
    </div>
  )
}

