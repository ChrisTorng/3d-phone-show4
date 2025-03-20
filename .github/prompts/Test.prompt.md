# 3D 手機展示平台測試指南

本文件提供 3D 手機展示平台的測試策略與指南，確保專案功能正常運作並符合預期需求。

## 1. 測試環境設定

### 1.1 測試前準備
- 確保已安裝 Python 3.7+
- 確保瀏覽器支援 WebGL
- 安裝所有相依套件：`pip install -r requirements.txt`
- 安裝測試相依套件：`pip install pytest selenium`

### 1.2 測試環境
- **本地測試環境**：執行 `python index.py`，訪問 `http://localhost:5000`
- **瀏覽器支援測試**：Chrome、Firefox、Safari、Edge 最新版本
- **裝置相容性**：桌面電腦、平板、手機

## 2. 單元測試

### 2.1 後端單元測試
使用 Pytest 測試框架執行後端功能測試：

```bash
pytest tests/test_backend.py -v
```

測試範圍：
- API 端點回應測試
- 資料格式驗證
- 錯誤處理邏輯
- 模型檔案處理功能

### 2.2 前端單元測試
使用 Jest 測試框架執行前端功能測試：

```bash
npm test
```

測試範圍：
- 3D 渲染函式
- 使用者互動事件處理
- 資料載入與處理
- UI 組件功能

## 3. 整合測試

### 3.1 API 整合測試
測試後端 API 與資料儲存的整合：

```bash
pytest tests/test_api_integration.py -v
```

測試項目：
- 手機資料 CRUD 操作
- 模型檔案存取整合
- API 回應格式與內容

### 3.2 前後端整合測試
測試前後端資料流與功能整合：

```bash
pytest tests/test_frontend_backend_integration.py -v
```

測試項目：
- 前端 API 呼叫
- 資料顯示整合
- 模型載入與渲染流程

## 4. 功能測試

### 4.1 3D 展示功能測試

#### 4.1.1 模型載入測試
- 檢查所有手機模型是否正確載入
- 測試不同格式模型的相容性
- 驗證模型比例與位置自動調整功能

#### 4.1.2 互動控制測試
- 測試手動旋轉功能（左/右方向）
- 測試縮放控制功能（放大/縮小）
- 測試自動旋轉模式
- 測試滑鼠拖曳操作
- 測試觸控螢幕操作

#### 4.1.3 展示效果測試
- 驗證材質渲染品質
- 測試光源效果
- 檢查動畫流暢度

### 4.2 使用者介面測試

#### 4.2.1 導航選單測試
- 測試手機型號切換
- 測試當前選擇指示功能
- 測試響應式設計在不同螢幕尺寸的表現

#### 4.2.2 控制面板測試
- 測試所有控制按鈕功能
- 測試按鈕狀態指示
- 測試按鈕互動回饋

#### 4.2.3 資訊展示測試
- 測試所有手機資訊的正確顯示
- 測試資訊分類與切換功能
- 測試長內容的溢出處理

## 5. 效能測試

### 5.1 載入效能測試
- 測試模型載入時間（目標 < 3 秒）
- 測試初始頁面載入時間
- 測試資源快取效果

### 5.2 互動效能測試
- 測試互動操作回應時間（目標 < 100ms）
- 測試同時多種操作的效能
- 測試在低效能裝置上的表現

### 5.3 網路效能測試
- 測試不同網路條件下的載入效能
- 測試斷線重連處理
- 測試資源快取策略效果

## 6. 相容性測試

### 6.1 瀏覽器相容性測試
使用 Selenium 進行跨瀏覽器測試：

```bash
pytest tests/test_browser_compatibility.py -v
```

測試瀏覽器：
- Chrome (最新版)
- Firefox (最新版)
- Safari (最新版)
- Edge (最新版)

### 6.2 裝置相容性測試
測試不同裝置類型與螢幕尺寸：
- 桌面電腦 (1920x1080 及以上)
- 平板電腦 (768x1024)
- 手機 (375x667)

## 7. 安全性測試

### 7.1 檔案安全測試
- 測試路徑遍歷防護
- 測試檔案類型驗證
- 測試存取權限控制

### 7.2 API 安全測試
- 測試輸入資料驗證
- 測試錯誤訊息過濾
- 測試資源使用限制

## 8. 自動化測試流程

### 8.1 CI/CD 整合測試
在 GitHub Actions 中設定自動測試流程：

```yaml
# .github/workflows/test.yml 範例
name: Test Suite
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          pip install pytest selenium
      - name: Run tests
        run: |
          pytest tests/
```

### 8.2 測試報告
- 產生測試覆蓋率報告
- 設定測試結果通知機制
- 整合測試報告到 CI/CD 流程

## 9. 測試案例範例

### 9.1 後端 API 測試範例
```python
def test_get_all_phones():
    response = client.get('/api/phones')
    assert response.status_code == 200
    data = response.get_json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert 'id' in data[0]
    assert 'name' in data[0]
```

### 9.2 前端互動測試範例
```javascript
test('手機旋轉控制功能', () => {
  // 模擬場景設定
  const scene = new THREE.Scene();
  const phone = loadPhoneModel('test_phone.glb');
  
  // 初始旋轉值
  const initialRotation = phone.rotation.y;
  
  // 模擬旋轉按鈕點擊
  rotateRight(phone);
  
  // 驗證旋轉是否正確
  expect(phone.rotation.y).toBeGreaterThan(initialRotation);
});
```

## 10. 測試優先順序

1. **最高優先級**
   - 核心 3D 展示功能
   - API 端點功能
   - 主要使用者互動功能

2. **中等優先級**
   - 相容性測試
   - 效能測試
   - 次要功能測試

3. **低優先級**
   - 極端情境測試
   - 視覺細節測試
   - 增強功能測試

## 11. 錯誤回報與修復流程

1. 在 GitHub Issues 中以「[BUG]」標籤建立新議題
2. 詳細描述問題、重現步驟與預期結果
3. 標記相關標籤與優先級
4. 指派負責人員
5. 開發修復解決方案
6. 提交針對特定問題的測試案例
7. 確認修復並關閉議題