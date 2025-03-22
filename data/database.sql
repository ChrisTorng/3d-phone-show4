-- 建立手機資料表
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
);

-- 刪除現有資料以避免重複
DELETE FROM phones;

-- 插入手機資料
INSERT INTO phones (id, name, screen, processor, camera, battery, storage, model_path, special_features)
VALUES 
    (
        'iphone_16_pro_max',
        'iPhone 16 Pro Max',
        '6.9 inch OLED',
        'Apple A18 Pro',
        '108MP 主鏡頭 + 48MP 超廣角 + 12MP 望遠',
        '4685 mAh',
        '256 GB / 512 GB / 1 TB',
        'models/iphone_16_pro_max.glb',
        '動態島、光學變焦、ProMotion 120Hz 螢幕'
    ),
    (
        'samsung_galaxy_s22_ultra',
        'Samsung Galaxy S22 Ultra',
        '6.8 inch Dynamic AMOLED 2X',
        'Qualcomm Snapdragon 8 Gen 1',
        '108MP 主鏡頭 + 12MP 超廣角 + 10MP 望遠 + 10MP 潛望式鏡頭',
        '5000 mAh',
        '128 GB / 256 GB / 512 GB / 1 TB',
        'models/samsung_galaxy_s22_ultra.glb',
        'S Pen 支援、100倍空間變焦、45W 快速充電'
    ),
    (
        'samsung_galaxy_z_flip_3',
        'Samsung Galaxy Z Flip 3',
        '6.7 inch 主螢幕 + 1.9 inch 外螢幕',
        'Qualcomm Snapdragon 888',
        '12MP 主鏡頭 + 12MP 超廣角',
        '3300 mAh',
        '128 GB / 256 GB',
        'models/Samsung_Galaxy_Z_Flip_3.glb',
        '折疊螢幕、IPX8 防水、無線充電'
    );
