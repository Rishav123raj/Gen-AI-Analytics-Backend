import sqlite3

def init_db():
    """Initialize the SQLite database."""
    conn = sqlite3.connect(':memory:')
    cursor = conn.cursor()
    
    # Create tables
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY,
        name TEXT,
        email TEXT,
        revenue REAL,
        region TEXT,
        join_date TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS products (
        id INTEGER PRIMARY KEY,
        name TEXT,
        category TEXT,
        price REAL,
        inventory INTEGER,
        supplier TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY,
        product_id INTEGER,
        customer_id INTEGER,
        amount REAL,
        date TEXT,
        region TEXT
    )
    """)
    
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees (
        id INTEGER PRIMARY KEY,
        name TEXT,
        department TEXT,
        salary REAL,
        hire_date TEXT
    )
    """)
    
    conn.commit()
    return conn