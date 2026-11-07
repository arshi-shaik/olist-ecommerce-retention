import pandas as pd
import numpy as np

def calculate_cohort_matrix(df):
    """
    Builds a percentage-based user cohort matrix to track month-over-month retention.
    Customers are grouped by the calendar month of their first purchase.
    """
    print("Building customer cohort retention matrix...")
    
    # Extract the calendar month for each order and the customer's first purchase month
    df['invoice_month'] = df['order_purchase_timestamp'].dt.to_period('M')
    df['cohort_month'] = df.groupby('customer_unique_id')['order_purchase_timestamp'].transform('min').dt.to_period('M')
    
    # Calculate the month distance index (Month 0, Month 1, Month 2, etc.)
    df['cohort_index'] = (df['invoice_month'] - df['cohort_month']).apply(lambda x: x.n)
    
    # Count unique users in each cohort month split by distance index
    cohort_counts = df.groupby(['cohort_month', 'cohort_index'])['customer_unique_id'].nunique().reset_index()
    cohort_pivot = cohort_counts.pivot(index='cohort_month', columns='cohort_index', values='customer_unique_id')
    
    # Divide each column by the baseline size (Month 0) to get percentage rates
    cohort_sizes = cohort_pivot.iloc[:, 0]
    retention_matrix = cohort_pivot.divide(cohort_sizes, axis=0)
    
    return retention_matrix

def calculate_rfm_segments(df):
    """
    Computes standard Recency, Frequency, and Monetary scores.
    Uses custom boundaries for frequency to handle Olist's heavy one-time buyer skew.
    """
    print("Generating behavioral RFM customer segments...")
    
    # Set the snapshot date to 1 day after the absolute final recorded order in the data
    snapshot_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    
    # Compute raw metrics per user
    rfm = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (snapshot_date - x.max()).days, # Recency
        'order_id': 'nunique',                                               # Frequency
        'payment_value': 'sum'                                               # Monetary Spend
    }).rename(columns={'order_purchase_timestamp': 'Recency', 'order_id': 'Frequency', 'payment_value': 'Monetary'})
    
    # Score Recency and Monetary into equal quintiles (1 to 5)
    rfm['R'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1]).astype(int) # Recent orders get a 5
    rfm['M'] = pd.qcut(rfm['Monetary'], q=5, labels=[1, 2, 3, 4, 5]).astype(int) # High spend gets a 5
    
    # Fix the Frequency skew manually: 90%+ bought once, so automatic qcut breaks.
    # Manual routing rules map raw order counts cleanly to logical scores:
    rfm['F'] = rfm['Frequency'].apply(lambda x: 1 if x == 1 else (4 if x == 2 else 5))
    
    # Assign descriptive user personas based on final scores
    def map_persona(row):
        r, f, m = row['R'], row['F'], row['M']
        
        # High-value users who haven't ordered recently
        if r in [2, 3] and f >= 4:
            return "At Risk - High Value (Priority Save)"
        # Highly engaged, top-spending active customers
        elif r >= 4 and f >= 4:
            return "Champions"
        # Historically great customers who went completely dormant months ago
        elif r == 1 and f >= 4:
            return "Cannot Lose Them - Inactive"
        # Inactive, one-time low spenders
        elif r <= 2 and f == 1:
            return "Hibernating / Lost"
        # Standard casual shoppers
        else:
            return "Standard Casual Shopper"
            
    rfm['Segment'] = rfm.apply(map_persona, axis=1)
    
    return rfm
