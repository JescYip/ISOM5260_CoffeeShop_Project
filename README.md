# Coffee Ordering System ☕

A comprehensive coffee shop ordering system with modern user interface, database management, and detailed business reporting features.

## 🌟 Features

### Client Features
- **Product Browsing**: Browse coffee and other products by category
- **Shopping Cart Management**: Add, modify, and remove items
- **Online Ordering**: Complete order processing workflow
- **Order History**: View past orders and details
- **Member System**: User registration and login functionality

### Admin Dashboard
- **Real-time Dashboard**: Sales overview and key metrics
- **Sales Reports**: Detailed sales analysis by date range
- **Product Analysis**: Product sales rankings and statistics
- **Customer Analysis**: Customer spending behavior analysis
- **Order Management**: Unified management of all orders
- **Secure Access**: Password-protected admin login

### Database Features
- **Complete Relational Database Design**: Customer, product, order, category tables
- **Data Integrity**: Foreign key constraints and data validation
- **Member System**: Support for regular and member customers
- **SQL Reports**: Complex SQL queries for management reports

## 🚀 Quick Start

### Requirements
- Python 3.7+
- Flask 2.3+
- SQLite3

### Installation Steps

1. **Clone the project**
   ```bash
   git clone <https://github.com/JescYip/ISOM5260_CoffeeShop_Project.git>
   cd coffee-ordering-system
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Start the application**
   ```bash
   python app.py
   ```

4. **Access the system**
   - Client: http://localhost:5050
   - Admin Dashboard: http://localhost:5050/admin
     - Username: `admin`
     - Password: `admin123`

## 📊 Database Structure

The system uses a relational database design with the following main tables:

- **CYEAE_CUSTOMER**: Customer information table
- **CYEAE_MEMBER_CUSTOMERS**: Member customer table
- **CYEAE_CATEGORY**: Product category table
- **CYEAE_PRODUCT**: Product information table
- **CYEAE_ORDERS**: Orders table
- **CYEAE_ORDER_ITEMS**: Order items table

## 🎯 Main Features

### 1. Product Management
- Display products by category (Coffee, Tea, Desserts, Light Meals)
- Product pricing and inventory management
- Product sales statistics

### 2. Order Processing
- Shopping cart functionality
- Customer information collection
- Multiple payment method support
- Order status tracking

### 3. Customer Management
- Customer information management
- Member system with registration and login
- Customer spending analysis

### 4. Reporting System
- **Sales Reports**: Daily sales statistics, order counts, average order values
- **Product Reports**: Product sales rankings, revenue statistics
- **Customer Reports**: Customer spending rankings, loyalty analysis

## 🛠 Technology Stack

### Backend
- **Flask**: Web framework
- **SQLite**: Database
- **Python**: Backend logic

### Frontend
- **HTML5/CSS3**: Page structure and styling
- **JavaScript**: Interactive logic
- **Responsive Design**: Adapts to various devices

### Database
- **SQLite**: Lightweight relational database
- **Complex SQL Queries**: Generate various business reports

## 📱 Interface Preview

### Client Interface
- Modern product display page
- Intuitive shopping cart management
- Streamlined order process
- Clear order history

### Admin Dashboard
- Real-time data dashboard
- Detailed sales reports
- Product and customer analysis
- Order management interface

## 🔧 Configuration

### Database Configuration
The system automatically creates SQLite database file `coffee_shop.db` and initializes sample data.

### Sample Data
The system includes the following sample data:
- 4 product categories
- 10 products
- 3 sample customers
- 1 member customer (Email: sarah@example.com, Password: 123456)

### Image Support
Product images are stored in `static/picture/` directory and served via `/picture/` route.

## 📈 Reporting Features

### SQL Query Examples

1. **Sales Report Query**
   ```sql
   SELECT 
       DATE(o.ORDER_DATE) as order_date,
       COUNT(o.ORDER_ID) as order_count,
       SUM(o.TOTAL_AMOUNT) as total_sales,
       AVG(o.TOTAL_AMOUNT) as avg_order_value
   FROM CYEAE_ORDERS o
   WHERE DATE(o.ORDER_DATE) BETWEEN ? AND ?
   GROUP BY DATE(o.ORDER_DATE)
   ORDER BY order_date DESC
   ```

2. **Product Sales Analysis**
   ```sql
   SELECT 
       p.NAME as product_name,
       c.CATEGORY_NAME,
       SUM(oi.QUANTITY) as total_quantity,
       SUM(oi.LINE_AMOUNT) as total_revenue
   FROM CYEAE_ORDER_ITEMS oi
   JOIN CYEAE_PRODUCT p ON oi.PRODUCT_ID = p.PRODUCT_ID
   JOIN CYEAE_CATEGORY c ON p.CATEGORY_ID = c.CATEGORY_ID
   GROUP BY p.PRODUCT_ID
   ORDER BY total_revenue DESC
   ```

## 🚀 Deployment Recommendations

### Development Environment
- Use built-in Flask development server
- SQLite database file

### Production Environment
- Use Gunicorn or uWSGI for deployment
- Consider PostgreSQL or MySQL database
- Configure reverse proxy (Nginx)
- Enable HTTPS

**Enjoy your coffee time!** ☕✨
