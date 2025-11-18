-- ================================================
-- COMPANIES TABLE
-- ================================================
CREATE TABLE IF NOT EXISTS companies (
    symbol VARCHAR(20) PRIMARY KEY,
    name VARCHAR(255),
    exchange VARCHAR(50),
    industry VARCHAR(100),
    marketcap DECIMAL(20, 2),
    country VARCHAR(100),
    ipo DATE,
    weburl VARCHAR(500),
    logo VARCHAR(500),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_companies_marketcap ON companies(marketcap DESC);
CREATE INDEX idx_companies_industry ON companies(industry);

-- ================================================
-- QUOTES TABLE
-- ================================================
CREATE TABLE IF NOT EXISTS quotes (
    id SERIAL PRIMARY KEY,
    symbol VARCHAR(20) NOT NULL REFERENCES companies(symbol) ON DELETE CASCADE,
    current_price DECIMAL(12, 4),
    high_price DECIMAL(12, 4),
    low_price DECIMAL(12, 4),
    open_price DECIMAL(12, 4),
    prev_close DECIMAL(12, 4),
    change DECIMAL(12, 4),
    percent_change DECIMAL(8, 4),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_quotes_symbol ON quotes(symbol);
CREATE INDEX idx_quotes_timestamp ON quotes(timestamp DESC);
CREATE INDEX idx_quotes_symbol_timestamp ON quotes(symbol, timestamp DESC);

-- ================================================
-- FUNDAMENTALS TABLE
-- ================================================
CREATE TABLE IF NOT EXISTS fundamentals (
    symbol VARCHAR(20) PRIMARY KEY REFERENCES companies(symbol) ON DELETE CASCADE,
    metrics JSONB NOT NULL,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE INDEX idx_fundamentals_metrics ON fundamentals USING GIN(metrics);

-- ================================================
-- USEFUL VIEWS
-- ================================================

-- Latest quote for each stock
CREATE OR REPLACE VIEW latest_quotes AS
SELECT DISTINCT ON (symbol)
    symbol,
    current_price,
    change,
    percent_change,
    timestamp
FROM quotes
ORDER BY symbol, timestamp DESC;

-- Portfolio overview
CREATE OR REPLACE VIEW portfolio_view AS
SELECT 
    c.symbol,
    c.name,
    c.industry,
    c.marketcap,
    lq.current_price,
    lq.change,
    lq.percent_change,
    lq.timestamp as last_update
FROM companies c
LEFT JOIN latest_quotes lq ON c.symbol = lq.symbol
ORDER BY c.marketcap DESC;

-- ================================================
-- HELPER FUNCTIONS
-- ================================================

-- Get top/worst performers
CREATE OR REPLACE FUNCTION get_top_performers(limit_count INTEGER DEFAULT 5)
RETURNS TABLE(
    symbol VARCHAR(20),
    name VARCHAR(255),
    current_price DECIMAL(12, 4),
    percent_change DECIMAL(8, 4)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.symbol,
        c.name,
        lq.current_price,
        lq.percent_change
    FROM companies c
    INNER JOIN latest_quotes lq ON c.symbol = lq.symbol
    WHERE lq.percent_change IS NOT NULL
    ORDER BY lq.percent_change DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- ================================================
-- SAMPLE DATA QUERIES
-- ================================================

-- View your portfolio
-- SELECT * FROM portfolio_view;

-- Get top 5 gainers
-- SELECT * FROM get_top_performers(5);

-- Get historical prices for a stock
-- SELECT symbol, current_price, timestamp 
-- FROM quotes 
-- WHERE symbol = 'AAPL' 
-- ORDER BY timestamp DESC 
-- LIMIT 10;