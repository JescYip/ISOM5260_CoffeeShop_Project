from flask import Flask, request, jsonify, render_template, redirect, url_for, session, send_from_directory
import os
from flask_cors import CORS
from database import CoffeeShopDB
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'change-this-secret'  
CORS(app)

db = CoffeeShopDB()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/admin')
def admin():
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    return render_template('admin.html')

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'GET':
        return render_template('admin_login.html')
    data = request.form if request.form else request.get_json(silent=True) or {}
    username = data.get('username')
    password = data.get('password')
    if username == 'admin' and password == 'admin123':
        session['admin_logged_in'] = True
        return redirect(url_for('admin'))
    return render_template('admin_login.html', error='Invalid credentials'), 401

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    return redirect(url_for('admin_login'))


@app.route('/api/products', methods=['GET'])
def get_products():
    try:
        products = db.get_all_products()
        product_list = []
        for product in products:
            product_list.append({
                'id': product[0],
                'name': product[1],
                'price': float(product[2]),
                'is_active': product[3],
                'category': product[4]
            })
        return jsonify({'success': True, 'data': product_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/categories', methods=['GET'])
def get_categories():
    try:
        categories = db.get_categories()
        category_list = []
        for category in categories:
            category_list.append({
                'id': category[0],
                'name': category[1],
                'description': category[2]
            })
        return jsonify({'success': True, 'data': category_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/customers', methods=['POST'])
def create_customer():
    try:
        data = request.get_json()
        customer_id = db.create_customer(
            name=data['name'],
            phone=data.get('phone', ''),
            email=data.get('email', ''),
            address=data.get('address', ''),
            customer_type=data.get('customer_type', 'regular')
        )
        return jsonify({'success': True, 'customer_id': customer_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Auth endpoints
@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        phone = data.get('phone', '')
        address = data.get('address', '')
        date_of_birth = data.get('date_of_birth')

        if not all([name, email, password]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Create customer as member
        customer_id = db.create_customer(
            name=name,
            phone=phone,
            email=email,
            address=address,
            customer_type='member'
        )
        db.create_member_customer(customer_id, password, date_of_birth)

        return jsonify({'success': True, 'data': {
            'customer_id': customer_id,
            'name': name,
            'email': email
        }})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        if not all([email, password]):
            return jsonify({'success': False, 'error': 'Missing email or password'}), 400

        member = db.verify_member_login(email, password)
        if not member:
            return jsonify({'success': False, 'error': 'Invalid email or password'}), 401
        return jsonify({'success': True, 'data': member})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/customers/verify', methods=['POST'])
def verify_customer():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email', '')
        phone = data.get('phone', '')
        
        if not name:
            return jsonify({'success': False, 'error': 'Name is required'}), 400
        
        potential_members = db.find_potential_members_by_name(name)
        
        if not potential_members:
            return jsonify({'success': False, 'error': 'No member found with this name'}), 404        
        if email or phone:
            verified_member = db.verify_member_identity(name, email, phone)
            if verified_member:
                return jsonify({
                    'success': True, 
                    'verified': True,
                    'customer': {
                        'customer_id': verified_member[0],
                        'name': verified_member[1],
                        'customer_type': verified_member[5]
                    }
                })
            else:
                return jsonify({
                    'success': False, 
                    'error': 'Email or phone does not match any member with this name'
                }), 400
        
        return jsonify({
            'success': True,
            'verified': False,
            'requires_verification': True,
            'message': f'Found {len(potential_members)} potential member(s) with name "{name}". Please provide email or phone for verification.'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/orders', methods=['POST'])
def create_order():
    try:
        data = request.get_json()
        
        customer_id = data.get('customer_id')
        if not customer_id:
            customer_name = data['customer_name']
            customer_email = data.get('customer_email', '')
            customer_phone = data.get('customer_phone', '')
            
            if customer_email or customer_phone:
                existing_customer = db.find_customer_by_name_and_email(customer_name, customer_email if customer_email else None)
                if existing_customer:
                    customer_id = existing_customer[0]
                else:
                    customer_id = db.create_customer(
                        name=customer_name,
                        phone=customer_phone,
                        email=customer_email,
                        address=data.get('customer_address', '')
                    )
            else:
                potential_members = db.find_potential_members_by_name(customer_name)
                if potential_members:
                    force_regular = data.get('force_regular', False)
                    if force_regular:
                        customer_id = db.create_customer(
                            name=customer_name,
                            phone=customer_phone,
                            email=customer_email,
                            address=data.get('customer_address', '')
                        )
                    else:
                        return jsonify({
                            'success': False, 
                            'error': 'VERIFICATION_REQUIRED',
                            'message': f'Found potential member(s) with name "{customer_name}". Please provide email or phone for verification.'
                        }), 400
                else:
                    customer_id = db.create_customer(
                        name=customer_name,
                        phone=customer_phone,
                        email=customer_email,
                        address=data.get('customer_address', '')
                    )
        
        # Apply member default preferences (if provided or available)
        payment_method = data.get('payment_method')
        if not payment_method and customer_id:
            # try read member default_pay
            prefs = db.get_member_preferences(customer_id)
            for p in prefs:
                if p[0] == 'default_pay':
                    payment_method = p[1]
                    break
        if not payment_method:
            payment_method = 'cash'

        order_id = db.create_order(
            customer_id=customer_id,
            payment_method=payment_method,
            order_items=data['items']
        )
        
        return jsonify({'success': True, 'order_id': order_id})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/orders', methods=['GET'])
def get_orders():
    try:
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        customer_id = request.args.get('customer_id')
        orders = db.get_order_history(customer_id)
        
        order_list = []
        for order in orders:
            order_list.append({
                'order_id': order[0],
                'customer_name': order[1],
                'order_date': order[2],
                'payment_method': order[3],
                'total_amount': float(order[4]) if order[4] is not None else 0.0
            })
        
        return jsonify({'success': True, 'data': order_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/orders/<int:order_id>/details', methods=['GET'])
def get_order_details(order_id):
    try:
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        items = db.get_order_details(order_id)
        
        item_list = []
        for item in items:
            item_list.append({
                'product_id': item[0],
                'product_name': item[1],
                'quantity': item[2],
                'unit_price': float(item[3]),
                'line_amount': float(item[4])
            })
        
        return jsonify({'success': True, 'data': item_list})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/sales', methods=['GET'])
def get_sales_report():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        report = db.get_sales_report(start_date, end_date)
        
        report_data = []
        for row in report:
            report_data.append({
                'date': row[0],
                'order_count': row[1],
                'total_sales': float(row[2]) if row[2] else 0,
                'avg_order_value': float(row[3]) if row[3] else 0
            })
        
        return jsonify({'success': True, 'data': report_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/products', methods=['GET'])
def get_product_sales_report():
    try:
        report = db.get_product_sales_report()
        
        report_data = []
        for row in report:
            report_data.append({
                'product_name': row[0],
                'category': row[1],
                'total_quantity': row[2],
                'total_revenue': float(row[3]) if row[3] else 0,
                'order_count': row[4]
            })
        
        return jsonify({'success': True, 'data': report_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/reports/customers', methods=['GET'])
def get_customer_report():
    try:
        report = db.get_customer_report()
        
        report_data = []
        for row in report:
            report_data.append({
                'customer_id': row[0],  
                'customer_name': row[1],
                'customer_type': row[2],
                'order_count': row[3] if row[3] else 0,
                'total_spent': float(row[4]) if row[4] else 0,
                'avg_order_value': float(row[5]) if row[5] else 0,
                'last_order_date': row[6]
            })
        
        return jsonify({'success': True, 'data': report_data})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/member/preferences', methods=['GET', 'POST'])
def manage_member_preferences():
    try:
        if request.method == 'GET':
            customer_id = request.args.get('customer_id')
            if not customer_id:
                return jsonify({'success': False, 'error': 'Customer ID is required'}), 400
            
            preferences = db.get_member_preferences(customer_id)
            favorites = db.get_member_favorite_products(customer_id)
            
            preference_data = []
            for pref in preferences:
                preference_data.append({
                    'type': pref[0],
                    'value': pref[1],
                    'created_date': pref[2]
                })
            
            favorite_data = []
            for fav in favorites:
                favorite_data.append({
                    'product_id': fav[0],
                    'name': fav[1],
                    'price': float(fav[2]),
                    'total_quantity': fav[3],
                    'order_count': fav[4]
                })
            
            return jsonify({
                'success': True, 
                'data': {
                    'preferences': preference_data,
                    'favorites': favorite_data
                }
            })
        
        elif request.method == 'POST':
            data = request.get_json()
            customer_id = data.get('customer_id')
            preference_type = data.get('preference_type')
            preference_value = data.get('preference_value')
            
            if not all([customer_id, preference_type, preference_value]):
                return jsonify({'success': False, 'error': 'Missing required fields'}), 400
            
            db.save_member_preference(customer_id, preference_type, preference_value)
            return jsonify({'success': True, 'message': 'Preference saved successfully'})
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/member/<int:customer_id>', methods=['GET'])
def get_member_details(customer_id):
    try:
        if not session.get('admin_logged_in'):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 401
        
        member = db.get_member_by_customer_id(customer_id)
        if not member:
            return jsonify({'success': False, 'error': 'Member not found'}), 404
        
        preferences = db.get_member_preferences(customer_id)
        preference_data = []
        for pref in preferences:
            preference_data.append({
                'type': pref[0],
                'value': pref[1],
                'created_date': pref[2]
            })
        
        favorites = db.get_member_favorite_products(customer_id)
        favorite_data = []
        for fav in favorites:
            favorite_data.append({
                'product_id': fav[0],
                'name': fav[1],
                'price': float(fav[2]),
                'total_quantity': fav[3],
                'order_count': fav[4]
            })
        
        orders = db.get_order_history(customer_id)
        order_stats = {
            'total_orders': len(orders),
            'total_spent': sum(float(order[4]) for order in orders) if orders else 0,
            'last_order_date': orders[0][2] if orders else None
        }
        
        return jsonify({
            'success': True,
            'data': {
                'customer_id': member[0],
                'name': member[1],
                'phone': member[2],
                'email': member[3],
                'address': member[4],
                'customer_type': member[5],
                'date_of_birth': member[7],
                'registration_date': member[8],
                'preferences': preference_data,
                'favorites': favorite_data,
                'order_stats': order_stats
            }
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Serve images under /picture/* from static/picture directory
@app.route('/picture/<path:filename>')
def serve_picture(filename):
    pictures_dir = os.path.join(app.static_folder, 'picture')
    return send_from_directory(pictures_dir, filename)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5050)