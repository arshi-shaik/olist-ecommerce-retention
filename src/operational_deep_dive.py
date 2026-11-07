import pandas as pd

def analyze_delivery_impact(df):
    """
    Analyzes how delivery performance impacts customer review scores.
    Calculates the difference between estimated and actual delivery dates.
    """
    print("Analyzing logistics performance against customer reviews...")
    
    # Calculate the variance window in days
    # Positive numbers = Late delivery | Negative numbers = Arrived early
    df['delivery_delay_days'] = (df['order_delivered_customer_date'] - df['order_estimated_delivery_date']).dt.days
    
    # Drop rows missing shipping tracking timestamps or review metrics
    clean_ops = df.dropna(subset=['delivery_delay_days', 'review_score']).copy()
    
    # Bucket transactions by delivery performance status
    clean_ops['delivery_performance'] = clean_ops['delivery_delay_days'].apply(
        lambda x: 'Late Delivery' if x > 0 else 'On-Time / Early'
    )
    
    # Aggregate average review scores and totals across brackets
    summary_stats = clean_ops.groupby('delivery_performance').agg({
        'review_score': 'mean',
        'customer_unique_id': 'count'
    }).rename(columns={
        'review_score': 'Average_Review_Score', 
        'customer_unique_id': 'Total_Order_Volume'
    })
    
    # Format the review outputs to a readable decimal layout
    summary_stats['Average_Review_Score'] = summary_stats['Average_Review_Score'].round(2)
    
    print("Operational deep dive complete.")
    return summary_stats

if __name__ == "__main__":
    print("Operational module loaded successfully.")
