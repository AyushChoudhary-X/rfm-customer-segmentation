-- 1. Customer Count Summary
-- Total customers, avg recency, avg frequency, avg monetary
SELECT 
    COUNT(CustomerID) AS Total_Customers,
    ROUND(AVG(Recency), 2) AS Avg_Recency,
    ROUND(AVG(Frequency), 2) AS Avg_Frequency,
    ROUND(AVG(Monetary), 2) AS Avg_Monetary
FROM rfm_values;

-- 2. Revenue by Country
-- Top 15 countries by total revenue
SELECT 
    Country,
    ROUND(SUM(TotalPrice), 2) AS Total_Revenue
FROM transactions
GROUP BY Country
ORDER BY Total_Revenue DESC
LIMIT 15;

-- 3. Monthly Revenue Trend
-- Revenue grouped by year-month
SELECT 
    DATE_FORMAT(InvoiceDate, '%Y-%m') AS Year_Month,
    ROUND(SUM(TotalPrice), 2) AS Monthly_Revenue
FROM transactions
GROUP BY Year_Month
ORDER BY Year_Month;

-- 4. Top 20 Customers by Revenue
-- CustomerID, total spend, order count
SELECT 
    CustomerID,
    ROUND(SUM(TotalPrice), 2) AS Total_Spend,
    COUNT(DISTINCT InvoiceNo) AS Order_Count
FROM transactions
GROUP BY CustomerID
ORDER BY Total_Spend DESC
LIMIT 20;

-- 5. Top 20 Best-Selling Products
-- StockCode, Description, total quantity sold, total revenue
SELECT 
    StockCode,
    MAX(Description) AS Description,
    SUM(Quantity) AS Total_Quantity_Sold,
    ROUND(SUM(TotalPrice), 2) AS Total_Revenue
FROM transactions
GROUP BY StockCode
ORDER BY Total_Quantity_Sold DESC
LIMIT 20;

-- 6. Segment Distribution
-- Count and percentage of customers in each segment
SELECT 
    Segment,
    COUNT(CustomerID) AS Customer_Count,
    ROUND(COUNT(CustomerID) * 100.0 / (SELECT COUNT(*) FROM customer_segments), 2) AS Percentage
FROM customer_segments
GROUP BY Segment
ORDER BY Customer_Count DESC;

-- 7. Average RFM by Segment
-- Mean R, F, M values per segment
SELECT 
    Segment,
    COUNT(CustomerID) AS Customer_Count,
    ROUND(AVG(Recency), 2) AS Avg_Recency,
    ROUND(AVG(Frequency), 2) AS Avg_Frequency,
    ROUND(AVG(Monetary), 2) AS Avg_Monetary
FROM customer_segments
GROUP BY Segment
ORDER BY Customer_Count DESC;

-- 8. Revenue Contribution by Segment
-- Total and percentage of revenue per segment
SELECT 
    Segment,
    ROUND(SUM(Monetary), 2) AS Total_Revenue,
    ROUND(SUM(Monetary) * 100.0 / (SELECT SUM(Monetary) FROM customer_segments), 2) AS Revenue_Percentage
FROM customer_segments
GROUP BY Segment
ORDER BY Total_Revenue DESC;

-- 9. Daily Transaction Volume
-- Number of orders per day
SELECT 
    DATE(InvoiceDate) AS Transaction_Date,
    COUNT(DISTINCT InvoiceNo) AS Total_Orders
FROM transactions
GROUP BY Transaction_Date
ORDER BY Transaction_Date;

-- 10. Customer Retention Cohort
-- First purchase month vs subsequent months
WITH FirstPurchase AS (
    SELECT 
        CustomerID,
        DATE_FORMAT(MIN(InvoiceDate), '%Y-%m-01') AS Cohort_Month
    FROM transactions
    GROUP BY CustomerID
)
SELECT 
    fp.Cohort_Month,
    DATE_FORMAT(t.InvoiceDate, '%Y-%m-01') AS Order_Month,
    COUNT(DISTINCT t.CustomerID) AS Customer_Count
FROM transactions t
JOIN FirstPurchase fp ON t.CustomerID = fp.CustomerID
GROUP BY fp.Cohort_Month, Order_Month
ORDER BY fp.Cohort_Month, Order_Month;

-- 11. Revenue by Day of Week
-- Which days generate most revenue
SELECT 
    DAYNAME(InvoiceDate) AS Day_Of_Week,
    DAYOFWEEK(InvoiceDate) AS Day_Index,
    ROUND(SUM(TotalPrice), 2) AS Total_Revenue
FROM transactions
GROUP BY Day_Of_Week, Day_Index
ORDER BY Day_Index;

-- 12. Returning vs One-Time Customers
-- Count split
WITH CustomerOrders AS (
    SELECT 
        CustomerID, 
        COUNT(DISTINCT InvoiceNo) AS Order_Count
    FROM transactions
    GROUP BY CustomerID
)
SELECT 
    CASE 
        WHEN Order_Count = 1 THEN 'One-Time'
        ELSE 'Returning'
    END AS Customer_Type,
    COUNT(CustomerID) AS Customer_Count,
    ROUND(COUNT(CustomerID) * 100.0 / (SELECT COUNT(*) FROM CustomerOrders), 2) AS Percentage
FROM CustomerOrders
GROUP BY Customer_Type;
