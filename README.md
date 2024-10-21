# 自動購票機器人

這是一個使用 Selenium 自動化購票的 Python 專案。

## 功能

- 自動連接到已開啟的 Chrome 瀏覽器
- 自動選擇票種和數量
- 自動填寫驗證碼（使用 ddddocr 進行識別）
- 自動完成購票流程

## 安裝

1. 克隆此儲存庫：
```bash
git clone https://github.com/your-username/ticket-bot.git
cd ticket-bot
```

2. 設置虛擬環境：
```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

## 使用方法

1. 確保您已經開啟 Chrome 瀏覽器，並使用遠程調試模式。在命令行中運行以下命令：
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9527
```

2. 在 Chrome 中打開目標購票網站。

3. 運行腳本：
```bash
python main.py
```

4. 腳本將自動連接到開啟的 Chrome 瀏覽器並開始執行購票流程。

## 注意事項

- 請確保您的 Chrome 瀏覽器版本與 ChromeDriver 版本相匹配。
- 使用此腳本時請遵守相關網站的使用條款和規定。
- 驗證碼識別可能不是 100% 準確，可能需要手動干預。

## 貢獻

歡迎提交 Pull Requests 來改進此專案。對於重大更改，請先開啟一個 issue 討論您想要更改的內容。

## 授權

[MIT License](LICENSE)