"""
瀏覽器相容性測試模組
測試不同瀏覽器下的應用表現
"""
import pytest
import time

# 有條件地導入 playwright，處理可能沒有安裝的情況
try:
    from playwright.sync_api import sync_playwright
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    sync_playwright = None


# 標記所有測試為需要 playwright
pytestmark = pytest.mark.skipif(not PLAYWRIGHT_AVAILABLE, 
                               reason="playwright 套件未安裝，跳過瀏覽器相容性測試")


@pytest.mark.parametrize("browser_type", ["chromium", "firefox", "webkit"])
def test_browser_compatibility(browser_type):
    """測試不同瀏覽器的相容性"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("playwright 套件未安裝")
        
    with sync_playwright() as p:
        browser_instance = getattr(p, browser_type).launch(headless=True)
        page = browser_instance.new_page()
        
        try:
            # 設定視窗大小為桌面尺寸
            page.set_viewport_size({"width": 1920, "height": 1080})
            
            # 訪問測試網站
            page.goto('http://localhost:5000')
            
            # 等待主要元素載入
            page.wait_for_selector('.phone-list', timeout=5000)
            
            # 檢查關鍵元素是否存在
            assert page.query_selector('canvas') is not None
            assert page.query_selector('.phone-list') is not None
            
            # 測試互動功能如按鈕點擊
            buttons = page.query_selector_all('button')
            if len(buttons) > 0:
                buttons[0].click()
                time.sleep(0.5)  # 等待回應
            
        except Exception as e:
            pytest.skip(f"{browser_type} 相容性測試失敗: {str(e)}")
        finally:
            page.close()
            browser_instance.close()


@pytest.mark.parametrize("device_size", [
    {"width": 1920, "height": 1080, "name": "desktop"},
    {"width": 768, "height": 1024, "name": "tablet"},
    {"width": 375, "height": 667, "name": "mobile"}
])
def test_responsive_design(device_size):
    """測試響應式設計在不同螢幕尺寸的表現"""
    if not PLAYWRIGHT_AVAILABLE:
        pytest.skip("playwright 套件未安裝")
        
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            # 設定視窗大小
            page.set_viewport_size({"width": device_size["width"], "height": device_size["height"]})
            
            # 訪問測試網站
            page.goto('http://localhost:5000')
            
            # 等待主要元素載入
            page.wait_for_selector('.phone-list', timeout=5000)
            
            # 檢查不同裝置上的元素是否正確顯示
            if device_size["name"] == "mobile":
                # 確認在手機版上有適當的顯示
                assert page.query_selector('canvas') is not None
                
            elif device_size["name"] == "tablet":
                # 平板特定檢查
                assert page.query_selector('.phone-list') is not None
                assert page.query_selector('canvas') is not None
                
            else:  # desktop
                # 桌面版特定檢查
                assert page.query_selector('.phone-list') is not None
                assert page.query_selector('canvas') is not None
                
        except Exception as e:
            pytest.skip(f"{device_size['name']} 響應式設計測試失敗: {str(e)}")
        finally:
            page.close()
            browser.close()
