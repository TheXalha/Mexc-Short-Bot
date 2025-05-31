import os
from pathlib import Path
from dotenv import load_dotenv

# Export edilecek fonksiyonları belirt
__all__ = ['validate_environment']

def check_env_file():
    """Env dosyasının varlığını kontrol eder"""
    env_path = Path('.env')
    if env_path.exists():
        print("✅ .env dosyası bulundu!")
        load_dotenv(env_path)
        return True
    else:
        print("❌ .env dosyası bulunamadı!")
        print("💡 Lütfen .env dosyası oluşturun ve MEXC_API_KEY ekleyin")
        return False

def check_api_keys():
    """API key'lerin varlığını kontrol eder"""
    api_key = os.getenv('MEXC_API_KEY')
    
    if not api_key:
        print("❌ MEXC_API_KEY bulunamadı!")
        print("💡 .env dosyasına MEXC_API_KEY=your_api_key_here ekleyin")
        return False
    
    print("✅ MEXC_API_KEY bulundu!")
    return True

def check_scanner_file():
    """Scanner dosyasının varlığını kontrol eder"""
    scanner_path = Path('scanner.py')
    if scanner_path.exists():
        print("✅ scanner.py dosyası bulundu!")
        return True
    else:
        print("❌ scanner.py dosyası bulunamadı!")
        print("💡 scanner.py dosyasının aynı klasörde olduğundan emin olun")
        return False

def validate_environment():
    """Tüm gereksinimleri kontrol eder ve True/False döner"""
    print("🔍 Sistem kontrolleri yapılıyor...")
    print("=" * 40)
    
    # Tüm kontrolleri yap
    env_ok = check_env_file()
    api_ok = check_api_keys() if env_ok else False
    scanner_ok = check_scanner_file()
    
    print("=" * 40)
    
    # Sonuç
    if env_ok and api_ok and scanner_ok:
        print("✅ Tüm kontroller başarılı!")
        return True
    else:
        print("❌ Bazı gereksinimler eksik!")
        return False
