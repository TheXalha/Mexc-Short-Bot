# trade.py
import requests
import os
from dotenv import load_dotenv

def open_short_position(token, take_profit_percentage):
    """Yeni token ile 1x kaldıraç ile short pozisyon açar"""
    
    # .env dosyasından API anahtarlarını ve miktarı al
    load_dotenv()
    api_key = os.getenv('MEXC_API_KEY')
    secret_key = os.getenv('MEXC_SECRET_KEY')
    trade_quantity = os.getenv('TRADE_QUANTITY', 1)  # Varsayılan miktar 1
    
    # API isteği için gerekli başlıklar
    headers = {
        'X-MEXC-APIKEY': api_key,
        'X-MEXC-SECRETKEY': secret_key
    }
    
    # İşlem açma isteği
    url = "https://api.mexc.com/api/v3/order"
    params = {
        'symbol': token,
        'side': 'SELL',  # Short pozisyon açmak için
        'type': 'MARKET',  # Market order
        'quantity': trade_quantity,  # Miktar
        'takeProfit': str(take_profit_percentage)  # Take profit yüzdesi
    }
    
    response = requests.post(url, headers=headers, params=params)
    
    if response.status_code == 200:
        print(f"✅ Short pozisyon açıldı: {token}")
    else:
        print(f"❌ Hata: {response.json()}")
