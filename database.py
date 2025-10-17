import sqlite3
import hashlib
from datetime import datetime, date

class DatabaseManager:
    def __init__(self, db_path='coffee_shop.db'):
        self.db_path = db_path
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    def verify_password(self, password, hash_value):
        return self.hash_password(password) == hash_value

class CoffeeShopDB:
    def __init__(self):
        self.db_manager = DatabaseManager()
    
    def get_all_products(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT p.PRODUCT_ID, p.NAME, p.PRICE, p.IS_ACTIVE, c.CATEGORY_NAME
            FROM CYEAE_PRODUCT p
            LEFT JOIN CYEAE_CATEGORY c ON p.CATEGORY_ID = c.CATEGORY_ID
            WHERE p.IS_ACTIVE = 'Y'
            ORDER BY c.CATEGORY_NAME, p.NAME
        """)
        products = cursor.fetchall()
        conn.close()
        return products
    
    def get_categories(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT CATEGORY_ID, CATEGORY_NAME, DESCRIPTION FROM CYEAE_CATEGORY ORDER BY CATEGORY_NAME")
        categories = cursor.fetchall()
        conn.close()
        return categories
    
    def create_customer(self, name, phone, email, address, customer_type='regular'):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO CYEAE_CUSTOMER (NAME, PHONE, EMAIL, ADDRESS, CUSTOMER_TYPE)
            VALUES (?, ?, ?, ?, ?)
        """, (name, phone, email, address, customer_type))
        customer_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return customer_id

    def create_member_customer(self, customer_id, password, date_of_birth=None):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        try:
            password_hash = self.db_manager.hash_password(password)
            cursor.execute(
                """
                INSERT INTO CYEAE_MEMBER_CUSTOMERS (CUSTOMER_ID, PASSWORD_HASH, DATE_OF_BIRTH)
                VALUES (?, ?, ?)
                """,
                (customer_id, password_hash, date_of_birth)
            )
            conn.commit()
        finally:
            conn.close()

    def get_member_by_email(self, email):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT c.CUSTOMER_ID, c.NAME, c.PHONE, c.EMAIL, c.ADDRESS, c.CUSTOMER_TYPE,
                   m.PASSWORD_HASH, m.DATE_OF_BIRTH, m.REGISTRATION_DATE
            FROM CYEAE_CUSTOMER c
            JOIN CYEAE_MEMBER_CUSTOMERS m ON c.CUSTOMER_ID = m.CUSTOMER_ID
            WHERE c.EMAIL = ?
            """,
            (email,)
        )
        row = cursor.fetchone()
        conn.close()
        return row

    def verify_member_login(self, email, password):
        member = self.get_member_by_email(email)
        if not member:
            return None
        password_hash = member[6]
        if self.db_manager.verify_password(password, password_hash):
            return {
                'customer_id': member[0],
                'name': member[1],
                'phone': member[2],
                'email': member[3],
                'address': member[4],
                'customer_type': member[5],
                'date_of_birth': member[7],
                'registration_date': member[8]
            }
        return None
    
    def create_order(self, customer_id, payment_method, order_items):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            total_amount = 0
            for item in order_items:
                cursor.execute("SELECT PRICE FROM CYEAE_PRODUCT WHERE PRODUCT_ID = ?", (item['product_id'],))
                price = cursor.fetchone()[0]
                total_amount += price * item['quantity']
            
            cursor.execute("""
                INSERT INTO CYEAE_ORDERS (CUSTOMER_ID, PAYMENT_METHOD, TOTAL_AMOUNT)
                VALUES (?, ?, ?)
            """, (customer_id, payment_method, total_amount))
            
            order_id = cursor.lastrowid
            
            for item in order_items:
                cursor.execute("SELECT PRICE FROM CYEAE_PRODUCT WHERE PRODUCT_ID = ?", (item['product_id'],))
                unit_price = cursor.fetchone()[0]
                line_amount = unit_price * item['quantity']
                
                cursor.execute("""
                    INSERT INTO CYEAE_ORDER_ITEMS (ORDER_ID, PRODUCT_ID, QUANTITY, UNIT_PRICE, LINE_AMOUNT)
                    VALUES (?, ?, ?, ?, ?)
                """, (order_id, item['product_id'], item['quantity'], unit_price, line_amount))
            
            conn.commit()
            return order_id
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_order_history(self, customer_id=None):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        if customer_id:
            cursor.execute("""
                SELECT o.ORDER_ID, c.NAME, o.ORDER_DATE, o.PAYMENT_METHOD, o.TOTAL_AMOUNT
                FROM CYEAE_ORDERS o
                JOIN CYEAE_CUSTOMER c ON o.CUSTOMER_ID = c.CUSTOMER_ID
                WHERE o.CUSTOMER_ID = ?
                ORDER BY o.ORDER_DATE DESC
            """, (customer_id,))
        else:
            cursor.execute("""
                SELECT o.ORDER_ID, c.NAME, o.ORDER_DATE, o.PAYMENT_METHOD, o.TOTAL_AMOUNT
                FROM CYEAE_ORDERS o
                JOIN CYEAE_CUSTOMER c ON o.CUSTOMER_ID = c.CUSTOMER_ID
                ORDER BY o.ORDER_DATE DESC
            """)
        
        orders = cursor.fetchall()
        conn.close()
        return orders
    
    def get_order_details(self, order_id):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT oi.PRODUCT_ID, p.NAME, oi.QUANTITY, oi.UNIT_PRICE, oi.LINE_AMOUNT
            FROM CYEAE_ORDER_ITEMS oi
            JOIN CYEAE_PRODUCT p ON oi.PRODUCT_ID = p.PRODUCT_ID
            WHERE oi.ORDER_ID = ?
        """, (order_id,))
        
        items = cursor.fetchall()
        conn.close()
        return items
    
    def get_sales_report(self, start_date=None, end_date=None):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        base_query = """
            SELECT 
                DATE(o.ORDER_DATE) as order_date,
                COUNT(o.ORDER_ID) as order_count,
                SUM(o.TOTAL_AMOUNT) as total_sales,
                AVG(o.TOTAL_AMOUNT) as avg_order_value
            FROM CYEAE_ORDERS o
            WHERE 1=1
        """
        
        params = []
        if start_date:
            base_query += " AND DATE(o.ORDER_DATE) >= ?"
            params.append(start_date)
        if end_date:
            base_query += " AND DATE(o.ORDER_DATE) <= ?"
            params.append(end_date)
            
        base_query += " GROUP BY DATE(o.ORDER_DATE) ORDER BY order_date DESC"
        
        cursor.execute(base_query, params)
        report = cursor.fetchall()
        conn.close()
        return report
    
    def get_product_sales_report(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT 
                p.NAME as product_name,
                c.CATEGORY_NAME,
                SUM(oi.QUANTITY) as total_quantity,
                SUM(oi.LINE_AMOUNT) as total_revenue,
                COUNT(DISTINCT oi.ORDER_ID) as order_count
            FROM CYEAE_ORDER_ITEMS oi
            JOIN CYEAE_PRODUCT p ON oi.PRODUCT_ID = p.PRODUCT_ID
            JOIN CYEAE_CATEGORY c ON p.CATEGORY_ID = c.CATEGORY_ID
            GROUP BY p.PRODUCT_ID, p.NAME, c.CATEGORY_NAME
            ORDER BY total_revenue DESC
        """)
        
        report = cursor.fetchall()
        conn.close()
        return report
    
    def get_customer_report(self):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT 
                c.CUSTOMER_ID,
                c.NAME as customer_name,
                c.CUSTOMER_TYPE,
                COUNT(o.ORDER_ID) as order_count,
                SUM(o.TOTAL_AMOUNT) as total_spent,
                AVG(o.TOTAL_AMOUNT) as avg_order_value,
                MAX(o.ORDER_DATE) as last_order_date
            FROM CYEAE_CUSTOMER c
            LEFT JOIN CYEAE_ORDERS o ON c.CUSTOMER_ID = o.CUSTOMER_ID
            GROUP BY c.CUSTOMER_ID, c.NAME, c.CUSTOMER_TYPE
            ORDER BY total_spent DESC
        """)
        
        report = cursor.fetchall()
        conn.close()
        return report
    
    def find_customer_by_name_and_email(self, name, email=None):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        if email:
            cursor.execute("""
                SELECT CUSTOMER_ID, NAME, PHONE, EMAIL, ADDRESS, CUSTOMER_TYPE
                FROM CYEAE_CUSTOMER 
                WHERE UPPER(NAME) = UPPER(?) AND EMAIL = ?
                ORDER BY 
                    CASE WHEN CUSTOMER_TYPE = 'member' THEN 1 ELSE 2 END,
                    CUSTOMER_ID DESC
                LIMIT 1
            """, (name, email))
        else:
            cursor.execute("""
                SELECT CUSTOMER_ID, NAME, PHONE, EMAIL, ADDRESS, CUSTOMER_TYPE
                FROM CYEAE_CUSTOMER 
                WHERE UPPER(NAME) = UPPER(?)
                ORDER BY 
                    CASE WHEN CUSTOMER_TYPE = 'member' THEN 1 ELSE 2 END,
                    CUSTOMER_ID DESC
                LIMIT 1
            """, (name,))
        
        customer = cursor.fetchone()
        conn.close()
        return customer
    
    def find_potential_members_by_name(self, name):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT CUSTOMER_ID, NAME, PHONE, EMAIL, ADDRESS, CUSTOMER_TYPE
            FROM CYEAE_CUSTOMER 
            WHERE UPPER(NAME) = UPPER(?) AND CUSTOMER_TYPE = 'member'
            ORDER BY CUSTOMER_ID DESC
        """, (name,))
        
        members = cursor.fetchall()
        conn.close()
        return members
    
    def verify_member_identity(self, name, email=None, phone=None):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        if email:
            cursor.execute("""
                SELECT CUSTOMER_ID, NAME, PHONE, EMAIL, ADDRESS, CUSTOMER_TYPE
                FROM CYEAE_CUSTOMER 
                WHERE UPPER(NAME) = UPPER(?) AND EMAIL = ? AND CUSTOMER_TYPE = 'member'
                LIMIT 1
            """, (name, email))
        elif phone:
            cursor.execute("""
                SELECT CUSTOMER_ID, NAME, PHONE, EMAIL, ADDRESS, CUSTOMER_TYPE
                FROM CYEAE_CUSTOMER 
                WHERE UPPER(NAME) = UPPER(?) AND PHONE = ? AND CUSTOMER_TYPE = 'member'
                LIMIT 1
            """, (name, phone))
        else:
            conn.close()
            return None
        
        member = cursor.fetchone()
        conn.close()
        return member
    
    def save_member_preference(self, customer_id, preference_type, preference_value):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                SELECT PREFERENCE_ID FROM CYEAE_MEMBER_PREFERENCES 
                WHERE CUSTOMER_ID = ? AND PREFERENCE_TYPE = ?
            """, (customer_id, preference_type))
            
            existing = cursor.fetchone()
            
            if existing:
                cursor.execute("""
                    UPDATE CYEAE_MEMBER_PREFERENCES 
                    SET PREFERENCE_VALUE = ?, CREATED_DATE = CURRENT_TIMESTAMP
                    WHERE PREFERENCE_ID = ?
                """, (preference_value, existing[0]))
            else:
                cursor.execute("""
                    INSERT INTO CYEAE_MEMBER_PREFERENCES (CUSTOMER_ID, PREFERENCE_TYPE, PREFERENCE_VALUE)
                    VALUES (?, ?, ?)
                """, (customer_id, preference_type, preference_value))
            
            conn.commit()
            return True
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def get_member_preferences(self, customer_id):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT PREFERENCE_TYPE, PREFERENCE_VALUE, CREATED_DATE
            FROM CYEAE_MEMBER_PREFERENCES 
            WHERE CUSTOMER_ID = ?
            ORDER BY CREATED_DATE DESC
        """, (customer_id,))
        
        preferences = cursor.fetchall()
        conn.close()
        return preferences
    
    def get_member_favorite_products(self, customer_id):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT p.PRODUCT_ID, p.NAME, p.PRICE, SUM(oi.QUANTITY) as total_quantity, COUNT(oi.ORDER_ID) as order_count
            FROM CYEAE_ORDER_ITEMS oi
            JOIN CYEAE_PRODUCT p ON oi.PRODUCT_ID = p.PRODUCT_ID
            JOIN CYEAE_ORDERS o ON oi.ORDER_ID = o.ORDER_ID
            WHERE o.CUSTOMER_ID = ?
            GROUP BY p.PRODUCT_ID, p.NAME, p.PRICE
            ORDER BY total_quantity DESC, order_count DESC
            LIMIT 5
        """, (customer_id,))
        
        favorites = cursor.fetchall()
        conn.close()
        return favorites
    
    def get_member_by_customer_id(self, customer_id):
        conn = self.db_manager.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT c.CUSTOMER_ID, c.NAME, c.PHONE, c.EMAIL, c.ADDRESS, c.CUSTOMER_TYPE,
                   m.PASSWORD_HASH, m.DATE_OF_BIRTH, m.REGISTRATION_DATE
            FROM CYEAE_CUSTOMER c
            LEFT JOIN CYEAE_MEMBER_CUSTOMERS m ON c.CUSTOMER_ID = m.CUSTOMER_ID
            WHERE c.CUSTOMER_ID = ? AND c.CUSTOMER_TYPE = 'member'
        """, (customer_id,))
        
        member = cursor.fetchone()
        conn.close()
        return member