import sqlite3
import os

def init_db():
    """Initialize the vulnerable database - NO SECURITY WHATSOEVER"""
    if os.path.exists('shop.db'):
        os.remove('shop.db')
    
    conn = sqlite3.connect('shop.db')
    cursor = conn.cursor()
    
    # Users table - PLAIN TEXT PASSWORDS (VULNERABLE!)
    cursor.execute('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL
        )
    ''')
    
    # Products table
    cursor.execute('''
        CREATE TABLE products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            description TEXT,
            price REAL NOT NULL,
            stock INTEGER NOT NULL
        )
    ''')
    
    # Orders table - NO FOREIGN KEY CONSTRAINTS (VULNERABLE!)
    cursor.execute('''
        CREATE TABLE orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            product_id INTEGER,
            quantity INTEGER,
            total REAL
        )
    ''')
    
    # Insert test data
    # INTENTIONAL: Plain text passwords, predictable usernames
    cursor.executemany('''
        INSERT INTO users (username, password, role) VALUES (?, ?, ?)
    ''', [
        ('user1', 'user123', 'customer'),
        ('staff1', 'staff123', 'staff'),
        ('admin', 'admin123', 'admin')
    ])
    
    cursor.executemany('''
        INSERT INTO products (name, description, price, stock) VALUES (?, ?, ?, ?)
    ''', [
        ('Laptop', 'Gaming laptop', 999.99, 10),
        ('Mouse', 'Wireless mouse', 29.99, 50),
        ('Keyboard', 'Mechanical keyboard', 149.99, 25),
        ('Monitor', '24" monitor', 199.99, 15)
    ])
    
    conn.commit()
    conn.close()
    print("Vulnerable database initialized!")

if __name__ == '__main__':
    init_db()
