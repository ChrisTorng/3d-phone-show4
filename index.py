from flask import Flask, jsonify, send_from_directory, render_template, request, abort
import os
import json
from werkzeug.utils import secure_filename
import logging
import sys

# 判斷是否為開發環境
is_development = __name__ == '__main__' or os.environ.get('FLASK_ENV') == 'development'

# 設定日誌記錄
if is_development:
    # 開發環境：輸出到檔案和控制台
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler("app.log"),
            logging.StreamHandler()
        ]
    )
else:
    # 生產環境：完全不輸出日誌
    logging.basicConfig(
        level=logging.CRITICAL,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.NullHandler()
        ]
    )

logger = logging.getLogger(__name__)

app = Flask(__name__)

# 手機資料路徑
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
MODELS_PATH = os.path.join(os.path.dirname(__file__), 'models')

# 確保資料目錄存在
if not os.path.exists(DATA_PATH):
    try:
        os.makedirs(DATA_PATH)
    except Exception as e:
        logger.error(f"無法建立資料目錄: {e}")

# 預設手機資料
DEFAULT_PHONES = [
    {
        'id': 'iphone_16_pro_max',
        'name': 'iPhone 16 Pro Max',
        'screen': '6.9 inch OLED',
        'processor': 'Apple A18 Pro',
        'camera': '108MP 主鏡頭 + 48MP 超廣角 + 12MP 望遠',
        'battery': '4685 mAh',
        'storage': '256 GB / 512 GB / 1 TB',
        'model_path': 'models/iphone_16_pro_max.glb',
        'special_features': '動態島、光學變焦、ProMotion 120Hz 螢幕'
    },
    {
        'id': 'samsung_galaxy_s22_ultra',
        'name': 'Samsung Galaxy S22 Ultra',
        'screen': '6.8 inch Dynamic AMOLED 2X',
        'processor': 'Qualcomm Snapdragon 8 Gen 1',
        'camera': '108MP 主鏡頭 + 12MP 超廣角 + 10MP 望遠 + 10MP 潛望式鏡頭',
        'battery': '5000 mAh',
        'storage': '128 GB / 256 GB / 512 GB / 1 TB',
        'model_path': 'models/samsung_galaxy_s22_ultra.glb',
        'special_features': 'S Pen 支援、100倍空間變焦、45W 快速充電'
    },
    {
        'id': 'samsung_galaxy_z_flip_3',
        'name': 'Samsung Galaxy Z Flip 3',
        'screen': '6.7 inch 主螢幕 + 1.9 inch 外螢幕',
        'processor': 'Qualcomm Snapdragon 888',
        'camera': '12MP 主鏡頭 + 12MP 超廣角',
        'battery': '3300 mAh',
        'storage': '128 GB / 256 GB',
        'model_path': 'models/Samsung_Galaxy_Z_Flip_3.glb',
        'special_features': '折疊螢幕、IPX8 防水、無線充電'
    }
]

# 保存預設資料到 JSON 檔案
def save_default_data():
    try:
        phones_file = os.path.join(DATA_PATH, 'phones.json')
        if not os.path.exists(phones_file):
            with open(phones_file, 'w', encoding='utf-8') as f:
                json.dump(DEFAULT_PHONES, f, ensure_ascii=False, indent=4)
            logger.info("已建立預設手機資料文件")
    except Exception as e:
        logger.error(f"保存預設資料時發生錯誤: {e}")

# 讀取手機資料
def load_phones_data():
    try:
        phones_file = os.path.join(DATA_PATH, 'phones.json')
        if os.path.exists(phones_file):
            with open(phones_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            save_default_data()
            return DEFAULT_PHONES
    except Exception as e:
        logger.error(f"讀取手機資料時發生錯誤: {e}")
        return DEFAULT_PHONES

# 處理路徑遍歷嘗試
def safe_path_join(base, path):
    path = secure_filename(path)
    full_path = os.path.normpath(os.path.join(base, path))
    
    # 確保路徑在基礎目錄內
    if not full_path.startswith(os.path.abspath(base)):
        logger.warning(f"嘗試存取基礎目錄外的路徑: {path}")
        return None
    return full_path

@app.route('/api/phones', methods=['GET'])
def get_phones():
    try:
        phones = load_phones_data()
        return jsonify(phones)
    except Exception as e:
        logger.error(f"API 處理錯誤: {e}")
        return jsonify({'error': '讀取手機資料時發生錯誤'}), 500

@app.route('/api/phones/<phone_id>', methods=['GET'])
def get_phone(phone_id):
    try:
        phones = load_phones_data()
        phone = next((p for p in phones if p['id'] == phone_id), None)
        
        if phone:
            return jsonify(phone)
        else:
            return jsonify({'error': '找不到指定的手機'}), 404
    except Exception as e:
        logger.error(f"API 處理錯誤: {e}")
        return jsonify({'error': '讀取手機資料時發生錯誤'}), 500

@app.route('/models/<path:filename>', methods=['GET'])
def get_model(filename):
    try:
        safe_path = safe_path_join(MODELS_PATH, filename)
        if safe_path and os.path.exists(safe_path):
            directory, file = os.path.split(safe_path)
            return send_from_directory(directory, file)
        else:
            logger.warning(f"嘗試存取不存在的模型檔案: {filename}")
            return jsonify({'error': '找不到模型檔案'}), 404
    except Exception as e:
        logger.error(f"提供模型時發生錯誤: {e}")
        return jsonify({'error': '讀取模型檔案時發生錯誤'}), 500

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        logger.error(f"渲染首頁時發生錯誤: {e}")
        return "無法載入頁面，請稍後再試", 500

@app.route('/<path:filename>', methods=['GET'])
def get_resource(filename):
    try:
        # 防止存取敏感檔案
        if filename in ['app.log', 'index.py'] or filename.startswith('data/'):
            return jsonify({'error': '無法存取此資源'}), 403
            
        safe_path = safe_path_join(os.path.dirname(__file__), filename)
        if safe_path and os.path.exists(safe_path):
            directory, file = os.path.split(safe_path)
            return send_from_directory(directory, file)
        else:
            logger.warning(f"嘗試存取不存在的資源: {filename}")
            return jsonify({'error': '找不到資源'}), 404
    except Exception as e:
        logger.error(f"提供資源時發生錯誤: {e}")
        return jsonify({'error': '讀取資源時發生錯誤'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': '找不到請求的資源'}), 404

@app.errorhandler(500)
def internal_server_error(error):
    logger.error(f"內部伺服器錯誤: {error}")
    return jsonify({'error': '內部伺服器錯誤'}), 500

# 建立資料目錄與預設資料
try:
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
    save_default_data()
except Exception as e:
    logger.error(f"初始化時發生錯誤: {e}")

if __name__ == '__main__':
    # 開發環境中使用 debug 模式
    app.run(debug=True)
else:
    # 正式環境中關閉 debug
    app.debug = False