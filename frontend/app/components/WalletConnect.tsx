"use client"

import { useState, useEffect } from "react"

export function WalletConnect() {
  const [walletAddress, setWalletAddress] = useState<string | null>(null)

  useEffect(() => {
    checkIfWalletIsConnected()
  }, [])

  async function checkIfWalletIsConnected() {
    try {
      const { ethereum } = window as any
      if (ethereum) {
        const accounts = await ethereum.request({ method: "eth_accounts" })
        if (accounts.length > 0) {
          setWalletAddress(accounts[0])
        }
      }
    } catch (error) {
      console.error("Error checking wallet connection:", error)
    }
  }

  async function connectWallet() {
    try {
      const { ethereum } = window as any
      if (!ethereum) {
        alert("Please install MetaMask!")
        return
      }

      const accounts = await ethereum.request({ method: "eth_requestAccounts" })
      setWalletAddress(accounts[0])
    } catch (error) {
      console.error("Error connecting wallet:", error)
    }
  }

  return (
    <div>
      {walletAddress ? (
        <span className="text-sm">
          Connected: {walletAddress.slice(0, 6)}...{walletAddress.slice(-4)}
        </span>
      ) : (
        <button
          onClick={connectWallet}
          className="bg-blue-500 hover:bg-blue-600 text-white font-bold py-2 px-4 rounded"
        >
          Connect Wallet
        </button>
      )}
    </div>
  )
}

