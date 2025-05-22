import os

DB_PATH = os.path.join(os.path.dirname(__file__), 'data/restaurant.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

MATERIAL_CODES = {
    '食材': 'SC',
    '配料': 'PL',
    '调料': 'TL',
    '工具': 'GJ'
}

COLOR_SCHEME = {
    'background': '#F0F0F0',
    'text': '#333333',
    'primary': '#4A90E2',
    'warning': '#FF6B6B'
}

VALID_UNITS = ['克', '千克', '毫升', '升', '个', '包', '瓶', '袋']