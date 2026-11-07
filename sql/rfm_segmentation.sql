-- Step 1: Calculate raw behavioral values relative to the data log boundaries
WITH raw_rfm AS (
    SELECT 
        c.customer_unique_id,
        -- Mocking a static snapshot evaluation checkpoint date
        DATE('2018-09-04') - DATE(MAX(o.order_purchase_timestamp)) AS recency,
        COUNT(DISTINCT o.order_id) AS frequency,
        SUM(p.payment_value) AS monetary
    FROM olist_orders_dataset o
    JOIN olist_customers_dataset c ON o.customer_id = c.customer_id
    LEFT JOIN olist_order_payments_dataset p ON o.order_id = p.order_id
    WHERE o.order_status = 'delivered'
    GROUP BY c.customer_unique_id
),

-- Step 2: Assign quintile rankings for Recency/Monetary and map Frequency thresholds
scored_rfm AS (
    SELECT 
        customer_unique_id,
        recency, frequency, monetary,
        NTILE(5) OVER (ORDER BY recency DESC) AS r_score, -- Lower recency days = higher score value
        NTILE(5) OVER (ORDER BY monetary ASC) AS m_score,  -- Higher monetary spend = higher score value
        CASE 
            WHEN frequency = 1 THEN 1
            WHEN frequency = 2 THEN 4
            ELSE 5
        END AS f_score
    FROM raw_rfm
)

-- Step 3: Route final score combinations into descriptive audience persona tiers
SELECT 
    customer_unique_id,
    recency, frequency, monetary,
    CASE 
        WHEN r_score IN (2, 3) AND f_score >= 4 THEN 'At Risk - High Value (Priority Save)'
        WHEN r_score >= 4 AND f_score >= 4 THEN 'Champions'
        WHEN r_score <= 2 AND f_score = 1 THEN 'Hibernating / Lost'
        ELSE 'Standard Casual Shopper'
    END AS customer_segment
FROM scored_rfm;
