"""
測試共用設定與 fixture
"""
import os
import sys
import pytest
from flask import Flask
from flask.testing import FlaskClient

# 將專案根目錄加入 sys.path
sys.path.insert(0, os.path.abspath(os.path.dirname(os.path.dirname(__file__))))

# 從 index 模組導入 app 物件
try:
    from index import app as flask_app
except ImportError:
    flask_app = Flask('test_app')  # 建立測試用應用


@pytest.fixture
def app():
    """建立測試用 Flask 應用"""
    flask_app.config.update({
        "TESTING": True,
    })
    yield flask_app


@pytest.fixture
def client(app):
    """建立測試用 Flask 客戶端"""
    return app.test_client()


@pytest.fixture
def mock_phone_data():
    """模擬手機資料"""
    return [
        {
            'id': 'test_phone_1',  # 使用字串型態 ID
            'name': '測試手機 A',
            'model': 'TestPhoneA',
            'dimensions': '150 x 70 x 8 mm',
            'weight': '180 g',
            'display': '6.5 inches, AMOLED',
            'cpu': 'Snapdragon 888',
            'memory': '8GB RAM, 128GB Storage',
            'model_path': '/models/phone_a.glb'
        },
        {
            'id': 'test_phone_2',  # 使用字串型態 ID
            'name': '測試手機 B',
            'model': 'TestPhoneB',
            'dimensions': '160 x 75 x 9 mm',
            'weight': '200 g',
            'display': '6.8 inches, Super AMOLED',
            'cpu': 'Dimensity 9000',
            'memory': '12GB RAM, 256GB Storage',
            'model_path': '/models/phone_b.glb'
        }
    ]
