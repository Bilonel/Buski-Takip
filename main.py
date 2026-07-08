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
        
        # Etiket bağımlılığını tamamen kaldırıyoruz.
        # Sayfadaki tüm yazıları satır satır parçalayarak listeye alıyoruz.
        ham_satirlar = soup.get_text(separator="\n").split("\n")
        
        gonderilen_kesintiler = set()
        
        for ham_satir in ham_satirlar:
            # Satır içi gereksiz boşlukları temizle
            satir = " ".join(ham_satir.split()).strip()
            
            # Çok kısa veya alakasız menü başlıklarını ele (Kesinti açıklamaları genelde uzundur)
            if len(satir) < 20:
                continue
                
            satir_kucuk = turkce_kucult(satir)
            
            for kelime in TAKIP_LISTESI:
                # Aradığımız kelime (örn: "nilüfer") bu metin bloğunun içinde geçiyor mu?
                if kelime in satir_kucuk:
                    # MÜKERRER KONTROLÜ: Aynı açıklamayı tekrar tekrar gönderme
                    if satir_kucuk not in gonderilen_kesintiler:
                        gonderilen_kesintiler.add(satir_kucuk)
                        
                        mesaj = f"🚨 *BUSKİ SU KESİNTİSİ UYARISI!*\n\n" \
                                f"🔍 *Eşleşen Kelime:* `{kelime.upper()}`\n\n" \
                                f"📝 *Kesinti Detayı:*\n{satir}"
                        
                        print(f"Eşleşme bulundu ({kelime}), Telegram'a gönderiliyor...")
                        telegram_mesaj_gonder(mesaj)
                        break # Bu satır için Telegram'a mesaj gitti, diğer kelimelere bakma
                        
        if not gonderilen_kesintiler:
            print("Takip listenizdeki kelimelerle eşleşen aktif bir kesinti bulunamadı.")
            
    except Exception as e:
        print(f"Script çalışırken bir hata oluştu: {e}")

if __name__ == "__main__":
    print("BUSKİ Çoklu Kelime Takip Sistemi Başlatıldı...")
    kesintileri_kontrol_et()
