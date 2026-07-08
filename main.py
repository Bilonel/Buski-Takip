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
        
        # BUSKİ'nin yeni sitesindeki gerçek kesinti kartları (Kutuları)
        kesinti_kartlari = soup.find_all("div", class_="kesinti-item")
        
        # Eğer site tamamen yeni sınıfa geçmişse üsttekini, eski uyumluluk için alttakini arar
        if not kesinti_kartlari:
            # Sınıf ismi içerebilecek genel kart yapılarını yedek olarak tarıyoruz
            kesinti_kartlari = soup.select('[class*="kesinti-item"], [class*="kesinti-liste"], .kesinti-box')
            
        # Hala bulamadıysa, HTML'deki en genel kapsayıcıları yedek plan olarak tarar (Sistem asla çökmez)
        if not kesinti_kartlari:
            kesinti_kartlari = soup.find_all("div", class_="card")
            
        gonderilen_kesintiler = set()
        
        for kart in kesinti_kartlari:
            # Kartın içindeki tüm metni (başlık, ilçe, detay) tek parça halinde alıyoruz
            metin = kart.get_text(separator=" | ").strip()
            # Gereksiz iç içe boşlukları temizle
            metin = " ".join(metin.split())
            
            metin_kucuk = turkce_kucult(metin)
            
            if len(metin) < 15:
                continue
                
            for kelime in TAKIP_LISTESI:
                # Aradığımız kelime bu kesinti kartının herhangi bir yerinde var mı?
                if kelime in metin_kucuk:
                    if metin_kucuk not in gonderilen_kesintiler:
                        gonderilen_kesintiler.add(metin_kucuk)
                        
                        mesaj = f"🚨 *BUSKİ SU KESİNTİSİ UYARISI!*\n\n" \
                                f"🔍 *Eşleşen Kelime:* `{kelime.upper()}`\n\n" \
                                f"📝 *Kesinti Detayı:*\n{metin}"
                        
                        print(f"Eşleşme bulundu ({kelime}), Telegram'a gönderiliyor...")
                        telegram_mesaj_gonder(mesaj)
                        break 
                        
        if not gonderilen_kesintiler:
            print("Takip listenizdeki kelimelerle eşleşen aktif bir kesinti bulunamadı.")
            
    except Exception as e:
        print(f"Script çalışırken bir hata oluştu: {e}")

if __name__ == "__main__":
    print("BUSKİ Çoklu Kelime Takip Sistemi Başlatıldı...")
    kesintileri_kontrol_et()
