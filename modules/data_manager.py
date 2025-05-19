import sqlite3
from tkinter import messagebox
from config import DB_PATH, MATERIAL_TYPES, VALID_UNITS


class MaterialManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH)

    def _generate_id(self, material_type):
        """生成物料ID（如SC001）"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM materials WHERE type=? ORDER BY id DESC LIMIT 1",
            (material_type,)
        )
        result = cursor.fetchone()

        prefix = MATERIAL_TYPES[material_type]
        if result:
            last_num = int(result[0][2:])
            new_num = last_num + 1
        else:
            new_num = 1
        return f"{prefix}{new_num:03d}"

    def material_exists(self, name, material_type):
        """检查物料是否已存在"""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT id FROM materials WHERE name=? AND type=?",
            (name, material_type)
        )
        return cursor.fetchone() is not None

    def add_or_update_material(self, name, material_type, category, unit_price, unit):
        """添加或更新物料"""
        try:
            # 输入验证
            if not name.strip():
                raise ValueError("物料名称不能为空")
            if unit not in VALID_UNITS:
                raise ValueError(f"无效单位，请选择：{', '.join(VALID_UNITS)}")

            # 检查是否已存在同名同类型物料
            if self.material_exists(name, material_type):
                # 获取现有ID
                cursor = self.conn.cursor()
                cursor.execute(
                    "SELECT id FROM materials WHERE name=? AND type=?",
                    (name, material_type)
                )
                material_id = cursor.fetchone()[0]

                # 更新价格和单位
                cursor.execute('''UPDATE materials 
                               SET unit_price=?, unit=?
                               WHERE id=?''',
                               (unit_price, unit, material_id))
                action = "更新"
            else:
                # 生成新ID
                material_id = self._generate_id(material_type)
                cursor = self.conn.cursor()
                cursor.execute('''INSERT INTO materials 
                               (id, name, type, category, unit_price, unit)
                               VALUES (?, ?, ?, ?, ?, ?)''',
                               (material_id, name, material_type, category, unit_price, unit))
                action = "添加"

            self.conn.commit()
            return action
        except sqlite3.IntegrityError:
            messagebox.showerror("错误", "物料名称已存在！")
            return None
        except Exception as e:
            messagebox.showerror("未知错误", str(e))
            return None

    def get_all_materials(self):
        """获取所有物料数据"""
        return self.conn.execute("SELECT * FROM materials").fetchall()