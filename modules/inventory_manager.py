import sqlite3
from datetime import datetime
from config import DB_PATH
from tkinter import messagebox


class InventoryManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)

    def add_purchase(self, material_id, quantity, unit_price):
        try:
            cursor = self.conn.cursor()
            cursor.execute('''
                INSERT INTO purchases (material_id, quantity, unit_price, purchase_date)
                VALUES (?, ?, ?, ?)
            ''', (material_id, quantity, unit_price, datetime.now().date()))

            cursor.execute('''
                INSERT INTO inventory_logs 
                (material_id, change_type, quantity, unit_price)
                VALUES (?, '采购入库', ?, ?)
            ''', (material_id, quantity, unit_price))

            self.conn.commit()
            return True
        except Exception as e:
            messagebox.showerror("采购失败", str(e))
            return False

    def get_current_stock(self, material_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT SUM(
                CASE WHEN change_type='采购入库' THEN quantity 
                     ELSE -quantity 
                END
            ) 
            FROM inventory_logs 
            WHERE material_id=?
        ''', (material_id,))
        return cursor.fetchone()[0] or 0.0

    def get_weighted_cost(self, material_id):
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT SUM(quantity * unit_price) / SUM(quantity)
            FROM inventory_logs
            WHERE material_id=? AND change_type='采购入库'
        ''', (material_id,))
        return round(cursor.fetchone()[0], 2)