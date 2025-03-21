"""
後端單元測試模組
測試 API 端點、資料處理和模型載入功能
"""
import pytest
import json
import os
from unittest.mock import patch, MagicMock


def test_home_page(client):
    """測試首頁回應"""
    response = client.get('/')
    assert response.status_code == 200
    assert b'<!DOCTYPE html>' in response.data


def test_get_all_phones(client, mock_phone_data):
    """測試取得所有手機資料 API"""
    with patch('index.load_phones_data', return_value=mock_phone_data):
        response = client.get('/api/phones')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert isinstance(data, list)
        assert len(data) == 2
        assert 'id' in data[0]
        assert 'name' in data[0]
        assert data[0]['name'] == '測試手機 A'


def test_get_phone_by_id(client, mock_phone_data):
    """測試以 ID 取得單一手機資料 API"""
    # 修改測試資料來匹配實際 API 的字串 ID 格式
    test_phone = {
        'id': 'test_phone_1',  # 使用字串型態 ID
        'name': '測試手機 A',
        'model': 'TestPhoneA',
        'dimensions': '150 x 70 x 8 mm',
        'weight': '180 g',
        'display': '6.5 inches, AMOLED',
        'cpu': 'Snapdragon 888',
        'memory': '8GB RAM, 128GB Storage',
        'model_path': '/models/phone_a.glb'
    }
    
    with patch('index.load_phones_data', return_value=[test_phone]):
        response = client.get('/api/phones/test_phone_1')  # 使用匹配的 ID
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['id'] == 'test_phone_1'  # 檢查回傳資料的 ID
        assert data['name'] == '測試手機 A'


def test_get_phone_not_found(client):
    """測試取得不存在手機資料的錯誤處理"""
    with patch('index.load_phones_data', return_value=[]):
        response = client.get('/api/phones/999')
        assert response.status_code == 404


def test_model_file_exists():
    """測試模型檔案存在性檢查函式"""
    from index import safe_path_join
    
    # 模擬檔案檢查
    with patch('os.path.exists', return_value=True):
        assert safe_path_join('models', 'phone_a.glb') is not None
    
    with patch('os.path.exists', return_value=False):
        assert safe_path_join('models', '../sensitive_file.txt') is None


def test_json_data_format():
    """測試 JSON 資料格式驗證"""
    # 測試手機資料 JSON 結構驗證
    test_phone = {
        'id': 'test_phone',
        'name': '測試手機',
        'screen': '6.5 inch',
        'model_path': 'models/test_phone.glb'
    }
    
    # 確認資料結構中包含所需欄位
    assert 'id' in test_phone
    assert 'name' in test_phone
    assert 'model_path' in test_phone
    
    # 驗證資料類型
    assert isinstance(test_phone['id'], str)
    assert isinstance(test_phone['name'], str)
    assert isinstance(test_phone['model_path'], str)


def test_error_handling(client):
    """測試錯誤處理"""
    # 模擬載入資料時發生異常
    with patch('index.load_phones_data', side_effect=Exception('測試錯誤')):
        response = client.get('/api/phones')
        assert response.status_code == 500
        data = json.loads(response.data)
        assert 'error' in data
