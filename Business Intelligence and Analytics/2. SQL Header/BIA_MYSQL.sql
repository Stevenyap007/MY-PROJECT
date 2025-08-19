CREATE DATABASE sales_dw;
USE sales_dw;

-- ---------------------------------------------------------------------------------------------

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