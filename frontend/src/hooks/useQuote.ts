// frontend/src/hooks/useQuote.ts

import { useState, useEffect } from 'react';
import axios from 'axios';

// Type definition for the stock quote data received from the backend
interface StockQuote {
    symbol: string;
    name: string;
    price: number | null;
    changeAmount: number | null;
    changePercent: number | null;
    error?: string; // Optional error field for individual tickers
}

/**
 * Custom hook to fetch and periodically update stock quotes from the backend API.
 * @param tickers - An array of stock ticker symbols to fetch.
 * @returns An object containing the quotes data, loading state, and error message.
 */
const useQuotes = (tickers: string[]) => {
    const [quotes, setQuotes] = useState<StockQuote[]>([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState<string | null>(null);

    const fetchQuotes = async () => {
        if (tickers.length === 0) {
            setLoading(false);
            return;
        }

        // Set loading state before fetching
        setLoading(true);
        setError(null);
        
        // Construct the backend endpoint URL with tickers
        const url = `/api/markets/live-prices?tickers=${tickers.join(',')}`;

        try {
            // Make the API call to the Django backend
            const response = await axios.get<StockQuote[]>(url);
            setQuotes(response.data);
        } catch (err) {
            console.error("Failed to fetch quotes:", err);
            setError("Failed to retrieve stock data from the server.");
        } finally {
            // End loading state
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchQuotes(); // Initial data fetch on component mount

        // Set up periodic polling for real-time updates (e.g., every 10 seconds)
        // Note: Using a non-official API like yfinance requires careful rate limit management.
        const pollingInterval = 10000; // 10 seconds
        const intervalId = setInterval(fetchQuotes, pollingInterval); 

        // Cleanup function to clear the interval when the component unmounts
        return () => clearInterval(intervalId);
    }, [tickers.join(',')]); // Re-run effect if the list of tickers changes

    return { quotes, loading, error };
};

export default useQuotes;