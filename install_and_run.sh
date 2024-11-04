#!/bin/bash

# کلون کردن مخزن
git clone https://github.com/celenor/Eth-wallet-scan.git
cd Eth-wallet-scan 

# نصب وابستگی‌ها
echo "Installing dependencies..."
sudo apt update
sudo apt install -y python3 python3-pip
pip3 install -r requirements.txt

# اجرای اسکریپت
echo "Running the Ethereum balance checker..."
python3 ETH_WALLET_SCANNER.py
