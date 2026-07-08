import requests
from bs4 import BeautifulSoup
import urllib3

# SSL Uyarılarını kesin olarak gizle
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TELEGRAM_TOKEN = "8300011544:AAHFan1w4HjWbDKqoLcTHM3CfHY4HukgeEk"
CHAT_ID = "@BURSASUKESINTIBOTU"

# Takip listesini tamamen KÜÇÜK HARF ile yazın
TAKIP_LISTESI = ["nilüfer", "görükle"]
URL = "https://www.buski.gov.tr/gunluk-su-kesintileri"

def telegram_mesaj_gonder(mesaj):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHAT_ID,
        "text": mensaje, # Markdown uyumluluğu için
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
        
        # BUSKİ listesindeki ana tabloyu hedef alıyoruz
        tablo = soup.find("table")
        if not tablo:
            print("Sayfada kesinti tablosu bulunamadı.")
            return
            
        satirlar = tablo.find_all("tr")
        gonderilen_kesintiler = set()
        
        for satir in satirlar:
            # Tablonun sütun başlıklarını (İlçe, Tarih vs.) atla
            if satir.find("th"):
                continue
                
            # Satırın içindeki tüm metni sütunları ayırt edecek şekilde temizce çekiyoruz
            # (Örn: "Osmangazi | ... | Nilüfer ilçesi etkilenecektir")
            metin = satir.get_text(separator=" | ").strip()
            metin_kucuk = turkce_kucult(metin)
            
            if len(metin) < 10:
                continue
                
            for kelime in TAKIP_LISTESI:
                # Aradığımız kelime satırın BAŞINDA, ORTASINDA veya AÇIKLAMASINDA geçiyor mu?
                if kelime in metin_kucuk:
                    # Mükerrer (aynı satırı defalarca gönderme) kontrolü
                    if metin_kucuk not in gonderilen_kesintiler:
                        gonderilen_kesintiler.add(metin_kucuk)
                        
                        mesaj = f"🚨 *BUSKİ SU KESİNTİSİ UYARISI!*\n\n" \
                                f"🔍 *Eşleşen Kelime:* `{kelime.upper()}`\n\n" \
                                f"📝 *Kesinti Detayı:*\n{metin}"
                        
                        print(f"Eşleşme bulundu ({kelime}), Telegram'a gönderiliyor...")
                        telegram_mesaj_gonder(mesaj)
                        break # Bu satırda eşleşme bulundu, diğer anahtar kelimelere bakma (tek mesaj kuralı)
                        
        if not gonderilen_kesintiler:
            print("Takip listenizdeki kelimelerle eşleşen bir kesinti bulunamadı.")
            
    except Exception as e:
        print(f"Script çalışırken bir hata oluştu: {e}")

if __name__ == "__main__":
    print("BUSKİ Çoklu Kelime Takip Sistemi Başlatıldı...")
    kesintileri_kontrol_et()
