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

def get_mexc_futures_pairs(logger, headers):
    """MEXC'teki tüm futures çiftlerini çeker."""
    url = "https://api.mexc.com/api/v3/exchangeInfo"
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status() # HTTP hatalarını yakala
        
        current_pairs = set()
        for symbol_info in response.json()['symbols']:
            # Futures tokenleri için USDT çiftlerini ve aktif işlemde olanları al
            if symbol_info['symbol'].endswith('USDT') and symbol_info['status'] == 'TRADING':
                current_pairs.add(symbol_info['symbol'])
        return current_pairs
    except requests.exceptions.RequestException as e:
        logger.error(f"API isteği hatası: {e}")
        return None
    except KeyError:
        logger.error("API yanıtında 'symbols' anahtarı bulunamadı veya yanıt beklenenden farklı.")
        return None
    except Exception as e:
        logger.error(f"Piyasa çiftlerini çekerken beklenmeyen hata: {e}")
        return None

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
    initial_pairs = None
    while initial_pairs is None:
        logger.info("Başlangıç futures çiftleri listesi çekiliyor...")
        initial_pairs = get_mexc_futures_pairs(logger, headers)
        if initial_pairs is None:
            logger.warning("Başlangıç çiftleri çekilemedi, 30 saniye sonra tekrar denenecek.")
            time.sleep(30) # Hata durumunda bekle
    
    logger.info(f"Başlangıç: {len(initial_pairs)} futures çifti bulundu.")
    
    # Yeni token için sürekli kontrol
    while True:
        try:
            current_pairs = get_mexc_futures_pairs(logger, headers)
            if current_pairs is None:
                logger.warning("Güncel çiftler çekilemedi, bir sonraki döngüde tekrar denenecek.")
                time.sleep(10) # Hata durumunda beklemeden önce 10 saniye bekle
                continue

            # Yeni çift var mı kontrol et
            new_pairs = current_pairs - initial_pairs
            
            if new_pairs:
                new_token = list(new_pairs)[0]
                
                # Log'a yaz
                logger.info(f"🚀 YENİ TOKEN BULUNDU: {new_token}")
                logger.info(f"Token: {new_token} - Tarih: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                
                print(f"🚀 Yeni futures token bulundu: {new_token}")
                
                # Yeni token bulunduğunda initial_pairs'ı güncelle
                initial_pairs = current_pairs 
                
                return new_token
            
            # Her 10 kontrol'da bir durum log'u
            if not hasattr(wait_for_new_mexc_futures, 'check_count'):
                wait_for_new_mexc_futures.check_count = 0
            
            wait_for_new_mexc_futures.check_count += 1
            
            if wait_for_new_mexc_futures.check_count % 10 == 0:
                logger.info(f"Tarama devam ediyor... ({wait_for_new_mexc_futures.check_count} kontrol yapıldı)")
            
            time.sleep(10)  # 10 saniye bekle
            
        except Exception as e:
            logger.error(f"Kontrol döngüsünde beklenmeyen hata: {e}")
            time.sleep(30) # Hata durumunda 30 saniye bekle