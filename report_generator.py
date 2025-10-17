#!/usr/bin/env python3
"""
Coffee Shop Database Report Generator
=====================================

This script generates comprehensive reports from the coffee shop database,
including charts (PNG) and data tables (CSV) for LaTeX integration.

Usage:
    python report_generator.py [--config config.yaml] [--output-dir reports/]

Author: Coffee Shop Analytics Team
Date: 2024
"""

import sqlite3
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import yaml
import argparse
import os
from datetime import datetime, timedelta
import numpy as np
from pathlib import Path

# Set style for better-looking charts
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

class CoffeeShopReportGenerator:
    def __init__(self, db_path='coffee_shop.db', output_dir='reports'):
        self.db_path = db_path
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # Create subdirectories
        (self.output_dir / 'charts').mkdir(exist_ok=True)
        (self.output_dir / 'data').mkdir(exist_ok=True)
        (self.output_dir / 'latex').mkdir(exist_ok=True)
        
        # Connect to database
        self.conn = sqlite3.connect(self.db_path)
        
    def execute_query(self, query, params=None):
        """Execute SQL query and return DataFrame"""
        return pd.read_sql_query(query, self.conn, params=params)
    
    def save_chart(self, fig, filename, dpi=300):
        """Save matplotlib figure as PNG"""
        chart_path = self.output_dir / 'charts' / f"{filename}.png"
        fig.savefig(chart_path, dpi=dpi, bbox_inches='tight', 
                   facecolor='white', edgecolor='none')
        plt.close(fig)
        return chart_path
    
    def save_csv(self, df, filename):
        """Save DataFrame as CSV"""
        csv_path = self.output_dir / 'data' / f"{filename}.csv"
        df.to_csv(csv_path, index=False)
        return csv_path
    
    def generate_sales_trends_report(self):
        """Generate daily sales trends report"""
        print("Generating sales trends report...")
        
        # Get last 30 days of sales data
        query = """
        SELECT 
            DATE(ORDER_DATE) as order_date,
            COUNT(ORDER_ID) as order_count,
            SUM(TOTAL_AMOUNT) as total_sales,
            AVG(TOTAL_AMOUNT) as avg_order_value
        FROM CYEAE_ORDERS 
        WHERE DATE(ORDER_DATE) >= DATE('now', '-30 days')
        GROUP BY DATE(ORDER_DATE)
        ORDER BY order_date
        """
        
        df = self.execute_query(query)
        
        if df.empty:
            print("No sales data found for the last 30 days")
            return
        
        # Create sales trend chart
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        # Daily sales amount
        ax1.plot(df['order_date'], df['total_sales'], marker='o', linewidth=2, markersize=6)
        ax1.set_title('Daily Sales Revenue (Last 30 Days)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Sales Amount (HKD)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        ax1.tick_params(axis='x', rotation=45)
        
        # Daily order count
        ax2.bar(df['order_date'], df['order_count'], alpha=0.7, color='skyblue')
        ax2.set_title('Daily Order Count (Last 30 Days)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Number of Orders', fontsize=12)
        ax2.set_xlabel('Date', fontsize=12)
        ax2.grid(True, alpha=0.3)
        ax2.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        chart_path = self.save_chart(fig, 'sales_trends')
        csv_path = self.save_csv(df, 'sales_trends')
        
        print(f"Sales trends chart saved: {chart_path}")
        print(f"Sales trends data saved: {csv_path}")
        
        return {
            'chart': chart_path,
            'data': csv_path,
            'summary': {
                'total_revenue': df['total_sales'].sum(),
                'avg_daily_sales': df['total_sales'].mean(),
                'total_orders': df['order_count'].sum(),
                'avg_daily_orders': df['order_count'].mean()
            }
        }
    
    def generate_product_performance_report(self):
        """Generate product performance analysis"""
        print("Generating product performance report...")
        
        query = """
        SELECT 
            p.NAME as product_name,
            c.CATEGORY_NAME,
            SUM(oi.QUANTITY) as total_quantity,
            SUM(oi.LINE_AMOUNT) as total_revenue,
            COUNT(DISTINCT oi.ORDER_ID) as order_count,
            AVG(oi.QUANTITY) as avg_quantity_per_order
        FROM CYEAE_ORDER_ITEMS oi
        JOIN CYEAE_PRODUCT p ON oi.PRODUCT_ID = p.PRODUCT_ID
        JOIN CYEAE_CATEGORY c ON p.CATEGORY_ID = c.CATEGORY_ID
        GROUP BY p.PRODUCT_ID, p.NAME, c.CATEGORY_NAME
        ORDER BY total_revenue DESC
        """
        
        df = self.execute_query(query)
        
        if df.empty:
            print("No product sales data found")
            return
        
        # Create product performance charts
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Top 10 products by revenue
        top_products = df.head(10)
        ax1.barh(range(len(top_products)), top_products['total_revenue'])
        ax1.set_yticks(range(len(top_products)))
        ax1.set_yticklabels(top_products['product_name'], fontsize=10)
        ax1.set_title('Top 10 Products by Revenue', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Revenue (HKD)', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # Revenue by category
        category_revenue = df.groupby('CATEGORY_NAME')['total_revenue'].sum().sort_values(ascending=True)
        ax2.barh(range(len(category_revenue)), category_revenue.values)
        ax2.set_yticks(range(len(category_revenue)))
        ax2.set_yticklabels(category_revenue.index, fontsize=10)
        ax2.set_title('Revenue by Category', fontsize=14, fontweight='bold')
        ax2.set_xlabel('Revenue (HKD)', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # Quantity sold by category
        category_quantity = df.groupby('CATEGORY_NAME')['total_quantity'].sum().sort_values(ascending=True)
        ax3.barh(range(len(category_quantity)), category_quantity.values, color='lightcoral')
        ax3.set_yticks(range(len(category_quantity)))
        ax3.set_yticklabels(category_quantity.index, fontsize=10)
        ax3.set_title('Quantity Sold by Category', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Total Quantity', fontsize=12)
        ax3.grid(True, alpha=0.3)
        
        # Average order value by product
        top_avg = df.nlargest(10, 'avg_quantity_per_order')
        ax4.bar(range(len(top_avg)), top_avg['avg_quantity_per_order'], color='lightgreen')
        ax4.set_xticks(range(len(top_avg)))
        ax4.set_xticklabels(top_avg['product_name'], rotation=45, ha='right', fontsize=9)
        ax4.set_title('Top 10 Products by Avg Quantity per Order', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Avg Quantity per Order', fontsize=12)
        ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        chart_path = self.save_chart(fig, 'product_performance')
        csv_path = self.save_csv(df, 'product_performance')
        
        print(f"Product performance chart saved: {chart_path}")
        print(f"Product performance data saved: {csv_path}")
        
        return {
            'chart': chart_path,
            'data': csv_path,
            'summary': {
                'total_products': len(df),
                'top_product': df.iloc[0]['product_name'],
                'top_category': df.groupby('CATEGORY_NAME')['total_revenue'].sum().idxmax(),
                'total_revenue': df['total_revenue'].sum()
            }
        }
    
    def generate_customer_analysis_report(self):
        """Generate customer behavior analysis"""
        print("Generating customer analysis report...")
        
        query = """
        SELECT 
            c.CUSTOMER_ID,
            c.NAME as customer_name,
            c.CUSTOMER_TYPE,
            COUNT(o.ORDER_ID) as order_count,
            SUM(o.TOTAL_AMOUNT) as total_spent,
            AVG(o.TOTAL_AMOUNT) as avg_order_value,
            MAX(o.ORDER_DATE) as last_order_date,
            MIN(o.ORDER_DATE) as first_order_date
        FROM CYEAE_CUSTOMER c
        LEFT JOIN CYEAE_ORDERS o ON c.CUSTOMER_ID = o.CUSTOMER_ID
        GROUP BY c.CUSTOMER_ID, c.NAME, c.CUSTOMER_TYPE
        ORDER BY total_spent DESC
        """
        
        df = self.execute_query(query)
        
        if df.empty:
            print("No customer data found")
            return
        
        # Calculate customer lifetime (days between first and last order)
        df['last_order_date'] = pd.to_datetime(df['last_order_date'])
        df['first_order_date'] = pd.to_datetime(df['first_order_date'])
        df['customer_lifetime_days'] = (df['last_order_date'] - df['first_order_date']).dt.days
        df['customer_lifetime_days'] = df['customer_lifetime_days'].fillna(0)
        
        # Create customer analysis charts
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # Customer spending distribution
        spending_data = df[df['total_spent'] > 0]['total_spent']
        ax1.hist(spending_data, bins=20, alpha=0.7, color='skyblue', edgecolor='black')
        ax1.set_title('Customer Spending Distribution', fontsize=14, fontweight='bold')
        ax1.set_xlabel('Total Spent (HKD)', fontsize=12)
        ax1.set_ylabel('Number of Customers', fontsize=12)
        ax1.grid(True, alpha=0.3)
        
        # Customer type comparison
        type_stats = df.groupby('CUSTOMER_TYPE').agg({
            'total_spent': ['mean', 'count'],
            'order_count': 'mean'
        }).round(2)
        
        types = type_stats.index
        avg_spending = type_stats[('total_spent', 'mean')]
        customer_counts = type_stats[('total_spent', 'count')]
        
        ax2.bar(types, avg_spending, alpha=0.7, color=['lightcoral', 'lightgreen'])
        ax2.set_title('Average Spending by Customer Type', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Average Total Spent (HKD)', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # Add count labels on bars
        for i, (type_name, count) in enumerate(zip(types, customer_counts)):
            ax2.text(i, avg_spending.iloc[i] + 5, f'n={count}', ha='center', fontsize=10)
        
        # Order frequency distribution
        order_freq = df[df['order_count'] > 0]['order_count']
        ax3.hist(order_freq, bins=15, alpha=0.7, color='lightgreen', edgecolor='black')
        ax3.set_title('Order Frequency Distribution', fontsize=14, fontweight='bold')
        ax3.set_xlabel('Number of Orders', fontsize=12)
        ax3.set_ylabel('Number of Customers', fontsize=12)
        ax3.grid(True, alpha=0.3)
        
        # Customer lifetime vs spending
        active_customers = df[df['customer_lifetime_days'] > 0]
        if not active_customers.empty:
            ax4.scatter(active_customers['customer_lifetime_days'], 
                       active_customers['total_spent'], 
                       alpha=0.6, s=60)
            ax4.set_title('Customer Lifetime vs Total Spending', fontsize=14, fontweight='bold')
            ax4.set_xlabel('Customer Lifetime (Days)', fontsize=12)
            ax4.set_ylabel('Total Spent (HKD)', fontsize=12)
            ax4.grid(True, alpha=0.3)
        
        plt.tight_layout()
        chart_path = self.save_chart(fig, 'customer_analysis')
        csv_path = self.save_csv(df, 'customer_analysis')
        
        print(f"Customer analysis chart saved: {chart_path}")
        print(f"Customer analysis data saved: {csv_path}")
        
        return {
            'chart': chart_path,
            'data': csv_path,
            'summary': {
                'total_customers': len(df),
                'active_customers': len(df[df['order_count'] > 0]),
                'avg_spending': df['total_spent'].mean(),
                'top_customer': df.iloc[0]['customer_name'] if not df.empty else 'N/A'
            }
        }
    
    def generate_payment_method_report(self):
        """Generate payment method analysis"""
        print("Generating payment method report...")
        
        query = """
        SELECT 
            PAYMENT_METHOD,
            COUNT(*) as order_count,
            SUM(TOTAL_AMOUNT) as total_revenue,
            AVG(TOTAL_AMOUNT) as avg_order_value
        FROM CYEAE_ORDERS
        WHERE PAYMENT_METHOD IS NOT NULL
        GROUP BY PAYMENT_METHOD
        ORDER BY total_revenue DESC
        """
        
        df = self.execute_query(query)
        
        if df.empty:
            print("No payment method data found")
            return
        
        # Create payment method charts
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
        
        # Revenue by payment method (pie chart)
        colors = ['#ff9999', '#66b3ff', '#99ff99', '#ffcc99']
        wedges, texts, autotexts = ax1.pie(df['total_revenue'], 
                                          labels=df['PAYMENT_METHOD'], 
                                          autopct='%1.1f%%',
                                          colors=colors,
                                          startangle=90)
        ax1.set_title('Revenue Distribution by Payment Method', fontsize=14, fontweight='bold')
        
        # Order count by payment method (bar chart)
        bars = ax2.bar(df['PAYMENT_METHOD'], df['order_count'], 
                      color=colors[:len(df)], alpha=0.7)
        ax2.set_title('Order Count by Payment Method', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Number of Orders', fontsize=12)
        ax2.set_xlabel('Payment Method', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{int(height)}', ha='center', va='bottom', fontsize=10)
        
        plt.tight_layout()
        chart_path = self.save_chart(fig, 'payment_methods')
        csv_path = self.save_csv(df, 'payment_methods')
        
        print(f"Payment method chart saved: {chart_path}")
        print(f"Payment method data saved: {csv_path}")
        
        return {
            'chart': chart_path,
            'data': csv_path,
            'summary': {
                'total_payment_methods': len(df),
                'most_popular': df.iloc[0]['PAYMENT_METHOD'],
                'total_orders': df['order_count'].sum(),
                'total_revenue': df['total_revenue'].sum()
            }
        }
    
    def generate_executive_summary(self):
        """Generate executive summary with key metrics"""
        print("Generating executive summary...")
        
        # Get key metrics
        metrics_queries = {
            'total_revenue': "SELECT SUM(TOTAL_AMOUNT) as total FROM CYEAE_ORDERS",
            'total_orders': "SELECT COUNT(*) as total FROM CYEAE_ORDERS",
            'total_customers': "SELECT COUNT(*) as total FROM CYEAE_CUSTOMER",
            'active_customers': "SELECT COUNT(DISTINCT CUSTOMER_ID) as total FROM CYEAE_ORDERS",
            'avg_order_value': "SELECT AVG(TOTAL_AMOUNT) as total FROM CYEAE_ORDERS",
            'total_products': "SELECT COUNT(*) as total FROM CYEAE_PRODUCT WHERE IS_ACTIVE = 'Y'"
        }
        
        summary = {}
        for metric, query in metrics_queries.items():
            result = self.execute_query(query)
            summary[metric] = result.iloc[0]['total'] if not result.empty else 0
        
        # Get recent activity (last 7 days)
        recent_query = """
        SELECT 
            COUNT(*) as orders_last_7_days,
            SUM(TOTAL_AMOUNT) as revenue_last_7_days
        FROM CYEAE_ORDERS 
        WHERE DATE(ORDER_DATE) >= DATE('now', '-7 days')
        """
        recent_result = self.execute_query(recent_query)
        if not recent_result.empty:
            summary['orders_last_7_days'] = recent_result.iloc[0]['orders_last_7_days']
            summary['revenue_last_7_days'] = recent_result.iloc[0]['revenue_last_7_days']
        else:
            summary['orders_last_7_days'] = 0
            summary['revenue_last_7_days'] = 0
        
        # Create summary DataFrame
        summary_df = pd.DataFrame([summary])
        csv_path = self.save_csv(summary_df, 'executive_summary')
        
        print(f"Executive summary saved: {csv_path}")
        return {
            'data': csv_path,
            'summary': summary
        }
    
    def generate_latex_report(self, reports):
        """Generate LaTeX report with all charts and data"""
        print("Generating LaTeX report...")
        
        latex_content = """
\\documentclass[11pt,a4paper]{article}
\\usepackage[margin=1in]{geometry}
\\usepackage{graphicx}
\\title{Coffee Shop Simple Charts}
\\date{\\today}
\\begin{document}
\\maketitle

% Sales trends
\\begin{figure}[h]
\\centering
\\includegraphics[width=0.95\\textwidth]{../charts/sales_trends.png}
\\end{figure}

% Product performance
\\begin{figure}[h]
\\centering
\\includegraphics[width=0.95\\textwidth]{../charts/product_performance.png}
\\end{figure}

% Customer analysis
\\begin{figure}[h]
\\centering
\\includegraphics[width=0.95\\textwidth]{../charts/customer_analysis.png}
\\end{figure}

% Payment methods
\\begin{figure}[h]
\\centering
\\includegraphics[width=0.95\\textwidth]{../charts/payment_methods.png}
\\end{figure}

\\end{document}
"""
        
        latex_path = self.output_dir / 'latex' / 'coffee_shop_report.tex'
        with open(latex_path, 'w', encoding='utf-8') as f:
            f.write(latex_content)
        
        print(f"LaTeX report saved: {latex_path}")
        return latex_path
    
    def run_all_reports(self):
        """Generate all reports"""
        print("=" * 60)
        print("COFFEE SHOP DATABASE REPORT GENERATOR")
        print("=" * 60)
        print(f"Database: {self.db_path}")
        print(f"Output Directory: {self.output_dir}")
        print("=" * 60)
        
        reports = {}
        
        # Generate all reports
        reports['sales_trends'] = self.generate_sales_trends_report()
        reports['product_performance'] = self.generate_product_performance_report()
        reports['customer_analysis'] = self.generate_customer_analysis_report()
        reports['payment_methods'] = self.generate_payment_method_report()
        reports['executive_summary'] = self.generate_executive_summary()
        
        # Generate LaTeX report
        latex_path = self.generate_latex_report(reports)
        
        print("=" * 60)
        print("REPORT GENERATION COMPLETE")
        print("=" * 60)
        print(f"All reports saved to: {self.output_dir}")
        print(f"LaTeX report: {latex_path}")
        print("\nTo compile the LaTeX report:")
        print(f"cd {self.output_dir}/latex && pdflatex coffee_shop_report.tex")
        print("=" * 60)
        
        return reports
    
    def close(self):
        """Close database connection"""
        self.conn.close()

def main():
    parser = argparse.ArgumentParser(description='Generate coffee shop database reports')
    parser.add_argument('--db', default='coffee_shop.db', help='Database file path')
    parser.add_argument('--output-dir', default='reports', help='Output directory')
    parser.add_argument('--config', help='Configuration file (YAML)')
    
    args = parser.parse_args()
    
    # Initialize report generator
    generator = CoffeeShopReportGenerator(args.db, args.output_dir)
    
    try:
        # Generate all reports
        reports = generator.run_all_reports()
        
    finally:
        generator.close()

if __name__ == '__main__':
    main()
