#!/bin/bash

# 創建虛擬環境
python3 -m venv ticket_bot_env

# 激活虛擬環境
source ticket_bot_env/bin/activate

# 安裝所需套件
pip install -r requirements.txt

echo "使用 'source ticket_bot_env/bin/activate' 來激活虛擬環境。"