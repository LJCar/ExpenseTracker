import sqlite3

DB_NAME = "ExpenseTracker.db"

DEFAULT_CATEGORIES = ["food", "housing", "clothing", "entertainment", "utilities", "transportation"]

def initialize_database():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    # Create categories table
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT UNIQUE NOT NULL
                )''')

    # Populate default categories if not already present
    for category in DEFAULT_CATEGORIES:
        c.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category.lower(),))

    # Create transactions table with foreign key
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT NOT NULL,
                    amount REAL NOT NULL,
                    type TEXT CHECK(type IN ('DEBIT', 'CREDIT')) NOT NULL,
                    category_id INTEGER NOT NULL,
                    date DATE NOT NULL,
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE,
                )''')

    conn.commit()
    conn.close()