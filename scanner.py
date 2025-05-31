import requests
import time
import os
import logging
from datetime import datetime
from dotenv import load_dotenv

# Export edilecek fonksiyonları belirt
__all__ = ['wait_for_new_mexc_futures']

# Logging konfigürasyonu
def setup_logging():
    """Log dosyasını ayarla"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('mexc_new_tokens.log', encoding='utf-8'),
            logging.StreamHandler()  # Console'a da yazdır
        ]
    )
    return logging.getLogger(__name__)

def wait_for_new_mexc_futures():
    """Yeni futures token listelenene kadar bekler ve ilk yeni tokeni döndürür"""
    
    # Logger'ı başlat
    logger = setup_logging()
    
    # .env dosyasından API key'i al
    load_dotenv()
    api_key = os.getenv('MEXC_API_KEY')
    
    headers = {}
    if api_key:
        headers['X-MEXC-APIKEY'] = api_key
    
    logger.info("MEXC yeni token tarayıcısı başlatıldı")
    
    # Başlangıç çiftlerini al
    try:
        url = "https://api.mexc.com/api/v3/exchangeInfo"
        response = requests.get(url, headers=headers)
        initial_pairs = set()
        
        for symbol in response.json()['symbols']:
            if symbol['symbol'].endswith('USDT') and symbol['status'] == 'TRADING':
                initial_pairs.add(symbol['symbol'])
        
        logger.info(f"Başlangıç: {len(initial_pairs)} futures çifti bulundu")
        
    except Exception as e:
        logger.error(f"Başlangıç hatası: {e}")
        return None
    
    # Yeni token için sürekli kontrol
    while True:
        try:
            response = requests.get(url, headers=headers)
            current_pairs = set()
            
            for symbol in response.json()['symbols']:
                if symbol['symbol'].endswith('USDT') and symbol['status'] == 'TRADING':
                    current_pairs.add(symbol['symbol'])
            
            # Yeni çift var mı kontrol et
            new_pairs = current_pairs - initial_pairs
            
            if new_pairs:
                new_token = list(new_pairs)[0]
                
                # Log'a yaz
                logger.info(f"🚀 YENİ TOKEN BULUNDU: {new_token}")
                logger.info(f"Token: {new_token} - Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                print(f"🚀 Yeni futures token bulundu: {new_token}")
                return new_token
            
            # Her 10 kontrol'da bir durum log'u
            if not hasattr(wait_for_new_mexc_futures, 'check_count'):
                wait_for_new_mexc_futures.check_count = 0
            
            wait_for_new_mexc_futures.check_count += 1
            
            if wait_for_new_mexc_futures.check_count % 10 == 0:
                logger.info(f"Tarama devam ediyor... ({wait_for_new_mexc_futures.check_count} kontrol yapıldı)")
            
            time.sleep(10)  # 10 saniye bekle
            
        except Exception as e:
            logger.error(f"Kontrol hatası: {e}")
            time.sleep(30)
