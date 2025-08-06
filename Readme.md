
# Demires Çağrı Yönetim Sistemi Dokümantasyonu

## Genel Bakış
Bu sistem, soru oluşturma, sınıflandırma ve yanıtlama için yapay zeka entegrasyonuna sahip bir çağrı yönetim uygulamasıdır. Web arayüzü için ASP.NET Core MVC bileşenlerinden ve arka uç işleme için Python servislerinden oluşur.

## Sistem Bileşenleri

### 1. Kimlik Doğrulama Sistemi
**Dosyalar:**
- `GirisEkraniController.cs`
- `GirisEkrani.cshtml`
- `Kullanici.cs`

**İşlevsellik:**
- Kullanıcılar için oturum açma işlevi sağlar
- Kimlik bilgilerini veritabanına göre doğrular
- Başarılı oturum açma işleminde oturum değişkenlerini ayarlar:
- KullaniciID (Kullanıcı Kimliği)
- RolDepartmanID (Rol/Departman Kimliği)
- RolDepartmanAdi (Rol/Departman Adı)
- Kullanıcıları rollerine göre yönlendirir:
- Admin (UserID=1) → AdminCagrilar
- Diğer kullanıcılar → Cagrilar

### 2. Çağrı Yönetimi Web Arayüzü
**Dosyalar:**
- `CagrilarController.cs`
- `AdminCagrilar.cshtml`
- `Cagrilar.cs`

**İşlevsellik:**
- Çağrıları üç kategoride görüntüler:
1. **Kategorilendirilmemiş**: DepartmentID=1 olan çağrılar (henüz sınıflandırılmamış)
2. **Cevaplanmamış**: Status=1 olan çağrılar (yanıt bekleniyor)
3. **Cevaplanmış**: Status=0 olan çağrılar (tamamlanmış)
- Çağrı verilerini her 3 saniyede bir yenilemek için AJAX kullanır
- Mesaj içeriği için özel biçimlendirme (Soru-Cevap biçimi için parantezleri ayrıştırma)

### 3. Veritabanı Modelleri
**Dosyalar:**
- `Cagrilar.cs` (Çağrı modeli)
- `Kullanici.cs` (Kullanıcı modeli)
- `RolDepartman.cs` (Rol/Departman modeli)
- `ErrorViewModel.cs`

**Yapı:**
- **Çağrılar (Çağrılar)** tablosu:
- CagriID, Konu (Subject), MusteriID (Customer), CevaplayanID (Cevaplayan)
- DepartmanID (Departman), Durum (Durum), Mesaj (Mesaj)
- **Kullanici (Kullanıcılar)** tablosu:
- KullaniciID, KullaniciAdi (Kullanıcı Adı), Sifre (Şifre), RolDepartmanID

### 4. Yapay Zeka Destekli Hizmetler

#### a) Soru Oluşturma Hizmeti (`SoruOlustur.py`)
- İki kategoride rastgele teknik sorular oluşturur:
- Muhasebe (MUHASEBE)
- Teknik Destek (TEKNİK DESTEK)
- Soru oluşturmak için Ollama'nın LLaMA3 modelini kullanır
- Özellikler:
- Sürekli çalışma (her 10 saniyede bir soru oluşturur)
- Manuel tetikleme için REST API uç noktası
- Soruları Departman 7'deki kullanıcılara rastgele atar
- Soruları veritabanında başlangıç DepartmentID=1 ile depolar

#### b) Soru Sınıflandırma Hizmeti (`SoruSınıflandır.py`)
- Sınıflandırır Kategorilendirilmemiş sorular (DepartmentID=1) şu şekildedir:
- Muhasebe (DepartmentID=2)
- Teknik Destek (DepartmentID=3)
- Sınıflandırma kararları için LLaMA3 kullanır
- Özellikler:
- Sürekli izleme (her 5 saniyede bir kontrol eder)
- Manuel sınıflandırma için REST API
- Hata işleme ve yeniden deneme mantığı

#### c) Soru Cevaplama Hizmeti (`SoruCevapla.py`)
- Bekleyen soruları cevaplar (Durum=1)
- Özellikler:
- Özlü cevaplar oluşturmak için LLaMA3 kullanır
- Cevapları departman üyelerine rastgele atar
- Cevapları Soru-Cevap formatında biçimlendirir (orijinal mesaja ekler)
- Çağrı durumunu cevaplandı olarak günceller (Durum=0)
- Bekleyen çağrı olmadığında 30 saniyelik aralıklarla çalışır

### 5. Hata İşleme
**Dosyalar:**
- `Error.cshtml`
- `ErrorViewModel.cs`

**İşlevsellik:**
- Geliştirme modunda hata bilgilerini görüntüler
- Sorun giderme için istek kimliğini gösterir
- Güvenlik odaklı tasarım (üretimdeki ayrıntıları gizler)

## İş Akışı

1. **Soru Oluşturma**:
- Python hizmeti rastgele sorular oluşturur → veritabanında saklanır (DepartmanKimliği=1)

2. **Sınıflandırma**:
- Sınıflandırma hizmeti yeni kategorilendirilmemiş soruları algılar
- Yapay zeka uygun departmanı belirler
- DepartmanKimliğini günceller (2 veya 3)

3. **Web Arayüzü**:
- Yönetici üç kategoride çağrı görür
- Her 3 saniyede bir otomatik yenilenir

4. **Cevaplama**:
- Cevaplama hizmeti cevaplanmamış soruları seçer
- Yapay zeka yanıt oluşturur
- Rastgele departman üyesine atar
- Çağrı durumunu günceller

5. **Kullanıcı Etkileşimi**:
- Kullanıcılar web arayüzü üzerinden oturum açar
- Role göre uygun görünüme yönlendirilir
- Gerçek zamanlı çağrıyı görüntüler Veri

## Teknik Yığın
- **Arka Uç**: ASP.NET Core MVC, Entity Framework Core
- **Veritabanı**: SQL Server
- **Yapay Zeka Hizmetleri**: Python (Flask), LLaMA3 ile Ollama
- **Ön Uç**: Razor görünümleri, jQuery, Bootstrap