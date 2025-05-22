import sqlite3
from config import DB_PATH


def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 物料表
    c.execute('''CREATE TABLE IF NOT EXISTS materials (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        type TEXT CHECK(type IN ('食材','配料','调料','工具')),
        unit_price REAL CHECK(unit_price >= 0),
        unit TEXT,
        stock REAL DEFAULT 0
    )''')

    # 菜品表
    c.execute('''CREATE TABLE IF NOT EXISTS dishes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        base_cost REAL DEFAULT 0,
        final_cost REAL DEFAULT 0
    )''')

    # 配方表
    c.execute('''CREATE TABLE IF NOT EXISTS recipe_items (
        dish_id INTEGER NOT NULL,
        material_id TEXT NOT NULL,
        quantity REAL NOT NULL,
        FOREIGN KEY(dish_id) REFERENCES dishes(id),
        FOREIGN KEY(material_id) REFERENCES materials(id)
    )''')

    # 采购记录表（新增）
    c.execute('''CREATE TABLE IF NOT EXISTS purchases (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_id TEXT NOT NULL,
        quantity REAL NOT NULL,
        unit_price REAL NOT NULL,
        purchase_date DATE NOT NULL,
        FOREIGN KEY(material_id) REFERENCES materials(id)
    )''')

    # 库存流水表（新增）
    c.execute('''CREATE TABLE IF NOT EXISTS inventory_logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        material_id TEXT NOT NULL,
        change_type TEXT CHECK(change_type IN ('采购入库','菜品消耗')),
        quantity REAL NOT NULL,
        unit_price REAL,
        log_time DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY(material_id) REFERENCES materials(id)
    )''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_db()
    print("数据库初始化完成，路径：", DB_PATH)