#!/usr/bin/env python3
"""
Step 4: Customer Segmentation
This script categorizes customers into descriptive segments based on their RFM scores.
It assigns segments using a priority-based rule system, saves the results to CSV, 
and updates the customer_segments table in the database.
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

def assign_segment(row):
    R, F, M = row['R_Score'], row['F_Score'], row['M_Score']
    
    # Priority-based assignments
    if R == 1 and F == 1 and M == 1:
        return 'Lost'
    if R <= 2 and F >= 4 and M >= 4:
        return "Can't Lose Them"
    if R >= 4 and F >= 4 and M >= 4:
        return 'Champions'
    if R >= 4 and F == 1 and M == 1:
        return 'Recent Customers'
        
    # Broader categories
    if R >= 3 and F >= 3 and M >= 3:
        return 'Loyal Customers'
    if R >= 3 and F >= 1 and M >= 1:
        # Avoid overriding specific low-F/M
        if R >= 4 and F == 1 and M == 1:
            return 'Recent Customers'
        if R >= 3 and F <= 2 and M <= 2:
            return 'Promising'
        return 'Potential Loyalists'
        
    if R >= 3 and F <= 2 and M <= 2:
        return 'Promising'
        
    if R >= 2 and F >= 2 and M >= 2 and (R <= 3 and F <= 3 and M <= 3):
        return 'Need Attention'
        
    if (R == 2 or R == 3) and F <= 2 and M <= 2:
        return 'About to Sleep'
        
    if R <= 2 and F >= 3 and M >= 3:
        return 'At Risk'
        
    if R <= 2 and F <= 2 and M <= 2:
        return 'Hibernating'
        
    return 'Other'

def main():
    project_root = Path(__file__).resolve().parent.parent
    processed_dir = project_root / 'data' / 'processed'
    rfm_scores_path = processed_dir / 'rfm_scores.csv'
    segments_path = processed_dir / 'rfm_segments.csv'
    
    print(f"Loading RFM scores from {rfm_scores_path}...")
    if not rfm_scores_path.exists():
        print(f"Error: File not found {rfm_scores_path}")
        return
        
    df = pd.read_csv(rfm_scores_path)
    
    print("Assigning customer segments...")
    df['Segment'] = df.apply(assign_segment, axis=1)
    
    print("\n--- Segment Distribution ---")
    segment_counts = df['Segment'].value_counts()
    segment_pcts = df['Segment'].value_counts(normalize=True) * 100
    
    dist_df = pd.DataFrame({
        'Count': segment_counts,
        'Percentage (%)': segment_pcts.round(2)
    })
    print(dist_df)
    print("----------------------------\n")
    
    print(f"Saving segments to {segments_path}...")
    df.to_csv(segments_path, index=False)
    
    print("Updating customer_segments table in MySQL...")
    try:
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Truncate and insert (table already created by 02_create_database.py)
        cursor.execute("TRUNCATE TABLE customer_segments")
        
        insert_query = """
        INSERT INTO customer_segments 
            (CustomerID, R_Score, F_Score, M_Score, RFM_Score, RFM_Total, Recency, Frequency, Monetary, Segment)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        records = list(df[['CustomerID', 'R_Score', 'F_Score', 'M_Score', 'RFM_Score', 
                           'RFM_Total', 'Recency', 'Frequency', 'Monetary', 'Segment']].itertuples(index=False, name=None))
        
        batch_size = 10000
        for i in range(0, len(records), batch_size):
            cursor.executemany(insert_query, records[i:i + batch_size])
            
        conn.commit()
        cursor.close()
        conn.close()
        print("Database update completed.")
        
    except Error as e:
        print(f"MySQL Error: {e}")

if __name__ == "__main__":
    main()
