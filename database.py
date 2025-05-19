import sqlite3
from config import DB_PATH


def init_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # 创建物料表（修正字段名）
    c.execute('''CREATE TABLE IF NOT EXISTS materials (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL UNIQUE,
        type TEXT CHECK(type IN ('食材','配料','调料','工具')),
        category TEXT,
        unit_price REAL CHECK(unit_price >= 0),
        unit TEXT,
        stock REAL DEFAULT 0
    )''')

    conn.commit()
    conn.close()


if __name__ == "__main__":
    init_database()
    print("✅ 数据库初始化完成！路径：", DB_PATH)