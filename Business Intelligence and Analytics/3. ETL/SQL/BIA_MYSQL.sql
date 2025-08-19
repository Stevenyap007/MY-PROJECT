CREATE DATABASE sales_dw;
USE sales_dw;

-- ---------------------------------------------------------------------------------------------
-- CREATING TABLE FOR DIMENSION
DESCRIBE dim_customer;
CREATE TABLE dim_customer (
    customer_key INT PRIMARY KEY AUTO_INCREMENT,   -- Surrogate key for DW joins
    customer_id INT,                       -- Natural key from source
    customer_fname VARCHAR(100),
    customer_lname VARCHAR(100),
    customer_email VARCHAR(100),
    customer_segment VARCHAR(50),
    customer_country VARCHAR(50),
    customer_state VARCHAR(50),
    customer_city VARCHAR(50),
    customer_street VARCHAR(100),
    customer_zipcode VARCHAR(20)
);

CREATE TABLE dim_product (
    Product_ID INT PRIMARY KEY AUTO_INCREMENT,
    Product_Card_ID VARCHAR(50),
    Product_Name VARCHAR(255),
    Product_Category_ID INT,
    Product_Description TEXT,
    Product_Image_URL TEXT,
    Product_Price DECIMAL(10,2),
    Product_Status INT
);

CREATE TABLE dim_date (
    date_id BIGINT PRIMARY KEY,               -- Format: YYYYMMDD
    full_date DATETIME,
    year INT,
    semester VARCHAR(2),                   -- NEW: 'S1' or 'S2'
    quarter VARCHAR(2),
    month INT,
    month_name VARCHAR(15),
    day INT,
    day_name VARCHAR(15),
    week_of_year INT,                      -- Optional, see below
    is_weekend BOOLEAN                     -- Optional, see below
);

CREATE TABLE dim_shipping_mode (
    shipping_mode_id INT PRIMARY KEY AUTO_INCREMENT,
    shipping_mode_name VARCHAR(50) NOT NULL
);

CREATE TABLE dim_market (
    market_id INT PRIMARY KEY AUTO_INCREMENT,
    market_name VARCHAR(50) NOT NULL
);

CREATE TABLE dim_segment (
    segment_id INT PRIMARY KEY AUTO_INCREMENT,
    segment_name VARCHAR(100)
);

CREATE TABLE dim_category (
    Product_Category_ID INT PRIMARY KEY AUTO_INCREMENT,     -- Unique product category identifier
    Category_ID INT,                         -- Higher-level category, can repeat
    Category_Name VARCHAR(255),
    Department_ID INT,
    Department_Name VARCHAR(255)
);

CREATE TABLE dim_order_location (
    order_location_id INT PRIMARY KEY AUTO_INCREMENT,
    order_city VARCHAR(100),
    order_state VARCHAR(100),
    order_country VARCHAR(100),
    order_region VARCHAR(100),
    order_zipcode VARCHAR(20)
);

CREATE TABLE dim_customer_location (
    customer_location_id INT PRIMARY KEY AUTO_INCREMENT,
    customer_street VARCHAR(150),
    customer_city VARCHAR(100),
    customer_state VARCHAR(100),
    customer_country VARCHAR(100),
    customer_zipcode VARCHAR(20),
    latitude DECIMAL(10,7),
    longitude DECIMAL(10,7)
);


-- Buat table yang menerupai database csv

-- CREATE TABLE raw_supply_data (
--     `Type` VARCHAR(50),
--     `Days for shipping (real)` INT,
--     `Days for shipment (scheduled)` INT,
--     `Benefit per order` DECIMAL(15,2),
--     `Sales per customer` DECIMAL(15,2),
--     `Delivery Status` VARCHAR(50),
--     `Late_delivery_risk` TINYINT,
--     `Category Id` INT,
--     `Category Name` VARCHAR(255),
--     `Customer City` VARCHAR(100),
--     `Customer Country` VARCHAR(100),
--     `Customer Email` VARCHAR(150),
--     `Customer Fname` VARCHAR(100),
--     `Customer Id` INT,
--     `Customer Lname` VARCHAR(100),
--     `Customer Password` VARCHAR(255),
--     `Customer Segment` VARCHAR(50),
--     `Customer State` VARCHAR(50),
--     `Customer Street` VARCHAR(150),
--     `Customer Zipcode` VARCHAR(20),
--     `Department Id` INT,
--     `Department Name` VARCHAR(255),
--     `Latitude` DECIMAL(10,8),
--     `Longitude` DECIMAL(11,8),
--     `Market` VARCHAR(50),
--     `Order City` VARCHAR(100),
--     `Order Country` VARCHAR(100),
--     `Order Customer Id` INT,
--     `order date (DateOrders)` VARCHAR(50),
--     `Order Id` INT,
--     `Order Item Cardprod Id` INT,
--     `Order Item Discount` DECIMAL(15,2),
--     `Order Item Discount Rate` DECIMAL(10,4),
--     `Order Item Id` INT,
--     `Order Item Product Price` DECIMAL(15,2),
--     `Order Item Profit Ratio` DECIMAL(10,4),
--     `Order Item Quantity` INT,
--     `Sales` DECIMAL(15,2),
--     `Order Item Total` DECIMAL(15,2),
--     `Order Profit Per Order` DECIMAL(15,2),
--     `Order Region` VARCHAR(100),
--     `Order State` VARCHAR(100),
--     `Order Status` VARCHAR(50),
--     `Order Zipcode` VARCHAR(20),
--     `Product Card Id` INT,
--     `Product Category Id` INT,
--     `Product Description` TEXT,
--     `Product Image` TEXT,
--     `Product Name` VARCHAR(255),
--     `Product Price` DECIMAL(15,2),
--     `Product Status` TINYINT,
--     `shipping date (DateOrders)` VARCHAR(50),
--     `Shipping Mode` VARCHAR(50)
-- );


-- ---------------------------------------------------------------------------------------------------------
-- Create fact table buat masing masing busines process
-- DROP TABLE fact_order;
CREATE TABLE fact_order (
    Order_ID INT NOT NULL,
    Product_ID INT NOT NULL,
    Date_ID BIGINT NOT NULL,  -- This stores Order Date's date_id from dim_date
    Customer_ID INT NOT NULL,
    Market_ID INT NOT NULL,
    Location_ID INT NOT NULL,
    Type VARCHAR(50),
    Order_Status VARCHAR(50),
    Quantity INT,
    Order_Item_Total DECIMAL(15,2),
    Discount DECIMAL(15,2),
    Profit DECIMAL(15,2),
    
    -- Composite Primary Key
    PRIMARY KEY (Order_ID, Product_ID),

    -- Foreign Keys
    CONSTRAINT fk_fact_order_date
        FOREIGN KEY (Date_ID) REFERENCES dim_date(date_id),
    CONSTRAINT fk_fact_order_customer
        FOREIGN KEY (Customer_ID) REFERENCES dim_customer(customer_key),
    CONSTRAINT fk_fact_order_product
        FOREIGN KEY (Product_ID) REFERENCES dim_product(product_id),
    CONSTRAINT fk_fact_order_market
        FOREIGN KEY (Market_ID) REFERENCES dim_market(market_id),
    CONSTRAINT fk_fact_order_location
        FOREIGN KEY (Location_ID) REFERENCES dim_order_location(order_location_id)
);

-- Masukkin value beberapa variable dari raw supply data ke fact_Order 
INSERT INTO fact_order (
    Order_ID,
    Product_ID,
    Date_ID,
    Customer_ID,
    Market_ID,
    Location_ID,
    Type,
    Order_Status,
    Quantity,
    Order_Item_Total,
    Discount,
    Profit
)
SELECT
    r.`Order ID`,
    dp.Product_ID,
    dd.date_id,
    dc.customer_key,
    dm.market_id,
    dol.order_location_id,
    r.`Type`,
    r.`Order Status`,
    SUM(r.`Order Item Quantity`) AS Quantity,
    SUM(r.`Order Item Total`) AS Order_Item_Total,
    SUM(r.`Order Item Discount`) AS Discount,
    SUM(r.`Order Profit Per Order`) AS Profit
FROM raw_supply_data r
JOIN dim_date dd
    ON dd.full_date = STR_TO_DATE(r.`order date (DateOrders)`, '%c/%e/%Y %H:%i')
JOIN dim_customer dc
    ON TRIM(r.`Customer Id`) = TRIM(dc.customer_id)
JOIN dim_product dp
    ON r.`Product Card Id` = dp.Product_Card_ID
JOIN dim_market dm
    ON r.`Market` = dm.market_name
JOIN dim_order_location dol
    ON r.`Order City` = dol.order_city
    AND r.`Order State` = dol.order_state
    AND r.`Order Country` = dol.order_country
    AND r.`Order Region` = dol.order_region
	AND (
    r.`Order Zipcode` = dol.order_zipcode OR (
      (r.`Order Zipcode` IS NULL OR r.`Order Zipcode` = '') AND 
      (dol.order_zipcode IS NULL OR dol.order_zipcode = '')
    )
  )
GROUP BY
    r.`Order ID`,
    dp.Product_ID,
    dd.date_id,
    dc.customer_key,
    dm.market_id,
    dol.order_location_id,
    r.`Type`,
    r.`Order Status`;

-- ------------------------------------------------------------------------------------

Create fact table buat shipping and delivery 
DROP TABLE fact_shipping;
CREATE TABLE fact_shipping (
    Shipping_ID INT AUTO_INCREMENT PRIMARY KEY,
    
    Customer_ID INT,
    Shipping_Date_ID BIGINT NOT NULL,
    Shipping_Mode_ID INT,
    Location_ID INT,
    Market_ID INT,

    Type VARCHAR(50),
    Delivery_Status VARCHAR(50),
    
    Days_Shipping_Real INT,
    Days_Shipping_Scheduled INT,
    Late_Delivery_Risk BOOLEAN,

    -- Foreign Key Constraints
    CONSTRAINT fk_fact_shipping_customer
        FOREIGN KEY (Customer_ID) REFERENCES dim_customer(customer_key),
    CONSTRAINT fk_fact_shipping_date
        FOREIGN KEY (Shipping_Date_ID) REFERENCES dim_date(date_id),
    CONSTRAINT fk_fact_shipping_mode
        FOREIGN KEY (Shipping_Mode_ID) REFERENCES dim_shipping_mode(shipping_mode_id),
    CONSTRAINT fk_fact_shipping_location
        FOREIGN KEY (Location_ID) REFERENCES dim_order_location(order_location_id),
    CONSTRAINT fk_fact_shipping_market
        FOREIGN KEY (Market_ID) REFERENCES dim_market(market_id)
);

Masukkin value beberapa variable dari raw supply data ke Fact_Shipping
INSERT INTO fact_shipping (
    Customer_ID,
    Shipping_Date_ID,
    Shipping_Mode_ID,
    Location_ID,
    Market_ID,
    Type,
    Delivery_Status,
    Days_Shipping_Real,
    Days_Shipping_Scheduled,
    Late_Delivery_Risk
)
SELECT DISTINCT
    dc.customer_key,
    dd.date_id,
    dsm.shipping_mode_id,
    dol.order_location_id,
    dm.market_id,
    rs.`Type`,
    rs.`Delivery Status`,
    rs.`Days for shipping (real)`,
    rs.`Days for shipment (scheduled)`,
    rs.`Late_delivery_risk`
FROM raw_supply_data rs
JOIN dim_customer dc 
    ON rs.`Customer Id` = dc.customer_id
JOIN dim_date dd 
    ON dd.full_date = STR_TO_DATE(rs.`shipping date (DateOrders)`, '%c/%e/%Y %H:%i')
JOIN dim_shipping_mode dsm 
    ON rs.`Shipping Mode` = dsm.shipping_mode_name 
JOIN dim_order_location dol 
    ON rs.`Order City` = dol.order_city 
    AND rs.`Order State` = dol.order_state
    AND rs.`Order Country` = dol.order_country
    AND rs.`Order Region` = dol.order_region
    AND (
    rs.`Order Zipcode` = dol.order_zipcode OR (
      (rs.`Order Zipcode` IS NULL OR rs.`Order Zipcode` = '') AND 
      (dol.order_zipcode IS NULL OR dol.order_zipcode = '')
    )
  )
JOIN dim_market dm 
    ON rs.`Market` = dm.market_name;


-- ---------------------------------------------------------------------------------------------------------


Create fact table buat fact_customer_engagement
DROP TABLE fact_customer_engagement;
CREATE TABLE fact_customer_engagement (
    Customer_Engagement_ID INT AUTO_INCREMENT PRIMARY KEY NOT NULL,  -- FK to dim_customer.customer_key
    Customer_ID INT NOT NULL,
    Segment_ID INT NOT NULL,             -- FK to dim_customer_segment (optional)
    Location_ID INT NOT NULL,            -- FK to dim_order_location
    Market_ID INT NOT NULL,              -- FK to dim_market
    Last_Order_Date_ID BIGINT,           -- FK to dim_date (last order date)

    Total_Orders INT,
    Total_Items INT,
    Total_Amount DECIMAL(15, 2),
    Total_Sales DECIMAL(15, 2),
    Total_Profit DECIMAL(15, 2),
    Avg_Order_Value DECIMAL(15, 2),
    Avg_Days_to_Ship DECIMAL(10, 2),

    CONSTRAINT fk_customer_engagement_customer
        FOREIGN KEY (Customer_ID) REFERENCES dim_customer(customer_key),
    CONSTRAINT fk_customer_engagement_segment
        FOREIGN KEY (Segment_ID) REFERENCES dim_segment(segment_id),
    CONSTRAINT fk_customer_engagement_location
        FOREIGN KEY (Location_ID) REFERENCES dim_customer_location(customer_location_id),
    CONSTRAINT fk_customer_engagement_market
        FOREIGN KEY (Market_ID) REFERENCES dim_market(market_id),
    CONSTRAINT fk_customer_engagement_last_order_date
        FOREIGN KEY (Last_Order_Date_ID) REFERENCES dim_date(date_id)
);

-- Masukkin value beberapa variable dari raw supply data ke fact_customer_engagement
INSERT INTO fact_customer_engagement (
    Customer_ID,
    Segment_ID,
    Location_ID,
    Market_ID,
    Last_Order_Date_ID,
    Total_Orders,
    Total_Items,
    Total_Amount,
    Total_Sales,
    Total_Profit,
    Avg_Order_Value,
    Avg_Days_to_Ship
)
SELECT
    dc.customer_key,
    ds.segment_id,
    dcl.customer_location_id,
    dm.market_id,
    MAX(dd.date_id) AS Last_Order_Date_ID,
    COUNT(DISTINCT r.`Order Id`) AS Total_Orders,
    SUM(r.`Order Item Quantity`) AS Total_Items,
    SUM(r.`Order Item Total`) AS Total_Amount,
    SUM(r.`Sales per customer`) AS Total_Sales,
    SUM(r.`Benefit per order`) AS Total_Profit,
    SUM(r.`Sales per customer`) / COUNT(DISTINCT r.`Order Id`) AS Avg_Order_Value,
    AVG(r.`Days for shipping (real)`) AS Avg_Days_to_Ship
FROM
    raw_supply_data r
JOIN
    dim_customer dc 
    ON TRIM(r.`Customer Id`) = TRIM(dc.customer_id)
JOIN
    dim_segment ds 
    ON r.`Customer Segment` = ds.segment_name
JOIN dim_customer_location dcl
    ON r.`Customer City` = dcl.customer_city
    AND r.`Customer State` = dcl.customer_state
    AND r.`Customer Country` = dcl.customer_country
	AND r.`Customer Zipcode` = dcl.customer_zipcode
    AND r.`Latitude` = dcl.latitude
    AND r.`Longitude` = dcl.longitude
JOIN dim_market dm
    ON r.`Market` = dm.market_name
JOIN dim_date dd
    ON dd.full_date = STR_TO_DATE(r.`order date (DateOrders)`, '%c/%e/%Y %H:%i')
GROUP BY
    dc.customer_key,
    ds.segment_id,
    dcl.customer_location_id,
	dm.market_id;
SHOW WARNINGS;

-- --------------------------------------------------------------------------------------------
-- Create fact table buat Fact_Product_Stats
-- ===========================================================
-- FACT: Product Stats (aggregated per date per product)
-- Grain: One row per date_id + product_id (+ category_id)
-- ===========================================================
-- drop TABLE fact_product_stats;
CREATE TABLE fact_product_stats (
    date_id BIGINT NOT NULL,                  -- FK to dim_date
    product_id INT NOT NULL,                  -- FK to dim_product
    category_id INT NOT NULL,                  -- FK to dim_category

    total_orders INT,
    units_sold INT,
    total_sales DECIMAL(15, 2),
    total_profit DECIMAL(15, 2),
    avg_discount DECIMAL(10, 2),
    avg_shipping_days DECIMAL(10, 2),
    avg_profit_margin DECIMAL(10, 4),
    total_customers INT,

    -- Primary Key (aggregated grain)
    PRIMARY KEY (date_id, product_id),

    -- Foreign Key Constraints
    CONSTRAINT fk_fps_date
        FOREIGN KEY (date_id) REFERENCES dim_date(date_id),
    CONSTRAINT fk_fps_product
        FOREIGN KEY (product_id) REFERENCES dim_product(product_id),
    CONSTRAINT fk_fps_category
        FOREIGN KEY (category_id) REFERENCES dim_category(product_category_id)
);

-- ============================================
-- Populate fact_product_stats
-- Grain: date_id + product_id
-- ============================================

INSERT INTO fact_product_stats (
    date_id,
    product_id,
    category_id,
    total_orders,
    units_sold,
    total_sales,
    total_profit,
    avg_discount,
    avg_shipping_days,
    avg_profit_margin,
    total_customers
)
SELECT
    dd.date_id,
    dp.product_id,
    dcg.product_category_id,

    COUNT(DISTINCT r.`Order Id`) AS total_orders,
    SUM(r.`Order Item Quantity`) AS units_sold,
    SUM(r.`Order Item Total`) AS total_sales,
    SUM(r.`Order Profit Per Order`) AS total_profit,
    AVG(r.`Order Item Discount Rate`) AS avg_discount,
    AVG(r.`Days for shipping (real)`) AS avg_shipping_days,
    (SUM(r.`Order Profit Per Order`) / NULLIF(SUM(r.`Order Item Total`),0)) AS avg_profit_margin,
    COUNT(DISTINCT r.`Customer Id`) AS total_customers

FROM raw_supply_data r
JOIN dim_date dd
    ON dd.full_date = STR_TO_DATE(r.`order date (DateOrders)`, '%c/%e/%Y %H:%i')
JOIN dim_product dp
    ON r.`Product Card Id` = dp.Product_Card_ID
JOIN dim_category dcg
    ON dp.Product_Category_ID = dcg.product_category_id
GROUP BY
    dd.date_id,
    dp.product_id,
    dcg.product_category_id;

-- SHOW WARNINGS;

-- --------------------------------------------------------------------------------------------
Create fact table buat Fact_Sales
drop TABLE fact_sales;
CREATE TABLE fact_sales (
    Sales_ID INT PRIMARY KEY AUTO_INCREMENT,
    Product_ID INT NOT NULL,
    Customer_ID INT NOT NULL,
    Order_Date_ID BIGINT NOT NULL,
    Location_ID INT NOT NULL,
    Market_ID INT NOT NULL,
    Segment_ID INT NOT NULL,
    Shipping_Mode_ID INT NOT NULL,
	Order_ID VARCHAR(50), -- from CSV, no FK constraint if dim_order not present
    Sales_Per_Customer DECIMAL(12,2),
    Benefit_Per_Order DECIMAL(12,2),
    Order_Profit_Ratio DECIMAL(5,2),
    Days_for_Shipping_Real INT,
    Days_for_Shipment_Scheduled INT,
    Late_Delivery_Risk TINYINT, -- 0 or 1
    Product_Price DECIMAL(12,2),
    Discount DECIMAL(5,2),
    Quantity INT,
    Total_Sales DECIMAL(12,2),
    Total_Profit DECIMAL(12,2),
    
    -- Foreign key constraints to dimensions
    CONSTRAINT fk_fs_product
		FOREIGN KEY (Product_ID) REFERENCES dim_product(product_id),
	CONSTRAINT fk_fs_customer    
		FOREIGN KEY (Customer_ID) REFERENCES dim_customer(customer_key),
	CONSTRAINT fk_fs_order_date
		FOREIGN KEY (Order_Date_ID ) REFERENCES dim_date(date_id),
	CONSTRAINT fk_fs_location
		FOREIGN KEY (Location_ID) REFERENCES dim_order_location(order_location_id),
	CONSTRAINT fk_fs_market
		FOREIGN KEY (Market_ID) REFERENCES dim_market(market_id),
	CONSTRAINT fk_fs_segment
		FOREIGN KEY (Segment_ID) REFERENCES dim_segment(segment_id),
	CONSTRAINT fk_fs_shipping_mode
		FOREIGN KEY (Shipping_Mode_ID) REFERENCES dim_shipping_mode(shipping_mode_id)
);

-- Masukkin value beberapa variable dari raw supply data ke Fact_Sales

INSERT INTO fact_sales (
    Product_ID,
    Customer_ID,
    Order_Date_ID,
    Location_ID,
    Market_ID,
    Segment_ID,
    Shipping_Mode_ID,
    Order_ID,
    Sales_Per_Customer,
    Benefit_Per_Order,
    Order_Profit_Ratio,
    Days_for_Shipping_Real,
    Days_for_Shipment_Scheduled,
    Late_Delivery_Risk,
    Product_Price,
    Discount,
    Quantity,
    Total_Sales,
    Total_Profit
)
SELECT DISTINCT
    dp.Product_ID,
    dc.Customer_Key,
    dd.Date_ID,
    dol.Order_Location_ID,
    dm.Market_ID,
    ds.Segment_ID,
    dsm.Shipping_Mode_ID,
    r.`Order ID`,
    r.`Sales per customer`,
    r.`Benefit per order`,
    r.`Order Item Profit Ratio`,
    r.`Days for shipping (real)`,
    r.`Days for shipment (scheduled)`,
    r.`Late_delivery_risk`,
    r.`Product Price`,
    r.`Order Item Discount Rate`,
    r.`Order Item Quantity`,
    (r.`Order Item Product Price` - r.`Order Item Discount` ) *  r.`Order Item Quantity` AS Total_Sales,
    r.`Benefit per order` * r.`Order Item Quantity` AS Total_Profit
FROM raw_supply_data r
JOIN dim_product dp 
    ON r.`Product Card Id` = dp.Product_Card_ID
JOIN dim_customer dc
    ON TRIM(r.`Customer Id`) = TRIM(dc.customer_id)
JOIN dim_date dd
    ON dd.full_date = STR_TO_DATE(r.`order date (DateOrders)`, '%c/%e/%Y %H:%i')
JOIN dim_order_location dol
    ON r.`Order City` = dol.order_city
    AND r.`Order State` = dol.order_state
    AND r.`Order Country` = dol.order_country
    AND r.`Order Region` = dol.order_region
	AND (
    r.`Order Zipcode` = dol.order_zipcode OR (
      (r.`Order Zipcode` IS NULL OR r.`Order Zipcode` = '') AND 
      (dol.order_zipcode IS NULL OR dol.order_zipcode = '')
    )
  )
JOIN dim_market dm
    ON r.`Market` = dm.market_name
JOIN dim_segment ds
    ON r.`Customer Segment` = ds.segment_name
JOIN dim_shipping_mode dsm
    ON r.`Shipping Mode` = dsm.shipping_mode_name ;






-- --------------------------Validate Relationships -------------------------------
-- ============================================
-- Validate Relationshipss
-- Grain: Fact Sales
-- ============================================
-- SELECT fs.Sales_ID, fs.Product_ID
-- FROM Fact_Sales fs
-- LEFT JOIN Dim_Product dp
--     ON fs.Product_ID = dp.Product_ID
-- WHERE dp.Product_ID IS NULL;

-- SELECT fs.Sales_ID, fs.Customer_ID
-- FROM Fact_Sales fs
-- LEFT JOIN Dim_Customer dc
--     ON fs.Customer_ID = dc.Customer_Key
-- WHERE dc.Customer_Key IS NULL;

-- SELECT fs.Sales_ID, fs.Order_Date_ID
-- FROM Fact_Sales fs
-- LEFT JOIN Dim_Date dd
--     ON fs.Order_Date_ID = dd.Date_ID
-- WHERE dd.Date_ID IS NULL;

-- SELECT fs.Sales_ID, fs.Location_ID
-- FROM Fact_Sales fs
-- LEFT JOIN Dim_Order_Location dol
--     ON fs.Location_ID = dol.Order_Location_ID
-- WHERE dol.Order_Location_ID IS NULL;

-- SELECT fs.Sales_ID, fs.Market_ID
-- FROM Fact_Sales fs
-- LEFT JOIN Dim_Market dm
--     ON fs.Market_ID = dm.Market_ID
-- WHERE dm.Market_ID IS NULL;

-- SELECT fs.Sales_ID, fs.Segment_ID
-- FROM Fact_Sales fs
-- LEFT JOIN Dim_Segment ds
--     ON fs.Segment_ID = ds.Segment_ID
-- WHERE ds.Segment_ID IS NULL;

-- SELECT fs.Sales_ID, fs.Shipping_Mode_ID
-- FROM Fact_Sales fs
-- LEFT JOIN Dim_Shipping_Mode dsm
--     ON fs.Shipping_Mode_ID = dsm.Shipping_Mode_ID
-- WHERE dsm.Shipping_Mode_ID IS NULL;

-- If all queries return 0 rows → ✅ All your foreign key references are valid.
-- If any query returns rows → ❌ You have orphan records.

-- --------------------------Create Indexes for Performance -------------------------------

-- ============================================
-- Create Indexes for Performance
-- Grain: Fact Order
-- ============================================
-- 1. Time + Customer (customer orders over time)
CREATE INDEX idx_fact_order_date_customer
    ON fact_order(Date_ID, Customer_ID);

-- 2. Time + Product (product sales trend over time)
CREATE INDEX idx_fact_order_date_product
    ON fact_order(Date_ID, Product_ID);

-- 3. Location + Market (market performance by region)
CREATE INDEX idx_fact_order_location_market
    ON fact_order(Location_ID, Market_ID);

-- 4. Status + Date (tracking orders by status over time)
CREATE INDEX idx_fact_order_status_date
    ON fact_order(Order_Status, Date_ID);

-- 5. Customer + Market (customer behavior in different markets)
CREATE INDEX idx_fact_order_customer_market
    ON fact_order(Customer_ID, Market_ID);

-- ============================================
-- Create Indexes for Performance
-- Grain: Fact Shipping
-- ============================================
-- 1. Date + Delivery_Status (tracking delivery performance over time)
CREATE INDEX idx_fact_shipping_date_status
    ON fact_shipping(Shipping_Date_ID, Delivery_Status);

-- 2. Customer + Date (customer shipping patterns)
CREATE INDEX idx_fact_shipping_customer_date
    ON fact_shipping(Customer_ID, Shipping_Date_ID);

-- 3. Location + Market (shipping volumes by region and market)
CREATE INDEX idx_fact_shipping_location_market
    ON fact_shipping(Location_ID, Market_ID);

-- 4. Shipping_Mode + Date (analyzing mode efficiency over time)
CREATE INDEX idx_fact_shipping_mode_date
    ON fact_shipping(Shipping_Mode_ID, Shipping_Date_ID);

-- 5. Late_Delivery_Risk + Date (tracking late deliveries over time)
CREATE INDEX idx_fact_shipping_late_risk_date
    ON fact_shipping(Late_Delivery_Risk, Shipping_Date_ID);

-- ============================================
-- Create Indexes for Performance
-- Grain: Fact customer Engagement
-- ============================================
-- 1. Customer-based queries (most frequent lookups)
CREATE INDEX idx_customer_engagement_customer
    ON fact_customer_engagement(Customer_ID);

-- 2. Segment + Market (segmentation reports)
CREATE INDEX idx_customer_engagement_segment_market
    ON fact_customer_engagement(Segment_ID, Market_ID);

-- 3. Location + Market (regional breakdowns)
CREATE INDEX idx_customer_engagement_location_market
    ON fact_customer_engagement(Location_ID, Market_ID);

-- 4. Last Order Date + Market (recency analysis by market)
CREATE INDEX idx_customer_engagement_last_order_market
    ON fact_customer_engagement(Last_Order_Date_ID, Market_ID);

-- 5. Customer + Last Order Date (customer churn/retention analysis)
CREATE INDEX idx_customer_engagement_customer_last_order
    ON fact_customer_engagement(Customer_ID, Last_Order_Date_ID);

-- ============================================
-- Create Indexes for Performance
-- Grain: Fact Product_Stats
-- ============================================
-- 1. Category-level lookups
CREATE INDEX idx_fps_category
    ON fact_product_stats(category_id);

-- 2. Category + Date (category sales over time)
CREATE INDEX idx_fps_category_date
    ON fact_product_stats(category_id, date_id);

-- 3. Product-level time series (fast retrieval by product)
CREATE INDEX idx_fps_product_date
    ON fact_product_stats(product_id, date_id);

-- 4. Date-level aggregation (all products on a given date or range)
CREATE INDEX idx_fps_date
    ON fact_product_stats(date_id);

-- ============================================
-- Create Indexes for Performance
-- Grain: Fact Sales
-- ============================================
-- Index on Product_ID for product-based analysis
CREATE INDEX idx_fact_sales_product_id
    ON Fact_Sales(Product_ID);

-- Index on Customer_ID for customer-based analysis
CREATE INDEX idx_fact_sales_customer_id
    ON Fact_Sales(Customer_ID);

-- Index on Order_Date_ID for time-based filtering
CREATE INDEX idx_fact_sales_order_date_id
    ON Fact_Sales(Order_Date_ID);

-- Index on Location_ID for location-based queries
CREATE INDEX idx_fact_sales_location_id
    ON Fact_Sales(Location_ID);

-- Index on Market_ID for market dimension lookups
CREATE INDEX idx_fact_sales_market_id
    ON Fact_Sales(Market_ID);

-- Index on Segment_ID for segmentation reporting
CREATE INDEX idx_fact_sales_segment_id
    ON Fact_Sales(Segment_ID);

-- Index on Shipping_Mode_ID for shipping analysis
CREATE INDEX idx_fact_sales_shipping_mode_id
    ON Fact_Sales(Shipping_Mode_ID);




-- ------------------------------------------------------------------------------------------------------------
-- Create isi dari dimensi date (ETL FOR DATE DIMENSION)

INSERT INTO dim_date (
    date_id, full_date, year, semester, quarter, month, month_name,
    day, day_name, week_of_year, is_weekend
)
SELECT DISTINCT
    DATE_FORMAT(STR_TO_DATE(combined_date, '%m/%d/%Y %H:%i'), '%Y%m%d%H%i') AS date_id,
    STR_TO_DATE(combined_date, '%m/%d/%Y %H:%i') AS full_date,
    YEAR(STR_TO_DATE(combined_date, '%m/%d/%Y %H:%i')) AS year,
    CASE 
        WHEN MONTH(STR_TO_DATE(combined_date, '%m/%d/%Y %H:%i')) <= 6 THEN 'S1'
        ELSE 'S2'
    END AS semester,
    CONCAT('Q', QUARTER(STR_TO_DATE(combined_date, '%m/%d/%Y %H:%i'))) AS quarter,
    MONTH(STR_TO_DATE(combined_date, '%m/%d/%Y %H:%i')) AS month,
    MONTHNAME(STR_TO_DATE(combined_date, '%m/%d/%Y %H:%i')) AS month_name,
    DAY(STR_TO_DATE(combined_date, '%m/%d/%Y %H:%i')) AS day,
    DAYNAME(STR_TO_DATE(combined_date, '%m/%d/%Y %H:%i')) AS day_name,
    WEEK(STR_TO_DATE(combined_date, '%m/%d/%Y %H:%i'), 3) AS week_of_year,
    CASE 
        WHEN DAYOFWEEK(STR_TO_DATE(combined_date, '%m/%d/%Y %H:%i')) IN (1, 7) THEN TRUE
        ELSE FALSE
    END AS is_weekend
FROM (
    SELECT `order date (DateOrders)` AS combined_date
    FROM raw_supply_data
    UNION
    SELECT `shipping date (DateOrders)` AS combined_date
    FROM raw_supply_data
) AS all_dates
WHERE combined_date IS NOT NULL
  AND combined_date <> '';


-- -------------------------------------------------------------------------------------------------------------------------------------------
-- CEK transformasi yang di penatho sudah memindahkan data ke table dimensinya
-- fungsi wat debug dan check
SELECT * FROM dim_customer LIMIT 10;
SELECT * FROM dim_product LIMIT 10;
SELECT * FROM dim_shipping_mode LIMIT 10;
SELECT * FROM dim_market LIMIT 10;
SELECT * FROM dim_segment LIMIT 10;
SELECT * FROM dim_category LIMIT 10;
SELECT * FROM dim_order_location LIMIT 10;
SELECT * FROM dim_customer_location LIMIT 10;
SELECT * FROM dim_date LIMIT 10;
SELECT * FROM fact_order LIMIT 10;
SELECT * FROM fact_shipping LIMIT 10;
SELECT * FROM fact_customer_engagement LIMIT 10;
SELECT * FROM fact_product_stats LIMIT 10;
SELECT * FROM fFact_Sales LIMIT 10;
SELECT * FROM raw_supply_data LIMIT 10;
SHOW TABLES;
-- ------------------------------------------------------------------------------------------
-- cek duplicate ada gak di dimensi
-- SELECT 
--     raw.product_card_id,
--     raw.product_name,
--     raw.product_category_id,
--     raw.product_description,
--     raw.product_image,
--     raw.product_price,
--     raw.product_status,
--     
--     COUNT(*) AS count_in_raw,                       -- How many times in raw CSV
--     
--     COALESCE(clean.count_in_dim, 0) AS count_in_dim -- How many times now in dim_product

-- FROM (
--     SELECT 
--         `Product Card Id` AS product_card_id,
--         `Product Name` AS product_name,
--         `Product Category Id` AS product_category_id,
--         `Product Description` AS product_description,
--         `Product Image` AS product_image,
--         `Product Price` AS product_price,
--         `Product Status` AS product_status
--     FROM raw_supply_data
-- ) AS raw

-- LEFT JOIN (
--     SELECT 
--         Product_Card_ID AS product_card_id,
--         Product_Name AS product_name,
--         Product_Category_ID AS product_category_id,
--         Product_Description AS product_description,
--         Product_Image_URL AS product_image,
--         Product_Price AS product_price,
--         Product_Status AS product_status,
--         COUNT(*) AS count_in_dim
--     FROM dim_product
--     GROUP BY Product_Card_ID, Product_Name, Product_Category_ID,
--              Product_Description, Product_Image_URL,
--              Product_Price, Product_Status
-- ) AS clean
-- ON raw.product_card_id = clean.product_card_id
--    AND raw.product_name = clean.product_name
--    AND raw.product_category_id = clean.product_category_id
--    AND raw.product_description = clean.product_description
--    AND raw.product_image = clean.product_image
--    AND raw.product_price = clean.product_price
--    AND raw.product_status = clean.product_status

-- GROUP BY raw.product_card_id, raw.product_name, raw.product_category_id,
--          raw.product_description, raw.product_image,
--          raw.product_price, raw.product_status, clean.count_in_dim

-- ORDER BY count_in_raw DESC;
-- ---------------------------------------------------------------------------------------
-- cek duplicate di fact table
-- SELECT 
--     Order_ID,
--     Product_ID,
--     Date_ID,
--     Customer_ID,
--     Market_ID,
--     Location_ID,
--     Order_Status,
--     COUNT(*) AS cnt
-- FROM fact_order
-- GROUP BY 
--     Order_ID,
--     Product_ID,
--     Date_ID,
--     Customer_ID,
--     Market_ID,
--     Location_ID,
--     Order_Status
-- HAVING cnt > 1;


-- SELECT 
--     COUNT(*) AS total_rows,
--     COUNT(DISTINCT CONCAT_WS('-', Order_ID, Product_ID, Date_ID, Customer_ID, Market_ID, Location_ID, Order_Status)) AS unique_rows
-- FROM fact_order;

-- SELECT COUNT(*) AS total_columns
-- FROM INFORMATION_SCHEMA.COLUMNS
-- WHERE TABLE_NAME = 'fact_order';

-- SELECT COLUMN_NAME
-- FROM INFORMATION_SCHEMA.COLUMNS
-- WHERE TABLE_NAME = 'fact_order';

-- SELECT 
--   COUNT(Order_ID) AS order_id_count,
--   COUNT(Product_ID) AS product_id_count,
--   COUNT(Date_ID) AS date_id_count,
--   COUNT(Customer_ID) AS customer_id_count,
--   COUNT(Market_ID) AS market_id_count,
--   COUNT(Location_ID) AS location_id_count,
--   COUNT(Order_Status) AS order_status_count,
--   COUNT(Quantity) AS quantity_count,
--   COUNT(Order_Item_Total) AS total_count,
--   COUNT(Discount) AS discount_count,
--   COUNT(Profit) AS profit_count
-- FROM fact_order;





-- SELECT DISTINCT r.`order date (DateOrders)`
-- FROM raw_supply_data r
-- LEFT JOIN dim_date d 
--   ON d.full_date = DATE(STR_TO_DATE(r.`order date (DateOrders)`, '%m/%d/%Y %H:%i'))
-- WHERE d.date_id IS NULL;









