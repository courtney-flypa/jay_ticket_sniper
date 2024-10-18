#!/bin/bash

# 創建虛擬環境
python3 -m venv ticket_bot_env

# 激活虛擬環境
source ticket_bot_env/bin/activate

# 安裝所需套件
pip install -r requirements.txt

# 創建 requirements.txt
pip freeze > requirements.txt

# 創建 ticket_bot.py
touch ticket_bot.py

echo "虛擬環境已設置完成，ticket_bot.py 文件已創建。"
echo "使用 'source ticket_bot_env/bin/activate' 來激活虛擬環境。"