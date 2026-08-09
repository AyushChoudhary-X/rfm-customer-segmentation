"""
Step 6 - Export for Power BI

This script exports cleaned data and various aggregations to a multi-sheet 
Excel file and individual CSVs for consumption in Power BI dashboards.
It processes both transactions and RFM data to provide clear aggregated metrics.
"""
import pandas as pd
from pathlib import Path
import os

def main():
    # Setup paths
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / 'data' / 'processed'
    
    # Ensure directory exists
    data_dir.mkdir(parents=True, exist_ok=True)
    
    txn_path = data_dir / 'cleaned_transactions.csv'
    rfm_path = data_dir / 'rfm_segments.csv'
    
    print("Loading data...")
    if not txn_path.exists() or not rfm_path.exists():
        print(f"Warning: Missing required files in {data_dir}.")
        print("Please ensure cleaned_transactions.csv and rfm_segments.csv exist.")
        return
        
    try:
        txn_df = pd.read_csv(txn_path)
        rfm_df = pd.read_csv(rfm_path)
        if 'InvoiceDate' in txn_df.columns:
            txn_df['InvoiceDate'] = pd.to_datetime(txn_df['InvoiceDate'])
    except Exception as e:
        print(f"Failed to load data: {e}")
        return
        
    print("Preparing sheets for export...")
    
    # 1. Transactions (sample if > 50000 to keep file size manageable)
    if len(txn_df) > 50000:
        transactions_sheet = txn_df.sample(n=50000, random_state=42)
    else:
        transactions_sheet = txn_df.copy()
        
    # 2 & 3. RFM Scores & Segments
    rfm_scores_sheet = rfm_df.copy()
    customer_segments_sheet = pd.DataFrame()
    if 'Segment' in rfm_df.columns and 'CustomerID' in rfm_df.columns:
        customer_segments_sheet = rfm_df[['CustomerID', 'Segment']].copy()
    
    # 4. Monthly Revenue
    monthly_rev_sheet = pd.DataFrame()
    if 'InvoiceDate' in txn_df.columns and 'Revenue' in txn_df.columns:
        monthly_grp = txn_df.groupby([txn_df['InvoiceDate'].dt.year.rename('Year'), 
                                      txn_df['InvoiceDate'].dt.month.rename('Month')])
        monthly_rev_sheet = monthly_grp.agg(
            Revenue=('Revenue', 'sum'),
            OrderCount=('InvoiceNo', 'nunique'),
            CustomerCount=('CustomerID', 'nunique')
        ).reset_index()
        monthly_rev_sheet['YearMonth'] = monthly_rev_sheet['Year'].astype(str) + '-' + monthly_rev_sheet['Month'].astype(str).str.zfill(2)
        
    # 5. Country Revenue
    country_rev_sheet = pd.DataFrame()
    if 'Country' in txn_df.columns and 'Revenue' in txn_df.columns:
        country_rev_sheet = txn_df.groupby('Country').agg(
            Revenue=('Revenue', 'sum'),
            OrderCount=('InvoiceNo', 'nunique'),
            CustomerCount=('CustomerID', 'nunique')
        ).reset_index()
        country_rev_sheet['AvgOrderValue'] = country_rev_sheet['Revenue'] / country_rev_sheet['OrderCount']
        
    # 6. Segment Summary
    segment_summary_sheet = pd.DataFrame()
    if 'Segment' in rfm_df.columns:
        segment_summary_sheet = rfm_df.groupby('Segment').agg(
            CustomerCount=('CustomerID', 'nunique'),
            TotalRevenue=('Monetary', 'sum'),
            AvgRecency=('Recency', 'mean'),
            AvgFrequency=('Frequency', 'mean'),
            AvgMonetary=('Monetary', 'mean')
        ).reset_index()
        total_customers = segment_summary_sheet['CustomerCount'].sum()
        segment_summary_sheet['Percentage'] = segment_summary_sheet['CustomerCount'] / total_customers
        
    # 7. Daily Revenue
    daily_rev_sheet = pd.DataFrame()
    if 'InvoiceDate' in txn_df.columns and 'Revenue' in txn_df.columns:
        daily_rev_sheet = txn_df.groupby(txn_df['InvoiceDate'].dt.date.rename('Date')).agg(
            Revenue=('Revenue', 'sum'),
            OrderCount=('InvoiceNo', 'nunique')
        ).reset_index()

    # Dictionary of sheets
    sheets = {
        'Transactions': transactions_sheet,
        'RFM_Scores': rfm_scores_sheet,
        'Customer_Segments': customer_segments_sheet,
        'Monthly_Revenue': monthly_rev_sheet,
        'Country_Revenue': country_rev_sheet,
        'Segment_Summary': segment_summary_sheet,
        'Daily_Revenue': daily_rev_sheet
    }
    
    excel_path = data_dir / 'powerbi_export.xlsx'
    
    print(f"\nExporting data to Excel: {excel_path}")
    try:
        with pd.ExcelWriter(excel_path, engine='openpyxl') as writer:
            for sheet_name, df in sheets.items():
                if not df.empty:
                    # Write to Excel
                    df.to_excel(writer, sheet_name=sheet_name, index=False)
                    print(f" - Sheet '{sheet_name}' created with {len(df)} rows.")
                    
                    # Also write to separate CSVs
                    csv_path = data_dir / f"{sheet_name.lower()}.csv"
                    df.to_csv(csv_path, index=False)
    except ModuleNotFoundError:
        print("Error: 'openpyxl' module is required to write Excel files. (pip install openpyxl)")
        print("Falling back to exporting only CSV files...")
        for sheet_name, df in sheets.items():
            if not df.empty:
                csv_path = data_dir / f"{sheet_name.lower()}.csv"
                df.to_csv(csv_path, index=False)
                print(f" - CSV '{sheet_name.lower()}.csv' created with {len(df)} rows.")
    except Exception as e:
        print(f"An error occurred during export: {e}")

    print("\nExport process completed successfully.")

if __name__ == '__main__':
    main()
