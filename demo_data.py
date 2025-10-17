#!/usr/bin/env python3
"""
Demo Data Generator - Fixed Version
Generate additional demo data for Coffee Ordering System
All data in English to match the system requirements
"""

from database import CoffeeShopDB
from datetime import datetime, timedelta
import random
import argparse

def generate_demo_data(seed: int, start_date_str: str, end_date_str: str, num_orders: int, reset_orders: bool,
                       num_customers: int, member_ratio: float):
    """Deterministically generate mixed regular/member customers and orders.
    All customers exist in CYEAE_CUSTOMER; members also exist in CYEAE_MEMBER_CUSTOMERS.
    Orders are within [start_date, end_date].
    """
    db = CoffeeShopDB()

    rnd = random.Random(seed)
    print("🎭 Generating demo data (seeded)...")

    # Enforce max 15 customers as requested
    num_customers = min(int(num_customers), 15)

    # Optional reset: only clear orders, keep customers unless desired otherwise
    if reset_orders:
        conn = db.db_manager.get_connection()
        cur = conn.cursor()
        cur.execute("DELETE FROM CYEAE_ORDER_ITEMS")
        cur.execute("DELETE FROM CYEAE_ORDERS")
        conn.commit()
        conn.close()
        print("♻️  Existing orders cleared.")

    # 1) Create customers deterministically
    first_names = [
        'Alice','Bob','Carol','David','Emma','Frank','Grace','Henry','Ivy','Jack','Karen','Leo','Mia','Noah','Olivia','Paul'
    ]
    last_names = ['Smith','Johnson','Williams','Brown','Jones','Miller','Davis','Wilson','Taylor','Lee']

    created_customer_ids = []
    for i in range(num_customers):
        full_name = f"{rnd.choice(first_names)} {rnd.choice(last_names)}"
        phone = f"13{rnd.randint(100000000, 999999999)}"
        email = f"{full_name.lower().replace(' ','.')}@example.com"
        address = rnd.choice(['Kowloon','Hong Kong Island','New Territories'])
        ctype = 'member' if rnd.random() < member_ratio else 'regular'
        try:
            cid = db.create_customer(full_name, phone, email, address, ctype)
            created_customer_ids.append((cid, ctype))
            if ctype == 'member':
                try:
                    db.create_member_customer(cid, 'password123', '1990-01-01')
                except Exception:
                    pass
            print(f"Customer: {full_name} ({ctype}) -> {cid}")
        except Exception:
            # try to lookup if exists
            cust = db.find_customer_by_name_and_email(full_name, email)
            if cust:
                created_customer_ids.append((cust[0], cust[5]))
                print(f"Existing customer reused: {full_name} ({cust[5]}) -> {cust[0]}")

    # 2) Generate orders deterministically in the date window
    start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
    end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
    total_days = (end_date - start_date).days

    products = db.get_all_products()
    product_ids = [p[0] for p in products]
    payment_methods = ['cash','card','alipay','wechat']

    for _ in range(num_orders):
        cust_id, _ctype = rnd.choice(created_customer_ids)
        k = rnd.randint(1, 4)
        order_items = []
        for __ in range(k):
            pid = rnd.choice(product_ids)
            qty = rnd.randint(1, 3)
            if not any(x['product_id'] == pid for x in order_items):
                order_items.append({'product_id': pid, 'quantity': qty})
        if not order_items:
            continue
        pay = rnd.choice(payment_methods)
        order_id = db.create_order(cust_id, pay, order_items)
        # set date
        order_dt = start_date + timedelta(days=rnd.randint(0, total_days),
                                          hours=rnd.randint(8, 20), minutes=rnd.randint(0,59), seconds=rnd.randint(0,59))
        conn = db.db_manager.get_connection()
        cur = conn.cursor()
        cur.execute("UPDATE CYEAE_ORDERS SET ORDER_DATE=? WHERE ORDER_ID=?", (order_dt.strftime('%Y-%m-%d %H:%M:%S'), order_id))
        conn.commit(); conn.close()
        print(f"Order #{order_id} for customer {cust_id} at {order_dt:%Y-%m-%d %H:%M:%S}")

    # 3) Summary
    print("\nDemo data generation completed!")
    print("\nData Statistics:")
    sales_report = db.get_sales_report()
    total_sales = sum(row[2] if row[2] else 0 for row in sales_report)
    total_orders = sum(row[1] for row in sales_report)
    print(f" Total Sales: ${total_sales:.2f}")
    print(f" Total Orders: {total_orders}")
    print(f" Average Order Value: ${total_sales/total_orders if total_orders>0 else 0:.2f}")

    # who are active (>=1 order)
    customer_report = db.get_customer_report()
    active_customers = len([c for c in customer_report if (c[3] or 0) > 0])
    print(f" Active Customers: {active_customers}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Seeded demo data generator (members + regulars)')
    parser.add_argument('--seed', type=int, default=21199517)
    parser.add_argument('--start', type=str, default='2025-09-16')
    parser.add_argument('--end', type=str, default='2025-10-15')
    parser.add_argument('--orders', type=int, default=80)
    parser.add_argument('--reset-orders', action='store_true')
    parser.add_argument('--customers', type=int, default=15)
    parser.add_argument('--member-ratio', type=float, default=0.4)
    args = parser.parse_args()
    generate_demo_data(seed=args.seed,
                       start_date_str=args.start,
                       end_date_str=args.end,
                       num_orders=args.orders,
                       reset_orders=args.reset_orders,
                       num_customers=args.customers,
                       member_ratio=args.member_ratio)