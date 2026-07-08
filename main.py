import requests
from bs4 import BeautifulSoup
import urllib3
import os
import hashlib

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

TELEGRAM_TOKEN = "8300011544:AAHFan1w4HjWbDKqoLcTHM3CfHY4HukgeEk"
CHAT_ID = "@BURSASUKESINTIBOTU"
TAKIP_LISTESI = ["nilüfer", "görükle"]
URL = "https://www.buski.gov.tr/gunluk-su-kesintileri"
HAFIZA_DOSYASI = "kesinti_hafizasi.txt"

def telegram_mesaj_gonder(mesaj):
    telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": CHAT_ID, "text": mesaj, "parse_mode": "Markdown"}
    try:
        requests.post(telegram_url, json=payload, timeout=10)
    except Exception as e:
        print(f"Telegram mesajı gönderilemedi: {e}")

def turkce_kucult(metin):
    return metin.replace('I', 'ı').replace('İ', 'i').lower()

# Eski gönderilen kesintileri dosyadan okuma fonksiyonu
def hafizayi_yukle():
    if not os.path.exists(HAFIZA_DOSYASI):
        return set()
    with open(HAFIZA_DOSYASI, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

# Yeni gönderilen kesintileri dosyaya yazma fonksiyonu
def hafizaya_kaydet(eski_hafiza, yeni_kesintiler):
    # Hem eskileri hem yenileri birleştirip dosyaya yazıyoruz
    tum_hafiza = eski_hafiza.union(yeni_kesintiler)
    with open(HAFIZA_DOSYASI, "w", encoding="utf-8") as f:
        for kesinti_id in tum_hafiza:
            f.write(f"{kesinti_id}\n")

def kesintileri_kontrol_et():
    session = requests.Session()
    session.verify = False 
    headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36..."}
    
    try:
        response = session.get(URL, headers=headers, timeout=20)
        if response.status_code != 200:
            print(f"BUSKİ sitesine erişilemedi: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, "html.parser")
        ham_satirlar = soup.get_text(separator="\n").split("\n")
        
        # Günler arası kalıcı hafızayı yükle
        gecmis_gonderilenler = hafizayi_yukle()
        bu_turda_gonderilenler = set()
        
        for ham_satir in ham_satirlar:
            satir = " ".join(ham_satir.split()).strip()
            if len(satir) < 20:
                continue
                
            satir_kucuk = turkce_kucult(satir)
            
            for kelime in TAKIP_LISTESI:
                if kelime in satir_kucuk:
                    # Her kesinti metni için benzersiz bir şifreli kimlik (MD5) oluşturuyoruz
                    kesinti_id = hashlib.md5(satir_kucuk.encode('utf-8')).hexdigest()
                    
                    # Eğer bu kesinti DAHA ÖNCEKİ GÜNLERDE gönderildiyse PAS GEÇ
                    if kesinti_id in gecmis_gonderilenler:
                        continue
                        
                    # Aynı turda mükerrer göndermeyi de engelle
                    if kesinti_id not in bu_turda_gonderilenler:
                        bu_turda_gonderilenler.add(kesinti_id)
                        
                        mesaj = f"🚨 *BUSKİ SU KESİNTİSİ UYARISI!*\n\n" \
                                f"🔍 *Eşleşen Kelime:* `{kelime.upper()}`\n\n" \
                                f"📝 *Kesinti Detayı:*\n{satir}"
                        
                        print(f"Yeni kesinti bulundu ({kelime}), Telegram'a gönderiliyor...")
                        telegram_mesaj_gonder(mesaj)
                        break 
                        
        # Yeni gönderilenleri kalıcı hafıza dosyasına işle
        if bu_turda_gonderilenler:
            hafizaya_kaydet(gecmis_gonderilenler, bu_turda_gonderilenler)
            print(f"{len(bu_turda_gonderilenler)} yeni kesinti hafızaya kaydedildi.")
        else:
            print("Yeni bir kesinti yok, hafıza güncellenmedi.")
            
    except Exception as e:
        print(f"Script çalışırken bir hata oluştu: {e}")

if __name__ == "__main__":
    kesintileri_kontrol_et()
