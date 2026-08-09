#!/usr/bin/env python3
"""
Step 3: RFM Scoring
This script calculates RFM scores (1-5) using quintiles based on the raw RFM values.
It handles duplicate bin edges gracefully, combines the scores into an RFM_Score string
and RFM_Total numeric value, saves the results to CSV, and updates the database.
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
from pathlib import Path

DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'unix_socket': '/tmp/mysql.sock',
    'database': 'rfm_analytics'
}

def get_rfm_values_from_db():
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        query = "SELECT * FROM rfm_values"
        df = pd.read_sql(query, conn)
        return df, conn
    except Error as e:
        print(f"Database error: {e}")
        return None, None

def assign_score(series, labels, reverse=False):
    """
    Assigns scores based on quintiles. Handles duplicate edges by dropping duplicates
    and using rank if necessary.
    """
    try:
        return pd.qcut(series, q=5, labels=labels, duplicates='drop')
    except ValueError:
        # Fallback using rank if qcut fails due to too many duplicates
        ranks = series.rank(method='first', ascending=not reverse)
        return pd.qcut(ranks, q=5, labels=labels)

def main():
    project_root = Path(__file__).resolve().parent.parent
    processed_dir = project_root / 'data' / 'processed'
    rfm_scores_path = processed_dir / 'rfm_scores.csv'
    
    print("Fetching RFM values from database...")
    df, conn = get_rfm_values_from_db()
    
    if df is None or df.empty:
        print("Error: No data retrieved from rfm_values table.")
        return
        
    print("Calculating RFM scores using quintiles...")
    
    # R score: 1-5 (lowest recency = 5) -> reversed
    df['R_Score'] = assign_score(df['Recency'], labels=[5, 4, 3, 2, 1], reverse=True).astype(int)
    
    # F score: 1-5 (highest frequency = 5)
    df['F_Score'] = assign_score(df['Frequency'], labels=[1, 2, 3, 4, 5]).astype(int)
    
    # M score: 1-5 (highest monetary = 5)
    df['M_Score'] = assign_score(df['Monetary'], labels=[1, 2, 3, 4, 5]).astype(int)
    
    # Create RFM_Score string and RFM_Total
    df['RFM_Score'] = df['R_Score'].astype(str) + df['F_Score'].astype(str) + df['M_Score'].astype(str)
    df['RFM_Total'] = df['R_Score'] + df['F_Score'] + df['M_Score']
    
    print("\n--- Score Distribution Summary ---")
    print("R_Score counts:")
    print(df['R_Score'].value_counts().sort_index())
    print("\nF_Score counts:")
    print(df['F_Score'].value_counts().sort_index())
    print("\nM_Score counts:")
    print(df['M_Score'].value_counts().sort_index())
    print("----------------------------------\n")
    
    print(f"Saving RFM scores to {rfm_scores_path}...")
    processed_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(rfm_scores_path, index=False)
    
    if conn and conn.is_connected():
        cursor = conn.cursor()
        print("Updating rfm_scores table in database...")
        # Create table if not exists
        create_table_sql = """
        CREATE TABLE IF NOT EXISTS rfm_scores (
            CustomerID INT PRIMARY KEY,
            Recency INT,
            Frequency INT,
            Monetary DECIMAL(10,2),
            R_Score INT,
            F_Score INT,
            M_Score INT,
            RFM_Score VARCHAR(5),
            RFM_Total INT
        )
        """
        cursor.execute(create_table_sql)
        
        # Truncate and insert
        cursor.execute("TRUNCATE TABLE rfm_scores")
        
        insert_query = """
        INSERT INTO rfm_scores (CustomerID, Recency, Frequency, Monetary, R_Score, F_Score, M_Score, RFM_Score, RFM_Total)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Prepare data
        records = list(df[['CustomerID', 'Recency', 'Frequency', 'Monetary', 
                          'R_Score', 'F_Score', 'M_Score', 'RFM_Score', 'RFM_Total']].itertuples(index=False, name=None))
                          
        # Batch insert
        batch_size = 10000
        for i in range(0, len(records), batch_size):
            cursor.executemany(insert_query, records[i:i + batch_size])
        
        conn.commit()
        cursor.close()
        conn.close()
        print("Database update completed.")

if __name__ == "__main__":
    main()
