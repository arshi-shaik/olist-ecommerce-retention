-- Step 1: Isolate each customer's onboarding "birth" month
WITH customer_cohorts AS (
    SELECT 
        customer_unique_id,
        DATE_TRUNC('month', MIN(order_purchase_timestamp)) AS cohort_month
    FROM olist_orders_dataset o
    JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
    WHERE order_status = 'delivered'
    GROUP BY customer_unique_id
),

-- Step 2: Extract individual order months and connect to user cohort profiles
order_activity AS (
    SELECT 
        c.customer_unique_id,
        c.cohort_month,
        DATE_TRUNC('month', o.order_purchase_timestamp) AS order_month,
        -- Calculate month intervals passed since user onboarding
        (EXTRACT(YEAR FROM o.order_purchase_timestamp) - EXTRACT(YEAR FROM c.cohort_month)) * 12 +
        (EXTRACT(MONTH FROM o.order_purchase_timestamp) - EXTRACT(MONTH FROM c.cohort_month)) AS cohort_index
    FROM olist_orders_dataset o
    JOIN olist_customers_dataset cust ON o.customer_id = cust.customer_id
    JOIN customer_cohorts c ON cust.customer_unique_id = c.customer_unique_id
    WHERE o.order_status = 'delivered'
)

-- Step 3: Pivot customer counts horizontally across cohort indices
SELECT 
    cohort_month,
    COUNT(DISTINCT CASE WHEN cohort_index = 0 THEN customer_unique_id END) AS month_0_baseline,
    COUNT(DISTINCT CASE WHEN cohort_index = 1 THEN customer_unique_id END) AS month_1_retained,
    COUNT(DISTINCT CASE WHEN cohort_index = 2 THEN customer_unique_id END) AS month_2_retained,
    COUNT(DISTINCT CASE WHEN cohort_index = 3 THEN customer_unique_id END) AS month_3_retained
FROM order_activity
GROUP BY cohort_month
ORDER BY cohort_month;
