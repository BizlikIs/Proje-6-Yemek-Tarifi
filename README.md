# 🍽️ Menü · MASTERCLASS — Yemek Tarif Platformu

> PyQt5 tabanlı masaüstü yemek tarif yönetim uygulaması.
> Michelin restoranı estetiğinde koyu çikolata + amber altın temalı arayüz.
> **Üye** ve **Admin** olmak üzere iki rollü giriş sistemi.

---

## 📋 Proje Bilgileri

| Alan             | Değer                                              |
|------------------|----------------------------------------------------|
| **Proje**        | Proje 6 — Yemek Tarif Platformu                   |
| **Dil**          | Python 3                                           |
| **Çatı**         | PyQt5 (masaüstü GUI)                               |
| **Veritabanı**   | SQLite3                                            |
| **Dosya Sayısı** | 4 (`models.py`, `app.py`, `test.py`, `README.md`)  |
| **Test Sayısı**  | 62 (tümü başarılı)                                 |
| **Roller**       | `uye` (varsayılan) · `admin` (tam yetki)           |

---

## 🔐 Giriş Hesapları

Uygulama ilk açıldığında otomatik olarak aşağıdaki demo hesaplar oluşturulur:

| Rol        | E-posta            | Şifre       | Yetki                                   |
|------------|--------------------|-------------|-----------------------------------------|
| **Üye**    | `sef@menu.com`     | `1234`      | Tarif ekleme, favori, plan, alışveriş   |
| **Admin**  | `admin@menu.com`   | `admin1234` | Tarif/kullanıcı/yorum silme (tam yetki) |

> **Kendi hesabını oluşturmak için:** Giriş ekranındaki **ÜYE** sekmesinin altındaki "Hesabın yok mu? **ÜYE OL →**" linkine tıkla. Ad, soyad, e-posta ve şifreni gir, kaydol — otomatik olarak giriş yapılır.

> Hazır demo hesaplarla test etmek için **ÜYE** veya **ADMİN** sekmesinden "HAZIR DEMO İLE DOLDUR" butonunu kullan.

---

## 🏗️ Sınıf Yapısı (UML Diyagramı)

```
┌──────────────────────────────────────────────────────────────────┐
│                     Veritabani (yardımcı)                        │
│  ● db_path, conn, cursor                                         │
│  ○ baglanti_kur() → Connection                                   │
│  ○ tablolari_olustur()   ★ rol kolonu + migration                │
│  ○ kapat()                                                       │
└──────────────────────────────────────────────────────────────────┘
         │ kullanılır (bire-bir)
         ▼
┌────────────────────────────────────────────┐
│           Kullanici (ana sınıf 1)          │
│  ● kullanici_id, ad, soyad, email, rol     │
│  ○ ekle(ad, soyad, email, sifre, rol)      │  ★ rol='uye'|'admin'
│  ○ giris_yap(email, sifre) → dict|None     │
│  ○ getir(id), listele(), guncelle()        │
│  ○ sil(id, zorla=False)                    │  ★ zorla=admin kademeli
│  ○ tarif_degerlendir(kid, tid, puan,yorum) │
│  ○ degerlendirme_sil(degerlendirme_id)     │  ★ admin yorum silme
│  ○ degerlendirmelerim(kid)                 │
│  ○ _sifre_hashle(sifre) → SHA-256          │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│             Tarif (ana sınıf 2)            │
│  ● tarif_id, tarif_adi, kategori,          │
│    hazirlama_suresi, porsiyon, zorluk      │
│  ○ tarif_ekle(adi, kat, sure, kid, ...)    │
│  ○ tarif_guncelle(tid, **kwargs)           │
│  ○ getir(id), listele(), ara(), sil()      │
│  ○ ortalama_puan(tid) → float              │
│  ○ degerlendirmeler(tid) → list            │
│  ▸ KATEGORILER = [Çorba, Ana Yemek, ...]   │
│  ▸ ZORLUK_SEVIYELERI = [Kolay, Orta, Zor]  │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│           Malzeme (ana sınıf 3)            │
│  ● malzeme_adi, miktar, birim              │
│  ○ ekle(tid, adi, miktar, birim)           │
│  ○ getir(id), listele(tid)                 │
│  ○ guncelle(mid, **kwargs), sil(mid)       │
│  ○ topla(tid) → int                        │
└────────────────────────────────────────────┘

┌────────────────────────────────────────────┐
│      IstatistikYoneticisi (yardımcı)       │
│  ○ genel_istatistikler() → dict            │
│  ○ en_populer_tarifler(limit) → list       │
│  ○ kategori_ortalamalari() → list          │
└────────────────────────────────────────────┘
```

### İlişkiler

- `Kullanici` **1 ——→ N** `Tarif` (bir kullanıcı birçok tarif ekleyebilir)
- `Tarif` **1 ——→ N** `Malzeme` (bir tarifin birçok malzemesi olur)
- `Kullanici` **N ←——→ N** `Tarif` üzerinden `Degerlendirme` (çoktan çoğa, UPSERT mantığı)
- `Kullanici.rol = 'admin'` olan kullanıcılar tüm verileri silebilir (cascade)

---

## 📁 Dosya Yapısı

```
proje6/
├── models.py          # Veritabanı + 3 ana sınıf + rol + admin metodları
├── app.py             # PyQt5 arayüz + Üye/Admin giriş + silme panelleri
├── test.py            # 57 test senaryosu
├── README.md          # Bu dosya
└── tarif_platformu.db # (çalıştırınca otomatik oluşur, admin hesabı seed edilir)
```

---

## ✨ Özellikler

### Giriş Sistemi (Yeni)
- **İki sekmeli giriş**: ÜYE / ADMİN toggle butonları
- E-posta + şifre doğrulama (SHA-256 hash)
- **Üye kayıt formu**: ÜYE sekmesinin altında "ÜYE OL" linki → Ad / Soyad / E-posta / Şifre / Şifre Tekrar alanlı form
- Kayıt tamamlanınca otomatik giriş yapılır (yeni üye `rol='uye'` olarak oluşturulur)
- Demo hesap panelinde tek tıkla alan doldurma
- Admin girişinde sidebar'da şarap kırmızısı avatar + "◆ ADMIN · TAM YETKI" rozeti
- Admin hesabıyla üye sekmesinden de giriş yapılabilir (otomatik yetki yükseltme)
- Güvenlik: admin hesapları sadece seed ile oluşturulur; kayıt formundan admin yaratılamaz

### Admin Yetkileri (Yeni)
- **Tarif silme**: Her tarifin detay sayfasında "🗑 TARİFİ SİL" butonu (onay diyaloğu ile)
- **Yorum silme**: Her değerlendirme satırının sağında × butonu
- **Kullanıcı silme**: Kullanıcılar tablosunda "Sil" butonu (kendi hesabını silemez)
- Kullanıcı silindiğinde tüm tarifleri, malzemeleri, yorumları, favorileri, notları, haftalık planı ve alışveriş listesi birlikte temizlenir (cascade)
- Tüm admin işlemleri aktivite günlüğüne `[ADMIN]` etiketiyle kaydedilir

### Arayüz Sayfaları (9 adet)
1. **Gösterge Paneli (Dashboard)** — Özet kartlar, halka grafik (kategori dağılımı), çubuk grafik (zorluk dağılımı), popüler tarifler, aktivite günlüğü
2. **Tarifler** — Arama çubuğu, kategori filtre butonları, TarifKartı bileşenleri
3. **Tarif Detayı** — Hero kart, malzeme listesi, yapılış adımları, yıldız derecelendirme, yorum listesi (+ admin silme butonları)
4. **Yeni Tarif** — Form: ad/açıklama/yapılış/kategori/zorluk/süre/porsiyon + dinamik malzeme satırları
5. **Kullanıcılar** — Kayıtlı üyelerin tablo görünümü + rol sütunu (+ admin için silme butonu)
6. **İstatistikler** — Genel özet, kategori analiz tablosu, popüler tarifler
7. **Favorilerim** — Kullanıcının favori tarifleri
8. **Haftalık Plan** — 7 gün için tarif planlayıcı + mutfak zamanlayıcı
9. **Alışveriş Listesi** — Birleşik liste, aldın/almadın durumu, metin dışa aktarım

### Özel Widget'lar
- `SefAmblemi` — **Tamir edildi**: sap artık M rozetinin dışından başlar, bıçak ağzı simetrik yaprak biçimli, çatalın boynu ve 4 sivri dişi var
- `HalkaGrafik` — Animasyonlu donut chart (QPainter)
- `CubukGrafik` — Animasyonlu bar chart (QPainter)
- `YildizDerecelendirme` — 5 yıldızlı etkileşimli puan widget'ı
- `StatKart` — Gradient şeritli istatistik kartı
- `TarifKarti` — Hoverable tarif özet kartı
- `Toast` — 3 türde (başarı/hata/bilgi) anlık bildirim
- `CanliSaat` — Üst çubukta canlı saat
- `MutfakZamanlayici` — Geri sayım sayacı

### Güvenlik
- SHA-256 ile şifre hash'leme (düz metin saklanmaz)
- SQL enjeksiyonu koruması (parametreli sorgular)
- Giriş doğrulama (e-posta formatı, min 4 karakter şifre)
- `CHECK (rol IN ('uye','admin'))` — veritabanı seviyesinde rol kısıtı
- Admin kendi hesabını silemez (UI'da engelli)
- Silme işlemleri QMessageBox onaylı

### Veri Yapıları
- SQLite3 ile **8 tablo**: `kullanicilar`, `tarifler`, `malzemeler`, `degerlendirmeler`, `favoriler`, `sefin_notlari`, `alisveris_listesi`, `haftalik_planlar`
- UPSERT mantığı ile değerlendirme (aynı kullanıcı + aynı tarif → güncellenir)
- CHECK constraint ile 1-5 puan aralığı ve `uye/admin` rol garantisi
- Kademeli silme: admin bir kullanıcıyı silerse, o kullanıcının tüm verileri otomatik temizlenir
- Geriye dönük uyumluluk: eski veritabanları `ALTER TABLE` migration ile otomatik güncellenir

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- Python 3.8+
- PyQt5

### Kurulum
```bash
pip install PyQt5
```

### Çalıştırma
```bash
python app.py
```

Uygulama ilk açıldığında `tarif_platformu.db` dosyasını otomatik oluşturur ve demo hesapları seed eder (üye + admin).

### Testleri Çalıştırma
```bash
python test.py
```

Beklenen çıktı: **62 başarılı / 0 başarısız / 62 toplam (100%)**

---

## 🎨 Tema ve Estetik

**Michelin restoranı** estetiğinde tasarlanmıştır:

| Renk             | Kod       | Kullanım                        |
|------------------|-----------|---------------------------------|
| Koyu Çikolata    | `#0c0806` | Ana arka plan                   |
| Amber Altın      | `#d4a574` | Birincil vurgu                  |
| Adaçayı Yeşili   | `#9cae85` | Başarı/pozitif                  |
| Şarap Kırmızısı  | `#a0425c` | **Admin rozeti** / silme butonu |
| Yanık Bakır      | `#c17b5c` | İkincil vurgu                   |
| Sıcak Krem       | `#f5ece0` | Ana metin                       |

- Serif tipografi: **Georgia** (başlıklar, sayılar, marka)
- Sans-serif: **Segoe UI** (gövde metin, etiketler)
- Özel QPainter çizimleri ile animasyonlu grafikler ve logo

---

## 🧪 Test Kapsamı (62 Test)

| Modül                    | Test Sayısı | Kapsam                                    |
|--------------------------|:-----------:|-------------------------------------------|
| Kullanıcı                |      6      | Ekleme, giriş, şifre, e-posta engeli       |
| Tarif                    |     12      | CRUD, filtreleme, arama, doğrulama         |
| Malzeme                  |      7      | CRUD, sayma, doğrulama                     |
| Alışveriş Listesi        |      4      | Ekleme, birleşik özet, durum, dışa aktarım |
| Haftalık Plan            |      4      | Kaydetme, listeleme, güncelleme, temizleme |
| Değerlendirme            |      6      | Puan verme, UPSERT, aralık kontrolü        |
| Silme                    |      3      | Kademeli silme, bütünlük koruması          |
| **Admin**                |     **10**  | Rol ekleme, yetki, cascade, yorum silme    |
| **Üye Kayıt (yeni)**     |      **5**  | Varsayılan rol, boş/zayıf doğrulama, tekrar |
| İstatistik               |      4      | Genel istatistik, kategori, popülerlik     |

---

## 📌 Teknik Notlar

- Tüm kodlar **Türkçe** değişken/fonksiyon adları ve yorumlarla yazılmıştır
- `VeriYoneticisi` singleton deseni ile tüm veritabanı işlemleri tek noktadan yönetilir
- Aktivite günlüğü `AKTIVITE` global listesi ile bellekte tutulur (son 30 kayıt)
- `AnaPencere._admin_mi()` → aktif kullanıcının admin olup olmadığını dönen yardımcı
- Admin silme işlemleri üç yerde: `_admin_tarif_sil`, `_admin_yorum_sil`, `_admin_kullanici_sil`
- Kullanıcı silme `zorla=True` flag'i ile 7 tabloyu birden temizler (transaction'lı)
- Eski veritabanlarına `rol` kolonu `ALTER TABLE` ile otomatik eklenir (`'uye'` varsayılanı)
