#!/usr/bin/env python3
"""
Step 2: Create Database and Load Data
This script creates the MySQL database `rfm_analytics` if it doesn't exist,
creates necessary tables from SQL scripts, bulk inserts the cleaned transaction data,
and executes queries to calculate initial RFM values.
"""

import pandas as pd
import mysql.connector
from mysql.connector import Error
from pathlib import Path

# Database config
DB_CONFIG = {
    'host': 'localhost',
    'user': 'root',
    'password': 'password',
    'unix_socket': '/tmp/mysql.sock'
}
DB_NAME = 'rfm_analytics'

def create_database(cursor):
    print(f"Creating database {DB_NAME} if it doesn't exist...")
    cursor.execute(f"CREATE DATABASE IF NOT EXISTS {DB_NAME}")

def execute_sql_file(cursor, filepath):
    if not filepath.exists():
        print(f"SQL script not found: {filepath}")
        return False
        
    print(f"Executing SQL from: {filepath}")
    with open(filepath, 'r') as file:
        sql_script = file.read()
        
    # Split by semicolon and execute each statement
    sql_commands = sql_script.split(';')
    for command in sql_commands:
        if command.strip():
            try:
                cursor.execute(command)
            except Error as e:
                print(f"Error executing command: {command[:50]}... \n{e}")
                
    return True

def main():
    project_root = Path(__file__).resolve().parent.parent
    cleaned_data_path = project_root / 'data' / 'processed' / 'cleaned_transactions.csv'
    sql_create_tables = project_root / 'sql' / 'create_tables.sql'
    sql_rfm_queries = project_root / 'sql' / 'rfm_queries.sql'
    
    conn = None
    try:
        print("Connecting to MySQL server...")
        conn = mysql.connector.connect(**DB_CONFIG)
        cursor = conn.cursor()
        
        # Create DB and select it
        create_database(cursor)
        cursor.execute(f"USE {DB_NAME}")
        
        # Create tables
        execute_sql_file(cursor, sql_create_tables)
        conn.commit()
        
        # Load cleaned data
        if not cleaned_data_path.exists():
            print(f"Error: Cleaned data not found at {cleaned_data_path}")
            return
            
        print(f"Loading data from {cleaned_data_path}...")
        df = pd.read_csv(cleaned_data_path)
        
        # Bulk insert into transactions
        print("Inserting records into transactions table...")
        insert_query = """
        INSERT INTO transactions (InvoiceNo, StockCode, Description, Quantity, InvoiceDate, UnitPrice, CustomerID, Country, TotalPrice)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        
        # Prepare data for insertion (convert nan to None)
        df_records = df.where(pd.notnull(df), None)
        records = list(df_records.itertuples(index=False, name=None))
        
        batch_size = 10000
        total_rows = len(records)
        
        for i in range(0, total_rows, batch_size):
            batch = records[i:i + batch_size]
            cursor.executemany(insert_query, batch)
            conn.commit()
            print(f"Inserting batch {i//batch_size + 1} of {total_rows//batch_size + 1}... ({min(i+batch_size, total_rows)}/{total_rows})")
            
        print("Transaction data inserted successfully.")
        
        # Execute RFM Queries
        print("Executing RFM calculation queries...")
        execute_sql_file(cursor, sql_rfm_queries)
        conn.commit()
        
        # Print row counts
        tables = ['transactions', 'rfm_values']
        print("\n--- Final Row Counts ---")
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                count = cursor.fetchone()[0]
                print(f"{table}: {count} rows")
            except Error:
                print(f"{table}: Table not found or error counting.")
        print("------------------------\n")
        
    except Error as e:
        print(f"MySQL Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if conn and conn.is_connected():
            cursor.close()
            conn.close()
            print("MySQL connection closed.")

if __name__ == "__main__":
    main()
