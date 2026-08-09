# Power BI Dashboard Setup Guide — RFM Customer Segmentation

## Prerequisites
- Power BI Desktop (Windows) or Power BI Service (web)
- The exported file: `data/processed/powerbi_export.xlsx`

## Step 1: Import Data
1. Open Power BI Desktop.
2. Click on **Get Data** -> **Excel workbook** from the Home ribbon.
3. Navigate to and select `data/processed/powerbi_export.xlsx`.
4. In the Navigator window, select all the relevant sheets (e.g., `Customer_Segments`, `Transactions`, `Dates`).
5. Click **Transform Data** to open the Power Query Editor.
6. **Data Type Configurations**:
   - Ensure `CustomerID` is set to Text (to prevent unintended aggregations).
   - Ensure `Monetary` is set to Decimal Number or Fixed Decimal Number (Currency).
   - Ensure `Recency` and `Frequency` are set to Whole Numbers.
   - Ensure date columns are formatted as Date or Date/Time.
7. Click **Close & Apply**.

## Step 2: Data Model (Star Schema)
Power BI utilizes relationships to filter and cross-highlight visuals. Set up a Star Schema where your main facts (Transactions or Segments) are at the center, surrounded by dimension tables.

### Relationships Setup:
- Go to the **Model View** in Power BI (the icon on the far left).
- Drag the `CustomerID` from the `Customer_Segments` table to the `CustomerID` in the `Transactions` table (1-to-many relationship).
- If you have a `Dates` or `Calendar` table, link its `Date` column to the `InvoiceDate` in `Transactions`.

### Text-based Diagram:
```text
   [Date Dimension]                  [Geography Dimension]
           |                                   |
     (1 to Many)                         (1 to Many)
           |                                   |
           v                                   v
  [Transactions (Fact)] <--(Many to 1)-- [Customer_Segments (Fact/Dim)]
```

## Step 3: DAX Measures
To create these measures, right-click on your `Customer_Segments` table and select **New Measure**. Copy and paste the following DAX codes:

```dax
Total Revenue = SUM(Customer_Segments[Monetary])
Total Customers = COUNTROWS(Customer_Segments)
Avg Order Value = DIVIDE([Total Revenue], SUM(Customer_Segments[Frequency]))
Avg Recency = AVERAGE(Customer_Segments[Recency])
Avg Frequency = AVERAGE(Customer_Segments[Frequency])
Champions Count = CALCULATE(COUNTROWS(Customer_Segments), Customer_Segments[Segment] = "Champions")
Champions % = DIVIDE([Champions Count], [Total Customers])
At Risk Count = CALCULATE(COUNTROWS(Customer_Segments), Customer_Segments[Segment] = "At Risk")
At Risk % = DIVIDE([At Risk Count], [Total Customers])
Revenue per Customer = DIVIDE([Total Revenue], [Total Customers])
```
*Explanation: These measures calculate the core KPIs of your customer base, allowing you to instantly assess the size and value of different segments, particularly your 'Champions' and 'At Risk' customers.*

## Step 4: Recommended Dashboard Layout

### Page 1: Executive Overview
- **Row 1:** KPI Cards displaying `Total Revenue`, `Total Customers`, `Avg Order Value`, and `Avg Recency`.
- **Row 2:** Segment Donut Chart (Segments as Legend, `Total Customers` as Values) on the left, Monthly Revenue Line Chart on the right.
- **Row 3:** Top 10 Countries Bar Chart (left), Revenue by Segment Bar Chart (right).
- **Top Header:** Add a Segment slicer (dropdown) to allow filtering the whole page.

### Page 2: Customer Deep Dive
- **RFM Bubble Chart:** Scatter chart (X-axis = `Frequency`, Y-axis = `Recency`, Bubble Size = `Monetary`, Legend/Color = `Segment`).
- **Customer Table:** A detailed table listing `CustomerID`, `Segment`, `Recency`, `Frequency`, and `Monetary`. Apply conditional formatting to highlight high values.
- **Segment Comparison Matrix:** Matrix visual showing Segments in rows, and measures like `Total Customers`, `Avg Recency`, `Avg Frequency`, `Avg Order Value` in columns.
- **Monetary Distribution:** Histogram (Column chart) showing bins of Monetary values on the X-axis and Count of Customers on the Y-axis.

### Page 3: Trends & Geography
- **Revenue Trend:** Line chart over time, with a hierarchy toggle to drill up/down between Daily, Weekly, and Monthly views.
- **Geographic Map:** Filled map or bubble map colored by `Total Revenue` per region/country.
- **Day of Week Analysis:** Bar chart showing `Total Revenue` or `Transactions` grouped by the day of the week.
- **Product Performance Table:** If product-level data is available, a table showing top-selling items and their associated customer segments.

## Step 5: Formatting & Theming
Use a professional dark theme to make the colors pop.
- **Background:** #1a1a2e
- **Cards:** #16213e
- **Accent 1:** #00D4AA (teal)
- **Accent 2:** #FF6B6B (coral)
- **Text:** #e0e0e0
- **Font:** Segoe UI or DIN

### Importing a Custom Theme JSON:
1. Save the JSON code below into a file named `RFM_DarkTheme.json`.
2. In Power BI, go to the **View** ribbon.
3. Click the dropdown arrow in the Themes gallery.
4. Select **Browse for themes** and choose your JSON file.

```json
{
  "name": "RFM Dark Theme",
  "dataColors": ["#00D4AA", "#FF6B6B", "#4ECDC4", "#FF8C42", "#FFEAA7", "#45B7D1", "#6C5CE7", "#DDA0DD"],
  "background": "#1a1a2e",
  "foreground": "#e0e0e0",
  "tableAccent": "#00D4AA",
  "visualStyles": {
    "*": {
      "*": {
        "outspace": [{"color": {"solid": {"color": "#1a1a2e"}}}],
        "background": [{"show": true, "color": {"solid": {"color": "#16213e"}}, "transparency": 0}],
        "visualHeader": [{"foreground": {"solid": {"color": "#e0e0e0"}}}]
      }
    },
    "page": {
      "*": {
        "background": [{"color": {"solid": {"color": "#1a1a2e"}}, "transparency": 0}],
        "outspace": [{"color": {"solid": {"color": "#1a1a2e"}}}]
      }
    }
  },
  "textClasses": {
    "label": {"fontFace": "Segoe UI", "color": "#e0e0e0"},
    "callout": {"fontFace": "DIN", "color": "#00D4AA"},
    "title": {"fontFace": "Segoe UI Semibold", "color": "#e0e0e0"}
  }
}
```

## Step 6: Segment Color Mapping
Ensure visual consistency across all pages by hardcoding the segment colors. Go to the Format pane of your visuals (like the Donut chart) -> Data colors, and apply these exact hex codes:
- **Champions:** #00D4AA
- **Loyal Customers:** #4ECDC4
- **Potential Loyalists:** #45B7D1
- **Recent Customers:** #96CEB4
- **Promising:** #FFEAA7
- **Need Attention:** #FF8C42
- **About to Sleep:** #DDA0DD
- **At Risk:** #FF6B6B
- **Can't Lose Them:** #FF85A2
- **Hibernating:** #6C5CE7
- **Lost:** #636e72

## Tips & Best Practices
- **Cross-Filtering:** Ensure interactions are enabled between visuals (Format > Edit Interactions). Clicking a segment in the donut chart should filter the rest of the page.
- **Bookmarks & Buttons:** Use bookmarks to toggle between different views (e.g., showing 'Count of Customers' vs 'Total Revenue' on the same map) without crowding the dashboard.
- **Tooltips:** Create a custom tooltip page containing a mini line chart of customer purchase history, and attach it to your main tables and bubble charts.
- **Conditional Formatting:** Apply background color conditional formatting to the Customer Table (e.g., highlight the Monetary column with a gradient from dark blue to bright teal).
