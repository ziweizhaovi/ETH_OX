import { ChatInterface } from '@/components/chat/chat-interface';

export default function ChatPage() {
  return (
    <main className="container mx-auto py-8">
      <div className="max-w-4xl mx-auto">
        <h1 className="text-2xl font-bold mb-6">AI Trading Assistant</h1>
        <p className="text-muted-foreground mb-8">
          Chat with our AI assistant to help you trade AVAX and USDC. You can ask for:
          <ul className="list-disc list-inside mt-2 space-y-1">
            <li>Price analysis and market trends</li>
            <li>Execute trades between AVAX and USDC</li>
            <li>Position management advice</li>
            <li>Understanding fees and slippage</li>
          </ul>
        </p>
        <ChatInterface />
      </div>
    </main>
  );
} 