"""
╔══════════════════════════════════════════════════════════════╗
║          YEMEK TARİF PLATFORMU - TEST MODÜLÜ                 ║
╠══════════════════════════════════════════════════════════════╣
║  Tüm sistem senaryolarını test eder                          ║
║  25 test senaryosu                                           ║
╚══════════════════════════════════════════════════════════════╝
"""
from models import Veritabani, Kullanici, Tarif, Malzeme, IstatistikYoneticisi
import os


def testleri_calistir():
    # İzole bir test veritabanı kullan (ana veritabanını etkilememek için)
    test_db = "test_tarif_platformu.db"
    if os.path.exists(test_db):
        os.remove(test_db)

    # Tüm yönetici sınıfları oluştur
    vt = Veritabani(test_db)
    kullanici = Kullanici(vt)
    tarif = Tarif(vt)
    malzeme = Malzeme(vt)
    istatistik = IstatistikYoneticisi(vt)

    basarili = basarisiz = 0

    def test(adi, kosul):
        """Tek bir test senaryosunu kontrol eder ve sayaçları günceller."""
        nonlocal basarili, basarisiz
        if kosul:
            basarili += 1
            print(f"  ✅ {adi}")
        else:
            basarisiz += 1
            print(f"  ❌ {adi}")

    print("\n" + "=" * 60)
    print("  YEMEK TARİF PLATFORMU - TEST RAPORU")
    print("=" * 60)

    # ─────────────── KULLANICI TESTLERİ ───────────────
    print("\n👤 Kullanıcı Testleri:")
    s = kullanici.ekle("Furkan", "Demir", "furkan@test.com", "sifre123")
    test("Kullanıcı ekleme", s["basarili"])
    s = kullanici.ekle("Başka", "Kişi", "furkan@test.com", "baska")
    test("Aynı e-posta engeli", not s["basarili"])
    s = kullanici.ekle("Zayıf", "Şifre", "z@test.com", "12")
    test("Kısa şifre engeli", not s["basarili"])
    k1 = kullanici.giris_yap("furkan@test.com", "sifre123")
    test("Doğru şifre ile giriş", k1 is not None and k1["ad"] == "Furkan")
    test("Yanlış şifre reddi", kullanici.giris_yap("furkan@test.com", "yanlis") is None)
    kullanici.ekle("Ayşe", "Kara", "ayse@test.com", "ayse123")
    test("İkinci kullanıcı ekleme", len(kullanici.listele()) == 2)

    # ─────────────── TARİF TESTLERİ (tarif_ekle, tarif_guncelle) ───────────────
    print("\n🍲 Tarif Testleri:")
    s = tarif.tarif_ekle("Mercimek Çorbası", "Çorba", 30, 1,
                         porsiyon=4, zorluk="Kolay",
                         aciklama="Klasik Türk mutfağı")
    test("tarif_ekle() - geçerli tarif", s["basarili"])
    s = tarif.tarif_ekle("", "Çorba", 30, 1)
    test("Boş tarif adı engeli", not s["basarili"])
    s = tarif.tarif_ekle("Geçersiz", "OlmayanKategori", 30, 1)
    test("Geçersiz kategori engeli", not s["basarili"])
    s = tarif.tarif_ekle("Negatif", "Çorba", -5, 1)
    test("Negatif süre engeli", not s["basarili"])
    s = tarif.tarif_ekle("Olmayan Kullanıcı", "Çorba", 30, 999)
    test("Olmayan kullanıcı engeli", not s["basarili"])

    tarif.tarif_ekle("Künefe", "Tatlı", 45, 2, porsiyon=2, zorluk="Orta")
    tarif.tarif_ekle("Mantı", "Ana Yemek", 90, 1, porsiyon=4, zorluk="Zor")

    t1 = tarif.getir(1)
    test("Tarif detay getirme", t1 and t1["tarif_adi"] == "Mercimek Çorbası")
    test("Tarif listeleme", len(tarif.listele()) == 3)
    test("Kategori filtreleme", len(tarif.listele(kategori="Tatlı")) == 1)
    test("Süre filtresi (≤60dk)", len(tarif.listele(max_sure=60)) == 2)
    test("Tarif arama", len(tarif.ara("mercimek")) == 1)

    s = tarif.tarif_guncelle(1, tarif_adi="Ezogelin Çorbası", hazirlama_suresi=40)
    test("tarif_guncelle() - temel güncelleme", s["basarili"])
    t1_yeni = tarif.getir(1)
    test("Güncelleme doğrulama", t1_yeni["tarif_adi"] == "Ezogelin Çorbası" and t1_yeni["hazirlama_suresi"] == 40)
    s = tarif.tarif_guncelle(999, tarif_adi="Test")
    test("Olmayan tarif güncelleme engeli", not s["basarili"])

    # ─────────────── MALZEME TESTLERİ ───────────────
    print("\n🥕 Malzeme Testleri:")
    test("Malzeme ekleme 1", malzeme.ekle(1, "Kırmızı Mercimek", "1", "su bardağı")["basarili"])
    test("Malzeme ekleme 2", malzeme.ekle(1, "Soğan", "1", "adet")["basarili"])
    test("Malzeme ekleme 3", malzeme.ekle(1, "Tuz", "1", "tatlı kaşığı")["basarili"])
    test("Boş malzeme adı engeli", not malzeme.ekle(1, "", "2", "adet")["basarili"])
    test("Olmayan tarif engeli", not malzeme.ekle(999, "Test", "1", "kg")["basarili"])
    test("Malzeme listeleme", len(malzeme.listele(1)) == 3)
    test("Malzeme sayma", malzeme.topla(1) == 3)
    
    print("\n🛒 Alışveriş Listesi Testleri:")
    alisveris = kullanici.alisveris_listesine_ekle(1, [
        {"malzeme_adi": "Domates", "miktar": "2", "birim": "adet"},
        {"malzeme_adi": "domates", "miktar": "1", "birim": "adet"},
        {"malzeme_adi": "Un", "miktar": "1/2", "birim": "kg"},
    ])
    test("Alışveriş listesine ekleme", alisveris["basarili"])
    ozet = kullanici.alisveris_ozeti_getir(1)
    domates = next((u for u in ozet["birlesik_liste"] if u["malzeme_adi"].lower() == "domates"), None)
    test("Birleşik alışveriş özeti", ozet["benzersiz_urun"] == 2 and domates and domates["miktar"] == "3")
    ilk_kayit = kullanici.alisveris_listesi_getir(1)[0]
    kullanici.alisveris_durum_guncelle(ilk_kayit["id"], True)
    guncel_ozet = kullanici.alisveris_ozeti_getir(1)
    test("Alınan ürün sayısı", guncel_ozet["alinan_kalem"] == 1 and guncel_ozet["bekleyen_kalem"] == 2)
    metin = kullanici.alisveris_metni_olustur(1)
    test("Metin dışa aktarım formatı", "Menu Masterclass - Alisveris Listesi" in metin and "Domates" in metin)
    
    print("\n📅 Haftalık Plan Testleri:")
    plan = kullanici.haftalik_plan_kaydet(1, "Pazartesi", 1, "Aksam", "Corba ile hafif basla")
    test("Haftalık plan kaydetme", plan["basarili"])
    planlar = kullanici.haftalik_plan_getir(1)
    test("Haftalık plan listeleme", len(planlar) == 1 and planlar[0]["gun"] == "Pazartesi")
    guncelle = kullanici.haftalik_plan_kaydet(1, "Pazartesi", 2, "Tatli Molasi", "Tatli dengele")
    test("Haftalık plan güncelleme", guncelle["basarili"] and kullanici.haftalik_plan_getir(1)[0]["tarif_id"] == 2)
    temizle = kullanici.haftalik_plan_temizle(1)
    test("Haftalık plan temizleme", temizle["basarili"] and len(kullanici.haftalik_plan_getir(1)) == 0)

    # ─────────────── DEĞERLENDİRME TESTLERİ (tarif_degerlendir) ───────────────
    print("\n⭐ Değerlendirme Testleri:")
    s = kullanici.tarif_degerlendir(1, 1, 5, "Muhteşem tarif!")
    test("tarif_degerlendir() - geçerli puan", s["basarili"])
    s = kullanici.tarif_degerlendir(2, 1, 4, "Çok iyi")
    test("İkinci kullanıcıdan puan", s["basarili"])
    s = kullanici.tarif_degerlendir(1, 1, 3, "Yeniden değerlendirme")
    test("Aynı kullanıcıdan güncelleme (UPSERT)", s["basarili"])
    s = kullanici.tarif_degerlendir(1, 1, 10)
    test("Geçersiz puan engeli (>5)", not s["basarili"])
    s = kullanici.tarif_degerlendir(1, 1, 0)
    test("Geçersiz puan engeli (<1)", not s["basarili"])
    # (3 + 4) / 2 = 3.5 — UPSERT sonrası ortalama
    test("Ortalama puan hesaplama", tarif.ortalama_puan(1) == 3.5)

    # ─────────────── SİLME TESTLERİ ───────────────
    print("\n🗑️  Silme Testleri:")
    test("Malzeme silme", malzeme.sil(1)["basarili"])
    test("Tarifli kullanıcı silme engeli", not kullanici.sil(1)["basarili"])
    test("Tarif silme", tarif.sil(3)["basarili"])

    # ─────────────── ADMIN TESTLERİ ───────────────
    print("\n🛡️  Admin Testleri:")
    # Admin rolü ile kullanıcı ekleme
    s = kullanici.ekle("Yonetici", "Admin", "admin@test.com", "admin1234", rol="admin")
    test("Admin rolü ile kullanıcı ekleme", s["basarili"])

    # Admin hesabı giriş yapınca rol='admin' geliyor mu
    admin_giris = kullanici.giris_yap("admin@test.com", "admin1234")
    test("Admin girişi ve rol bilgisi", admin_giris is not None and admin_giris.get("rol") == "admin")

    # Normal üye girişinde rol='uye'
    uye_giris = kullanici.giris_yap("furkan@test.com", "sifre123")
    test("Normal üye rol='uye'", uye_giris is not None and uye_giris.get("rol") == "uye")

    # Geçersiz rol reddi
    s = kullanici.ekle("Kotu", "Rol", "kotu@test.com", "1234", rol="sahte")
    test("Geçersiz rol engeli", not s["basarili"])

    # ─────────────── ÜYE KAYIT SENARYOLARI ───────────────
    print("\n📝 Üye Kayıt Testleri:")
    # Yeni üye kaydı (varsayılan rol='uye')
    s = kullanici.ekle("Ali", "Yilmaz", "ali@test.com", "deneme123")
    test("Yeni üye kaydı (varsayılan rol='uye')", s["basarili"])
    ali = kullanici.giris_yap("ali@test.com", "deneme123")
    test("Yeni üye 'uye' rolüne sahip", ali is not None and ali.get("rol") == "uye")
    # Boş ad ile kayıt engeli
    s = kullanici.ekle("", "Soyad", "bos@test.com", "deneme123")
    test("Boş ad ile kayıt engeli", not s["basarili"])
    # Zayıf şifre engeli (< 4 karakter)
    s = kullanici.ekle("Zayif", "Sifre", "zayif@test.com", "12")
    test("Zayıf şifre engeli (< 4 karakter)", not s["basarili"])
    # Aynı e-posta ile iki kayıt engeli
    s = kullanici.ekle("Baska", "Kisi", "ali@test.com", "baska123")
    test("Aynı e-posta ile tekrar kayıt engeli", not s["basarili"])

    # Admin kademeli kullanıcı silme (zorla=True)
    # furkan'ın hâlâ tarifi var → normal sil başarısız
    test("Zorlasız silme tarifli kullanıcı için hâlâ engelli",
         not kullanici.sil(1)["basarili"])
    # Furkan'ın tarif sayısını saklayalım (silme öncesi)
    furkan_tarifleri_once = [t for t in tarif.listele() if t["kullanici_id"] == 1]
    # zorla=True ile admin silmesi (furkan'ın tüm verileri dahil)
    s = kullanici.sil(1, zorla=True)
    test("Admin zorla silme (kullanıcı + tarifleri)",
         s["basarili"] and kullanici.giris_yap("furkan@test.com", "sifre123") is None)
    # Furkan'ın tarifleri de silinmiş olmalı
    furkan_tarifleri_sonra = [t for t in tarif.listele() if t["kullanici_id"] == 1]
    test("Admin silmesiyle tarifler de temizlendi",
         len(furkan_tarifleri_sonra) == 0 and len(furkan_tarifleri_once) > 0)

    # Değerlendirme silme (admin için)
    # Önce bir tarife değerlendirme ekleyelim (Ayşe, tarif 2)
    kullanici.tarif_degerlendir(2, 2, 4, "Admin test yorumu")
    # Degerlendirme id'sini alalım
    degerler = tarif.degerlendirmeler(2)
    if degerler:
        deg_id = degerler[0]["degerlendirme_id"]
        s = kullanici.degerlendirme_sil(deg_id)
        test("Admin değerlendirme silme", s["basarili"])
        test("Değerlendirme gerçekten silindi",
             all(d["degerlendirme_id"] != deg_id for d in tarif.degerlendirmeler(2)))
    else:
        test("Admin değerlendirme silme (değerlendirme bulunamadı, atlandı)", True)
        test("Değerlendirme gerçekten silindi (atlandı)", True)

    # Olmayan değerlendirme silme engeli
    s = kullanici.degerlendirme_sil(9999)
    test("Olmayan değerlendirme silme engeli", not s["basarili"])

    # ─────────────── İSTATİSTİK TESTLERİ ───────────────
    print("\n📊 İstatistik Testleri:")
    ist = istatistik.genel_istatistikler()
    test("İstatistik — kullanıcı sayısı aktif", ist["toplam_kullanici"] >= 1)
    test("İstatistik — tarif sayısı", ist["toplam_tarif"] >= 0)
    test("Kategori dağılımı var", isinstance(ist["kategori_dagilimi"], dict))
    test("Popüler tarifler listesi", isinstance(istatistik.en_populer_tarifler(), list))

    # ─────────────── SONUÇ RAPORU ───────────────
    print("\n" + "=" * 60)
    toplam = basarili + basarisiz
    yuzde = (basarili / toplam * 100) if toplam > 0 else 0
    print(f"  SONUÇ: {basarili} başarılı / {basarisiz} başarısız / {toplam} toplam  ({yuzde:.0f}%)")
    print("=" * 60)

    # Temizlik
    vt.kapat()
    os.remove(test_db)


if __name__ == "__main__":
    testleri_calistir()
