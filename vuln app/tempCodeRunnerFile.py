from flask import Flask, render_template, request, redirect, url_for, session, abort
import sqlite3
from database import init_db

app = Flask(__name__)
app.secret_key = b'insecure_super_secret_key_123'  # INTENTIONAL: Hardcoded weak secret

# Initialize vulnerable database
init_db()

"""
SECURITY NOTICE
This application is DELIBERATELY VULNERABLE for educational purposes only!
- SQL Injection everywhere (string concatenation)
- IDOR (no ownership checks)
- Broken authentication/authorization
- Plaintext passwords
- Predictable session handling
NEVER deploy to production!
"""

def get_db_connection():
    """Get database connection"""
    conn = sqlite3.connect('shop.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        role_type = request.form.get('role', 'customer')
        
        # CRITICAL VULNERABILITY: SQL Injection via string concatenation
        conn = get_db_connection()
        query = f"""
            SELECT * FROM users 
            WHERE username = '{username}' 
            AND password = '{password}'
            AND role = '{role_type}'
        """
        print(f"SQL QUERY: {query}")  # Debug info for lab
        
        user = conn.execute(query).fetchone()
        conn.close()
        
        if user:
            # BROKEN SESSION HANDLING: Predictable, unsigned session data
            session['user_id'] = user['id']
            session['username'] = user['username']
            session['role'] = user['role']
            
            if user['role'] == 'admin':
                return redirect(url_for('admin'))
            elif user['role'] == 'staff':
                return redirect(url_for('dashboard'))
            else:
                return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid credentials")
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('dashboard.html', user=session)

@app.route('/products')
def products():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    search = request.args.get('search', '')
    
    # SQL INJECTION VULNERABLE: Product search
    conn = get_db_connection()
    query = f"""
        SELECT * FROM products 
        WHERE name LIKE '%{search}%' OR description LIKE '%{search}%'
    """
    print(f"PRODUCTS SQL: {query}")
    
    products = conn.execute(query).fetchall()
    conn.close()
    
    return render_template('products.html', products=products, user=session)

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # IDOR VULNERABILITY: No ownership check!
    user_id = request.args.get('id', session['user_id'])
    
    conn = get_db_connection()
    # SQL Injection + IDOR
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    print(f"PROFILE SQL: {query}")
    
    user = conn.execute(query).fetchone()
    conn.close()
    
    if not user:
        abort(404)
    
    return render_template('profile.html', profile_user=user, current_user=session)

@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # IDOR VULNERABILITY: View any user's orders
    user_id = request.args.get('user_id', session['user_id'])
    
    conn = get_db_connection()
    # SQL Injection vulnerable order lookup
    query = f"""
        SELECT o.*, p.name as product_name, u.username 
        FROM orders o 
        JOIN products p ON o.product_id = p.id 
        JOIN users u ON o.user_id = u.id 
        WHERE o.user_id = '{user_id}'
    """
    print(f"ORDERS SQL: {query}")
    
    orders = conn.execute(query).fetchall()
    conn.close()
    
    return render_template('orders.html', orders=orders, user_id=user_id, user=session)

@app.route('/customers')
def customers():
    # NO AUTH CHECK - Accessible to everyone!
    conn = get_db_connection()
    
    # SQL Injection in customer search
    search = request.args.get('search', '')
    query = f"SELECT * FROM users WHERE username LIKE '%{search}%' OR role LIKE '%{search}%'"
    print(f"CUSTOMERS SQL: {query}")
    
    customers = conn.execute(query).fetchall()
    conn.close()
    
    return render_template('customers.html', customers=customers)

@app.route('/admin')
def admin():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # BROKEN ACCESS CONTROL: Any logged-in user can access admin!
    
    conn = get_db_connection()
    
    # All users
    users = conn.execute("SELECT * FROM users").fetchall()
    
    # All orders
    orders = conn.execute("""
        SELECT o.*, p.name as product_name, u.username 
        FROM orders o 
        JOIN products p ON o.product_id = p.id 
        JOIN users u ON o.user_id = u.id
    """).fetchall()
    
    # All products
    products = conn.execute("SELECT * FROM products").fetchall()
    
    conn.close()
    
    return render_template('admin.html', users=users, orders=orders, products=products, user=session)

@app.route('/admin/user')
def admin_user():
    # IDOR: Modify any user
    user_id = request.args.get('id')
    
    conn = get_db_connection()
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    user = conn.execute(query).fetchone()
    conn.close()
    
    return render_template('profile.html', profile_user=user, current_user=session)

@app.route('/order')
def single_order():
    # IDOR: View/modify any order
    order_id = request.args.get('order_id')
    
    conn = get_db_connection()
    query = f"SELECT * FROM orders WHERE id = '{order_id}'"
    order = conn.execute(query).fetchone()
    conn.close()
    
    return render_template('orders.html', orders=[order] if order else [], user=session)

if __name__ == '__main__':
    print("VULNERABLE SHOP APP STARTING...")
    print("Test Credentials:")
    print("   Customer: user1/user123")
    print("   Staff:    staff1/staff123") 
    print("   Admin:    admin/admin123")
    print("Access: http://127.0.0.1:5000")
    print("\nTry these exploits:")
    print("   1. SQLi: ' OR 1=1-- in login")
    print("   2. IDOR: /profile?id=1 (as any user)")
    print("   3. Admin bypass: Direct /admin access")
    app.run(debug=True, host='0.0.0.0', port=5000)
