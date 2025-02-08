"use client"

import { ChatInterface } from "@/components/chat/chat-interface"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

export function AIChat() {
  return (
    <Card className="w-full">
      <CardHeader>
        <CardTitle>AI Trading Assistant</CardTitle>
      </CardHeader>
      <CardContent>
        <ChatInterface />
      </CardContent>
    </Card>
  )
}

