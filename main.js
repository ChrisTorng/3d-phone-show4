import * as THREE from 'three';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import { OrbitControls } from 'three/examples/jsm/controls/OrbitControls.js';

/**
 * PhoneViewer 類別：處理3D手機模型的顯示與互動
 */
class PhoneViewer {
    constructor() {
        // 場景相關變數初始化
        this.scene = null;
        this.camera = null;
        this.renderer = null;
        this.controls = null;
        this.phoneModels = [];
        this.currentModelIndex = 0;
        this.isAutoRotating = false;
        
        // DOM 元素參考
        this.container = document.getElementById('container');
        this.phoneNav = document.getElementById('phone-nav');
        this.infoContainer = document.getElementById('info-container');
        
        // 控制按鈕參考
        this.rotateLeftBtn = document.getElementById('rotate-left');
        this.rotateRightBtn = document.getElementById('rotate-right');
        this.zoomInBtn = document.getElementById('zoom-in');
        this.zoomOutBtn = document.getElementById('zoom-out');
        this.autoRotateBtn = document.getElementById('auto-rotate');
        
        // 載入狀態追蹤
        this.isLoading = false;
        this.loadingManager = new THREE.LoadingManager();
        this.setupLoadingManager();
        
        // 初始化
        this.init();
        this.setupEventListeners();
    }
    
    /**
     * 設定載入管理器
     */
    setupLoadingManager() {
        this.loadingManager.onStart = () => {
            this.showLoader('載入模型中...');
            this.isLoading = true;
        };
        
        this.loadingManager.onLoad = () => {
            this.hideLoader();
            this.isLoading = false;
        };
        
        this.loadingManager.onProgress = (url, loaded, total) => {
            const percent = (loaded / total * 100).toFixed(0);
            this.updateLoaderText(`載入中: ${percent}%`);
        };
        
        this.loadingManager.onError = (url) => {
            console.error('載入資源時發生錯誤:', url);
            this.updateLoaderText('載入失敗，請重新整理頁面');
        };
    }
    
    /**
     * 初始化 3D 場景、相機和渲染器
     */
    init() {
        // 建立場景
        this.scene = new THREE.Scene();
        this.scene.background = new THREE.Color(0xf0f0f0);
        
        // 設定相機
        this.camera = new THREE.PerspectiveCamera(
            75, 
            this.container.clientWidth / this.container.clientHeight, 
            0.1, 
            1000
        );
        this.camera.position.set(0, 0, 5);
        
        // 設定渲染器
        this.renderer = new THREE.WebGLRenderer({ 
            antialias: true,
            alpha: true
        });
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
        this.renderer.setPixelRatio(window.devicePixelRatio);
        this.renderer.shadowMap.enabled = true;
        this.renderer.shadowMap.type = THREE.PCFSoftShadowMap;
        this.container.appendChild(this.renderer.domElement);
        
        // 設定控制
        this.controls = new OrbitControls(this.camera, this.renderer.domElement);
        this.controls.enableDamping = true;
        this.controls.dampingFactor = 0.05;
        this.controls.rotateSpeed = 0.8;
        this.controls.minDistance = 2;
        this.controls.maxDistance = 8;
        
        // 新增燈光
        this.setupLights();
        
        // 建立載入中指示器
        this.createLoader();
        
        // 讀取手機資訊並載入對應的模型
        this.fetchPhoneData();
        
        // 視窗大小調整事件處理
        window.addEventListener('resize', this.onWindowResize.bind(this), false);
        
        // 開始動畫迴圈
        this.animate();
    }
    
    /**
     * 設定場景中的燈光
     */
    setupLights() {
        // 環境光源
        const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
        this.scene.add(ambientLight);
        
        // 主要方向光源
        const mainLight = new THREE.DirectionalLight(0xffffff, 1);
        mainLight.position.set(5, 5, 5);
        mainLight.castShadow = true;
        mainLight.shadow.mapSize.width = 1024;
        mainLight.shadow.mapSize.height = 1024;
        this.scene.add(mainLight);
        
        // 補光
        const fillLight = new THREE.DirectionalLight(0xffffff, 0.5);
        fillLight.position.set(-5, 0, -5);
        this.scene.add(fillLight);
        
        // 背光
        const backLight = new THREE.DirectionalLight(0xffffff, 0.4);
        backLight.position.set(0, -5, -5);
        this.scene.add(backLight);
    }
    
    /**
     * 建立載入指示器
     */
    createLoader() {
        this.loaderElement = document.createElement('div');
        this.loaderElement.className = 'loader';
        
        const spinner = document.createElement('div');
        spinner.className = 'loader-spinner';
        
        this.loaderTextElement = document.createElement('div');
        this.loaderTextElement.textContent = '準備載入...';
        
        this.loaderElement.appendChild(spinner);
        this.loaderElement.appendChild(this.loaderTextElement);
        this.loaderElement.style.display = 'none';
        
        this.container.appendChild(this.loaderElement);
    }
    
    /**
     * 顯示載入指示器
     * @param {string} text - 載入提示文字
     */
    showLoader(text) {
        this.loaderElement.style.display = 'flex';
        this.loaderTextElement.textContent = text;
    }
    
    /**
     * 更新載入指示器文字
     * @param {string} text - 新的載入提示文字
     */
    updateLoaderText(text) {
        this.loaderTextElement.textContent = text;
    }
    
    /**
     * 隱藏載入指示器
     */
    hideLoader() {
        this.loaderElement.style.display = 'none';
    }
    
    /**
     * 設定控制按鈕的事件監聽器
     */
    setupEventListeners() {
        // 旋轉和縮放控制
        if (this.rotateLeftBtn) {
            this.rotateLeftBtn.addEventListener('click', () => this.rotateModel('left'));
        }
        
        if (this.rotateRightBtn) {
            this.rotateRightBtn.addEventListener('click', () => this.rotateModel('right'));
        }
        
        if (this.zoomInBtn) {
            this.zoomInBtn.addEventListener('click', () => this.zoomCamera('in'));
        }
        
        if (this.zoomOutBtn) {
            this.zoomOutBtn.addEventListener('click', () => this.zoomCamera('out'));
        }
        
        if (this.autoRotateBtn) {
            this.autoRotateBtn.addEventListener('click', () => this.toggleAutoRotation());
        }
    }
    
    /**
     * 旋轉模型
     * @param {string} direction - 旋轉方向 ('left' 或 'right')
     */
    rotateModel(direction) {
        if (!this.phoneModels.length) return;
        
        const currentModel = this.phoneModels[this.currentModelIndex].scene;
        const rotateSpeed = 0.3;
        const targetRotation = direction === 'left' ? currentModel.rotation.y + rotateSpeed : currentModel.rotation.y - rotateSpeed;
        
        // 使用動畫過渡效果
        const animateRotation = () => {
            requestAnimationFrame(animateRotation);
            const rotationStep = 0.01;
            if (direction === 'left' && currentModel.rotation.y < targetRotation) {
                currentModel.rotation.y = Math.min(currentModel.rotation.y + rotationStep, targetRotation);
            } else if (direction === 'right' && currentModel.rotation.y > targetRotation) {
                currentModel.rotation.y = Math.max(currentModel.rotation.y - rotationStep, targetRotation);
            } else {
                return; // 結束動畫
            }
        };
        
        animateRotation();
    }
    
    /**
     * 縮放相機視角
     * @param {string} direction - 縮放方向 ('in' 或 'out')
     */
    zoomCamera(direction) {
        const zoomSpeed = 0.5;
        
        if (direction === 'in' && this.camera.position.z > this.controls.minDistance) {
            this.camera.position.z -= zoomSpeed;
        } else if (direction === 'out' && this.camera.position.z < this.controls.maxDistance) {
            this.camera.position.z += zoomSpeed;
        }
    }
    
    /**
     * 切換自動旋轉功能
     */
    toggleAutoRotation() {
        this.isAutoRotating = !this.isAutoRotating;
        
        // 更新按鈕狀態
        if (this.autoRotateBtn) {
            if (this.isAutoRotating) {
                this.autoRotateBtn.classList.add('active');
            } else {
                this.autoRotateBtn.classList.remove('active');
            }
        }
    }
    
    /**
     * 從 API 讀取手機資訊
     */
    async fetchPhoneData() {
        try {
            this.showLoader('讀取手機資料中...');
            
            const response = await fetch('/api/phones');
            if (!response.ok) {
                throw new Error(`HTTP 錯誤！狀態: ${response.status}`);
            }
            
            const data = await response.json();
            console.log('手機資料:', data);
            
            // 建立手機導航選單
            this.createPhoneNavigation(data);
            
            // 載入所有模型
            await this.loadModels(data);
            
            // 初始顯示第一個手機的資訊
            this.updatePhoneInfo(0);
            
        } catch (error) {
            console.error('讀取手機資料時發生錯誤:', error);
            this.updateLoaderText(`讀取資料失敗: ${error.message}`);
        }
    }
    
    /**
     * 建立手機導航選單
     * @param {Array} phonesData - 手機資訊陣列
     */
    createPhoneNavigation(phonesData) {
        if (!this.phoneNav || !Array.isArray(phonesData)) return;
        
        this.phoneNav.innerHTML = '';
        
        phonesData.forEach((phone, index) => {
            const navItem = document.createElement('div');
            navItem.className = 'nav-item';
            navItem.textContent = phone.name;
            
            if (index === 0) {
                navItem.classList.add('active');
            }
            
            navItem.addEventListener('click', () => this.switchModel(index));
            this.phoneNav.appendChild(navItem);
        });
    }
    
    /**
     * 載入 3D 模型
     * @param {Array} phonesData - 手機資訊陣列
     */
    async loadModels(phonesData) {
        if (!Array.isArray(phonesData) || phonesData.length === 0) {
            console.error('無效的手機資料格式或空白資料');
            return;
        }

        const loader = new GLTFLoader(this.loadingManager);
        
        // 清除現有的模型
        this.phoneModels.forEach(model => {
            if (model && model.scene) {
                this.scene.remove(model.scene);
            }
        });
        this.phoneModels = [];

        // 載入每個手機模型
        const loadPromises = phonesData.map((phone, index) => {
            return new Promise((resolve, reject) => {
                if (!phone.model_path) {
                    console.warn(`手機 ${phone.name} 缺少模型路徑`);
                    resolve(null);
                    return;
                }

                console.log(`載入模型: ${phone.model_path}`);
                
                loader.load(
                    phone.model_path,
                    (gltf) => {
                        console.log(`模型 ${phone.name} 已載入`);
                        
                        // 初始時隱藏除第一個外的所有模型
                        gltf.scene.visible = (index === 0);
                        
                        // 調整模型大小和位置
                        this.adjustModel(gltf.scene);
                        
                        // 儲存模型及資訊
                        this.phoneModels[index] = {
                            scene: gltf.scene,
                            info: phone
                        };
                        
                        this.scene.add(gltf.scene);
                        resolve(gltf);
                    },
                    (xhr) => {
                        const progress = (xhr.loaded / xhr.total * 100).toFixed(2);
                        console.log(`${phone.name} 載入進度: ${progress}%`);
                    },
                    (error) => {
                        console.error(`載入模型 ${phone.model_path} 時發生錯誤:`, error);
                        reject(error);
                    }
                );
            });
        });

        try {
            await Promise.all(loadPromises);
            this.hideLoader();
        } catch (error) {
            console.error('載入模型時發生錯誤:', error);
            this.updateLoaderText('載入模型失敗，請重新整理頁面');
        }
    }
    
    /**
     * 調整模型大小和位置
     * @param {Object} modelScene - Three.js 模型場景
     */
    adjustModel(modelScene) {
        // 計算模型包圍盒以調整大小
        const box = new THREE.Box3().setFromObject(modelScene);
        const size = box.getSize(new THREE.Vector3()).length();
        const scaleFactor = 6 / size;
        
        modelScene.scale.set(scaleFactor, scaleFactor, scaleFactor);
        
        // 置中模型
        const center = new THREE.Vector3();
        box.getCenter(center);
        modelScene.position.sub(center.multiplyScalar(scaleFactor));
    }
    
    /**
     * 切換顯示的模型
     * @param {number} index - 模型索引
     */
    switchModel(index) {
        if (index < 0 || index >= this.phoneModels.length) return;
        
        // 更新導航項目的狀態
        const navItems = this.phoneNav.querySelectorAll('.nav-item');
        navItems.forEach((item, i) => {
            if (i === index) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
        
        // 隱藏當前模型
        if (this.phoneModels[this.currentModelIndex] && this.phoneModels[this.currentModelIndex].scene) {
            this.phoneModels[this.currentModelIndex].scene.visible = false;
        }
        
        // 更新當前模型索引
        this.currentModelIndex = index;
        
        // 顯示新模型
        if (this.phoneModels[index] && this.phoneModels[index].scene) {
            this.phoneModels[index].scene.visible = true;
            this.phoneModels[index].scene.rotation.set(0, 0, 0);
        }
        
        // 更新資訊面板
        this.updatePhoneInfo(index);
        
        // 重置相機控制
        this.controls.reset();
    }
    
    /**
     * 更新手機資訊顯示
     * @param {number} index - 手機索引
     */
    updatePhoneInfo(index) {
        if (!this.infoContainer || index < 0 || index >= this.phoneModels.length || !this.phoneModels[index]) {
            return;
        }

        const phoneInfo = this.phoneModels[index].info;
        
        if (phoneInfo) {
            this.infoContainer.innerHTML = `
                <h2>${phoneInfo.name}</h2>
                
                <div class="info-section">
                    <h3>螢幕規格</h3>
                    <div class="spec-item">
                        <div class="spec-label">尺寸：</div>
                        <div class="spec-value">${phoneInfo.screen}</div>
                    </div>
                </div>
                
                <div class="info-section">
                    <h3>效能</h3>
                    <div class="spec-item">
                        <div class="spec-label">處理器：</div>
                        <div class="spec-value">${phoneInfo.processor}</div>
                    </div>
                </div>
                
                <div class="info-section">
                    <h3>攝影</h3>
                    <div class="spec-item">
                        <div class="spec-label">相機：</div>
                        <div class="spec-value">${phoneInfo.camera}</div>
                    </div>
                </div>
                
                <div class="info-section">
                    <h3>電池與儲存</h3>
                    <div class="spec-item">
                        <div class="spec-label">電池：</div>
                        <div class="spec-value">${phoneInfo.battery}</div>
                    </div>
                    <div class="spec-item">
                        <div class="spec-label">儲存空間：</div>
                        <div class="spec-value">${phoneInfo.storage}</div>
                    </div>
                </div>
            `;
        }
    }
    
    /**
     * 處理視窗大小變更
     */
    onWindowResize() {
        if (!this.container) return;
        
        this.camera.aspect = this.container.clientWidth / this.container.clientHeight;
        this.camera.updateProjectionMatrix();
        this.renderer.setSize(this.container.clientWidth, this.container.clientHeight);
    }
    
    /**
     * 動畫迴圈
     */
    animate() {
        requestAnimationFrame(this.animate.bind(this));
        
        // 自動旋轉功能
        if (this.isAutoRotating && this.phoneModels.length > 0) {
            const currentModel = this.phoneModels[this.currentModelIndex].scene;
            if (currentModel) {
                currentModel.rotation.y += 0.01;
            }
        }
        
        this.controls.update();
        this.renderer.render(this.scene, this.camera);
    }
}

// 當頁面載入完成後初始化應用程式
document.addEventListener('DOMContentLoaded', () => {
    const phoneViewer = new PhoneViewer();
});