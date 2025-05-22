import sqlite3
from config import DB_PATH
from tkinter import messagebox
from modules.inventory_manager import InventoryManager


class RecipeManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)

    def create_dish(self, name):
        try:
            cursor = self.conn.cursor()
            cursor.execute('INSERT INTO dishes (name) VALUES (?)', (name,))
            self.conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            messagebox.showerror("错误", "菜品名称已存在！")
            return False

    def add_ingredient_to_dish(self, dish_id, material_id, quantity):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO recipe_items (dish_id, material_id, quantity)
                VALUES (?, ?, ?)
            ''', (dish_id, material_id, quantity))
            self.conn.commit()
            return True
        except Exception as e:
            messagebox.showerror("添加失败", str(e))
            return False

    def calculate_base_cost(self, dish_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT m.id, r.quantity
            FROM recipe_items r
            JOIN materials m ON r.material_id = m.id
            WHERE r.dish_id = ?
        ''', (dish_id,))

        total = 0.0
        for material_id, quantity in cursor.fetchall():
            unit_cost = InventoryManager().get_weighted_cost(material_id)
            total += unit_cost * quantity
        return round(total, 2)