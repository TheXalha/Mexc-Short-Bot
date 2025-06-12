# position.py
import os
import time
import hmac
import hashlib
import requests
from dotenv import load_dotenv

load_dotenv()  # .env dosyasını yükle

API_KEY = os.getenv("MEXC_API_KEY")
SECRET_KEY = os.getenv("MEXC_SECRET_KEY")
TRADE_QUANTITY = float(os.getenv("TRADE_QUANTITY", 1))
LEVERAGE = int(os.getenv("LEVERAGE", 10))
TAKE_PROFIT_PERCENTAGE = float(os.getenv("TAKE_PROFIT_PERCENTAGE", 25))

BASE_URL = "https://contract.mexc.com"

def _sign(params):
    query = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
    return hmac.new(SECRET_KEY.encode(), query.encode(), hashlib.sha256).hexdigest()

def _headers():
    return {"Content-Type": "application/x-www-form-urlencoded"}

def open_short_position(symbol):
    now = int(time.time() * 1000)

    # 1. Leverage ayarla
    leverage_url = f"{BASE_URL}/api/v1/private/position/change-leverage"
    leverage_data = {
        "api_key": API_KEY,
        "symbol": symbol,
        "positionOpenType": 1,  # cross
        "leverage": LEVERAGE,
        "timestamp": now
    }
    leverage_data["sign"] = _sign(leverage_data)
    r1 = requests.post(leverage_url, data=leverage_data, headers=_headers())
    if r1.status_code != 200:
        raise Exception(f"Kaldıraç ayarlanamadı: {r1.text}")

    # 2. Market short işlemi
    order_url = f"{BASE_URL}/api/v1/private/order/submit"
    order_data = {
        "api_key": API_KEY,
        "symbol": symbol,
        "price": "",  # market
        "vol": TRADE_QUANTITY,
        "leverage": LEVERAGE,
        "side": 2,  # short
        "type": 1,  # market
        "open_type": 1,
        "position_id": 0,
        "external_oid": f"bot-{int(time.time())}",
        "timestamp": now
    }
    order_data["sign"] = _sign(order_data)
    r2 = requests.post(order_url, data=order_data, headers=_headers())
    if r2.status_code != 200:
        raise Exception(f"İşlem açılamadı: {r2.text}")

    # 3. TP hesapla ve ekle
    entry_price = get_last_price(symbol)
    tp_price = round(entry_price * (1 - TAKE_PROFIT_PERCENTAGE / 100), 6)

    plan_url = f"{BASE_URL}/api/v1/private/planorder/submit"
    tp_data = {
        "api_key": API_KEY,
        "symbol": symbol,
        "trigger_price": tp_price,
        "price": tp_price,
        "vol": TRADE_QUANTITY,
        "side": 1,  # take profit = long
        "order_type": 1,
        "leverage": LEVERAGE,
        "position_id": 0,
        "timestamp": int(time.time() * 1000)
    }
    tp_data["sign"] = _sign(tp_data)
    r3 = requests.post(plan_url, data=tp_data, headers=_headers())
    if r3.status_code != 200:
        raise Exception(f"TP emri başarısız: {r3.text}")

    return {
        "status": "Short açıldı",
        "symbol": symbol,
        "entry_price": entry_price,
        "take_profit": tp_price
    }

def get_last_price(symbol):
    ticker_url = f"{BASE_URL}/api/v1/contract/ticker?symbol={symbol}"
    res = requests.get(ticker_url)
    if res.status_code == 200:
        return float(res.json()['data']['lastPrice'])
    else:
        raise Exception(f"Fiyat alınamadı: {res.text}")
