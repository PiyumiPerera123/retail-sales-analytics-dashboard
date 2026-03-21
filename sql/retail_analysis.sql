-- RETAIL SALES ANALYSIS SQL SCRIPT
USE retail_Project;

-- KPI CALCULATIONS

-- Total Revenue
SELECT ROUND(SUM(revenue),2) AS total_revenue
FROM sales_fact_table;

-- Total Orders
SELECT COUNT(DISTINCT order_id) AS total_orders
FROM sales_fact_table;

-- Total Customers
SELECT COUNT(DISTINCT customer_id) AS total_customers
FROM sales_fact_table;

-- Average Order Value
SELECT ROUND(SUM(revenue)/COUNT(DISTINCT order_id),2) AS avg_order_value
FROM sales_fact_table;

-- MONTHLY TREND
SELECT 
    year_month_txt,
    ROUND(SUM(revenue),2) AS total_revenue
FROM sales_fact_table
GROUP BY year_month_txt
ORDER BY year_month_txt;

-- REVENUE BY STATE

SELECT 
    state,
    ROUND(SUM(revenue),2) AS total_revenue
FROM sales_fact_table
GROUP BY state
ORDER BY total_revenue DESC;

-- PAYMENT METHOD ANALYSIS

SELECT 
    payment_method,
    COUNT(DISTINCT order_id) AS total_orders,
    ROUND(SUM(revenue),2) AS total_revenue
FROM sales_fact_table
GROUP BY payment_method
ORDER BY total_revenue DESC;

-- PRODUCT CATEGORY PERFORMANCE

SELECT 
    category,
    ROUND(SUM(revenue),2) AS total_revenue
FROM sales_fact_table
GROUP BY category
ORDER BY total_revenue DESC;

-- CUSTOMER ANALYSIS

-- Customers by Gender
SELECT 
    gender,
    COUNT(DISTINCT customer_id) AS total_customers
FROM sales_fact_table
GROUP BY gender;

-- Revenue by Age Group
SELECT 
    CASE
        WHEN age BETWEEN 18 AND 25 THEN '18-25'
        WHEN age BETWEEN 26 AND 35 THEN '26-35'
        WHEN age BETWEEN 36 AND 45 THEN '36-45'
        WHEN age BETWEEN 46 AND 55 THEN '46-55'
        ELSE '55+'
    END AS age_group,
    ROUND(SUM(revenue),2) AS total_revenue
FROM sales_fact_table
GROUP BY age_group;


-- DATA QUALITY CHECK

-- Null values check
SELECT COUNT(*) AS null_records
FROM sales_fact_table
WHERE customer_id IS NULL;

-- Negative revenue check
SELECT *
FROM sales_fact_table
WHERE revenue <= 0;