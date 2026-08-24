"""Step 9: K-Means Clustering — ML-based Segmentation vs Rule-based RFM"""

import sys
import logging
from pathlib import Path
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.decomposition import PCA

try:
    from kneed import KneeLocator
except ImportError:
    KneeLocator = None

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def main():
    try:
        # Set dark background and DPI
        plt.style.use('dark_background')
        dpi = 150
        
        # Setup directories
        project_root = Path(__file__).resolve().parent.parent
        data_path = project_root / 'data' / 'processed' / 'rfm_segments.csv'
        output_data_path = project_root / 'data' / 'processed' / 'kmeans_clusters.csv'
        images_dir = project_root / 'images'
        images_dir.mkdir(parents=True, exist_ok=True)
        
        if not data_path.exists():
            logging.error(f"Input data not found at {data_path}. Run previous steps first.")
            return
            
        logging.info(f"Loading data from {data_path}")
        df = pd.read_csv(data_path)
        
        # 1. Select features
        features = ['Recency', 'Frequency', 'Monetary']
        X = df[features]
        
        # 2. Standardize features
        logging.info("Standardizing features...")
        scaler = StandardScaler()
        X_scaled = scaler.fit_transform(X)
        X_scaled_df = pd.DataFrame(X_scaled, columns=features)
        
        # 3. Elbow Method
        logging.info("Running Elbow Method (K=2 to K=10)...")
        k_values = list(range(2, 11))
        inertias = []
        
        for k in k_values:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
            kmeans.fit(X_scaled)
            inertias.append(kmeans.inertia_)
            
        optimal_k_elbow = 5
        if KneeLocator is not None:
            try:
                kl = KneeLocator(k_values, inertias, curve="convex", direction="decreasing")
                if kl.elbow is not None:
                    optimal_k_elbow = kl.elbow
                    logging.info(f"KneeLocator found optimal K = {optimal_k_elbow}")
                else:
                    logging.info("KneeLocator could not find a clear elbow, defaulting to K=5")
            except Exception as e:
                logging.warning(f"KneeLocator failed: {e}. Defaulting to K=5")
        else:
            logging.info("kneed package not installed, defaulting Elbow K to 5")
            
        plt.figure(figsize=(8, 5))
        plt.plot(k_values, inertias, marker='o', color='#00D4AA', linewidth=2)
        plt.plot(optimal_k_elbow, inertias[optimal_k_elbow-2], marker='o', color='#FF6B6B', markersize=10, label=f'Optimal K={optimal_k_elbow}')
        plt.title('Elbow Method For Optimal K')
        plt.xlabel('Number of Clusters (K)')
        plt.ylabel('Inertia')
        plt.legend()
        plt.tight_layout()
        plt.savefig(images_dir / 'ml_07_elbow_method.png', dpi=dpi)
        plt.close()
        
        # 4. Silhouette Analysis
        logging.info("Running Silhouette Analysis...")
        silhouette_scores = []
        for k in k_values:
            kmeans = KMeans(n_clusters=k, random_state=42, n_init='auto')
            cluster_labels = kmeans.fit_predict(X_scaled)
            silhouette_avg = silhouette_score(X_scaled, cluster_labels)
            silhouette_scores.append(silhouette_avg)
            
        best_k = k_values[np.argmax(silhouette_scores)]
        logging.info(f"Best K based on Silhouette Score: {best_k}")
        
        colors = ['#008080' if k != best_k else '#00D4AA' for k in k_values] # teal bars, highlight best
        plt.figure(figsize=(8, 5))
        bars = plt.bar(k_values, silhouette_scores, color=colors)
        plt.title('Silhouette Scores For Different K')
        plt.xlabel('Number of Clusters (K)')
        plt.ylabel('Silhouette Score')
        plt.xticks(k_values)
        plt.tight_layout()
        plt.savefig(images_dir / 'ml_08_silhouette_scores.png', dpi=dpi)
        plt.close()
        
        # 5. Final Clustering
        logging.info(f"Running final KMeans with optimal K={best_k}...")
        final_kmeans = KMeans(n_clusters=best_k, random_state=42, n_init='auto')
        df['KMeans_Cluster'] = final_kmeans.fit_predict(X_scaled)
        
        # 6. Cluster Profiling
        logging.info("Cluster Profiling:")
        cluster_profiles = df.groupby('KMeans_Cluster')[['Recency', 'Frequency', 'Monetary']].mean()
        cluster_counts = df['KMeans_Cluster'].value_counts().sort_index()
        cluster_profiles['Count'] = cluster_counts
        
        # Simple heuristic labeling based on R, F, M relative to overall mean
        overall_mean_r = df['Recency'].mean()
        overall_mean_f = df['Frequency'].mean()
        overall_mean_m = df['Monetary'].mean()
        
        cluster_labels = {}
        for cluster, row in cluster_profiles.iterrows():
            r, f, m = row['Recency'], row['Frequency'], row['Monetary']
            print(f"Cluster {cluster} - Count: {int(row['Count'])}, Mean Recency: {r:.2f}, Mean Frequency: {f:.2f}, Mean Monetary: {m:.2f}")
            if r < overall_mean_r and f > overall_mean_f and m > overall_mean_m:
                label = 'Best Customers'
            elif r > overall_mean_r and f < overall_mean_f and m < overall_mean_m:
                label = 'Lost Customers'
            elif r < overall_mean_r and f < overall_mean_f:
                label = 'Recent/New Customers'
            elif f > overall_mean_r and m > overall_mean_m:
                label = 'Loyal/Big Spenders'
            else:
                label = 'Average Customers'
            cluster_labels[cluster] = label
            
        df['Cluster_Label'] = df['KMeans_Cluster'].map(cluster_labels)
        
        # 7. Comparison
        logging.info("Comparing KMeans with Rule-based Segments...")
        crosstab = pd.crosstab(df['Segment'], df['KMeans_Cluster'])
        print("\nCrosstab: Segment vs KMeans_Cluster\n", crosstab)
        
        ari = adjusted_rand_score(df['Segment'], df['KMeans_Cluster'])
        print(f"\nAdjusted Rand Index (ARI): {ari:.4f}")
        print("Interpretation: 0 indicates random assignment, 1 indicates perfect match.")
        
        # 8. Visualizations
        logging.info("Generating PCA and Cluster Visualizations...")
        pca = PCA(n_components=2, random_state=42)
        X_pca = pca.fit_transform(X_scaled)
        df['PCA1'] = X_pca[:, 0]
        df['PCA2'] = X_pca[:, 1]
        
        palette_colors = ['#00D4AA', '#FF6B6B', '#4ECDC4', '#45B7D1', '#FFEAA7', '#FF8C42', '#DDA0DD', '#6C5CE7', '#A8E6CF', '#FF85A2']
        
        # 8a. PCA by KMeans Cluster
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df, x='PCA1', y='PCA2', hue='KMeans_Cluster', palette=palette_colors[:best_k], s=50, alpha=0.8)
        plt.title('2D PCA Colored by KMeans Cluster')
        plt.legend(title='KMeans Cluster')
        plt.tight_layout()
        plt.savefig(images_dir / 'ml_09_kmeans_pca.png', dpi=dpi)
        plt.close()
        
        # 8b. PCA by Rule-based Segment
        unique_segments = df['Segment'].nunique()
        plt.figure(figsize=(10, 6))
        sns.scatterplot(data=df, x='PCA1', y='PCA2', hue='Segment', palette=palette_colors[:unique_segments] if unique_segments <= 10 else "tab20", s=50, alpha=0.8)
        plt.title('2D PCA Colored by Rule-based Segment')
        plt.legend(title='Segment', bbox_to_anchor=(1.05, 1), loc='upper left')
        plt.tight_layout()
        plt.savefig(images_dir / 'ml_10_rfm_segments_pca.png', dpi=dpi)
        plt.close()
        
        # 8c. Cluster centers bar chart
        cluster_centers = pd.DataFrame(final_kmeans.cluster_centers_, columns=features)
        cluster_centers.index.name = 'Cluster'
        cluster_centers.reset_index(inplace=True)
        melted_centers = pd.melt(cluster_centers, id_vars=['Cluster'], value_vars=features, var_name='Feature', value_name='Standardized Mean')
        
        plt.figure(figsize=(10, 6))
        sns.barplot(data=melted_centers, x='Cluster', y='Standardized Mean', hue='Feature', palette='Set2')
        plt.title('Cluster Profiles (Standardized R, F, M)')
        plt.axhline(0, color='white', linewidth=0.5, linestyle='--')
        plt.tight_layout()
        plt.savefig(images_dir / 'ml_11_cluster_profiles.png', dpi=dpi)
        plt.close()
        
        # 9. Save output
        out_cols = ['CustomerID', 'Recency', 'Frequency', 'Monetary', 'R_Score', 'F_Score', 'M_Score', 'Segment', 'KMeans_Cluster', 'Cluster_Label']
        existing_out_cols = [c for c in out_cols if c in df.columns]
        df[existing_out_cols].to_csv(output_data_path, index=False)
        logging.info(f"Saved clustering results to {output_data_path}")
        
        # 10. Summary
        print("\n--- Summary ---")
        print(f"Number of rule-based segments: {unique_segments}")
        print(f"Optimal number of KMeans clusters: {best_k}")
        print(f"ARI Score: {ari:.4f}")
        print("Key insight: Rule-based segments can be more granular, while ML clusters find naturally cohesive groups. Comparing the crosstab shows how rigid heuristic boundaries map to underlying data distributions.")
        
    except Exception as e:
        logging.exception(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
