import "./globals.css"
import { Inter } from "next/font/google"
import { Providers } from "./providers"
import { Navbar } from "./components/Navbar"
import type React from "react" // Added import for React

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: "AI-Powered DeFi Trading Assistant",
  description: "Connect to GMX & Dexalot on Avalanche, receive AI-driven trade recommendations, and execute trades.",
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body className={`${inter.className} bg-gray-900 text-white`}>
        <Providers>
          <Navbar />
          <main className="container mx-auto px-4 py-8">{children}</main>
        </Providers>
      </body>
    </html>
  )
}

