import requests
from bs4 import BeautifulSoup
import time

# --- AYARLARINIZI BURAYA YAZIN ---
TELEGRAM_TOKEN = "8300011544:AAHFan1w4HjWbDKqoLcTHM3CfHY4HukgeEk"
CHAT_ID = "@BURSASUKESINTIBOTU"
HEDEF_ILCE = "NİLÜFER"       # Küçük/Büyük harf duyarlılığı için büyük harf yazın
HEDEF_MAHALLE = "Görükle"    # Aramak istediğiniz mahalle adı

# BUSKİ Günlük Kesintiler Sayfası URL'si
URL = "https://www.buski.gov.tr/gunluk-su-kesintileri"

def telegram_mesaj_gonder(mesaj):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mesaj,
        "parse_mode": "Markdown"
    }
    requests.post(telegram_url, json=payload)

def kesintileri_kontrol_et():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = requests.get(URL, headers=headers, timeout=10)
        if response.status_code != 200:
            return
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # BUSKİ sitesindeki kesinti tablosunu veya listesini buluyoruz
        # Not: Site yapısı değiştikçe "table" veya "div" sınıfları güncellenebilir.
        kesinti_elementleri = soup.find_all(["tr", "div", "p"]) 
        
        for element in kesinti_elementleri:
            metin = element.get_text().upper()
            
            # Sizin bölgenizle ilgili bir eşleşme var mı kontrolü
            if HEDEF_ILCE in metin and HEDEF_MAHALLE in metin:
                kesinti_detayi = element.get_text().strip()
                
                # Telefonunuza gelecek mesaj formatı
                mesaj = f"🚨 *BUSKİ PLANLI SU KESİNTİSİ UYARISI!*\n\n📍 Bölge: {HEDEF_ILCE} / {HEDEF_MAHALLE}\n📝 Detay: {kesinti_detayi}"
                
                print("Eşleşme bulundu, telefona gönderiliyor...")
                telegram_mesaj_gonder(mesaj)
                return # Aynı gün mükerrer mesaj gelmesin diye durduruyoruz
                
    except Exception as e:
        print(f"Hata oluştu: {e}")

# Sistem günde 2 kez (Örn: Sabah 09:00 ve Akşam 18:00 gibi) kontrol edecek şekilde döngüye alınabilir
if __name__ == "__main__":
    print("BUSKİ Takip Sistemi Başlatıldı...")
    kesintileri_kontrol_et()
