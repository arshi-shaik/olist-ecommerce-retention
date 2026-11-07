import pandas as pd
import numpy as np

def calculate_cohort_matrix(df):
    """
    Computes a percentage-based customer cohort retention matrix.
    """
    print("📊 Computing customer cohort retention matrix...")
    df['invoice_month'] = df['order_purchase_timestamp'].dt.to_period('M')
    df['cohort_month'] = df.groupby('customer_unique_id')['order_purchase_timestamp'].transform('min').dt.to_period('M')
    df['cohort_index'] = (df['invoice_month'] - df['cohort_month']).apply(lambda x: x.n)
    
    cohort_counts = df.groupby(['cohort_month', 'cohort_index'])['customer_unique_id'].nunique().reset_index()
    cohort_pivot = cohort_counts.pivot(index='cohort_month', columns='cohort_index', values='customer_unique_id')
    
    cohort_sizes = cohort_pivot.iloc[:, 0]
    retention_matrix = cohort_pivot.divide(cohort_sizes, axis=0)
    return retention_matrix

def calculate_rfm_segments(df):
    """
    Computes Recency, Frequency, and Monetary scores with custom bins.
    """
    print("🎯 Engineering behavioral RFM clusters...")
    snapshot_date = df['order_purchase_timestamp'].max() + pd.Timedelta(days=1)
    
    rfm = df.groupby('customer_unique_id').agg({
        'order_purchase_timestamp': lambda x: (snapshot_date - x.max()).days,
        'order_id': 'nunique',
        'payment_value': 'sum'
    }).rename(columns={'order_purchase_timestamp': 'Recency', 'order_id': 'Frequency', 'payment_value': 'Monetary'})
    
    rfm['R'] = pd.qcut(rfm['Recency'], q=5, labels=[5, 4, 3, 2, 1]).astype(int)
    rfm['M'] = pd.qcut(rfm['Monetary'], q=5, labels=[1, 2, 3, 4, 5]).astype(int)
    rfm['F'] = rfm['Frequency'].apply(lambda x: 1 if x == 1 else (4 if x == 2 else 5))
    
    def segment_routing_tree(row):
        r, f, m = row['R'], row['F'], row['M']
        if r in [2, 3] and f >= 4:
            return "At Risk - High Value (Priority Save)"
        elif r >= 4 and f >= 4:
            return "Champions"
        elif r == 1 and f >= 4:
            return "Cannot Lose Them - Inactive"
        elif r <= 2 and f == 1:
            return "Hibernating / Lost"
        else:
            return "Standard Casual Shopper"
            
    rfm['Segment'] = rfm.apply(segment_routing_tree, axis=1)
    return rfm
