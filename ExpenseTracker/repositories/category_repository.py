import sqlite3
from typing import List

from ..models.category import Category
from ..interfaces.icategory import ICategory
from ..services.db import DB_NAME

class CategoryRepository(ICategory):

    def add_category(self, category: Category) -> bool:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO categories (name) VALUES (?)", (category.name.lower(),))
            conn.commit()
            return c.rowcount > 0
    def get_category_by_name(self, category_name: str) -> Category | None:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT id, name FROM categories WHERE name = ?", (category_name.lower(),))
            row = c.fetchone()
            return Category(id=row[0], name=row[1]) if row else None

    def get_all_categories(self) -> List[Category]:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT id, name FROM categories ORDER BY name ASC")
            rows = c.fetchall()
            return [Category(id=row[0], name=row[1]) for row in rows]

    def get_category_by_id(self, category_id: int) -> Category | None:
        with sqlite3.connect(DB_NAME) as conn:
            c = conn.cursor()
            c.execute("SELECT id, name FROM categories WHERE id = ?", (category_id,))
            row = c.fetchone()
            return Category(id=row[0], name=row[1]) if row else None

    def delete_category_by_name(self, category_name: str) -> bool:
        with sqlite3.connect(DB_NAME) as conn:
            conn.execute("PRAGMA foreign_keys = ON")
            c = conn.cursor()
            c.execute("DELETE FROM categories WHERE name = ?", (category_name.lower(),))
            conn.commit()
            return c.rowcount > 0





