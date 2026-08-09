-- DDL Script to create tables for RFM Analysis Project
-- Uses InnoDB engine and utf8mb4 charset

-- Table: transactions
-- Stores raw transaction data imported from source.
-- Contains invoice details, product info, customer ID, and calculated total price.
CREATE TABLE IF NOT EXISTS transactions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    InvoiceNo VARCHAR(20),
    StockCode VARCHAR(20),
    Description TEXT,
    Quantity INT,
    InvoiceDate DATETIME,
    UnitPrice DECIMAL(10,2),
    CustomerID INT,
    Country VARCHAR(50),
    TotalPrice DECIMAL(12,2),
    INDEX idx_customer (CustomerID),
    INDEX idx_invoice_date (InvoiceDate),
    INDEX idx_invoice_no (InvoiceNo)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: rfm_values 
-- Stores raw Recency, Frequency, and Monetary values calculated per customer.
-- Recency: Days since last purchase.
-- Frequency: Total number of purchases.
-- Monetary: Total money spent.
CREATE TABLE IF NOT EXISTS rfm_values (
    CustomerID INT PRIMARY KEY,
    Recency INT,
    Frequency INT,
    Monetary DECIMAL(12,2),
    LastPurchaseDate DATE,
    INDEX idx_recency (Recency),
    INDEX idx_frequency (Frequency)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: rfm_scores
-- Stores the scored (e.g., 1 to 5) R, F, M components and the combined RFM score string and total.
CREATE TABLE IF NOT EXISTS rfm_scores (
    CustomerID INT PRIMARY KEY,
    Recency INT,
    Frequency INT,
    Monetary DECIMAL(12,2),
    R_Score INT,
    F_Score INT,
    M_Score INT,
    RFM_Score VARCHAR(5),
    RFM_Total INT,
    INDEX idx_rfm_score (RFM_Score),
    INDEX idx_rfm_total (RFM_Total)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: customer_segments
-- Stores the final customer segmentation mapped from the RFM scores.
CREATE TABLE IF NOT EXISTS customer_segments (
    CustomerID INT PRIMARY KEY,
    R_Score INT,
    F_Score INT,
    M_Score INT,
    RFM_Score VARCHAR(5),
    RFM_Total INT,
    Recency INT,
    Frequency INT,
    Monetary DECIMAL(12,2),
    Segment VARCHAR(50),
    INDEX idx_segment (Segment)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
