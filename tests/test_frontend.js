/**
 * 前端單元測試
 * 使用 Jest 測試框架
 */

// 模擬 DOM 環境
document.body.innerHTML = `
<div id="app">
  <div class="phone-list"></div>
  <div class="viewer-container">
    <canvas id="phone-viewer"></canvas>
    <div class="control-panel">
      <button class="rotate-left">向左旋轉</button>
      <button class="rotate-right">向右旋轉</button>
      <button class="zoom-in">放大</button>
      <button class="zoom-out">縮小</button>
      <button class="auto-rotate">自動旋轉</button>
    </div>
  </div>
  <div class="phone-info"></div>
</div>
`;

// 模擬 Three.js
jest.mock('three', () => {
  return {
    Scene: jest.fn().mockImplementation(() => ({
      add: jest.fn()
    })),
    PerspectiveCamera: jest.fn().mockImplementation(() => ({
      position: { set: jest.fn() }
    })),
    WebGLRenderer: jest.fn().mockImplementation(() => ({
      setSize: jest.fn(),
      domElement: document.createElement('canvas'),
      setClearColor: jest.fn(),
      render: jest.fn()
    })),
    AmbientLight: jest.fn(),
    DirectionalLight: jest.fn().mockImplementation(() => ({
      position: { set: jest.fn() }
    })),
    Vector3: jest.fn(),
    Box3: jest.fn().mockImplementation(() => ({
      setFromObject: jest.fn(),
      getCenter: jest.fn().mockReturnValue({ x: 0, y: 0, z: 0 }),
      getSize: jest.fn().mockReturnValue({ x: 1, y: 1, z: 1 })
    })),
    Mesh: jest.fn()
  };
});

// 模擬 GLTFLoader
jest.mock('three/examples/jsm/loaders/GLTFLoader', () => {
  return {
    GLTFLoader: jest.fn().mockImplementation(() => ({
      load: jest.fn((url, onLoad) => {
        const mockGltf = {
          scene: {
            traverse: jest.fn(),
            position: { set: jest.fn() },
            rotation: { y: 0 }
          }
        };
        onLoad(mockGltf);
      })
    }))
  };
});

// 導入測試對象
const { 
  initViewer, 
  loadPhoneModel, 
  rotateLeft, 
  rotateRight, 
  zoomIn, 
  zoomOut, 
  toggleAutoRotate,
  updatePhoneInfo
} = require('../static/js/viewer');

describe('3D 手機檢視器功能', () => {
  let scene, camera, renderer, phoneModel;
  
  beforeEach(() => {
    // 設定初始測試環境
    const viewerResult = initViewer();
    scene = viewerResult.scene;
    camera = viewerResult.camera;
    renderer = viewerResult.renderer;
    phoneModel = null;
  });

  test('初始化檢視器', () => {
    expect(scene).toBeDefined();
    expect(camera).toBeDefined();
    expect(renderer).toBeDefined();
  });

  test('載入手機模型', async () => {
    const model = await loadPhoneModel('models/test_phone.glb', scene);
    expect(model).toBeDefined();
    expect(model.position).toBeDefined();
    phoneModel = model;
  });

  test('向左旋轉功能', () => {
    // 模擬手機模型
    phoneModel = { rotation: { y: 0 } };
    const initialRotation = phoneModel.rotation.y;
    
    rotateLeft(phoneModel);
    
    expect(phoneModel.rotation.y).toBeGreaterThan(initialRotation);
  });

  test('向右旋轉功能', () => {
    // 模擬手機模型
    phoneModel = { rotation: { y: 0 } };
    const initialRotation = phoneModel.rotation.y;
    
    rotateRight(phoneModel);
    
    expect(phoneModel.rotation.y).toBeLessThan(initialRotation);
  });

  test('放大功能', () => {
    // 模擬相機
    camera = { position: { z: 5 } };
    const initialZoom = camera.position.z;
    
    zoomIn(camera);
    
    expect(camera.position.z).toBeLessThan(initialZoom);
  });

  test('縮小功能', () => {
    // 模擬相機
    camera = { position: { z: 5 } };
    const initialZoom = camera.position.z;
    
    zoomOut(camera);
    
    expect(camera.position.z).toBeGreaterThan(initialZoom);
  });

  test('自動旋轉功能', () => {
    // 模擬自動旋轉狀態
    const autoRotate = { enabled: false };
    
    toggleAutoRotate(autoRotate);
    
    expect(autoRotate.enabled).toBe(true);
    
    toggleAutoRotate(autoRotate);
    
    expect(autoRotate.enabled).toBe(false);
  });

  test('更新手機資訊', () => {
    const infoContainer = document.querySelector('.phone-info');
    const phoneData = {
      name: '測試手機',
      model: 'TEST-123',
      dimensions: '150 x 70 x 8 mm',
      weight: '180 g',
      display: '6.5 inches, AMOLED',
      cpu: 'Snapdragon 888',
      memory: '8GB RAM, 128GB Storage'
    };
    
    updatePhoneInfo(phoneData);
    
    expect(infoContainer.innerHTML).toContain('測試手機');
    expect(infoContainer.innerHTML).toContain('TEST-123');
    expect(infoContainer.innerHTML).toContain('150 x 70 x 8 mm');
    expect(infoContainer.innerHTML).toContain('6.5 inches, AMOLED');
  });
});

describe('UI 互動測試', () => {
  test('按鈕點擊事件', () => {
    // 模擬點擊旋轉按鈕
    const rotateLeftBtn = document.querySelector('.rotate-left');
    const rotateRightBtn = document.querySelector('.rotate-right');
    const zoomInBtn = document.querySelector('.zoom-in');
    const zoomOutBtn = document.querySelector('.zoom-out');
    const autoRotateBtn = document.querySelector('.auto-rotate');
    
    // 模擬點擊事件處理函式
    const mockRotateLeft = jest.fn();
    const mockRotateRight = jest.fn();
    const mockZoomIn = jest.fn();
    const mockZoomOut = jest.fn();
    const mockAutoRotate = jest.fn();
    
    // 添加事件監聽器
    rotateLeftBtn.addEventListener('click', mockRotateLeft);
    rotateRightBtn.addEventListener('click', mockRotateRight);
    zoomInBtn.addEventListener('click', mockZoomIn);
    zoomOutBtn.addEventListener('click', mockZoomOut);
    autoRotateBtn.addEventListener('click', mockAutoRotate);
    
    // 模擬點擊事件
    rotateLeftBtn.click();
    rotateRightBtn.click();
    zoomInBtn.click();
    zoomOutBtn.click();
    autoRotateBtn.click();
    
    // 檢查事件是否觸發
    expect(mockRotateLeft).toHaveBeenCalledTimes(1);
    expect(mockRotateRight).toHaveBeenCalledTimes(1);
    expect(mockZoomIn).toHaveBeenCalledTimes(1);
    expect(mockZoomOut).toHaveBeenCalledTimes(1);
    expect(mockAutoRotate).toHaveBeenCalledTimes(1);
  });
});

describe('資料載入測試', () => {
  test('載入手機列表', async () => {
    // 模擬 fetch API
    global.fetch = jest.fn().mockImplementation(() =>
      Promise.resolve({
        ok: true,
        json: () => Promise.resolve([
          {
            id: 1,
            name: '測試手機 A',
            model: 'TestPhoneA',
            model_path: '/models/phone_a.glb'
          },
          {
            id: 2,
            name: '測試手機 B',
            model: 'TestPhoneB',
            model_path: '/models/phone_b.glb'
          }
        ])
      })
    );
    
    // 導入手機列表載入函式
    const { loadPhoneList } = require('../static/js/app');
    
    // 載入手機列表
    await loadPhoneList();
    
    // 檢查 DOM 是否更新
    const phoneList = document.querySelector('.phone-list');
    expect(phoneList.children.length).toBe(2);
    expect(phoneList.innerHTML).toContain('測試手機 A');
    expect(phoneList.innerHTML).toContain('測試手機 B');
  });
});
