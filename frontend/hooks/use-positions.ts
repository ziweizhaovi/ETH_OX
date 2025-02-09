import { useState, useEffect } from 'react';

export interface Position {
  id: string;
  asset: string;
  entryPrice: number;
  currentPrice: number;
  pnl: number;
  leverage: number;
}

export function usePositions() {
  const [positions, setPositions] = useState<Position[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchPositions = async () => {
    setIsLoading(true);
    setError(null);
    try {
      // First try to add a mock position if none exist
      const mockPosition = {
        type: 'long',
        entryPrice: 25.0,
        currentPrice: 26.5,
        pnl: 6.0,
        leverage: 5.0
      };

      await fetch('/api/v1/positions/mock/add', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(mockPosition),
      });

      // Then fetch all positions
      const response = await fetch('/api/v1/positions');
      if (!response.ok) {
        throw new Error('Failed to fetch positions');
      }
      const data = await response.json();
      setPositions(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch positions');
      console.error('Error fetching positions:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchPositions();
    // Set up polling for position updates
    const interval = setInterval(fetchPositions, 10000); // Update every 10 seconds
    return () => clearInterval(interval);
  }, []);

  const clearPositions = async () => {
    try {
      await fetch('/api/v1/positions/mock/clear', {
        method: 'POST'
      });
      await fetchPositions();
    } catch (err) {
      console.error('Error clearing positions:', err);
    }
  };

  return {
    positions,
    isLoading,
    error,
    refreshPositions: fetchPositions,
    clearPositions
  };
} 