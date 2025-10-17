-- Coffee Ordering System - Database Initialization Script
-- =========================================================
-- This script initializes the complete database schema and sample data
-- Usage: sqlite3 coffee_shop.db < database_final.sql
-- 
-- This script handles:
-- 1. Database schema creation (7 tables)
-- 2. Sample data insertion
-- 3. Index creation for performance
-- 4. Data verification
--
-- Note: For runtime operations, use database.py (Python class)

-- ============================================================================
-- DATABASE SCHEMA CREATION
-- ============================================================================

-- Disable foreign key checks during setup
PRAGMA foreign_keys = OFF;

-- Drop existing tables if they exist (in correct order due to dependencies)
DROP TABLE IF EXISTS CYEAE_ORDER_ITEMS;
DROP TABLE IF EXISTS CYEAE_ORDERS;
DROP TABLE IF EXISTS CYEAE_MEMBER_CUSTOMERS;
DROP TABLE IF EXISTS CYEAE_MEMBER_PREFERENCES;
DROP TABLE IF EXISTS CYEAE_PRODUCT;
DROP TABLE IF EXISTS CYEAE_CATEGORY;
DROP TABLE IF EXISTS CYEAE_CUSTOMER;

-- Re-enable foreign key checks
PRAGMA foreign_keys = ON;

-- ============================================================================
-- TABLE CREATION
-- ============================================================================

-- Customer table
CREATE TABLE CYEAE_CUSTOMER (
    CUSTOMER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME VARCHAR(100) NOT NULL,
    PHONE VARCHAR(30),
    EMAIL VARCHAR(120),
    ADDRESS VARCHAR(255),
    CUSTOMER_TYPE VARCHAR(10) DEFAULT 'regular'
);

-- Category table
CREATE TABLE CYEAE_CATEGORY (
    CATEGORY_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    CATEGORY_NAME VARCHAR(80) UNIQUE NOT NULL,
    DESCRIPTION VARCHAR(255)
);

-- Product table
CREATE TABLE CYEAE_PRODUCT (
    PRODUCT_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    NAME VARCHAR(120) NOT NULL,
    PRICE DECIMAL(10,2) NOT NULL,
    IS_ACTIVE CHAR(1) DEFAULT 'Y',
    CATEGORY_ID INTEGER,
    FOREIGN KEY (CATEGORY_ID) REFERENCES CYEAE_CATEGORY(CATEGORY_ID)
);

-- Member customers table
CREATE TABLE CYEAE_MEMBER_CUSTOMERS (
    CUSTOMER_ID INTEGER PRIMARY KEY,
    PASSWORD_HASH VARCHAR(255) NOT NULL,
    DATE_OF_BIRTH DATE,
    REGISTRATION_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CUSTOMER_ID) REFERENCES CYEAE_CUSTOMER(CUSTOMER_ID)
);

-- Member preferences table
CREATE TABLE CYEAE_MEMBER_PREFERENCES (
    PREFERENCE_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    CUSTOMER_ID INTEGER,
    PREFERENCE_TYPE VARCHAR(20) NOT NULL,
    PREFERENCE_VALUE VARCHAR(255) NOT NULL,
    CREATED_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (CUSTOMER_ID) REFERENCES CYEAE_CUSTOMER(CUSTOMER_ID)
);

-- Orders table
CREATE TABLE CYEAE_ORDERS (
    ORDER_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    CUSTOMER_ID INTEGER,
    ORDER_DATE TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PAYMENT_METHOD VARCHAR(20),
    TOTAL_AMOUNT DECIMAL(12,2),
    FOREIGN KEY (CUSTOMER_ID) REFERENCES CYEAE_CUSTOMER(CUSTOMER_ID)
);

-- Order items table
CREATE TABLE CYEAE_ORDER_ITEMS (
    ORDER_ITEM_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    ORDER_ID INTEGER,
    PRODUCT_ID INTEGER,
    QUANTITY INTEGER(10),
    UNIT_PRICE DECIMAL(10,2),
    LINE_AMOUNT DECIMAL(10,2),
    FOREIGN KEY (ORDER_ID) REFERENCES CYEAE_ORDERS(ORDER_ID),
    FOREIGN KEY (PRODUCT_ID) REFERENCES CYEAE_PRODUCT(PRODUCT_ID)
);

-- ============================================================================
-- SAMPLE DATA INSERTION
-- ============================================================================

-- Insert categories
INSERT INTO CYEAE_CATEGORY (CATEGORY_NAME, DESCRIPTION) VALUES 
('Coffee', 'Coffee beverages'),
('Tea', 'Tea drinks'),
('Dessert', 'Cakes and snacks'),
('Light Meal', 'Sandwiches and salads');

-- Insert products
INSERT INTO CYEAE_PRODUCT (NAME, PRICE, IS_ACTIVE, CATEGORY_ID) VALUES 
('Americano', 25.00, 'Y', 1),
('Latte', 32.00, 'Y', 1),
('Cappuccino', 30.00, 'Y', 1),
('Mocha', 35.00, 'Y', 1),
('chinesetea', 28.00, 'Y', 2),
('Milk Tea', 22.00, 'Y', 2),
('Cheesecake', 38.00, 'Y', 3),
('Tiramisu', 42.00, 'Y', 3),
('Ham Sandwich', 28.00, 'Y', 4),
('Caesar Salad', 32.00, 'Y', 4);

-- Insert sample customers
INSERT INTO CYEAE_CUSTOMER (NAME, PHONE, EMAIL, ADDRESS, CUSTOMER_TYPE) VALUES 
('John Smith', '13812345678', 'john@example.com', 'Kowloon', 'regular'),
('Sarah Johnson', '13987654321', 'sarah@example.com', 'Hong Kong Island', 'member'),
('Mike Wilson', '13555666777', 'mike@example.com', 'New Territories', 'regular');

-- Insert member customer data
INSERT INTO CYEAE_MEMBER_CUSTOMERS (CUSTOMER_ID, PASSWORD_HASH, DATE_OF_BIRTH) VALUES 
(2, 'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855', '1990-05-15');

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================

-- Create indexes on foreign keys for better performance
CREATE INDEX idx_orders_customer_id ON CYEAE_ORDERS(CUSTOMER_ID);
CREATE INDEX idx_order_items_order_id ON CYEAE_ORDER_ITEMS(ORDER_ID);
CREATE INDEX idx_order_items_product_id ON CYEAE_ORDER_ITEMS(PRODUCT_ID);
CREATE INDEX idx_product_category_id ON CYEAE_PRODUCT(CATEGORY_ID);
CREATE INDEX idx_member_preferences_customer_id ON CYEAE_MEMBER_PREFERENCES(CUSTOMER_ID);

-- Create indexes on frequently queried columns
CREATE INDEX idx_customer_email ON CYEAE_CUSTOMER(EMAIL);
CREATE INDEX idx_orders_date ON CYEAE_ORDERS(ORDER_DATE);
CREATE INDEX idx_product_active ON CYEAE_PRODUCT(IS_ACTIVE);

-- ============================================================================
-- VERIFICATION QUERIES
-- ============================================================================

-- Verify table creation
SELECT 'Tables created successfully' as status;

-- Verify data insertion
SELECT 'Categories: ' || COUNT(*) as categories_count FROM CYEAE_CATEGORY;
SELECT 'Products: ' || COUNT(*) as products_count FROM CYEAE_PRODUCT;
SELECT 'Customers: ' || COUNT(*) as customers_count FROM CYEAE_CUSTOMER;
SELECT 'Members: ' || COUNT(*) as members_count FROM CYEAE_MEMBER_CUSTOMERS;

-- ============================================================================
-- END OF SCRIPT
-- ============================================================================
