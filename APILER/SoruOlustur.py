import ast
import pyodbc
import requests
import random
import json
from flask import Flask
import time

app = Flask(__name__)

# Veritabanı bağlantı bilgileri
connection_string = (
    "Driver={SQL Server};"
    "Server=SAMETDEMIR\\SQLEXPRESS;"
    "Database=Demires;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)


def generate_random_question():
    """Rastgele bir soru oluşturur ve veritabanına kaydeder"""
    try:
        kategori = random.choice(["MUHASEBE", "TEKNİK DESTEK"])

        if kategori == "MUHASEBE":
            prompt = """
Faturalandırma ve tahsilat işlemleri
Çek/senet takibi ve ödemeleri
Bordro hazırlama ve maaş hesaplamaları
Vergi beyannameleri (KDV, kurumlar vergisi vb.)
Muhasebe yazılımları (Logo, Eta, Mikro vb.)
Finansal raporlama ve defter kayıtları
KDV tevkifatı ve vergi iadeleri
Ödeme planları ve banka mutabakatı
Muhasebe standartları (TFRS vb.)
Stok takip ve envanter yönetimi (finansal boyutu)

FORMAT = ["Konu", "Soru"]

Bu konular ile ilgili net ve teknik cavabı olan 1 adet türkçe soru yazacaksın. Çıktı YALNIZCA ["Konu", "Soru"] formatında olacak. 
Kesinlikle çift tırnak kullanmalısın. BAŞKA HİÇBİR AÇIKLAMA EKLEME.
"""
        else:
            prompt = """
Bilgisayar/yazılım donanım arızaları
Ağ bağlantı sorunları (VPN, wifi, ethernet)
Sunucu yönetimi ve bulut sistemleri
Yazıcı/tarayıcı kurulum ve arızaları
Veri tabanı yönetimi (SQL, Oracle vb.)
Güvenlik duvarı ve siber güvenlik
ERP/CRM sistemlerinin teknik sorunları
Otomasyon sistemleri ve API entegrasyonları
E-posta sunucu ve iletişim araçları sorunları
Yedekleme ve veri kurtarma işlemleri

FORMAT = ["Konu", "Soru"]

Bu konular ile ilgili net ve teknik cavabı olan 1 adet türkçe soru yazacaksın. Çıktı YALNIZCA ["Konu", "Soru"] formatında olacak.
Kesinlikle çift tırnak kullanmalısın. BAŞKA HİÇBİR AÇIKLAMA EKLEME.
"""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )

        # Yanıtı işleme
        if response.status_code != 200:
            raise Exception(f"API hatası: {response.status_code} - {response.text}")

        response_json = response.json()

        # Farklı Ollama API yanıt formatları için kontrol
        if "response" in response_json:
            ai_response = response_json["response"].strip()
        elif isinstance(response_json, str):
            ai_response = response_json.strip()
        else:
            raise Exception("Geçersiz API yanıt formatı")

        # Format düzeltmeleri
        if "'" in ai_response and '"' not in ai_response:
            ai_response = ai_response.replace("'", '"')

        if not ai_response.startswith("[") or not ai_response.endswith("]"):
            ai_response = f"[{ai_response}]"

        try:
            # JSON parse
            AICevapDizi = json.loads(ai_response)
        except json.JSONDecodeError:
            # Eğer hala parse edilemiyorsa, manuel ayır
            clean_response = ai_response.strip("[]").replace('"', '').replace("'", "")
            parts = clean_response.split(",", 1)
            if len(parts) == 2:
                AICevapDizi = [parts[0].strip(), parts[1].strip()]
            else:
                raise Exception("Soru formatı geçersiz")

        # Veritabanı bağlantısı
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()

        # Rastgele kullanıcı seçimi
        cursor.execute("SELECT KullaniciID FROM Kullanici WHERE RolDepartmanID = 7")
        rows = cursor.fetchall()
        if not rows:
            raise Exception("Kullanıcı bulunamadı")

        random_row = random.choice(rows)
        random_user_id = random_row.KullaniciID

        # Mesaj oluşturma
        Mesaj = f"{random_user_id}({AICevapDizi[1]})"

        # Veritabanına kaydetme
        cursor.execute("""
            INSERT INTO Çağrılar (Konu, MusteriID, CevaplayanID, DepartmanID, Durum, Mesaj)
            VALUES (?, ?, ?, ?, ?, ?)
            """, AICevapDizi[0], random_user_id, 1, 1, 1, Mesaj)

        conn.commit()
        conn.close()

        print({"status": "success", "message": "Soru başarıyla oluşturuldu ve kaydedildi"})
        return {"status": "success", "message": "Soru başarıyla oluşturuldu ve kaydedildi"}

    except Exception as e:
        error_msg = f"Hata oluştu: {str(e)}"
        print({"status": "error", "message": error_msg})
        return {"status": "error", "message": error_msg}


@app.route('/generate-question', methods=['GET'])
def generate_question_endpoint():
    """API endpoint for manually generating a question"""
    return generate_random_question()


def continuous_question_generation():
    """Sürekli soru üretmek için while döngüsü"""
    while True:
        try:
            print("Yeni soru üretiliyor...")
            result = generate_random_question()
            print(result)
            time.sleep(10)  # 10 saniye bekle
        except Exception as e:
            print(f"Hata oluştu, yeniden denenecek: {str(e)}")
            time.sleep(30)  # Hata durumunda 30 saniye bekle


if __name__ == '__main__':
    # Arka planda sürekli soru üretme işlemini başlat
    import threading

    thread = threading.Thread(target=continuous_question_generation)
    thread.daemon = True
    thread.start()

    # Flask uygulamasını başlat
    app.run(host='0.0.0.0', port=5000, use_reloader=False)