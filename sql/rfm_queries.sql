-- Script to calculate RFM values from the transactions table

-- Step 1: Truncate existing data to maintain idempotency
TRUNCATE TABLE rfm_values;

-- Step 2: Insert raw Recency, Frequency, and Monetary metrics.
-- Recency is calculated as the difference in days between the reference date (max invoice date + 1 day) and the customer's last invoice date.
-- Frequency is the count of distinct invoices.
-- Monetary is the sum of total prices for all transactions for a customer, filtering out customers with <= 0 total spend.
INSERT INTO rfm_values (CustomerID, Recency, Frequency, Monetary, LastPurchaseDate)
SELECT 
    CustomerID,
    DATEDIFF(
        (SELECT DATE_ADD(MAX(DATE(InvoiceDate)), INTERVAL 1 DAY) FROM transactions),
        MAX(DATE(InvoiceDate))
    ) AS Recency,
    COUNT(DISTINCT InvoiceNo) AS Frequency,
    ROUND(SUM(TotalPrice), 2) AS Monetary,
    MAX(DATE(InvoiceDate)) AS LastPurchaseDate
FROM transactions
GROUP BY CustomerID
HAVING Monetary > 0;
