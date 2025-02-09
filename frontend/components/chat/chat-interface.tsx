"use client"

import { useState } from "react"
import { usePositions } from "@/hooks/use-positions"
import { useWallet } from "@/app/contexts/WalletContext"
import { Button } from "@/components/ui/button"
import { Input } from "@/components/ui/input"
import { Message } from "@/types/chat"

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState("")
  const [isLoading, setIsLoading] = useState(false)
  const [isExecutingTrade, setIsExecutingTrade] = useState(false)
  const { refreshPositions } = usePositions()
  const { walletAddress, isConnected } = useWallet()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading || isExecutingTrade) return

    const userMessage: Message = {
      role: "user",
      content: input,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput("")
    setIsLoading(true)

    try {
      // Check if this is a trade confirmation
      const lastMessage = messages[messages.length - 1]
      if (lastMessage?.content.includes("Would you like to execute this trade?") && input.toLowerCase() === "yes") {
        setIsExecutingTrade(true)
        const response = await fetch(`${API_BASE_URL}/api/ai_agent/execute-trade`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: messages[messages.length - 2].content, // Get the original trade request
            wallet_address: walletAddress,
          }),
        });

        if (!response.ok) {
          const errorData = await response.text();
          throw new Error(`Failed to execute trade: ${errorData}`);
        }

        await refreshPositions()
        const confirmationMessage: Message = {
          role: "assistant",
          content: "Trade executed successfully.",
        }
        setMessages((prev) => [...prev, confirmationMessage])
      } else {
        // Send message to AI agent
        console.log("Sending message to AI:", input);
        const response = await fetch(`${API_BASE_URL}/api/ai_agent/chat`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          body: JSON.stringify({
            message: input,
            wallet_address: walletAddress,
          }),
        });

        if (!response.ok) {
          const errorData = await response.text();
          console.error("API Error:", {
            status: response.status,
            statusText: response.statusText,
            error: errorData
          });
          throw new Error(`Failed to get AI response: ${errorData}`);
        }

        const data = await response.json();
        console.log("AI Response:", data);
        const aiMessage: Message = {
          role: "assistant",
          content: data.response,
        }
        setMessages((prev) => [...prev, aiMessage])
      }
    } catch (error) {
      console.error("Error:", error);
      const errorMessage: Message = {
        role: "assistant",
        content: error instanceof Error ? error.message : "Sorry, there was an error processing your request. Please try again.",
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
      setIsExecutingTrade(false)
    }
  }

  if (!isConnected) {
    return (
      <div className="p-4 text-center text-gray-500">
        Connect your wallet to start trading
      </div>
    )
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {messages.map((message, index) => (
          <div
            key={index}
            className={`flex ${
              message.role === "user" ? "justify-end" : "justify-start"
            }`}
          >
            <div
              className={`max-w-[80%] rounded-lg px-4 py-2 ${
                message.role === "user"
                  ? "bg-blue-600 text-white"
                  : "bg-gray-700 text-gray-100"
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}
      </div>
      <form onSubmit={handleSubmit} className="p-4 border-t border-gray-700">
        <div className="flex gap-2">
          <Input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            placeholder="Type your message..."
            disabled={isLoading || isExecutingTrade}
          />
          <Button type="submit" disabled={isLoading || isExecutingTrade}>
            {isLoading ? "Sending..." : isExecutingTrade ? "Executing..." : "Send"}
          </Button>
        </div>
      </form>
    </div>
  )
} 