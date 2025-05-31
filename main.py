from checks import validate_environment
from scanner import wait_for_new_mexc_futures

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
    
    try:
        # Yeni token bekle
        new_token = wait_for_new_mexc_futures()
        
        if new_token:
            print("=" * 40)
            print(f"✅ BAŞARILI! Yeni token bulundu: {new_token}")
            print("🎯 Trade işlemlerine başlayabilirsiniz!")
        else:
            print("❌ Token bulunamadı veya hata oluştu")
            
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {e}")

if __name__ == "__main__":
    main()
