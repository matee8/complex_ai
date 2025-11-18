// frontend/src/components/StockCard.tsx (React/TypeScript/JSX)

import React from 'react';

// Type definition must match the data structure from useQuote.ts
interface StockQuote {
    symbol: string;
    name: string;
    price: number | null;
    changeAmount: number | null;
    changePercent: number | null;
    error?: string;
}

interface StockCardProps {
    quote: StockQuote;
}

const StockCard: React.FC<StockCardProps> = ({ quote }) => {
    if (quote.error) {
        return (
            // Display an error state card
            <div className="p-4 rounded-lg shadow-md w-64 bg-gray-200">
                <h3 className="text-xl font-bold text-gray-800">{quote.symbol}</h3>
                <p className="text-red-500 mt-2">Error: {quote.error}</p>
            </div>
        );
    }
    
    // Determine the color based on the price change (for styling)
    const isPositive = quote.changeAmount !== null && quote.changeAmount > 0;
    const isNegative = quote.changeAmount !== null && quote.changeAmount < 0;
    
    // Assign Tailwind CSS classes based on gain/loss
    const priceColor = isPositive ? 'text-green-600' : isNegative ? 'text-red-600' : 'text-gray-700';
    const bgColor = isPositive ? 'bg-green-50' : isNegative ? 'bg-red-50' : 'bg-white';

    // Format the change amount with a sign (+/-)
    const formatChangeAmount = (amount: number | null): string => {
        if (amount === null) return '---';
        const formatted = amount.toFixed(2);
        return amount > 0 ? `+${formatted}` : formatted;
    };

    // Format the change percentage with a sign (+/-)
    const formatChangePercent = (percent: number | null): string => {
        if (percent === null) return '---';
        const formatted = percent.toFixed(2);
        return percent > 0 ? `+${formatted}%` : `${formatted}%`;
    };

    return (
        <div className={`p-4 rounded-xl shadow-lg border ${bgColor} transition duration-300 hover:shadow-xl`}>
            <h2 className="text-2xl font-extrabold text-gray-800">{quote.symbol}</h2>
            <p className="text-md text-gray-500 truncate">{quote.name}</p>
            
            <div className="mt-3">
                {/* Current Price */}
                <p className={`text-4xl font-bold ${priceColor}`}>
                    {quote.price !== null ? `$${quote.price.toFixed(2)}` : '---'}
                </p>
                {/* Change Metrics */}
                <div className="flex justify-start items-center space-x-4 text-lg mt-2">
                    <span className={`font-semibold ${priceColor}`}>
                        {formatChangeAmount(quote.changeAmount)}
                    </span>
                    <span className={`font-medium ${priceColor}`}>
                        ({formatChangePercent(quote.changePercent)})
                    </span>
                </div>
            </div>
        </div>
    );
};

export default StockCard;