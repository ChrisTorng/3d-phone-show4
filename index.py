from flask import Flask, jsonify, send_from_directory, render_template, request, abort
import os
import json
import sqlite3
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
        format='%(asctime)s - %(name)s - %(levellevel)s - %(message)s',
        handlers=[
            logging.NullHandler()
        ]
    )

logger = logging.getLogger(__name__)

app = Flask(__name__)

# 資料路徑設定
DATA_PATH = os.path.join(os.path.dirname(__file__), 'data')
MODELS_PATH = os.path.join(os.path.dirname(__file__), 'models')
DB_PATH = os.path.join(DATA_PATH, 'phones.db')
SQL_INIT_PATH = os.path.join(DATA_PATH, 'database.sql')
JSON_PATH = os.path.join(DATA_PATH, 'phones.json')

# 確保資料目錄存在
if not os.path.exists(DATA_PATH):
    try:
        os.makedirs(DATA_PATH)
    except Exception as e:
        logger.error(f"無法建立資料目錄: {e}")

# 資料庫連線函式
def get_db_connection():
    """建立並返回資料庫連線"""
    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn
    except Exception as e:
        logger.error(f"資料庫連線錯誤: {e}")
        return None

def get_default_phones():
    """從 JSON 檔案讀取預設手機資料"""
    try:
        if os.path.exists(JSON_PATH):
            with open(JSON_PATH, 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        logger.error(f"讀取預設手機資料檔案錯誤: {e}")
    return []

# 初始化資料庫
def init_database():
    """從 SQL 檔案初始化資料庫結構和資料"""
    try:
        if not os.path.exists(SQL_INIT_PATH):
            logger.error("找不到資料庫初始化檔案")
            return
            
        conn = get_db_connection()
        if conn:
            with open(SQL_INIT_PATH, 'r', encoding='utf-8') as sql_file:
                conn.executescript(sql_file.read())
            conn.commit()
            conn.close()
            logger.info("資料庫初始化完成")
    except Exception as e:
        logger.error(f"資料庫初始化錯誤: {e}")

# 從預設資料建立資料庫
def create_db_from_default_data():
    """當 SQL 檔案不可用時，從 JSON 檔案建立資料庫"""
    try:
        conn = get_db_connection()
        if conn:
            # 建立表格
            conn.execute('''
            CREATE TABLE IF NOT EXISTS phones (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                screen TEXT NOT NULL,
                processor TEXT NOT NULL,
                camera TEXT NOT NULL,
                battery TEXT NOT NULL,
                storage TEXT NOT NULL,
                model_path TEXT NOT NULL,
                special_features TEXT NOT NULL
            )
            ''')
            
            # 清除現有資料
            conn.execute('DELETE FROM phones')
            
            # 從 JSON 檔案讀取並插入預設資料
            default_phones = get_default_phones()
            if default_phones:
                for phone in default_phones:
                    conn.execute('''
                    INSERT INTO phones (id, name, screen, processor, camera, battery, storage, model_path, special_features)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    ''', (
                        phone['id'], phone['name'], phone['screen'], phone['processor'], 
                        phone['camera'], phone['battery'], phone['storage'], 
                        phone['model_path'], phone['special_features']
                    ))
                
                conn.commit()
                logger.info("從 JSON 檔案建立資料庫完成")
            else:
                logger.error("無法讀取預設資料")
            
            conn.close()
    except Exception as e:
        logger.error(f"直接建立資料庫錯誤: {e}")

# 從資料庫讀取手機資料
def load_phones_data():
    """從 SQLite 資料庫讀取手機資料"""
    try:
        conn = get_db_connection()
        if conn:
            cursor = conn.execute('SELECT * FROM phones')
            phones = [dict(row) for row in cursor.fetchall()]
            conn.close()
            if phones:
                return phones
        
        # 如果資料庫讀取失敗或沒有資料，重新初始化資料庫並再次讀取
        init_database()
        conn = get_db_connection()
        if conn:
            cursor = conn.execute('SELECT * FROM phones')
            phones = [dict(row) for row in cursor.fetchall()]
            conn.close()
            return phones if phones else get_default_phones()
        
        # 若仍然失敗，返回從 JSON 讀取的預設資料
        return get_default_phones()
    except Exception as e:
        logger.error(f"讀取手機資料時發生錯誤: {e}")
        return get_default_phones()

# 保存手機資料到 JSON (為向後相容保留此函式)
def save_default_data():
    """保存預設資料到 JSON 檔案（為了向後相容性）"""
    try:
        phones_file = os.path.join(DATA_PATH, 'phones.json')
        if not os.path.exists(phones_file):
            with open(phones_file, 'w', encoding='utf-8') as f:
                json.dump(get_default_phones(), f, ensure_ascii=False, indent=4)
            logger.info("已建立預設手機資料文件")
    except Exception as e:
        logger.error(f"保存預設資料時發生錯誤: {e}")

# 處理路徑遍歷嘗試
def safe_path_join(base, path):
    # 處理常見靜態資源的特殊情況
    if path.endswith(('.css', '.js', '.html', '.png', '.jpg', '.jpeg', '.gif', '.glb')):
        # 對靜態資源使用專案根目錄
        project_root = os.path.dirname(__file__)
        full_path = os.path.normpath(os.path.join(project_root, path))
        if os.path.exists(full_path):
            return full_path
    
        # 特別針對 .glb 檔案在 models 目錄中進行第二次檢查
        if path.endswith('.glb'):
            model_path = os.path.normpath(os.path.join(MODELS_PATH, os.path.basename(path)))
            if os.path.exists(model_path):
                return model_path

    # 原有的安全檢查邏輯
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

# 初始化應用程式
try:
    # 確保資料目錄存在
    if not os.path.exists(DATA_PATH):
        os.makedirs(DATA_PATH)
    
    # 初始化資料庫
    init_database()
    
    # 為向後相容性保留 JSON 檔案
    save_default_data()
except Exception as e:
    logger.error(f"初始化時發生錯誤: {e}")

if __name__ == '__main__':
    # 開發環境中使用 debug 模式
    app.run(debug=True)
else:
    # 正式環境中關閉 debug
    app.debug = False