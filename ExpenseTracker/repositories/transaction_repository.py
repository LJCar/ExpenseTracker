import sqlite3
from datetime import date
from typing import List

from ..models.transaction import  Transaction
from ..interfaces.itransaction import ITransaction
from ..services.db import DB_NAME


def _build_transactions(rows) -> List[Transaction]:
    return [
        Transaction(
            id=row[0],
            description=row[1],
            amount=row[2],
            t_type=row[3],
            category_id=row[4],
            date=date.fromisoformat(row[5])
        )
        for row in rows
    ]


class TransactionRepository(ITransaction):

    def delete_transaction(self, t_id: int) -> bool:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("DELETE FROM transactions WHERE id = ?", (t_id,))
            conn.commit()
            return c.rowcount > 0

    def add_transaction(self, transaction: Transaction) -> bool:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO transactions "
                      "(description, amount, t_type, category_id, date ) VALUES (?, ?, ?, ?, ?)",
                      (transaction.description.lower(), transaction.amount, transaction.t_type,
                      transaction.category_id, transaction.date))
            return c.rowcount > 0

    def get_all_transactions(self) -> List[Transaction] | None:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT id, description, amount, t_type, category_id, date FROM transactions")
            rows = c.fetchall()

            if not rows:
                return None

            return _build_transactions(rows)

    def get_transactions_by_type(self, t_type: str) -> List[Transaction] | None:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT id, description, amount, t_type, category_id, date "
                      "FROM transactions WHERE t_type = ?", t_type.upper(),)
            rows = c.fetchall()
            if not rows:
                return None
            return _build_transactions(rows)

    def get_transaction_by_description(self, description: str) -> List[Transaction] | None:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT id, description, amount, t_type, category_id, date "
                      "FROM transactions WHERE description LIKE ? ", ("%" + description.lower() + "%",))
            rows = c.fetchall()
            if not rows:
                return None
            return _build_transactions(rows)

    def get_transactions_by_category_id(self, c_id: int) -> List[Transaction] | None:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT id, description, amount, t_type, category_id, date "
                      "FROM transactions WHERE category_id = ?", (c_id,))
            rows = c.fetchall()
            if not rows:
                return None
            return _build_transactions(rows)

    def get_transactions_by_month(self, year: int, month: int) -> List[Transaction] | None:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            target_month = f"{year}-{month:02d}"
            c.execute("SELECT id, description, amount, t_type, category_id, date "
                      "FROM transactions WHERE strftime('%Y-%m', date) = ?", (target_month,))

            rows = c.fetchall()
            if not rows:
                return None
            return _build_transactions(rows)

    def get_transactions_by_year(self, year: int) -> List[Transaction] | None:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT id, description, amount, t_type, category_id, date "
                      "FROM transactions WHERE strftime('%Y', date) = ?", (str(year),))
            rows = c.fetchall()
            if not rows:
                return None
            return _build_transactions(rows)

    def get_transaction_by_week(self, input_date: date) -> List[Transaction] | None:
        target_year = input_date.strftime('%Y')
        target_week = input_date.strftime('%W')

        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT id, description, amount, t_type, category_id, date "
                      "FROM transactions "
                      "WHERE strftime('%Y', date) = ? "
                      "AND strftime('%W', date) = ?", (target_year, target_week,))

            rows = c.fetchall()
            if not rows:
                return None
            return _build_transactions(rows)

    def get_transaction_by_day(self, input_date: date) -> List[Transaction] | None:
        target_day = input_date.isoformat()

        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT id, description, amount, t_type, category_id, date "
                      "FROM transactions WHERE date = ?", (target_day,))

            rows = c.fetchall()
            if not rows:
                return None
            return _build_transactions(rows)


