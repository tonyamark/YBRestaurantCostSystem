import sqlite3
from tkinter import messagebox
from config import DB_PATH, MATERIAL_CODES, VALID_UNITS


class MaterialManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)

    def _generate_id(self, material_type):
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM materials WHERE type=? ORDER BY id DESC LIMIT 1",
            (material_type,)
        )
        result = cursor.fetchone()
        prefix = MATERIAL_CODES[material_type]
        new_num = int(result[0][2:]) + 1 if result else 1
        return f"{prefix}{new_num:03d}"

    def add_material(self, name, material_type, unit_price, unit):
        try:
            if unit not in VALID_UNITS:
                raise ValueError(f"无效单位，可选：{', '.join(VALID_UNITS)}")

            material_id = self._generate_id(material_type)
            cursor = self.conn.cursor()
            cursor.execute('''INSERT INTO materials 
                           (id, name, type, unit_price, unit)
                           VALUES (?, ?, ?, ?, ?)''',
                           (material_id, name, material_type, unit_price, unit))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError as e:
            messagebox.showerror("错误", f"名称重复：{str(e)}")
            return False
        except Exception as e:
            messagebox.showerror("错误", str(e))
            return False

    def get_all_materials(self):
        return self.conn.execute("SELECT * FROM materials").fetchall()

    def delete_material(self, material_id):
        try:
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM materials WHERE id = ?", (material_id,))
            self.conn.commit()
            return cursor.rowcount > 0
        except Exception as e:
            messagebox.showerror("删除失败", str(e))
            return False