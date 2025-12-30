from datetime import timedelta
from flask import Flask, render_template, request, redirect, url_for, session, abort
import sqlite3
from database import init_db
import pickle
import base64

app = Flask(__name__)
app.secret_key = b'insecure_super_secret_key_123'

# Initialize database
init_db()

def get_db_connection():
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

        conn = get_db_connection()
        query = """
            SELECT * FROM users
            WHERE username = ?
            AND password = ?
            AND role = ?
        """
        user = conn.execute(query, (username, password, role_type)).fetchone()
        conn.close()

        if user:
            session.clear()
            session['user_id'] = int(user['id'])
            session['role'] = user['role']
            session.permanent = True
            app.permanent_session_lifetime = timedelta(minutes=30)
            return redirect(url_for('dashboard'))

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

    conn = get_db_connection()
    query = """
        SELECT * FROM products
        WHERE name LIKE ? OR description LIKE ?
    """
    products = conn.execute(query, (f'%{search}%', f'%{search}%')).fetchall()
    conn.close()

    return render_template('products.html', products=products, user=session)


@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    query = "SELECT * FROM users WHERE id = ?"
    user = conn.execute(query, (user_id,)).fetchone()
    conn.close()

    if not user:
        abort(404)

    return render_template('profile.html', profile_user=user, current_user=session)


@app.route('/orders')
def orders():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    conn = get_db_connection()
    query = """
        SELECT o.*, p.name AS product_name, u.username
        FROM orders o
        JOIN products p ON o.product_id = p.id
        JOIN users u ON o.user_id = u.id
        WHERE o.user_id = ?
    """
    orders = conn.execute(query, (user_id,)).fetchall()
    conn.close()

    return render_template('orders.html', orders=orders, user=session)


@app.route('/customers')
def customers():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    search = request.args.get('search', '')

    conn = get_db_connection()
    query = "SELECT * FROM users WHERE username LIKE ? OR role LIKE ?"
    customers = conn.execute(query, (f'%{search}%', f'%{search}%')).fetchall()
    conn.close()

    # 🔥 INTENTIONAL XSS: search reflected into template
    return render_template(
        'customers.html',
        customers=customers,
        search=search
    )


@app.route('/admin')
def admin():
    if 'user_id' not in session or session.get('role') != 'admin':
        abort(403)

    conn = get_db_connection()
    users = conn.execute("SELECT * FROM users").fetchall()
    products = conn.execute("SELECT * FROM products").fetchall()
    orders = conn.execute("""
        SELECT o.*, p.name AS product_name, u.username
        FROM orders o
        JOIN products p ON o.product_id = p.id
        JOIN users u ON o.user_id = u.id
    """).fetchall()
    conn.close()

    return render_template(
        'admin.html',
        users=users,
        products=products,
        orders=orders,
        user=session
    )


@app.route("/hackme", methods=["POST"])
def hackme():
    data = base64.urlsafe_b64decode(request.form['pickled'])
    obj = pickle.loads(data)  # 💣 DESERIALIZATION VULNERABILITY (INTENTIONAL)
    return "OK", 204


if __name__ == "__main__":
    print("PATCHED APP WITH INTENTIONAL XSS + DESERIALIZATION")
    print("XSS test: /customers?search=<script>alert(1)</script>")
    app.run(debug=True)
