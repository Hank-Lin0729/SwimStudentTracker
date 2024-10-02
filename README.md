# 游泳池管理系統

這是一個基於 Flask 的網頁應用程式，用於管理游泳池。它允許管理員匯入學生和教師名單，記錄學生和教師的進出紀錄，匯出紀錄，以及執行其他管理任務。

## 功能

- **登入系統**：有兩種用戶類型：管理員和一般用戶。
  - 管理員可以從設定頁面管理學生、教師和進出紀錄。
  - 學生和教師可以登錄進出游泳池的時間。
  
- **學生管理**：
  - 可透過 Excel 檔案匯入學生名單。
  - 可新增、編輯和刪除學生資料。
  
- **教師管理**：
  - 可透過 Excel 檔案匯入教師名單。
  - 可新增、編輯和刪除教師資料。
  
- **進出紀錄**：
  - 記錄學生和教師的進出時間。
  - 可匯出進出紀錄為 Excel 檔案。
  - 可刪除所有進出紀錄。

## 安裝說明

### 需求條件

- Python 3
- Flask
- MySQL
- Pandas
- XlsxWriter
- MySQL Connector

### 安裝步驟

1. clone專案：
    ```bash
    git clone https://github.com/your-username/swimming-pool-management.git
    cd swimming-pool-management
    ```

2. 安裝所需的 Python 套件：
    ```bash
    pip install -r requirements.txt
    ```

3. 設定 MySQL 資料庫：
    - 在 MySQL 中建立一個新的資料庫，並使用 `main.sql` 檔案來初始化資料庫：
      ```sql
      mysql -u root -p < main.sql
      ```

4. 更新 `app.py` 中的資料庫配置：
    - 將 `db_config` 中的資料庫名稱、用戶名、密碼和主機設置為您的 MySQL 資訊。

5. 啟動 Flask 伺服器：
    ```bash
    python app.py
    ```

6. 在瀏覽器中打開 [http://localhost:5000](http://localhost:5000) 開始使用系統。

## 檔案結構

- `app.py`: Flask 應用程式的主程式。
- `templates/`: 網頁模板檔案。
- `static/`: CSS 和 JavaScript 檔案。
- `uploads/`: 上傳的檔案會儲存在此目錄。
- `main.sql`: 初始化 MySQL 資料庫的 SQL 腳本。

## 如何使用

1. 登入系統：管理員和一般用戶都需要先登入才能使用系統。
2. 管理員可以匯入學生和教師名單，查看和管理進出紀錄，並匯出紀錄。
3. 學生和教師可以登錄自己的進出時間。

## 注意事項

- 確保正確配置 MySQL 資料庫，並按照上述步驟操作。
- 上傳的學生和教師名單必須為 `.xls` 或 `.xlsx` 格式。

## 開發者

- 此專案由林柏翰開發，歡迎進行改進與討論。
