# main.py
import json
import os
import time
from scan import get_all_futures_pairs
from position import open_short_position

PAIR_FILE = "pairs.json"
SCAN_INTERVAL_SECONDS = 60

def save_pairs_to_json(pairs):
    with open(PAIR_FILE, "w") as f:
        json.dump(pairs, f, indent=2)

def load_previous_pairs():
    if os.path.exists(PAIR_FILE):
        with open(PAIR_FILE, "r") as f:
            return json.load(f)
    return []

def delete_old_json():
    if os.path.exists(PAIR_FILE):
        os.remove(PAIR_FILE)

def main_loop():
    while True:
        print("\n[+] Pair taraması başlatılıyor...")
        
        # Pair'leri al
        current_pairs = get_all_futures_pairs()
        print(f"[=] {len(current_pairs)} pair bulundu.")

        # Önceki dosyayı oku
        previous_pairs = load_previous_pairs()
        
        # Yeni pair'leri bul
        new_pairs = [pair for pair in current_pairs if pair not in previous_pairs]
        
        if new_pairs:
            print(f"[!] Yeni {len(new_pairs)} pair bulundu. İşlem başlatılıyor...")
            for symbol in new_pairs:
                try:
                    result = open_short_position(symbol)
                    print(f"[✓] Short açıldı: {symbol} | Giriş: {result['entry_price']} | TP: {result['take_profit']}")
                except Exception as e:
                    print(f"[x] {symbol} için hata: {e}")
        else:
            print("[✓] Yeni pair yok. Beklemeye geçiliyor...")

        # JSON'u güncelle
        delete_old_json()
        save_pairs_to_json(current_pairs)

        print(f"[🕒] {SCAN_INTERVAL_SECONDS} saniye sonra tekrar tarama yapılacak...\n")
        time.sleep(SCAN_INTERVAL_SECONDS)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("Program manuel olarak durduruldu.")
