import requests
from bs4 import BeautifulSoup
import urllib3

# SSL Uyarılarını kesin olarak gizle
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TELEGRAM_TOKEN = "8300011544:AAHFan1w4HjWbDKqoLcTHM3CfHY4HukgeEk"
CHAT_ID = "@BURSASUKESINTIBOTU"
TAKIP_LISTESI = ["nilüfer", "görükle"]
URL = "https://www.buski.gov.tr/gunluk-su-kesintileri"

def telegram_mesaj_gonder(mesaj):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mesaj,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(telegram_url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

def turkce_kucult(metin):
    return metin.replace('I', 'ı').replace('İ', 'i').lower()

def kesintileri_kontrol_et():
    session = requests.Session()
    session.verify = False 
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = session.get(URL, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"BUSKİ sitesine erişilemedi. Durum kodu: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # --- BUSKİ'NİN GERÇEK TABLO YAPISI ---
        # Sayfadaki her bir kesinti kutusunu (satırını) buluyoruz
        kesinti_kutulari = soup.find_all("div", class_="kesinti-liste-item")
        
        if not kesinti_kutulari:
            print("Sayfada 'kesinti-liste-item' sınıfına ait bir veri bulunamadı. Yapı değişmiş olabilir.")
            return
            
        gonderilen_kesintiler = set()
        
        for kutu in kesinti_kutulari:
            # Kutunun içindeki tüm metinleri temiz bir şekilde birleştiriyoruz
            metin = kutu.get_text(separator=" | ").strip()
            # İç içe geçen çoklu boşlukları ve satır başlarını temizle
            metin = " ".join(metin.split())
            
            metin_kucuk = turkce_kucult(metin)
            
            for kelime in TAKIP_LISTESI:
                # Kelime bu kesinti kutusunun herhangi bir yerinde (başlık veya açıklama) geçiyor mu?
                if kelime in metin_kucuk:
                    if metin_kucuk not in gonderilen_kesintiler:
                        gonderilen_kesintiler.add(metin_kucuk)
                        
                        mesaj = f"🚨 *BUSKİ SU KESİNTİSİ UYARISI!*\n\n" \
                                f"🔍 *Eşleşen Kelime:* `{kelime.upper()}`\n\n" \
                                f"📝 *Kesinti Detayı:*\n{metin}"
                        
                        print(f"Eşleşme bulundu ({kelime}), Telegram'a gönderiliyor...")
                        telegram_mesaj_gonder(mesaj)
                        break # Bu kutu için işlemi bitir, sonraki kesinti kutusuna geç
                        
        if not gonderilen_kesintiler:
            print("Takip listenizdeki kelimelerle eşleşen bir kesinti bulunamadı.")
            
    except Exception as e:
        print(f"Script çalışırken bir hata oluştu: {e}")

if __name__ == "__main__":
    print("BUSKİ Çoklu Kelime Takip Sistemi Başlatıldı...")
    kesintileri_kontrol_et()
