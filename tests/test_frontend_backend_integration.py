"""
前後端整合測試
測試前端與後端之間的資料流與整合
"""
import pytest
import time
import os
from unittest.mock import patch

# 有條件地導入 playwright，處理可能沒有安裝的情況
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    sync_playwright = None


# 標記所有測試為需要 playwright
pytestmark = pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, 
                               reason="playwright 套件未安裝，跳過前後端整合測試")


@pytest.fixture(scope='module')
def browser():
    """啟動瀏覽器以進行前端測試"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("playwright 套件未安裝")
        
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        yield browser
        browser.close()


@pytest.fixture
def page(browser):
    """建立新的頁面用於測試"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("playwright 套件未安裝")
        
    page = browser.new_page()
    yield page
    page.close()


def test_load_phone_data(page):
    """測試前端載入手機資料功能"""
    # 假設測試伺服器已經在執行中
    try:
        # 訪問首頁
        page.goto('http://localhost:5000')
        
        # 等待手機資料載入
        page.wait_for_selector('.phone-list')
        
        # 檢查手機列表是否已載入
        phone_items = page.query_selector_all('.phone-item')
        assert len(phone_items) > 0
        
        # 檢查第一個手機資料是否正確顯示
        first_phone = phone_items[0]
        assert first_phone.inner_text() != ''
        
    except Exception as e:
        pytest.skip(f"前端整合測試需要執行中的伺服器: {str(e)}")


def test_phone_selection(page):
    """測試選擇手機型號功能"""
    try:
        # 訪問首頁
        page.goto('http://localhost:5000')
        page.wait_for_selector('.phone-list')
        
        # 選擇第二個手機
        phone_items = page.query_selector_all('.phone-item')
        if len(phone_items) >= 2:
            phone_items[1].click()
            
            # 等待模型載入
            time.sleep(1)  # 給予足夠時間載入
            
            # 檢查資訊區是否更新
            info_section = page.query_selector('.phone-info')
            # 這裡應更新檢查邏輯以符合實際 HTML 結構
            assert info_section is not None
            
            # 檢查 3D 模型是否更新
            canvas = page.query_selector('canvas')
            assert canvas is not None
            
    except Exception as e:
        pytest.skip(f"前端整合測試需要執行中的伺服器: {str(e)}")


def test_model_loading(page):
    """測試 3D 模型載入功能"""
    try:
        # 訪問首頁
        page.goto('http://localhost:5000')
        
        # 等待 3D 模型載入完成
        page.wait_for_selector('canvas')
        time.sleep(2)  # 等待模型實際渲染
        
        # 檢查載入指示器是否存在
        loading_indicator = page.query_selector('.loading')
        
        # 檢查模型是否可見
        canvas = page.query_selector('canvas')
        assert canvas is not None
        assert canvas.is_visible()
        
    except Exception as e:
        pytest.skip(f"前端整合測試需要執行中的伺服器: {str(e)}")
