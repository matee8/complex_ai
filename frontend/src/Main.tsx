// frontend/src/App.tsx

import React from 'react';
import useQuotes from './hooks/useQuote.ts';
import StockCard from './components/StockCard.tsx';

// List of tickers to display (can be stored in a separate config or fetched from another API later)
const STOCKS_TO_DISPLAY = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "META"
];

const Main: React.FC = () => {
    // Assuming Authentication is handled and user is logged in

    // Fetch stock data using the custom hook
    const { quotes, loading, error } = useQuotes(STOCKS_TO_DISPLAY);

    return (
        <div className="min-h-screen bg-gray-50 p-8">
            <h1 className="text-4xl font-extrabold text-gray-900 mb-8 border-b pb-2">
                Live Market Overview
            </h1>

            {/* ローディング中の表示 */}
            {loading && (
                <div className="flex justify-center items-center h-48">
                    <p className="text-xl text-gray-600">Loading real-time stock data...</p>
                </div>
            )}

            {/* エラー表示 */}
            {error && (
                <p className="text-xl text-red-600 bg-red-100 p-4 rounded-lg">
                    Data Fetch Error: {error}
                </p>
            )}

            {/* ↓↓↓ メインの株価カードグリッド ↓↓↓ */}
            {!loading && !error && (
                <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-6">
                    {quotes.map((quote) => (
                        <StockCard key={quote.symbol} quote={quote} />
                    ))}
                </div>
            )}
        </div>
    );
};

export default Main;