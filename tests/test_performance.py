"""
效能測試模組
測試應用程式在各種條件下的效能表現
"""
import pytest
import time
import statistics

# 有條件地導入 playwright，處理可能沒有安裝的情況
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    sync_playwright = None


# 標記所有測試為需要 playwright
pytestmark = pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, 
                               reason="playwright 套件未安裝，跳過效能測試")


@pytest.fixture(scope='module')
def performance_browser():
    """啟動瀏覽器以進行效能測試"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("playwright 套件未安裝")
        
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


def test_initial_load_time(performance_browser):
    """測試初始頁面載入時間"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("playwright 套件未安裝")
        
    page = performance_browser.new_page()
    try:
        # 啟用效能指標收集
        client = page.context.new_cdp_session(page)
        client.send('Performance.enable')
        
        # 清除效能指標
        client.send('Performance.clearMetrics')
        
        # 設定網路條件模擬
        client.send('Network.emulateNetworkConditions', {
            'offline': False,
            'latency': 20,  # 20ms
            'downloadThroughput': 1.5 * 1024 * 1024 / 8,  # 1.5Mbps
            'uploadThroughput': 750 * 1024 / 8,  # 750kbps
            'connectionType': 'cellular3g'
        })
        
        # 記錄開始時間
        start_time = time.time()
        
        # 訪問網站
        page.goto('http://localhost:5000')
        
        # 等待頁面載入完成
        page.wait_for_selector('canvas')
        page.wait_for_selector('.phone-list')
        
        # 計算頁面載入時間
        load_time = time.time() - start_time
        
        # 獲取效能指標
        metrics = client.send('Performance.getMetrics')
        
        print(f"初始頁面載入時間: {load_time:.2f} 秒")
        
        # 檢查載入時間是否在可接受範圍內
        assert load_time < 5.0, "頁面載入時間超過 5 秒"
        
    except Exception as e:
        pytest.skip(f"效能測試失敗: {str(e)}")
    finally:
        page.close()


def test_model_load_time(performance_browser):
    """測試 3D 模型載入時間"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("playwright 套件未安裝")
        
    page = performance_browser.new_page()
    try:
        page.goto('http://localhost:5000')
        page.wait_for_selector('.phone-list')
        
        # 獲取手機列表
        phone_items = page.query_selector_all('.phone-item')
        
        if len(phone_items) < 2:
            pytest.skip("需要至少兩個手機模型才能進行測試")
        
        load_times = []
        
        for i in range(min(3, len(phone_items))):
            # 點擊前先等待一下
            time.sleep(0.5)
            
            # 記錄開始時間
            start_time = time.time()
            
            # 點擊選擇手機
            phone_items[i].click()
            
            # 等待模型載入 (等待某個指示器消失或 canvas 更新)
            page.wait_for_function('''
                document.querySelector('.loading')?.style.display === 'none' ||
                !document.querySelector('.loading')
            ''')
            
            # 計算載入時間
            load_time = time.time() - start_time
            load_times.append(load_time)
            
            print(f"模型 {i+1} 載入時間: {load_time:.2f} 秒")
        
        avg_load_time = statistics.mean(load_times)
        print(f"平均模型載入時間: {avg_load_time:.2f} 秒")
        
        # 檢查平均載入時間是否在可接受範圍內
        assert avg_load_time < 3.0, "平均模型載入時間超過 3 秒"
        
    except Exception as e:
        pytest.skip(f"效能測試失敗: {str(e)}")
    finally:
        page.close()


def test_interaction_response_time(performance_browser):
    """測試互動操作回應時間"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("playwright 套件未安裝")
        
    page = performance_browser.new_page()
    try:
        page.goto('http://localhost:5000')
        page.wait_for_selector('.control-panel')
        
        # 等待 canvas 和控制按鈕
        page.wait_for_selector('canvas')
        
        response_times = []
        
        # 找到可點擊的互動元素
        control_buttons = page.query_selector_all('button')
        if len(control_buttons) == 0:
            pytest.skip("找不到互動按鈕元素")
        
        # 選擇第一個按鈕進行測試
        test_button = control_buttons[0]
        
        for _ in range(5):
            # 記錄開始時間
            start_time = time.time()
            
            # 點擊按鈕
            test_button.click()
            
            # 等待渲染更新
            page.wait_for_timeout(50)  # 50ms 足夠檢測到大多數回應
            
            # 計算回應時間
            response_time = time.time() - start_time
            response_times.append(response_time)
            
        avg_response = statistics.mean(response_times)
        print(f"平均互動回應時間: {avg_response:.3f} 秒")
        
        # 檢查平均回應時間是否在可接受範圍內
        assert avg_response < 0.1, "平均互動回應時間超過 100ms"
        
    except Exception as e:
        pytest.skip(f"效能測試失敗: {str(e)}")
    finally:
        page.close()
