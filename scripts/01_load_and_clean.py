#!/usr/bin/env python3
"""
Step 1: Load and Clean Data
This script is the first step of the RFM pipeline.
It loads raw transactions data, cleans it by removing invalid rows and missing values,
parses dates, and calculates total price. The cleaned dataset is then saved for the next step.
"""

import pandas as pd
from pathlib import Path
import os

def main():
    # Define paths
    project_root = Path(__file__).resolve().parent.parent
    raw_xlsx_path = project_root / 'data' / 'raw' / 'OnlineRetail.xlsx'
    raw_csv_path = project_root / 'data' / 'raw' / 'OnlineRetail.csv'
    processed_dir = project_root / 'data' / 'processed'
    cleaned_data_path = processed_dir / 'cleaned_transactions.csv'
    
    # Ensure processed directory exists
    processed_dir.mkdir(parents=True, exist_ok=True)
    
    # Try loading xlsx first (UCI repository), then CSV (Kaggle)
    try:
        if raw_xlsx_path.exists():
            print(f"Loading raw data from: {raw_xlsx_path}")
            df = pd.read_excel(raw_xlsx_path, engine='openpyxl')
        elif raw_csv_path.exists():
            print(f"Loading raw data from: {raw_csv_path}")
            df = pd.read_csv(raw_csv_path, encoding='ISO-8859-1')
        else:
            print(f"Error: No data file found. Place OnlineRetail.xlsx or OnlineRetail.csv in data/raw/")
            return
    except Exception as e:
        print(f"Failed to read data file: {e}")
        return
        
    initial_shape = df.shape
    print(f"Initial data shape: {initial_shape}")
    print("Initial Data Types:")
    print(df.dtypes)
    print("\nStarting data cleaning...")
    
    # Track initial nulls
    initial_nulls = df.isnull().sum()
    
    # 1. Remove rows with missing CustomerID
    df = df.dropna(subset=['CustomerID'])
    
    # 2. Remove cancelled transactions (InvoiceNo starting with 'C')
    df = df[~df['InvoiceNo'].astype(str).str.startswith('C')]
    
    # 3. Remove rows with Quantity <= 0 or UnitPrice <= 0
    df = df[(df['Quantity'] > 0) & (df['UnitPrice'] > 0)]
    
    # 4. Remove duplicate rows
    df = df.drop_duplicates()
    
    # 5. Create TotalPrice column
    df['TotalPrice'] = df['Quantity'] * df['UnitPrice']
    
    # 6. Parse InvoiceDate to datetime
    df['InvoiceDate'] = pd.to_datetime(df['InvoiceDate'])
    
    # 7. Convert CustomerID to int
    df['CustomerID'] = df['CustomerID'].astype(int)
    
    final_shape = df.shape
    
    print("\n--- Data Quality Summary ---")
    print(f"Rows removed: {initial_shape[0] - final_shape[0]}")
    print(f"Initial Null CustomerIDs: {initial_nulls['CustomerID']}")
    print(f"Final data shape: {final_shape}")
    print("Final Data Types:")
    print(df.dtypes)
    print("----------------------------\n")
    
    # Save cleaned data
    print(f"Saving cleaned data to: {cleaned_data_path}")
    df.to_csv(cleaned_data_path, index=False)
    print("Data cleaning completed successfully.")

if __name__ == "__main__":
    main()
