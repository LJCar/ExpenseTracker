import sqlite3

DB_NAME = "ExpenseTracker.db"

DEFAULT_CATEGORIES = ["food", "housing", "entertainment", "utilities", "transportation", "restaurant", "income"]

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
                    FOREIGN KEY (category_id) REFERENCES categories(id) ON DELETE CASCADE
                )''')

    # Create saved reports table
    c.execute('''CREATE TABLE IF NOT EXISTS saved_reports (
                    date date UNIQUE NOT NULL,
                    month INTEGER NOT NULL,
                    year INTEGER NOT NULL,
                    total REAL NOT NULL,
                    total_monthly_income REAL NOT NULL,
                    income_usage_percent REAL NOT NULL,
                    income_saved REAL NOT NULL,
                    avg_per_day REAL NOT NULL,
                    budget_used_percent REAL NOT NULL,
                    budget_cap REAL NOT NULL,
                    remaining_budget REAL NOT NULL,
                    is_on_track BOOLEAN NOT NULL
                )''')

    conn.commit()
    conn.close()