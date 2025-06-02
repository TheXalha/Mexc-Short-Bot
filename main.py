from checks import validate_environment
from scanner import wait_for_new_mexc_futures
from trade import open_short_position  # Yeni fonksiyonu içe aktar
import os
import time

def main():
    """Ana fonksiyon"""
    print("🚀 MEXC Yeni Token Tarayıcısı")
    print("=" * 40)
    
    # Tüm kontrolleri yap
    if not validate_environment():
        print("🛑 Program sonlandırılıyor...")
        return
    
    print("🔍 Yeni token taraması başlatılıyor...")
    print("=" * 40)
    
    while True:  # Sonsuz döngü
        try:
            # Yeni token bekle
            new_token = wait_for_new_mexc_futures()
            
            if new_token:
                print("=" * 40)
                print(f"✅ BAŞARILI! Yeni token bulundu: {new_token}")
                
                # .env dosyasından kar yüzdesini al
                take_profit_percentage = os.getenv('TAKE_PROFIT_PERCENTAGE', 25)  # Varsayılan %25
                
                # Short pozisyon aç
                open_short_position(new_token, take_profit_percentage)
                
                print("🎯 Trade işlemlerine başlayabilirsiniz!")
            else:
                print("❌ Token bulunamadı veya hata oluştu")
            
            time.sleep(10)  # 10 saniye bekle (isteğe bağlı)
            
        except Exception as e:
            print(f"❌ Beklenmeyen hata: {e}")
            time.sleep(30)  # Hata durumunda 30 saniye bekle

if __name__ == "__main__":
    main()
