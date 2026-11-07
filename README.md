
Data-Driven Retention Engineering & Operational Root-Cause Analysis

📌 Project Overview

This project uses 100,000 real anonymized orders from the Olist Brazilian E-Commerce dataset on Kaggle to solve the biggest problem in digital retail: why customers drop off after their first purchase.
Instead of relying on a giant, messy notebook, I built this as a modular, production-ready Python pipeline. It handles data cleaning across multiple transaction tables, runs a behavioral segmentation model, and maps out exactly where operational issues are causing customer churn.

🎯 Core Business Objectives

• Map the Customer Lifespan: Build monthly cohort retention tables to track user activity over time.
• Find Hidden Opportunities: Use an RFM (Recency, Frequency, Monetary) model to locate high-value customer segments that are slipping away but still saveable.
• Pinpoint the Churn Triggers: Quantify the financial impact of shipping delays by linking logistics performance directly to customer review scores and repeat purchases.

🚀 Key Insights

1. The Loyalty Gap: Month 1 customer retention drops below 5%. Olist behaves more like a single-transaction marketplace than a repeat-purchase ecosystem, making active re-engagement strategies vital.
2. The High-ROI Target: The absolute best audience to target for a win-back campaign is the "At Risk - High Value" segment—users who previously spent a lot or bought multiple times but haven't returned in 60-120 days.
3. The First Impression Rules: Logistics make or break customer loyalty. When a customer's very first order is late, their average review score drops from 4.2 stars to 1.5 stars, completely killing the chance of a second order.

🛠️ Tech Stack & Dependencies

• Data Processing: Python 3.x, Pandas, NumPy
• Architecture: Modular scripts (/src) for production code + Jupyter Notebooks for exploration
• Data Source: Olist Brazilian E-Commerce Dataset
