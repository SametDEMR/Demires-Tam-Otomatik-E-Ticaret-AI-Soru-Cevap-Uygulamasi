import json
import pyodbc
import requests
import random
import time


def main():
    # Veritabanı bağlantısı
    def get_db_connection():
        connection_string = (
            "Driver={SQL Server};"
            "Server=SAMETDEMIR\\SQLEXPRESS;"
            "Database=Demires;"
            "Trusted_Connection=yes;"
            "TrustServerCertificate=yes;"
        )
        return pyodbc.connect(connection_string)

    # AI'dan cevap alma fonksiyonu
    def get_ai_response(prompt):
        try:
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "llama3",
                    "prompt": prompt,
                    "stream": False,
                    "options": {"temperature": 0.3, "max_tokens": 100}
                },
                timeout=30
            )
            return response.json()["response"].strip().strip('"')
        except Exception as e:
            print(f"AI servis hatası: {str(e)}")
            return "Sistem şu anda cevap veremiyor, lütfen daha sonra tekrar deneyiniz."

    # Çağrı işleme fonksiyonu
    def process_call(cagri):
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            cagri_id, konu, mesaj = cagri.CagriID, cagri.Konu, cagri.Mesaj

            # Soruyu ayıkla
            soru = mesaj.split("(", 1)[1].rsplit(")", 1)[0] if "(" in mesaj and ")" in mesaj else mesaj

            # Prompt oluştur
            prompt = (f"Muhasebe sorusuna en fazla 2 cümlelik türkçe, kısa ve teknik cevap ver: \"{soru}\""
                      if konu == "MUHASEBE"
                      else f"Teknik destek sorusuna en fazla 2 cümlelik türkçe, kısa ve net cevap ver: \"{soru}\"")

            # AI'dan cevap al
            print(f"\nÇağrı ID: {cagri_id} için AI cevabı isteniyor...")
            ai_cevap = get_ai_response(prompt)
            print(f"AI Cevabı: {ai_cevap}")

            # İlgili departmandan rastgele kullanıcı seç
            cursor.execute("SELECT KullaniciID FROM Kullanici WHERE RolDepartmanID = ?",
                           (2 if konu == "MUHASEBE" else 3))
            kullanici_listesi = cursor.fetchall()

            if not kullanici_listesi:
                print("Uygun kullanıcı bulunamadı!")
                return False

            random_user_id = random.choice(kullanici_listesi).KullaniciID
            print(f"Atanan Kullanıcı ID: {random_user_id}")

            # Cevabı formatla ve güncelle
            mesaj_icerik = f"{random_user_id}({ai_cevap})"

            cursor.execute("""
                UPDATE Çağrılar 
                SET Mesaj = CAST(Mesaj AS NVARCHAR(MAX)) + ?,
                Durum = 0,
                CEvaplayanID = ?
                WHERE CagriID = ?
            """, (mesaj_icerik, random_user_id, cagri_id))

            conn.commit()
            print(f"Çağrı ID: {cagri_id} başarıyla güncellendi!")
            return True

        except Exception as e:
            conn.rollback()
            print(f"Hata oluştu: {str(e)}")
            return False
        finally:
            conn.close()

    # Ana işlem döngüsü
    print("Demires Çağrı Yönetim Sistemi başlatıldı...")
    print("Bekleyen çağrılar kontrol ediliyor...")

    while True:
        conn = get_db_connection()
        cursor = conn.cursor()

        try:
            # Bekleyen çağrıları çek
            cursor.execute("SELECT CagriID, Konu, Mesaj FROM Çağrılar WHERE Durum = 1")
            bekleyen_cagrilar = cursor.fetchall()

            if not bekleyen_cagrilar:
                print("Bekleyen çağrı bulunamadı. 30 saniye sonra tekrar kontrol edilecek...")
                time.sleep(30)
                continue

            # Rastgele bir çağrı seç
            cagri = random.choice(bekleyen_cagrilar)
            print(f"\nİşlenen Çağrı ID: {cagri.CagriID}, Konu: {cagri.Konu}")
            print(f"Orijinal Mesaj: {cagri.Mesaj}")

            # Çağrıyı işle
            success = process_call(cagri)

            if success:
                print("Çağrı başarıyla işlendi!")
            else:
                print("Çağrı işlenirken hata oluştu!")

            # 10 saniye bekle
            print("\n10 saniye sonra yeni çağrılar kontrol edilecek...")
            time.sleep(10)

        except Exception as e:
            print(f"Beklenmeyen hata: {str(e)}")
        finally:
            conn.close()


if __name__ == '__main__':
    main()