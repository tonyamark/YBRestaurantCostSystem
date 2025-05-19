import os

# 数据库路径
DB_PATH = os.path.join(os.path.dirname(__file__), 'data', 'restaurant.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

# 物料类型配置
MATERIAL_TYPES = {
    '食材': 'SC',
    '配料': 'PL',
    '调料': 'TL',
    '工具': 'GJ'
}

# 有效单位
VALID_UNITS = ['克', '千克', '毫升', '升', '个', '包', '瓶']