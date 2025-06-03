import requests
import json
import time
import hmac
import hashlib
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

API_KEY = os.getenv("API_KEY")
API_SECRET = os.getenv("API_SECRET")
AMOUNT = float(os.getenv("AMOUNT"))
LEVERAGE = int(os.getenv("LEVERAGE"))
TP_PERCENT = float(os.getenv("TAKE_PROFIT_PERCENT"))

PAIR_FILE = "mexc_futures_pairs.json"
API_URL = "https://contract.mexc.com"
LOG_FILE = "log.txt"

HEADERS = {
    "Content-Type": "application/json",
    "ApiKey": API_KEY
}

def log_to_file(message):
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{datetime.now()}] {message}\n")

def sign_request(params):
    sorted_params = sorted(params.items())
    encoded_params = "&".join([f"{k}={v}" for k, v in sorted_params])
    signature = hmac.new(API_SECRET.encode(), encoded_params.encode(), hashlib.sha256).hexdigest()
    return signature

def fetch_pairs():
    url = f"{API_URL}/api/v1/contract/detail"
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()
    return [item["symbol"] for item in data["data"]]

def load_old_pairs():
    if not os.path.exists(PAIR_FILE):
        return []
    with open(PAIR_FILE, "r") as f:
        return json.load(f)

def save_pairs(pairs):
    with open(PAIR_FILE, "w") as f:
        json.dump(pairs, f, indent=4)

def get_market_price(symbol):
    url = f"{API_URL}/api/v1/contract/market/depth?symbol={symbol}&depth=1"
    response = requests.get(url)
    data = response.json()
    return float(data["data"]["asks"][0][0])

def open_short_order(symbol, price):
    tp_price = round(price * (1 - TP_PERCENT / 100), 4)
    timestamp = int(time.time() * 1000)

    params = {
        "symbol": symbol,
        "price": price,
        "vol": AMOUNT,
        "leverage": LEVERAGE,
        "side": 2,  # short
        "type": 1,  # limit order
        "open_type": 1,
        "position_id": 0,
        "external_oid": f"bot_{timestamp}",
        "stop_loss_price": 0,
        "take_profit_price": tp_price,
        "position_mode": 1,
        "reduce_only": False,
        "timestamp": timestamp
    }

    signature = sign_request(params)
    params["sign"] = signature

    url = f"{API_URL}/api/v1/private/order/submit"
    response = requests.post(url, headers=HEADERS, json=params)
    result = response.json()

    if result.get("success"):
        msg = f"✅ SHORT açıldı: {symbol} @ {price}, TP: {tp_price}"
        print(msg)
        log_to_file(msg)
    else:
        msg = f"❌ İşlem hatası ({symbol}): {result}"
        print(msg)
        log_to_file(msg)

def bot_loop():
    print("Bot başlatıldı...")
    log_to_file("🔄 Bot başlatıldı.")
    
    while True:
        try:
            current_pairs = fetch_pairs()
            old_pairs = load_old_pairs()
            new_pairs = list(set(current_pairs) - set(old_pairs))

            if new_pairs:
                for symbol in new_pairs:
                    try:
                        log_to_file(f"🆕 Yeni pair bulundu: {symbol}")
                        price = get_market_price(symbol)
                        open_short_order(symbol, price)
                        old_pairs.append(symbol)
                        save_pairs(old_pairs)
                    except Exception as e:
                        error_msg = f"HATA - {symbol}: {e}"
                        print(error_msg)
                        log_to_file(error_msg)
            else:
                print(f"[{datetime.now()}] Yeni pair yok.")

            time.sleep(60)

        except Exception as e:
            error_msg = f"GENEL HATA: {e}"
            print(error_msg)
            log_to_file(error_msg)
            time.sleep(60)

if __name__ == "__main__":
    bot_loop()
