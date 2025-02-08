"use client"

import { useState } from "react"

export default function Settings() {
  const [autoExecute, setAutoExecute] = useState(false)
  const [preferredExchange, setPreferredExchange] = useState("GMX")

  const handleSave = () => {
    // TODO: Implement saving settings to backend or local storage
    console.log("Saving settings:", { autoExecute, preferredExchange })
    alert("Settings saved successfully!")
  }

  return (
    <div className="space-y-8">
      <h1 className="text-3xl font-bold">Settings</h1>

      <div className="space-y-4">
        <div>
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={autoExecute}
              onChange={(e) => setAutoExecute(e.target.checked)}
              className="form-checkbox h-5 w-5 text-blue-600"
            />
            <span>Auto-Execute Trades</span>
          </label>
          <p className="text-sm text-gray-400 mt-1">Allow AI to automatically execute trades based on risk level</p>
        </div>

        <div>
          <label className="block mb-2">Preferred Exchange</label>
          <select
            value={preferredExchange}
            onChange={(e) => setPreferredExchange(e.target.value)}
            className="w-full bg-gray-700 rounded px-3 py-2"
          >
            <option value="GMX">GMX</option>
            <option value="Dexalot">Dexalot</option>
          </select>
        </div>

        <button onClick={handleSave} className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded">
          Save Settings
        </button>
      </div>
    </div>
  )
}

