from flask import Flask, request, jsonify
import pyodbc
import requests
import time
from threading import Thread

app = Flask(__name__)

# Veritabanı bağlantı bilgileri
connection_string = (
    "Driver={SQL Server};"
    "Server=SAMETDEMIR\\SQLEXPRESS;"
    "Database=Demires;"
    "Trusted_Connection=yes;"
    "TrustServerCertificate=yes;"
)

def check_new_calls():
    """Yeni çağrıları kontrol eden fonksiyon"""
    print("Yeni çağrı kontrol servisi başlatıldı...")
    
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    # Son kontrol edilen ID'yi tutmak için
    last_checked_id = 0
    
    while True:
        try:
            # Yeni eklenen ve DepartmanID=1 olan çağrıları bul
            cursor.execute("""
                SELECT CagriID, Mesaj 
                FROM Çağrılar 
                WHERE DepartmanID = 1 AND CagriID > ?
                ORDER BY CagriID
            """, (last_checked_id,))
            
            rows = cursor.fetchall()
            
            for row in rows:
                cagri_id = row.CagriID
                soru = row.Mesaj
                
                print(f"Yeni çağrı işleniyor (ID: {cagri_id}): {soru}")
                
                try:
                    # Kategori belirleme isteği
                    response = requests.post(
                        "http://localhost:11434/api/generate",
                        json={
                            "model": "llama3",
                            "prompt": f"""{soru} sorusu aşağıdaki kategorilerden hangisine girer? 
- MUHASEBE: Fatura, çek/senet, bordro, vergi, beyanname, muhasebe yazılımları, muhasebe süreçleri, ödeme işlemleri, defter tutma, finansal raporlama, kdv tevkifatı, muhasebe standartları
- TEKNİK DESTEK: Bilgisayar, yazılım, donanım, ağ sorunları, sistem kurulumu, yazıcı arızaları, sunucu problemleri, teknik ekipman, veri tabanı, güvenlik duvarı, otomasyon sistemleri

Sadece kategori adını (MUHASEBE veya TEKNİK DESTEK) yazın, başka hiçbir açıklama eklemeyin.""",
                            "stream": False
                        },
                        timeout=30
                    )

                    kategori = response.json()["response"].strip().upper()
                    print(f"Belirlenen kategori: {kategori}")

                    # Kategoriye göre DepartmanID güncelleme
                    if kategori == "MUHASEBE":
                        new_dept_id = 2
                    elif kategori == "TEKNİK DESTEK":
                        new_dept_id = 3
                    else:
                        print(f"Geçersiz kategori: {kategori}. Varsayılan olarak Teknik Destek atandı.")
                        new_dept_id = 3

                    cursor.execute("""
                        UPDATE Çağrılar 
                        SET DepartmanID = ?
                        WHERE CagriID = ?
                    """, (new_dept_id, cagri_id))
                    
                    conn.commit()
                    print(f"Çağrı ID {cagri_id} güncellendi. Yeni DepartmanID: {new_dept_id}")
                    
                    # Son işlenen ID'yi güncelle
                    last_checked_id = max(last_checked_id, cagri_id)
                    
                except requests.exceptions.RequestException as e:
                    print(f"API isteği hatası (Çağrı ID: {cagri_id}): {str(e)}")
                    conn.rollback()
                except Exception as e:
                    print(f"Genel hata (Çağrı ID: {cagri_id}): {str(e)}")
                    conn.rollback()
            
            # 5 saniyede bir kontrol et
            time.sleep(5)
            
        except pyodbc.Error as e:
            print(f"Veritabanı hatası: {str(e)}")
            # Bağlantıyı yeniden kurmaya çalış
            try:
                conn.close()
            except:
                pass
            time.sleep(10)
            conn = pyodbc.connect(connection_string)
            cursor = conn.cursor()

@app.route('/process-call/<int:call_id>', methods=['POST'])
def process_single_call(call_id):
    """Tek bir çağrıyı manuel olarak işlemek için endpoint"""
    try:
        conn = pyodbc.connect(connection_string)
        cursor = conn.cursor()
        
        # Çağrıyı getir
        cursor.execute("""
            SELECT CagriID, Mesaj 
            FROM Çağrılar 
            WHERE CagriID = ?
        """, (call_id,))
        
        row = cursor.fetchone()
        
        if not row:
            return jsonify({"status": "error", "message": "Çağrı bulunamadı"}), 404
            
        soru = row.Mesaj
        
        # Kategori belirleme isteği
        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": f"""{soru} sorusu aşağıdaki kategorilerden hangisine girer? 
- MUHASEBE: Fatura, çek/senet, bordro, vergi, beyanname, muhasebe yazılımları, muhasebe süreçleri, ödeme işlemleri, defter tutma, finansal raporlama, kdv tevkifatı, muhasebe standartları
- TEKNİK DESTEK: Bilgisayar, yazılım, donanım, ağ sorunları, sistem kurulumu, yazıcı arızaları, sunucu problemleri, teknik ekipman, veri tabanı, güvenlik duvarı, otomasyon sistemleri

Sadece kategori adını (MUHASEBE veya TEKNİK DESTEK) yazın, başka hiçbir açıklama eklemeyin.""",
                "stream": False
            },
            timeout=30
        )

        kategori = response.json()["response"].strip().upper()
        print(f"Belirlenen kategori: {kategori}")

        # Kategoriye göre DepartmanID güncelleme
        if kategori == "MUHASEBE":
            new_dept_id = 2
        elif kategori == "TEKNİK DESTEK":
            new_dept_id = 3
        else:
            new_dept_id = 3  # Varsayılan

        cursor.execute("""
            UPDATE Çağrılar 
            SET DepartmanID = ?
            WHERE CagriID = ?
        """, (new_dept_id, call_id))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            "status": "success",
            "call_id": call_id,
            "new_department_id": new_dept_id,
            "category": kategori
        })
        
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    # Arka plan servisini başlat
    Thread(target=check_new_calls, daemon=True).start()
    
    # API'yi başlat
    app.run(host='0.0.0.0', port=5001, debug=True)