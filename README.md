# 📊 RFM Customer Segmentation Analytics

## 🎯 Project Overview
RFM (Recency, Frequency, Monetary) analysis is a proven marketing model for behavior-based customer segmentation. It groups customers based on their transaction history – how recently, how often, and how much they bought. This project analyzes e-commerce transaction data to construct an end-to-end data pipeline, segment customers using RFM metrics, and visualize the findings through custom Python visuals, a web dashboard, and a Power BI report.

## 🛠️ Tech Stack
- **Python 3.13** — Data processing, analysis, visualization
- **MySQL** — Relational database for structured data storage and SQL analytics
- **Power BI** — Interactive business intelligence dashboard
- **HTML/CSS/JS** — Web-based companion dashboard
- **Libraries**: pandas, numpy, matplotlib, seaborn, mysql-connector-python, Chart.js

## 📁 Project Structure
```text
rfm/
├── data/
│   ├── raw/               # Raw downloaded CSV files
│   └── processed/         # Cleaned and processed datasets
├── scripts/
│   ├── 01_load_and_clean.py
│   ├── 02_create_database.py
│   ├── 03_rfm_scoring.py
│   ├── 04_segmentation.py
│   ├── 05_eda_visuals.py
│   └── 06_export_powerbi.py
├── images/                # Generated visualizations
├── dashboard/
│   ├── index.html         # Web dashboard entry point
│   ├── style.css          # Dashboard styling
│   └── script.js          # Dashboard logic (Chart.js)
├── reports/
│   └── powerbi_guide.md   # Setup guide for Power BI
├── requirements.txt       # Python dependencies
└── README.md              # Project documentation
```

## 📦 Dataset
- **Source:** UCI Online Retail Dataset (via Kaggle)
- **Size:** ~541,909 transactions, 8 columns
- **Period:** Dec 2010 — Dec 2011
- **Domain:** UK-based online retail company
- **Link:** [Download from Kaggle](https://www.kaggle.com/datasets/carrie1/ecommerce-data)

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- MySQL 8.0+
- Power BI Desktop (optional, for `.pbix` dashboard)

### Installation
```bash
# Clone the repository
git clone <repo-url>
cd rfm

# Install Python dependencies
pip install -r requirements.txt

# Install MySQL (macOS)
brew install mysql
brew services start mysql

# Download dataset
# Visit: https://www.kaggle.com/datasets/carrie1/ecommerce-data
# Save as: data/raw/OnlineRetail.csv
```

### Run the Pipeline
```bash
python scripts/01_load_and_clean.py
python scripts/02_create_database.py
python scripts/03_rfm_scoring.py
python scripts/04_segmentation.py
python scripts/05_eda_visuals.py
python scripts/06_export_powerbi.py
```

## 📊 RFM Methodology
- **R (Recency):** Days since the customer's last purchase.
- **F (Frequency):** Total number of transactions by the customer.
- **M (Monetary):** Total amount spent by the customer.

Each metric is scored on a quintile scale (1-5), where 5 is the best (most recent, most frequent, highest spender).

### Customer Segments

| Segment | Description |
|---|---|
| **Champions** | Bought recently, buy often, and spend the most. |
| **Loyal Customers** | Spend good money and often. Responsive to promotions. |
| **Potential Loyalist** | Recent customers, spent a good amount, bought more than once. |
| **New Customers** | Bought most recently, but not often. |
| **Promising** | Recent shoppers, but haven't spent much. |
| **Need Attention** | Above average recency, frequency & monetary values. |
| **About To Sleep** | Below average recency, frequency & monetary values. |
| **At Risk** | Spent big money and purchased often, but long ago. |
| **Cannot Lose Them** | Made big purchases, and often, but haven't returned for a long time. |
| **Hibernating** | Last purchase was long back, low spenders and low number of orders. |
| **Lost** | Lowest recency, frequency, and monetary scores. |

## 📈 Sample Visualizations
During the pipeline execution, descriptive charts and exploratory data analysis (EDA) plots are generated and saved directly in the `images/` directory.

## 🖥️ Web Dashboard
A lightweight web-based dashboard is provided to explore the data using Chart.js.
Note: It requires running a local server to properly load the processed CSV data files.

```bash
# Run from the project root
python -m http.server 8000

# Visit http://localhost:8000/dashboard/
```

## 📊 Power BI Dashboard
For comprehensive, interactive BI analytics, please refer to the `reports/powerbi_guide.md` for detailed setup and usage instructions of the `.pbix` file.

## 🔑 Key Insights (Template)
*To be populated upon analysis completion:*
- **Customer distribution across segments:** *[Insight placeholder]*
- **Revenue concentration:** *[Insight placeholder]*
- **Churn risk analysis:** *[Insight placeholder]*
- **Geographic patterns:** *[Insight placeholder]*

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

## 🤝 Contributing
Contributions, issues, and feature requests are welcome!
Feel free to check the issues page.
