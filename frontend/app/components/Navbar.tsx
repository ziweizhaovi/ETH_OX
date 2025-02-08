"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { WalletConnect } from "./WalletConnect"

export function Navbar() {
  const pathname = usePathname()

  return (
    <nav className="bg-gray-800 p-4">
      <div className="container mx-auto flex justify-between items-center">
        <div className="flex space-x-4">
          <Link href="/" className={`${pathname === "/" ? "text-blue-400" : "text-white"} hover:text-blue-300`}>
            Dashboard
          </Link>
          <Link
            href="/insights"
            className={`${pathname === "/insights" ? "text-blue-400" : "text-white"} hover:text-blue-300`}
          >
            AI Insights
          </Link>
          <Link
            href="/settings"
            className={`${pathname === "/settings" ? "text-blue-400" : "text-white"} hover:text-blue-300`}
          >
            Settings
          </Link>
        </div>
        <WalletConnect />
      </div>
    </nav>
  )
}

