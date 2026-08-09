"""
Step 5 - Exploratory Data Analysis Visualizations

This script generates publication-quality EDA visualizations for the RFM
Customer Segmentation project. It reads processed transaction and segment
data, and outputs 10 charts in the 'images/' directory.
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import os
import sys

def main():
    # Setup paths
    base_dir = Path(__file__).resolve().parent.parent
    data_dir = base_dir / 'data' / 'processed'
    img_dir = base_dir / 'images'
    
    # Create images directory if it doesn't exist
    img_dir.mkdir(parents=True, exist_ok=True)
    
    # Check if data exists
    rfm_path = data_dir / 'rfm_segments.csv'
    txn_path = data_dir / 'cleaned_transactions.csv'
    
    if not rfm_path.exists() or not txn_path.exists():
        print(f"Warning: Required data files not found in {data_dir}")
        print("Please ensure rfm_segments.csv and cleaned_transactions.csv exist to run correctly.")
        print("Continuing with dummy logic to demonstrate structure if needed...")
        
    try:
        rfm_df = pd.read_csv(rfm_path)
        txn_df = pd.read_csv(txn_path)
        if 'InvoiceDate' in txn_df.columns:
            txn_df['InvoiceDate'] = pd.to_datetime(txn_df['InvoiceDate'])
    except Exception as e:
        print(f"Failed to load data: {e}")
        return
    
    # Styling configurations
    plt.style.use('dark_background')
    colors = ['#00D4AA', '#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', 
              '#FFEAA7', '#DDA0DD', '#FF8C42', '#6C5CE7', '#A8E6CF', '#FF85A2']
    sns.set_palette(sns.color_palette(colors))
    
    dpi = 150
    generated_charts = []
    
    def save_plot(fig, filename):
        """Helper to apply tight layout and save figure."""
        try:
            fig.tight_layout()
            filepath = img_dir / filename
            fig.savefig(filepath, dpi=dpi, facecolor=fig.get_facecolor(), edgecolor='none')
            print(f"Saved: images/{filename}")
            generated_charts.append(filename)
        except Exception as e:
            print(f"Error saving {filename}: {e}")
        finally:
            plt.close(fig)

    print("Generating visualizations...")

    # 1. 01_revenue_over_time.png
    if 'InvoiceDate' in txn_df.columns and 'Revenue' in txn_df.columns:
        txn_df['YearMonth'] = txn_df['InvoiceDate'].dt.to_period('M')
        monthly_rev = txn_df.groupby('YearMonth')['Revenue'].sum().reset_index()
        monthly_rev['YearMonth'] = monthly_rev['YearMonth'].astype(str)
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.plot(monthly_rev['YearMonth'], monthly_rev['Revenue'], color=colors[0], linewidth=3)
        ax.fill_between(monthly_rev['YearMonth'], monthly_rev['Revenue'], alpha=0.3, color=colors[0])
        ax.set_title("Monthly Revenue Over Time", fontsize=16, fontweight='bold', color='white')
        ax.set_xlabel("Month", fontsize=12)
        ax.set_ylabel("Revenue", fontsize=12)
        plt.xticks(rotation=45)
        save_plot(fig, '01_revenue_over_time.png')
    
    # 2. 02_top_countries_revenue.png
    if 'Country' in txn_df.columns and 'Revenue' in txn_df.columns:
        country_rev = txn_df[txn_df['Country'] != 'United Kingdom'].groupby('Country')['Revenue'].sum()
        country_rev = country_rev.nlargest(10).sort_values()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        country_rev.plot(kind='barh', color=colors[1], ax=ax)
        ax.set_title("Top 10 Countries by Revenue (Excl. UK)", fontsize=16, fontweight='bold', color='white')
        ax.set_xlabel("Revenue", fontsize=12)
        ax.set_ylabel("Country", fontsize=12)
        save_plot(fig, '02_top_countries_revenue.png')
        
    # 3. 03_rfm_distributions.png
    cols = ['Recency', 'Frequency', 'Monetary']
    if all(c in rfm_df.columns for c in cols):
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        for i, col in enumerate(cols):
            sns.histplot(rfm_df[col], kde=True, ax=axes[i], color=colors[i+2])
            axes[i].set_title(f"{col} Distribution", fontsize=14, fontweight='bold', color='white')
            axes[i].set_xlabel(col, fontsize=12)
            axes[i].set_ylabel("Count", fontsize=12)
        fig.suptitle("RFM Distributions", fontsize=16, fontweight='bold', color='white')
        save_plot(fig, '03_rfm_distributions.png')
        
    # 4. 04_segment_distribution.png
    if 'Segment' in rfm_df.columns:
        segment_counts = rfm_df['Segment'].value_counts().sort_values()
        
        fig, ax = plt.subplots(figsize=(10, 8))
        bars = ax.barh(segment_counts.index, segment_counts.values, color=colors[:len(segment_counts)])
        ax.set_title("Customer Count per Segment", fontsize=16, fontweight='bold', color='white')
        ax.set_xlabel("Count", fontsize=12)
        ax.set_ylabel("Segment", fontsize=12)
        ax.bar_label(bars, padding=3, color='white')
        save_plot(fig, '04_segment_distribution.png')
        
    # 5. 05_segment_treemap.png
    if 'Segment' in rfm_df.columns:
        # Alternative to squarify treemap using a 1D stacked bar (proportional)
        segment_counts = rfm_df['Segment'].value_counts().sort_values(ascending=False)
        total = segment_counts.sum()
        
        fig, ax = plt.subplots(figsize=(12, 4))
        left = 0
        for i, (seg, count) in enumerate(segment_counts.items()):
            pct = count / total
            ax.barh(0, pct, left=left, color=colors[i % len(colors)], edgecolor='black')
            if pct > 0.05:  # Only add text if block is wide enough
                ax.text(left + pct/2, 0, f"{seg}\n({pct:.1%})", 
                        ha='center', va='center', color='white', fontweight='bold', fontsize=10)
            left += pct
            
        ax.set_xlim(0, 1)
        ax.set_yticks([])
        ax.set_title("Customer Segments Proportion", fontsize=16, fontweight='bold', color='white')
        save_plot(fig, '05_segment_treemap.png')

    # 6. 06_rfm_scatter.png
    if all(c in rfm_df.columns for c in ['Recency', 'Frequency', 'Segment']):
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.scatterplot(data=rfm_df, x='Recency', y='Frequency', hue='Segment', 
                        palette=colors[:rfm_df['Segment'].nunique()], alpha=0.6, ax=ax)
        ax.set_title("Recency vs Frequency by Segment", fontsize=16, fontweight='bold', color='white')
        ax.set_xlabel("Recency", fontsize=12)
        ax.set_ylabel("Frequency", fontsize=12)
        save_plot(fig, '06_rfm_scatter.png')

    # 7. 07_monetary_by_segment.png
    if 'Monetary' in rfm_df.columns and 'Segment' in rfm_df.columns:
        # Sort by median monetary value
        order = rfm_df.groupby('Segment')['Monetary'].median().sort_values().index
        
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.boxplot(data=rfm_df, x='Monetary', y='Segment', order=order, 
                    palette=colors[:len(order)], ax=ax)
        ax.set_title("Monetary Value by Segment", fontsize=16, fontweight='bold', color='white')
        ax.set_xlabel("Monetary Value", fontsize=12)
        ax.set_ylabel("Segment", fontsize=12)
        # Cap the x-axis to limit effect of outliers
        ax.set_xlim(0, rfm_df['Monetary'].quantile(0.95))
        save_plot(fig, '07_monetary_by_segment.png')

    # 8. 08_rfm_heatmap.png
    heatmap_cols = ['R_Score', 'F_Score', 'M_Score', 'RFM_Total', 'Recency', 'Frequency', 'Monetary']
    heatmap_cols_exist = [c for c in heatmap_cols if c in rfm_df.columns]
    if len(heatmap_cols_exist) > 1:
        corr = rfm_df[heatmap_cols_exist].corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr, annot=True, cmap='mako', fmt='.2f', vmin=-1, vmax=1, ax=ax)
        ax.set_title("RFM Correlation Heatmap", fontsize=16, fontweight='bold', color='white')
        save_plot(fig, '08_rfm_heatmap.png')

    # 9. 09_top_customers.png
    if 'CustomerID' in rfm_df.columns and 'Monetary' in rfm_df.columns:
        top_cust = rfm_df.nlargest(15, 'Monetary').sort_values('Monetary')
        top_cust['CustomerID'] = top_cust['CustomerID'].astype(str)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        bars = ax.barh(top_cust['CustomerID'], top_cust['Monetary'], color=colors[6])
        ax.set_title("Top 15 Customers by Total Spend", fontsize=16, fontweight='bold', color='white')
        ax.set_xlabel("Total Spend", fontsize=12)
        ax.set_ylabel("Customer ID", fontsize=12)
        save_plot(fig, '09_top_customers.png')

    # 10. 10_revenue_by_weekday.png
    if 'InvoiceDate' in txn_df.columns and 'Revenue' in txn_df.columns:
        txn_df['Weekday'] = txn_df['InvoiceDate'].dt.day_name()
        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        
        revenue_weekday = txn_df.groupby('Weekday')['Revenue'].sum().reindex(weekday_order).fillna(0)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        revenue_weekday.plot(kind='bar', color=colors[7], ax=ax)
        ax.set_title("Total Revenue by Day of Week", fontsize=16, fontweight='bold', color='white')
        ax.set_xlabel("Day of Week", fontsize=12)
        ax.set_ylabel("Revenue", fontsize=12)
        plt.xticks(rotation=45)
        save_plot(fig, '10_revenue_by_weekday.png')

    print("\n--- Summary of Generated Charts ---")
    for chart in generated_charts:
        print(f"- {chart}")
    print(f"Total charts generated: {len(generated_charts)}")

if __name__ == '__main__':
    main()
