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
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, height/537.36) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        response = session.get(URL, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"BUSKİ sitesine erişilemedi. Durum kodu: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, "html.parser")
        
        # Gönderdiğiniz HTML'deki kesin var olan yapı: Tüm <tr> satırlarını çekiyoruz
        satirlar = soup.find_all("tr")
        
        if not satirlar:
            print("Sayfada hiçbir kesinti satırı bulunamadı.")
            return
            
        gonderilen_kesintiler = set()
        
        for satir in satirlar:
            # Tablonun sütun başlıklarını (İlçe, Tarih yazan satırı) atla
            if satir.find("th"):
                continue
                
            # Satırdaki metni sütunlar karışmasın diye boşluk bırakarak tek bir metne çeviriyoruz
            metin = satir.get_text(separator=" ").strip()
            # Satırın içindeki gereksiz boşluk ve alt satır karakterlerini temizle
            metin = " ".join(metin.split())
            
            metin_kucuk = turkce_kucult(metin)
            
            if len(metin) < 10:
                continue
                
            for kelime in TAKIP_LISTESI:
                # Kelime bu bütünsel satırın herhangi bir yerinde geçiyor mu?
                if kelime in metin_kucuk:
                    # MÜKERRER KONTROLÜ: Aynı satır metnini bir daha gönderme
                    if metin_kucuk not in gonderilen_kesintiler:
                        gonderilen_kesintiler.add(metin_kucuk)
                        
                        mesaj = f"🚨 *BUSKİ SU KESİNTİSİ UYARISI!*\n\n" \
                                f"🔍 *Eşleşen Kelime:* `{kelime.upper()}`\n\n" \
                                f"📝 *Kesinti Detayı:*\n{metin}"
                        
                        print(f"Eşleşme bulundu ({kelime}), Telegram'a gönderiliyor...")
                        telegram_mesaj_gonder(mesaj)
                        break # Bu satırı gönderdik, diğer anahtar kelimelere bakmadan sonraki tr satırına geç
                        
        if not gonderilen_kesintiler:
            print("Takip listenizdeki kelimelerle eşleşen bir kesinti bulunamadı.")
            
    except Exception as e:
        print(f"Script çalışırken bir hata oluştu: {e}")

if __name__ == "__main__":
    print("BUSKİ Çoklu Kelime Takip Sistemi Başlatıldı...")
    kesintileri_kontrol_et()
