"""
Step 7: Customer Churn Prediction using Logistic Regression
"""

import sys
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    classification_report,
    confusion_matrix,
    roc_auc_score,
    roc_curve,
)


def main():
    try:
        # Define project root
        project_root = Path(__file__).resolve().parent.parent
        
        # Paths
        data_path = project_root / "data" / "processed" / "rfm_segments.csv"
        images_dir = project_root / "images"
        predictions_path = project_root / "data" / "processed" / "churn_predictions.csv"
        
        # Create directories if they don't exist
        images_dir.mkdir(parents=True, exist_ok=True)
        predictions_path.parent.mkdir(parents=True, exist_ok=True)
        
        print(f"Loading data from: {data_path}")
        if not data_path.exists():
            print(f"Error: Data file not found at {data_path}")
            sys.exit(1)
            
        df = pd.read_csv(data_path)
        
        # 1. Create the Churned label
        median_recency = df['Recency'].median()
        df['Churned'] = (df['Recency'] > median_recency).astype(int)
        
        churn_counts = df['Churned'].value_counts()
        print(f"Median Recency: {median_recency}")
        print(f"Churn Split: \n{churn_counts}")
        
        # 2. Define X (features) and y (target)
        # Removed 'Recency', 'R_Score', and 'RFM_Total' to prevent Target Leakage
        features = ['F_Score', 'M_Score', 'Frequency', 'Monetary']
        X = df[features]
        y = df['Churned']
        
        print("Features defined. Proceeding to split data...")
        
        # 3. Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # 4. Scale features
        scaler = StandardScaler()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)
        
        # 5. Train LogisticRegression
        print("Training Logistic Regression model...")
        model = LogisticRegression(random_state=42, max_iter=1000)
        model.fit(X_train_scaled, y_train)
        
        # 6. Predict on test set
        y_pred = model.predict(X_test_scaled)
        y_pred_proba = model.predict_proba(X_test_scaled)[:, 1]
        
        # 7. Print classification_report
        print("\n--- Classification Report ---")
        report = classification_report(y_test, y_pred)
        print(report)
        report_dict = classification_report(y_test, y_pred, output_dict=True)
        accuracy = report_dict['accuracy']
        
        # 8. Print confusion_matrix
        print("--- Confusion Matrix ---")
        cm = confusion_matrix(y_test, y_pred)
        print(cm)
        
        # 9. Calculate and print ROC-AUC score
        auc = roc_auc_score(y_test, y_pred_proba)
        print(f"\nROC-AUC Score: {auc:.4f}")
        
        # Ensure plot styling
        plt.style.use('dark_background')
        
        # 10. Plot and save ROC curve
        print("Plotting ROC Curve...")
        fpr, tpr, _ = roc_curve(y_test, y_pred_proba)
        plt.figure(figsize=(8, 6))
        plt.plot(fpr, tpr, color='#00D4AA', lw=2, label=f'ROC Curve (AUC = {auc:.2f})')
        plt.plot([0, 1], [0, 1], color='#FF6B6B', lw=2, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver Operating Characteristic (ROC)')
        plt.legend(loc="lower right")
        roc_path = images_dir / "ml_01_roc_curve.png"
        plt.savefig(roc_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        # 11. Plot and save feature importance
        print("Plotting Feature Importance...")
        coefficients = model.coef_[0]
        feature_importance = pd.DataFrame({
            'Feature': features,
            'Importance': coefficients,
            'Abs_Importance': np.abs(coefficients)
        }).sort_values(by='Abs_Importance', ascending=True)
        
        plt.figure(figsize=(10, 6))
        plt.barh(feature_importance['Feature'], feature_importance['Importance'], color='#00D4AA')
        plt.title('Logistic Regression Feature Importance')
        plt.xlabel('Coefficient Value')
        plt.ylabel('Feature')
        plt.axvline(x=0, color='#FF6B6B', linestyle='--', alpha=0.7)
        feat_imp_path = images_dir / "ml_02_feature_importance.png"
        plt.savefig(feat_imp_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        top_features = feature_importance.sort_values(by='Abs_Importance', ascending=False)['Feature'].head(3).tolist()
        
        # 12. Plot and save confusion matrix heatmap
        print("Plotting Confusion Matrix Heatmap...")
        plt.figure(figsize=(8, 6))
        sns.heatmap(cm, annot=True, fmt='d', cmap='YlGnBu', cbar=False,
                    xticklabels=['Not Churned', 'Churned'],
                    yticklabels=['Not Churned', 'Churned'])
        plt.title('Confusion Matrix Heatmap')
        plt.ylabel('Actual')
        plt.xlabel('Predicted')
        cm_path = images_dir / "ml_03_confusion_matrix.png"
        plt.savefig(cm_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        # 13. Save the predictions
        print(f"Saving predictions to: {predictions_path}")
        X_all_scaled = scaler.transform(X)
        all_pred = model.predict(X_all_scaled)
        all_proba = model.predict_proba(X_all_scaled)[:, 1]
        
        predictions_df = pd.DataFrame({
            'CustomerID': df['CustomerID'] if 'CustomerID' in df.columns else df.index,
            'Churned_Actual': df['Churned'],
            'Churned_Predicted': all_pred,
            'Churn_Probability': all_proba
        })
        predictions_df.to_csv(predictions_path, index=False)
        
        # 14. Print a summary
        total_customers = len(df)
        churn_rate = churn_counts.get(1, 0) / total_customers * 100
        
        print("\n=== Execution Summary ===")
        print(f"Total Customers: {total_customers}")
        print(f"Overall Churn Rate: {churn_rate:.2f}%")
        print(f"Model Accuracy: {accuracy:.4f}")
        print(f"Model ROC-AUC: {auc:.4f}")
        print(f"Top 3 Most Important Features: {', '.join(top_features)}")
        
        # 15. Print business insight
        median_freq = df['Frequency'].median()
        subset = df[(df['Recency'] > median_recency) & (df['Frequency'] < median_freq)]
        if len(subset) > 0:
            insight_prob = subset['Churned'].mean() * 100
        else:
            insight_prob = 0.0
            
        print("\n=== Business Insight ===")
        print(f"Customers with Recency > {median_recency:.1f} days and Frequency < {median_freq:.1f} have {insight_prob:.1f}% churn probability.")
        
        print("\nProcess completed successfully.")
        
    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
