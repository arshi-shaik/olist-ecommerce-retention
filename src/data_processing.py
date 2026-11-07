import pandas as pd
import os

def load_and_clean_data(data_dirpath='data/'):
    """
    Loads, cleans, and merges the core Olist database files.
    Standardizes timestamps and aggregates split payments per transaction.
    """
    print("Reading raw Olist e-commerce CSV files...")
    
    # Define expected source data file paths
    customers_path = os.path.join(data_dirpath, 'olist_customers_dataset.csv')
    orders_path = os.path.join(data_dirpath, 'olist_orders_dataset.csv')
    payments_path = os.path.join(data_dirpath, 'olist_order_payments_dataset.csv')
    reviews_path = os.path.join(data_dirpath, 'olist_order_reviews_dataset.csv')
    
    # Fail early if any source file is missing from the directory
    for path in [customers_path, orders_path, payments_path, reviews_path]:
        if not os.path.exists(path):
            raise FileNotFoundError(
                f"Missing file error: {os.path.basename(path)} not found in '{data_dirpath}'. "
                "Please verify file placement before running the pipeline."
            )
            
    # Load dataset matrices
    customers = pd.read_csv(customers_path)
    orders = pd.read_csv(orders_path)
    payments = pd.read_csv(payments_path)
    reviews = pd.read_csv(reviews_path)
    
    # Filter for completed cycles to isolate successful deliveries
    orders = orders[orders['order_status'] == 'delivered'].copy()
    
    # Parse date strings into timestamps for tracking metrics
    date_columns = [
        'order_purchase_timestamp', 
        'order_approved_at', 
        'order_delivered_customer_date', 
        'order_estimated_delivery_date'
    ]
    for col in date_columns:
        orders[col] = pd.to_datetime(orders[col])
        
    # Aggregate transaction records to handle split payments (vouchers, multi-cards)
    print("Aggregating multi-row payment volumes per transaction...")
    payments_rolled_up = payments.groupby('order_id')['payment_value'].sum().reset_index()
    
    # Drop survey duplicates to ensure we only evaluate a user's final review score
    reviews_sorted = reviews.sort_values('review_creation_date')
    reviews_deduped = reviews_sorted.drop_duplicates(subset=['order_id'], keep='last')
    
    # Combine datasets into a single analytics-ready table
    print("Merging relational tracking schemas...")
    master_df = orders.merge(customers, on='customer_id', how='inner')
    master_df = master_df.merge(payments_rolled_up, on='order_id', how='left')
    master_df = master_df.merge(reviews_deduped[['order_id', 'review_score']], on='order_id', how='left')
    
    # Impute missing values with numeric fallbacks
    master_df['payment_value'] = master_df['payment_value'].fillna(0)
    
    print(f"Data cleanup successful. Generated a clean view of {master_df.shape:,} entries.")
    return master_df

if __name__ == "__main__":
    # Local runtime execution check
    try:
        processed_data = load_and_clean_data()
        print(processed_data.head(3))
    except Exception as e:
        print(f"Local workflow check failed: {e}")
