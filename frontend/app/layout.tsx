import "./globals.css"
import { Inter } from "next/font/google"
import { Providers } from "./providers"
import { Navbar } from "./components/Navbar"
import { WalletProvider } from "./contexts/WalletContext"
import type React from "react" // Added import for React

const inter = Inter({ subsets: ["latin"] })

export const metadata = {
  title: "ETH_OX",
  description: "ETH_OX Trading Platform",
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
          <WalletProvider>
            <Navbar />
            <main className="container mx-auto px-4 py-8">{children}</main>
          </WalletProvider>
        </Providers>
      </body>
    </html>
  )
}

