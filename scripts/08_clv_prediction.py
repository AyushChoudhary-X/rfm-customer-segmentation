"""
Step 8: Customer Lifetime Value (CLV) Prediction using Linear Regression
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error

# Set dark background style
plt.style.use('dark_background')

def main():
    try:
        # Define paths
        project_root = Path(__file__).resolve().parent.parent
        data_dir = project_root / 'data' / 'processed'
        images_dir = project_root / 'images'
        
        # Ensure directories exist
        images_dir.mkdir(parents=True, exist_ok=True)
        data_dir.mkdir(parents=True, exist_ok=True)

        print("Loading data...")
        rfm_path = data_dir / 'rfm_segments.csv'
        transactions_path = data_dir / 'cleaned_transactions.csv'
        
        if not rfm_path.exists() or not transactions_path.exists():
            print(f"Error: Required data files not found in {data_dir}.")
            return
            
        rfm = pd.read_csv(rfm_path)
        transactions = pd.read_csv(transactions_path)

        # Convert InvoiceDate to datetime
        transactions['InvoiceDate'] = pd.to_datetime(transactions['InvoiceDate'])

        print("Engineering features from transactions...")
        
        # 1. avg_order_value: mean TotalPrice per customer
        avg_order_value = transactions.groupby('CustomerID')['TotalPrice'].mean().reset_index()
        avg_order_value.rename(columns={'TotalPrice': 'avg_order_value'}, inplace=True)
        
        # 2. avg_days_between_orders
        # Sort by customer and date
        tx_sorted = transactions[['CustomerID', 'InvoiceDate']].drop_duplicates().sort_values(['CustomerID', 'InvoiceDate'])
        tx_sorted['prev_date'] = tx_sorted.groupby('CustomerID')['InvoiceDate'].shift(1)
        tx_sorted['days_between'] = (tx_sorted['InvoiceDate'] - tx_sorted['prev_date']).dt.days
        avg_days = tx_sorted.groupby('CustomerID')['days_between'].mean().fillna(0).reset_index()
        avg_days.rename(columns={'days_between': 'avg_days_between_orders'}, inplace=True)
        
        # 3. unique_products
        unique_products = transactions.groupby('CustomerID')['StockCode'].nunique().reset_index()
        unique_products.rename(columns={'StockCode': 'unique_products'}, inplace=True)
        
        # Merge engineered features
        features = avg_order_value.merge(avg_days, on='CustomerID', how='left')
        features = features.merge(unique_products, on='CustomerID', how='left')
        
        # Merge with RFM data
        print("Merging with RFM data...")
        data = rfm.merge(features, on='CustomerID', how='left')
        
        # Drop rows with NaN
        data.dropna(inplace=True)

        # Define Features (X) and Target (y)
        feature_cols = ['Recency', 'Frequency', 'R_Score', 'F_Score', 'M_Score', 
                        'avg_order_value', 'avg_days_between_orders', 'unique_products']
        
        X = data[feature_cols]
        y = data['Monetary'] # Target is actual CLV (Monetary value)
        
        # Train-Test Split
        print("Splitting and scaling data...")
        X_train, X_test, y_train, y_test, indices_train, indices_test = train_test_split(
            X, y, data.index, test_size=0.2, random_state=42
        )
        
        # Scale Features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # Train Ridge Regression Model
        print("Training Ridge Regression model...")
        model = Ridge(alpha=1.0, random_state=42)
        model.fit(X_train_scaled, y_train)
        
        # Predict on Test Set
        y_pred = model.predict(X_test_scaled)
        
        # Calculate Metrics
        r2 = r2_score(y_test, y_pred)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        print("\n--- Model Evaluation ---")
        print(f"R² Score: {r2:.4f}")
        print(f"MAE:      {mae:.2f}")
        print(f"RMSE:     {rmse:.2f}")
        
        # Predictions for whole dataset for tiers and saving
        X_scaled_all = scaler.transform(X)
        data['Predicted_CLV'] = model.predict(X_scaled_all)
        
        # Plot 1: Actual vs Predicted
        print("Generating plots...")
        plt.figure(figsize=(8, 6), dpi=150)
        plt.scatter(y_test, y_pred, color='#00D4AA', alpha=0.5, edgecolor='none')
        # Red diagonal line
        max_val = max(y_test.max(), y_pred.max())
        min_val = min(y_test.min(), y_pred.min())
        plt.plot([min_val, max_val], [min_val, max_val], color='red', linestyle='--')
        plt.title('Actual vs Predicted CLV')
        plt.xlabel('Actual CLV')
        plt.ylabel('Predicted CLV')
        plt.tight_layout()
        plt.savefig(images_dir / 'ml_04_clv_actual_vs_predicted.png')
        plt.close()
        
        # Plot 2: Feature Importance
        coefs = pd.Series(model.coef_, index=feature_cols).sort_values(key=abs)
        plt.figure(figsize=(8, 6), dpi=150)
        coefs.plot(kind='barh', color='teal')
        plt.title('Feature Importance (Ridge Coefficients)')
        plt.xlabel('Coefficient Value')
        plt.tight_layout()
        plt.savefig(images_dir / 'ml_05_clv_feature_importance.png')
        plt.close()
        
        # Plot 3: Residuals Distribution
        residuals = y_test - y_pred
        plt.figure(figsize=(8, 6), dpi=150)
        sns.histplot(residuals, kde=True, color='#4ECDC4', edgecolor='none')
        plt.title('Residuals Distribution')
        plt.xlabel('Residuals (Actual - Predicted)')
        plt.ylabel('Frequency')
        plt.tight_layout()
        plt.savefig(images_dir / 'ml_06_clv_residuals.png')
        plt.close()
        
        # Create CLV Tiers based on predictions
        q25 = data['Predicted_CLV'].quantile(0.25)
        q75 = data['Predicted_CLV'].quantile(0.75)
        
        def assign_tier(val):
            if val >= q75:
                return 'High'
            elif val <= q25:
                return 'Low'
            else:
                return 'Medium'
                
        data['CLV_Tier'] = data['Predicted_CLV'].apply(assign_tier)
        
        # Cross-tabulate CLV Tiers with RFM Segments
        print("\n--- CLV Tiers vs RFM Segments ---")
        crosstab = pd.crosstab(data['Segment'], data['CLV_Tier'], margins=True)
        print(crosstab)
        
        # Save Predictions
        out_cols = ['CustomerID', 'Monetary', 'Predicted_CLV', 'CLV_Tier', 'Segment']
        out_data = data[out_cols].rename(columns={'Monetary': 'Actual_CLV'})
        out_path = data_dir / 'clv_predictions.csv'
        out_data.to_csv(out_path, index=False)
        print(f"\nPredictions saved to {out_path}")
        
        # Business Summary
        print("\n--- Business Summary ---")
        avg_clv_per_segment = data.groupby('Segment')['Predicted_CLV'].mean().sort_values(ascending=False)
        print("Average Predicted CLV per Segment:")
        print(avg_clv_per_segment)
        
        print("\nSegments with Highest Predicted CLV:")
        print(avg_clv_per_segment.head(2))
        print("\nSegments with Lowest Predicted CLV:")
        print(avg_clv_per_segment.tail(2))

        print("\nCLV Prediction completed successfully.")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    main()
