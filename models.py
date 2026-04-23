"""
╔══════════════════════════════════════════════════════════════╗
║          YEMEK TARİF PLATFORMU - VERİ MODELLERİ             ║
╠══════════════════════════════════════════════════════════════╣
║  3 Ana Sınıf     : Tarif, Malzeme, Kullanici                 ║
║  2 Yardımcı Sınıf: Veritabani, IstatistikYoneticisi          ║
║  Veri Yapıları   : Liste (list), Sözlük (dict), Demet(tuple) ║
║  Veritabanı      : SQLite3                                   ║
║  Dosya           : models.py                                 ║
╚══════════════════════════════════════════════════════════════╝
"""

import sqlite3                               # SQLite veritabanı kütüphanesi
import hashlib                               # Şifre hash'leme (SHA-256) için
from typing import List, Dict, Optional      # Tip belirtme araçları
from datetime import datetime                # Tarih ve saat işlemleri


# ══════════════════════════════════════════════════════════════
#  YARDIMCI SINIF 1: VERİTABANI YÖNETİCİSİ
# ══════════════════════════════════════════════════════════════

class Veritabani:
    """
    SQLite veritabanı bağlantı yöneticisi.

    Veritabanı dosyasına bağlanır, gerekli tüm tabloları oluşturur
    ve bağlantıyı kapatma işlemlerini yönetir.

    Özellikler:
        db_path (str)     : Veritabanı dosya yolu
        conn (Connection) : SQLite bağlantı nesnesi
        cursor (Cursor)   : SQL sorgu çalıştırma nesnesi

    Metodlar:
        baglanti_kur()      : Veritabanına bağlantı kurar
        tablolari_olustur() : Tüm tabloları oluşturur
        kapat()             : Bağlantıyı kapatır
    """

    def __init__(self, db_path: str = "tarif_platformu.db"):
        """Veritabanı nesnesini başlatır ve bağlantı kurar."""
        self.db_path = db_path
        self.baglanti_kur()
        self.tablolari_olustur()

    def baglanti_kur(self) -> sqlite3.Connection:
        """
        SQLite veritabanına bağlantı kurar.
        row_factory sayesinde sorgu sonuçları sözlük gibi erişilebilir olur.
        """
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row        # Sonuçları sözlük formatına dönüştürür
        self.cursor = self.conn.cursor()
        # Foreign key kısıtlamalarını aktif et (SQLite varsayılan olarak kapalıdır)
        self.cursor.execute("PRAGMA foreign_keys = ON")
        return self.conn

    def tablolari_olustur(self):
        """
        Veritabanındaki tüm tabloları oluşturur.

        Tablolar:
            1. kullanicilar   - Kullanıcı bilgileri (şifre hash'li)
            2. tarifler       - Tarif bilgileri (kullanıcı ile bire-çok)
            3. malzemeler     - Malzeme bilgileri (tarif ile bire-çok)
            4. degerlendirmeler - Kullanıcı-Tarif değerlendirme tablosu
        """
        self.cursor.executescript("""
            -- Kullanıcılar tablosu (şifreli giriş + rol destekli)
            -- rol değerleri: 'uye' (normal üye) veya 'admin' (tam yetki)
            CREATE TABLE IF NOT EXISTS kullanicilar (
                kullanici_id INTEGER PRIMARY KEY AUTOINCREMENT,
                ad TEXT NOT NULL,
                soyad TEXT DEFAULT '',
                email TEXT UNIQUE NOT NULL,
                sifre_hash TEXT NOT NULL,
                biyografi TEXT DEFAULT '',
                rol TEXT DEFAULT 'uye' CHECK (rol IN ('uye', 'admin')),
                kayit_tarihi TEXT DEFAULT (datetime('now'))
            );

            -- Tarifler tablosu (kullanıcı ile ilişkili)
            CREATE TABLE IF NOT EXISTS tarifler (
                tarif_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarif_adi TEXT NOT NULL,
                kategori TEXT DEFAULT 'Ana Yemek',
                hazirlama_suresi INTEGER DEFAULT 30,
                porsiyon INTEGER DEFAULT 4,
                zorluk TEXT DEFAULT 'Orta',
                aciklama TEXT DEFAULT '',
                yapilis TEXT DEFAULT '',
                kullanici_id INTEGER NOT NULL,
                olusturma_tarihi TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(kullanici_id)
            );

            -- Malzemeler tablosu (tarif ile ilişkili)
            CREATE TABLE IF NOT EXISTS malzemeler (
                malzeme_id INTEGER PRIMARY KEY AUTOINCREMENT,
                tarif_id INTEGER NOT NULL,
                malzeme_adi TEXT NOT NULL,
                miktar TEXT NOT NULL,
                birim TEXT DEFAULT '',
                FOREIGN KEY (tarif_id) REFERENCES tarifler(tarif_id)
            );

            -- Değerlendirmeler tablosu (kullanıcı-tarif çoka-çok ilişki + puan)
            CREATE TABLE IF NOT EXISTS degerlendirmeler (
                degerlendirme_id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_id INTEGER NOT NULL,
                tarif_id INTEGER NOT NULL,
                puan INTEGER NOT NULL CHECK (puan BETWEEN 1 AND 5),
                yorum TEXT DEFAULT '',
                tarih TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(kullanici_id),
                FOREIGN KEY (tarif_id) REFERENCES tarifler(tarif_id),
                UNIQUE(kullanici_id, tarif_id)
            );

            -- Favoriler tablosu
            CREATE TABLE IF NOT EXISTS favoriler (
                favori_id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_id INTEGER NOT NULL,
                tarif_id INTEGER NOT NULL,
                eklenme_tarihi TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(kullanici_id),
                FOREIGN KEY (tarif_id) REFERENCES tarifler(tarif_id),
                UNIQUE(kullanici_id, tarif_id)
            );

            -- Şefin Notları tablosu
            CREATE TABLE IF NOT EXISTS sefin_notlari (
                not_id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_id INTEGER NOT NULL,
                tarif_id INTEGER NOT NULL,
                not_metni TEXT NOT NULL,
                guncellenme_tarihi TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(kullanici_id),
                FOREIGN KEY (tarif_id) REFERENCES tarifler(tarif_id),
                UNIQUE(kullanici_id, tarif_id)
            );

            -- Alışveriş Listesi tablosu
            CREATE TABLE IF NOT EXISTS alisveris_listesi (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_id INTEGER NOT NULL,
                malzeme_adi TEXT NOT NULL,
                miktar TEXT NOT NULL,
                birim TEXT DEFAULT '',
                alindi_mi INTEGER DEFAULT 0,
                FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(kullanici_id)
            );

            CREATE TABLE IF NOT EXISTS haftalik_planlar (
                plan_id INTEGER PRIMARY KEY AUTOINCREMENT,
                kullanici_id INTEGER NOT NULL,
                gun TEXT NOT NULL,
                tarif_id INTEGER NOT NULL,
                ogun TEXT DEFAULT 'Aksam',
                not_metni TEXT DEFAULT '',
                guncellenme_tarihi TEXT DEFAULT (datetime('now')),
                FOREIGN KEY (kullanici_id) REFERENCES kullanicilar(kullanici_id),
                FOREIGN KEY (tarif_id) REFERENCES tarifler(tarif_id),
                UNIQUE(kullanici_id, gun)
            );
        """)
        self.conn.commit()

        # Geriye dönük uyumluluk için gorsel_yolu sütununu ekle
        try:
            self.cursor.execute("ALTER TABLE tarifler ADD COLUMN gorsel_yolu TEXT DEFAULT ''")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Sütun zaten var

        # Geriye dönük uyumluluk için rol sütununu ekle (eski veritabanları için)
        try:
            self.cursor.execute("ALTER TABLE kullanicilar ADD COLUMN rol TEXT DEFAULT 'uye'")
            self.conn.commit()
        except sqlite3.OperationalError:
            pass  # Sütun zaten var

    def kapat(self):
        """Veritabanı bağlantısını güvenli şekilde kapatır."""
        self.conn.close()


# ══════════════════════════════════════════════════════════════
#  ANA SINIF 1: KULLANICI
# ══════════════════════════════════════════════════════════════

class Kullanici:
    """
    Kullanıcı sınıfı - Platformdaki tüm kullanıcıları yönetir.

    Özellikler:
        kullanici_id (int) : Kullanıcının benzersiz kimliği
        ad (str)           : Kullanıcının adı
        soyad (str)        : Kullanıcının soyadı
        email (str)        : E-posta adresi (giriş için)
        sifre_hash (str)   : SHA-256 ile hash'lenmiş şifre

    Metodlar:
        ekle()              - Yeni kullanıcı kaydı oluşturur
        giris_yap()         - E-posta ve şifreyle giriş doğrular
        getir()             - Kullanıcı bilgilerini getirir
        listele()           - Tüm kullanıcıları listeler
        guncelle()          - Kullanıcı bilgilerini günceller
        sil()               - Kullanıcıyı ve ilgili verileri siler
        tarif_degerlendir() - Bir tarife puan ve yorum verir (1-5 yıldız)
    """

    def __init__(self, db: Veritabani):
        """Kullanıcı yöneticisini başlatır."""
        self.db = db

    @staticmethod
    def _sifre_hashle(sifre: str) -> str:
        """Şifreyi SHA-256 ile hash'ler (geri dönüşümsüz güvenli saklama)."""
        return hashlib.sha256(sifre.encode("utf-8")).hexdigest()

    def ekle(self, ad: str, soyad: str, email: str, sifre: str,
             biyografi: str = "", rol: str = "uye") -> Dict:
        """
        Yeni kullanıcı kaydı oluşturur.
        E-posta benzersiz olmalıdır; şifre hash'lenerek saklanır.

        rol: 'uye' (varsayılan) veya 'admin'. Admin tüm verileri silebilir.
        """
        if not ad or not email or not sifre:
            return {"basarili": False, "mesaj": "Ad, e-posta ve şifre zorunludur."}
        if len(sifre) < 4:
            return {"basarili": False, "mesaj": "Şifre en az 4 karakter olmalıdır."}
        if rol not in ("uye", "admin"):
            return {"basarili": False, "mesaj": "Geçersiz rol (uye veya admin olmalı)."}
        try:
            self.db.cursor.execute(
                "INSERT INTO kullanicilar (ad, soyad, email, sifre_hash, biyografi, rol) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                (ad, soyad, email, self._sifre_hashle(sifre), biyografi, rol)
            )
            self.db.conn.commit()
            return {"basarili": True, "kullanici_id": self.db.cursor.lastrowid,
                    "mesaj": f"{ad} başarıyla kaydedildi."}
        except sqlite3.IntegrityError:
            return {"basarili": False, "mesaj": "Bu e-posta adresi zaten kayıtlı."}

    def giris_yap(self, email: str, sifre: str) -> Optional[Dict]:
        """
        E-posta ve şifre ile kullanıcı girişini doğrular.
        Başarılı ise kullanıcı sözlüğü, değilse None döndürür.
        """
        self.db.cursor.execute(
            "SELECT * FROM kullanicilar WHERE email = ? AND sifre_hash = ?",
            (email, self._sifre_hashle(sifre))
        )
        satir = self.db.cursor.fetchone()
        return dict(satir) if satir else None

    def getir(self, kullanici_id: int) -> Optional[Dict]:
        """Belirli bir kullanıcının bilgilerini getirir."""
        self.db.cursor.execute("SELECT * FROM kullanicilar WHERE kullanici_id = ?", (kullanici_id,))
        satir = self.db.cursor.fetchone()
        return dict(satir) if satir else None

    def listele(self) -> List[Dict]:
        """Tüm kullanıcıları ada göre sıralı listeler."""
        self.db.cursor.execute("SELECT * FROM kullanicilar ORDER BY ad")
        return [dict(satir) for satir in self.db.cursor.fetchall()]

    def guncelle(self, kullanici_id: int, **kwargs) -> Dict:
        """Kullanıcı bilgilerini günceller. Geçerli alanlar: ad, soyad, email, biyografi"""
        alanlar, degerler = [], []
        for anahtar, deger in kwargs.items():
            if anahtar in ("ad", "soyad", "email", "biyografi"):
                alanlar.append(f"{anahtar} = ?")
                degerler.append(deger)
        if not alanlar:
            return {"basarili": False, "mesaj": "Güncellenecek alan bulunamadı."}
        degerler.append(kullanici_id)
        self.db.cursor.execute(
            f"UPDATE kullanicilar SET {', '.join(alanlar)} WHERE kullanici_id = ?", degerler
        )
        self.db.conn.commit()
        return {"basarili": True, "mesaj": "Kullanıcı bilgileri güncellendi."}

    def sil(self, kullanici_id: int, zorla: bool = False) -> Dict:
        """
        Kullanıcıyı siler.

        zorla=False (varsayılan): Kullanıcının tarifleri varsa silme engellenir
                                   (veri bütünlüğünü korumak için).
        zorla=True  (admin yetkisi): Kullanıcının tüm tariflerini, malzemelerini,
                                      değerlendirmelerini, favorilerini, notlarını,
                                      alışveriş listesini ve haftalık planını da siler.
        """
        # Kullanıcı var mı?
        self.db.cursor.execute("SELECT 1 FROM kullanicilar WHERE kullanici_id = ?", (kullanici_id,))
        if not self.db.cursor.fetchone():
            return {"basarili": False, "mesaj": "Kullanıcı bulunamadı."}

        # Tarif kontrolü (zorla=False için)
        self.db.cursor.execute(
            "SELECT COUNT(*) AS sayi FROM tarifler WHERE kullanici_id = ?", (kullanici_id,)
        )
        tarif_sayisi = self.db.cursor.fetchone()["sayi"]

        if tarif_sayisi > 0 and not zorla:
            return {"basarili": False,
                    "mesaj": "Kullanıcının tarifleri var, önce onları silin."}

        try:
            # Admin kademeli silme: önce kullanıcının tariflerini (ve onlara bağlı
            # malzeme/değerlendirmeleri) temizle
            if zorla and tarif_sayisi > 0:
                self.db.cursor.execute(
                    "SELECT tarif_id FROM tarifler WHERE kullanici_id = ?", (kullanici_id,)
                )
                tarif_idleri = [r["tarif_id"] for r in self.db.cursor.fetchall()]
                for tid in tarif_idleri:
                    self.db.cursor.execute("DELETE FROM malzemeler WHERE tarif_id = ?", (tid,))
                    self.db.cursor.execute("DELETE FROM degerlendirmeler WHERE tarif_id = ?", (tid,))
                    self.db.cursor.execute("DELETE FROM favoriler WHERE tarif_id = ?", (tid,))
                    self.db.cursor.execute("DELETE FROM sefin_notlari WHERE tarif_id = ?", (tid,))
                    self.db.cursor.execute("DELETE FROM haftalik_planlar WHERE tarif_id = ?", (tid,))
                self.db.cursor.execute("DELETE FROM tarifler WHERE kullanici_id = ?", (kullanici_id,))

            # Kullanıcıya bağlı tüm yan verileri temizle
            self.db.cursor.execute("DELETE FROM degerlendirmeler WHERE kullanici_id = ?", (kullanici_id,))
            self.db.cursor.execute("DELETE FROM favoriler WHERE kullanici_id = ?", (kullanici_id,))
            self.db.cursor.execute("DELETE FROM sefin_notlari WHERE kullanici_id = ?", (kullanici_id,))
            self.db.cursor.execute("DELETE FROM alisveris_listesi WHERE kullanici_id = ?", (kullanici_id,))
            self.db.cursor.execute("DELETE FROM haftalik_planlar WHERE kullanici_id = ?", (kullanici_id,))
            self.db.cursor.execute("DELETE FROM kullanicilar WHERE kullanici_id = ?", (kullanici_id,))
            self.db.conn.commit()
            return {"basarili": True,
                    "mesaj": "Kullanıcı ve bağlı veriler silindi." if zorla else "Kullanıcı silindi."}
        except Exception as hata:
            self.db.conn.rollback()
            return {"basarili": False, "mesaj": f"Silme başarısız: {hata}"}

    def degerlendirme_sil(self, degerlendirme_id: int) -> Dict:
        """
        Belirli bir değerlendirmeyi (yorum + puanı) siler.
        Admin yetkisi için kullanılır — her kullanıcı her yorumu silemez.
        """
        self.db.cursor.execute(
            "DELETE FROM degerlendirmeler WHERE degerlendirme_id = ?", (degerlendirme_id,)
        )
        silinen = self.db.cursor.rowcount
        self.db.conn.commit()
        if silinen > 0:
            return {"basarili": True, "mesaj": "Değerlendirme silindi."}
        return {"basarili": False, "mesaj": "Değerlendirme bulunamadı."}

    def tarif_degerlendir(self, kullanici_id: int, tarif_id: int,
                          puan: int, yorum: str = "") -> Dict:
        """
        ★ GEREKLİ METOD ★
        Kullanıcının bir tarife 1-5 arası puan ve yorum vermesini sağlar.
        Aynı kullanıcı aynı tarifi ikinci kez değerlendirirse,
        eski puan ve yorum yenisiyle değiştirilir (UPSERT mantığı).
        """
        # 1-5 arası puan kontrolü
        if not (1 <= puan <= 5):
            return {"basarili": False, "mesaj": "Puan 1 ile 5 arasında olmalıdır."}

        # Tarif ve kullanıcı geçerliliği
        self.db.cursor.execute("SELECT 1 FROM kullanicilar WHERE kullanici_id = ?", (kullanici_id,))
        if not self.db.cursor.fetchone():
            return {"basarili": False, "mesaj": "Kullanıcı bulunamadı."}
        self.db.cursor.execute("SELECT 1 FROM tarifler WHERE tarif_id = ?", (tarif_id,))
        if not self.db.cursor.fetchone():
            return {"basarili": False, "mesaj": "Tarif bulunamadı."}

        # Mevcut değerlendirme varsa güncelle, yoksa ekle (UPSERT)
        self.db.cursor.execute(
            "SELECT degerlendirme_id FROM degerlendirmeler WHERE kullanici_id = ? AND tarif_id = ?",
            (kullanici_id, tarif_id)
        )
        mevcut = self.db.cursor.fetchone()
        if mevcut:
            self.db.cursor.execute(
                "UPDATE degerlendirmeler SET puan = ?, yorum = ?, tarih = datetime('now') "
                "WHERE degerlendirme_id = ?",
                (puan, yorum, mevcut["degerlendirme_id"])
            )
            mesaj = f"Değerlendirme güncellendi: {puan}/5"
        else:
            self.db.cursor.execute(
                "INSERT INTO degerlendirmeler (kullanici_id, tarif_id, puan, yorum) VALUES (?, ?, ?, ?)",
                (kullanici_id, tarif_id, puan, yorum)
            )
            mesaj = f"Değerlendirme eklendi: {puan}/5"
        self.db.conn.commit()
        return {"basarili": True, "mesaj": mesaj}

    def degerlendirmelerim(self, kullanici_id: int) -> List[Dict]:
        """Kullanıcının yaptığı tüm değerlendirmeleri tarif adlarıyla birlikte getirir."""
        self.db.cursor.execute("""
            SELECT d.*, t.tarif_adi, t.kategori
            FROM degerlendirmeler d
            JOIN tarifler t ON d.tarif_id = t.tarif_id
            WHERE d.kullanici_id = ?
            ORDER BY d.tarih DESC
        """, (kullanici_id,))
        return [dict(satir) for satir in self.db.cursor.fetchall()]

    def favori_ekle_cikar(self, kullanici_id: int, tarif_id: int) -> Dict:
        """Kullanıcının favorisine ekler, zaten varsa çıkarır."""
        self.db.cursor.execute("SELECT favori_id FROM favoriler WHERE kullanici_id = ? AND tarif_id = ?", (kullanici_id, tarif_id))
        mevcut = self.db.cursor.fetchone()
        if mevcut:
            self.db.cursor.execute("DELETE FROM favoriler WHERE favori_id = ?", (mevcut["favori_id"],))
            self.db.conn.commit()
            return {"basarili": True, "durum": "cikarildi", "mesaj": "Tarif favorilerden çıkarıldı."}
        else:
            self.db.cursor.execute("INSERT INTO favoriler (kullanici_id, tarif_id) VALUES (?, ?)", (kullanici_id, tarif_id))
            self.db.conn.commit()
            return {"basarili": True, "durum": "eklendi", "mesaj": "Tarif favorilere eklendi."}

    def favori_mi(self, kullanici_id: int, tarif_id: int) -> bool:
        self.db.cursor.execute("SELECT 1 FROM favoriler WHERE kullanici_id = ? AND tarif_id = ?", (kullanici_id, tarif_id))
        return bool(self.db.cursor.fetchone())

    def favorilerim(self, kullanici_id: int) -> List[Dict]:
        """Kullanıcının favoriye aldığı tarifleri getirir."""
        self.db.cursor.execute("""
            SELECT t.*, k.ad || ' ' || k.soyad AS ekleyen,
                   (SELECT AVG(puan) FROM degerlendirmeler WHERE tarif_id = t.tarif_id) AS ort_puan,
                   (SELECT COUNT(*) FROM degerlendirmeler WHERE tarif_id = t.tarif_id) AS puan_sayisi
            FROM favoriler f
            JOIN tarifler t ON f.tarif_id = t.tarif_id
            JOIN kullanicilar k ON t.kullanici_id = k.kullanici_id
            WHERE f.kullanici_id = ?
            ORDER BY f.eklenme_tarihi DESC
        """, (kullanici_id,))
        return [dict(satir) for satir in self.db.cursor.fetchall()]

    def not_kaydet(self, kullanici_id: int, tarif_id: int, not_metni: str) -> Dict:
        """Kullanıcının tarife özel şefin notunu kaydeder (UPSERT)."""
        self.db.cursor.execute("SELECT not_id FROM sefin_notlari WHERE kullanici_id = ? AND tarif_id = ?", (kullanici_id, tarif_id))
        mevcut = self.db.cursor.fetchone()
        if mevcut:
            self.db.cursor.execute("UPDATE sefin_notlari SET not_metni = ?, guncellenme_tarihi = datetime('now') WHERE not_id = ?", (not_metni, mevcut["not_id"]))
        else:
            self.db.cursor.execute("INSERT INTO sefin_notlari (kullanici_id, tarif_id, not_metni) VALUES (?, ?, ?)", (kullanici_id, tarif_id, not_metni))
        self.db.conn.commit()
        return {"basarili": True, "mesaj": "Şefin notu başarıyla kaydedildi."}

    def not_getir(self, kullanici_id: int, tarif_id: int) -> str:
        """Kullanıcının tarif için yazdığı şefin notunu getirir."""
        self.db.cursor.execute("SELECT not_metni FROM sefin_notlari WHERE kullanici_id = ? AND tarif_id = ?", (kullanici_id, tarif_id))
        mevcut = self.db.cursor.fetchone()
        return mevcut["not_metni"] if mevcut else ""

    # ─── ALIŞVERİŞ LİSTESİ İŞLEMLERİ ───
    def alisveris_listesine_ekle(self, kullanici_id: int, malzemeler: list) -> dict:
        """Belirtilen malzemeleri alışveriş listesine ekler.
        malzemeler listesi sözlük formatında olmalı: [{'malzeme_adi': 'x', 'miktar': '1', 'birim': 'adet'}, ...]"""
        try:
            for m in malzemeler:
                self.db.cursor.execute(
                    "INSERT INTO alisveris_listesi (kullanici_id, malzeme_adi, miktar, birim) VALUES (?, ?, ?, ?)",
                    (kullanici_id, m["malzeme_adi"], m.get("miktar", ""), m.get("birim", ""))
                )
            self.db.conn.commit()
            return {"basarili": True, "mesaj": "Malzemeler alışveriş listesine eklendi."}
        except sqlite3.Error as e:
            self.db.conn.rollback()
            return {"basarili": False, "mesaj": f"Hata: {str(e)}"}

    def alisveris_listesi_getir(self, kullanici_id: int) -> list:
        """Kullanıcının alışveriş listesindeki ürünleri döndürür."""
        self.db.cursor.execute("SELECT * FROM alisveris_listesi WHERE kullanici_id = ?", (kullanici_id,))
        return self.db.cursor.fetchall()

    @staticmethod
    def _miktar_sayiya_cevir(miktar: str) -> Optional[float]:
        """Metinsel miktarı mümkünse sayıya çevirir."""
        if miktar is None:
            return None
        metin = str(miktar).strip().replace(",", ".")
        if not metin:
            return None
        try:
            if "/" in metin:
                parcalar = metin.split("/")
                if len(parcalar) == 2:
                    pay = float(parcalar[0].strip())
                    payda = float(parcalar[1].strip())
                    if payda != 0:
                        return pay / payda
                    return None
            return float(metin)
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _sayi_metne_cevir(deger: float) -> str:
        """Sayısal miktarı okunabilir metne dönüştürür."""
        if float(deger).is_integer():
            return str(int(deger))
        return f"{deger:.2f}".rstrip("0").rstrip(".").replace(".", ",")

    @staticmethod
    def _metin_normallestir(metin: str) -> str:
        """Karşılaştırma için metni sadeleştirir."""
        return " ".join((metin or "").strip().lower().split())

    def alisveris_ozeti_getir(self, kullanici_id: int) -> Dict:
        """Alışveriş listesinin sayılarını ve birleştirilmiş görünümünü döndürür."""
        kayitlar = [dict(satir) for satir in self.alisveris_listesi_getir(kullanici_id)]
        ozet = {
            "toplam_kalem": len(kayitlar),
            "alinan_kalem": sum(1 for kayit in kayitlar if kayit.get("alindi_mi")),
            "bekleyen_kalem": sum(1 for kayit in kayitlar if not kayit.get("alindi_mi")),
            "benzersiz_urun": 0,
            "birlesik_liste": [],
        }
        gruplanmis = {}
        for kayit in kayitlar:
            ad = (kayit.get("malzeme_adi") or "").strip()
            birim = (kayit.get("birim") or "").strip()
            miktar = str(kayit.get("miktar", "")).strip()
            anahtar = (self._metin_normallestir(ad), self._metin_normallestir(birim))
            grup = gruplanmis.setdefault(anahtar, {
                "malzeme_adi": ad or "Adsız malzeme",
                "birim": birim,
                "kayit_sayisi": 0,
                "alinan_sayisi": 0,
                "bekleyen_sayisi": 0,
                "miktarlar": [],
                "sayisal_toplam": 0.0,
                "hepsi_sayisal": True,
            })
            grup["kayit_sayisi"] += 1
            if kayit.get("alindi_mi"):
                grup["alinan_sayisi"] += 1
            else:
                grup["bekleyen_sayisi"] += 1

            sayisal = self._miktar_sayiya_cevir(miktar)
            if sayisal is None:
                grup["hepsi_sayisal"] = False
                if miktar:
                    grup["miktarlar"].append(miktar)
            else:
                grup["sayisal_toplam"] += sayisal
                grup["miktarlar"].append(self._sayi_metne_cevir(sayisal))

        birlesik_liste = []
        for grup in gruplanmis.values():
            if grup["hepsi_sayisal"] and grup["miktarlar"]:
                miktar_metin = self._sayi_metne_cevir(grup["sayisal_toplam"])
            else:
                benzersiz = []
                for miktar in grup["miktarlar"]:
                    if miktar and miktar not in benzersiz:
                        benzersiz.append(miktar)
                miktar_metin = " + ".join(benzersiz) if benzersiz else ""
            birlesik_liste.append({
                "malzeme_adi": grup["malzeme_adi"],
                "birim": grup["birim"],
                "miktar": miktar_metin,
                "kayit_sayisi": grup["kayit_sayisi"],
                "alinan_sayisi": grup["alinan_sayisi"],
                "bekleyen_sayisi": grup["bekleyen_sayisi"],
                "tamamlandi_mi": grup["bekleyen_sayisi"] == 0,
            })

        birlesik_liste.sort(key=lambda kayit: (kayit["tamamlandi_mi"], kayit["malzeme_adi"].lower()))
        ozet["benzersiz_urun"] = len(birlesik_liste)
        ozet["birlesik_liste"] = birlesik_liste
        return ozet

    def alisveris_metni_olustur(self, kullanici_id: int, sadece_bekleyenler: bool = False) -> str:
        """Alışveriş listesini paylaşılabilir düz metin halinde üretir."""
        ozet = self.alisveris_ozeti_getir(kullanici_id)
        satirlar = ["Menu Masterclass - Alisveris Listesi", ""]
        for urun in ozet["birlesik_liste"]:
            if sadece_bekleyenler and urun["tamamlandi_mi"]:
                continue
            durum = "[x]" if urun["tamamlandi_mi"] else "[ ]"
            miktar = f"{urun['miktar']} {urun['birim']}".strip()
            tekrar = f" ({urun['kayit_sayisi']} kayit)" if urun["kayit_sayisi"] > 1 else ""
            satirlar.append(f"{durum} {urun['malzeme_adi']} - {miktar}{tekrar}".rstrip(" -"))
        return "\n".join(satirlar).strip()

    def alisveris_durum_guncelle(self, item_id: int, alindi_mi: bool):
        """Alışveriş listesindeki bir öğenin 'alindi_mi' durumunu günceller."""
        durum = 1 if alindi_mi else 0
        try:
            self.db.cursor.execute("UPDATE alisveris_listesi SET alindi_mi = ? WHERE id = ?", (durum, item_id))
            self.db.conn.commit()
        except sqlite3.Error:
            self.db.conn.rollback()

    def alisveris_listesi_temizle(self, kullanici_id: int, sadece_alinanlar: bool = False):
        """Kullanıcının alışveriş listesini temizler. Sadece alınanlar istenirse sadece onları siler."""
        try:
            if sadece_alinanlar:
                self.db.cursor.execute("DELETE FROM alisveris_listesi WHERE kullanici_id = ? AND alindi_mi = 1", (kullanici_id,))
            else:
                self.db.cursor.execute("DELETE FROM alisveris_listesi WHERE kullanici_id = ?", (kullanici_id,))
            self.db.conn.commit()
        except sqlite3.Error:
            self.db.conn.rollback()

    def haftalik_plan_getir(self, kullanici_id: int) -> List[Dict]:
        """Kullanıcının haftalık planını tarif bilgileriyle birlikte getirir."""
        self.db.cursor.execute("""
            SELECT hp.gun, hp.ogun, hp.not_metni, hp.tarif_id,
                   t.tarif_adi, t.kategori, t.hazirlama_suresi, t.zorluk
            FROM haftalik_planlar hp
            JOIN tarifler t ON hp.tarif_id = t.tarif_id
            WHERE hp.kullanici_id = ?
        """, (kullanici_id,))
        gun_sirasi = {
            "Pazartesi": 0, "Sali": 1, "Carsamba": 2, "Persembe": 3,
            "Cuma": 4, "Cumartesi": 5, "Pazar": 6,
        }
        kayitlar = [dict(satir) for satir in self.db.cursor.fetchall()]
        kayitlar.sort(key=lambda kayit: gun_sirasi.get(kayit["gun"], 99))
        return kayitlar

    def haftalik_plan_kaydet(
        self, kullanici_id: int, gun: str, tarif_id: Optional[int],
        ogun: str = "Aksam", not_metni: str = ""
    ) -> Dict:
        """Belirli bir gün için haftalık plan kaydı oluşturur ya da günceller."""
        if not gun:
            return {"basarili": False, "mesaj": "Gun bilgisi zorunludur."}

        try:
            if not tarif_id:
                self.db.cursor.execute(
                    "DELETE FROM haftalik_planlar WHERE kullanici_id = ? AND gun = ?",
                    (kullanici_id, gun)
                )
                self.db.conn.commit()
                return {"basarili": True, "mesaj": f"{gun} planindan tarif kaldirildi."}

            self.db.cursor.execute(
                "SELECT 1 FROM tarifler WHERE tarif_id = ?",
                (tarif_id,)
            )
            if not self.db.cursor.fetchone():
                return {"basarili": False, "mesaj": "Secilen tarif bulunamadi."}

            self.db.cursor.execute(
                "SELECT plan_id FROM haftalik_planlar WHERE kullanici_id = ? AND gun = ?",
                (kullanici_id, gun)
            )
            mevcut = self.db.cursor.fetchone()
            if mevcut:
                self.db.cursor.execute("""
                    UPDATE haftalik_planlar
                    SET tarif_id = ?, ogun = ?, not_metni = ?, guncellenme_tarihi = datetime('now')
                    WHERE plan_id = ?
                """, (tarif_id, ogun, not_metni.strip(), mevcut["plan_id"]))
            else:
                self.db.cursor.execute("""
                    INSERT INTO haftalik_planlar (kullanici_id, gun, tarif_id, ogun, not_metni)
                    VALUES (?, ?, ?, ?, ?)
                """, (kullanici_id, gun, tarif_id, ogun, not_metni.strip()))
            self.db.conn.commit()
            return {"basarili": True, "mesaj": f"{gun} plani kaydedildi."}
        except sqlite3.Error as hata:
            self.db.conn.rollback()
            return {"basarili": False, "mesaj": f"Hata: {hata}"}

    def haftalik_plan_temizle(self, kullanici_id: int) -> Dict:
        """Kullanıcının tüm haftalık plan kayıtlarını temizler."""
        try:
            self.db.cursor.execute(
                "DELETE FROM haftalik_planlar WHERE kullanici_id = ?",
                (kullanici_id,)
            )
            self.db.conn.commit()
            return {"basarili": True, "mesaj": "Haftalik plan temizlendi."}
        except sqlite3.Error:
            self.db.conn.rollback()
            return {"basarili": False, "mesaj": "Haftalik plan temizlenemedi."}


# ══════════════════════════════════════════════════════════════
#  ANA SINIF 2: TARİF
# ══════════════════════════════════════════════════════════════

class Tarif:
    """
    Tarif sınıfı - Platformdaki tüm yemek tariflerini yönetir.

    Özellikler:
        tarif_id (int)         : Tarifin benzersiz kimliği
        tarif_adi (str)        : Tarifin adı (ör. "Mercimek Çorbası")
        kategori (str)         : Tarif kategorisi (Çorba, Ana Yemek, Tatlı, vb.)
        hazirlama_suresi (int) : Dakika cinsinden hazırlama süresi
        porsiyon (int)         : Kaç kişilik olduğu
        zorluk (str)           : Kolay / Orta / Zor
        aciklama (str)         : Kısa açıklama
        yapilis (str)          : Hazırlanış adımları
        kullanici_id (int)     : Tarifi ekleyen kullanıcı

    Metodlar:
        tarif_ekle()    - ★ GEREKLİ ★ Yeni tarif kaydı oluşturur
        tarif_guncelle()- ★ GEREKLİ ★ Tarif bilgilerini günceller
        getir()         - Tek bir tarifi getirir (detay + kullanıcı adı)
        listele()       - Tüm tarifleri listeler (kategori/süre filtreleri)
        ara()           - Tarif adı ve açıklamada arama yapar
        sil()           - Tarifi ve ilgili malzeme/değerlendirmeleri siler
        ortalama_puan() - Tarifin ortalama değerlendirme puanını hesaplar
    """

    # Geçerli kategori listesi (sınıf seviyesinde sabit)
    KATEGORILER = ["Çorba", "Ana Yemek", "Tatlı", "Salata",
                   "Aperatif", "Kahvaltı", "İçecek", "Hamur İşi"]
    ZORLUK_SEVIYELERI = ["Kolay", "Orta", "Zor"]

    def __init__(self, db: Veritabani):
        """Tarif yöneticisini başlatır."""
        self.db = db

    def tarif_ekle(self, tarif_adi: str, kategori: str, hazirlama_suresi: int,
                   kullanici_id: int, porsiyon: int = 4, zorluk: str = "Orta",
                   aciklama: str = "", yapilis: str = "", gorsel_yolu: str = "") -> Dict:
        """
        ★ GEREKLİ METOD ★
        Yeni bir tarif kaydı oluşturur.

        Parametreler:
            tarif_adi        : Tarifin adı (zorunlu)
            kategori         : KATEGORILER listesinden biri
            hazirlama_suresi : Dakika cinsinden (pozitif olmalı)
            kullanici_id     : Tarifi ekleyen kullanıcının id'si
            porsiyon, zorluk, aciklama, yapilis : Opsiyonel alanlar

        Döndürür:
            {"basarili": bool, "tarif_id": int, "mesaj": str}
        """
        # Doğrulama kontrolleri
        if not tarif_adi or not tarif_adi.strip():
            return {"basarili": False, "mesaj": "Tarif adı boş olamaz."}
        if hazirlama_suresi <= 0:
            return {"basarili": False, "mesaj": "Hazırlama süresi pozitif olmalıdır."}
        if kategori not in self.KATEGORILER:
            return {"basarili": False,
                    "mesaj": f"Geçersiz kategori. Geçerliler: {', '.join(self.KATEGORILER)}"}
        if zorluk not in self.ZORLUK_SEVIYELERI:
            zorluk = "Orta"    # Varsayılan değer

        # Kullanıcının gerçekten var olduğunu doğrula
        self.db.cursor.execute("SELECT 1 FROM kullanicilar WHERE kullanici_id = ?", (kullanici_id,))
        if not self.db.cursor.fetchone():
            return {"basarili": False, "mesaj": "Geçersiz kullanıcı."}

        # Kayıt işlemi
        self.db.cursor.execute(
            """INSERT INTO tarifler
               (tarif_adi, kategori, hazirlama_suresi, porsiyon, zorluk,
                aciklama, yapilis, kullanici_id, gorsel_yolu)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (tarif_adi.strip(), kategori, hazirlama_suresi, porsiyon,
             zorluk, aciklama, yapilis, kullanici_id, gorsel_yolu)
        )
        self.db.conn.commit()
        return {"basarili": True, "tarif_id": self.db.cursor.lastrowid,
                "mesaj": f"'{tarif_adi}' tarifi başarıyla eklendi."}

    def tarif_guncelle(self, tarif_id: int, **kwargs) -> Dict:
        """
        ★ GEREKLİ METOD ★
        Tarif bilgilerini günceller.
        Sadece izin verilen alanlar güncellenir (SQL enjeksiyonu koruması).

        Örnek: tarif_guncelle(1, tarif_adi="Yeni Ad", hazirlama_suresi=45)
        """
        izinli_alanlar = ("tarif_adi", "kategori", "hazirlama_suresi",
                          "porsiyon", "zorluk", "aciklama", "yapilis", "gorsel_yolu")
        alanlar, degerler = [], []

        for anahtar, deger in kwargs.items():
            if anahtar in izinli_alanlar:
                # Ek doğrulamalar
                if anahtar == "kategori" and deger not in self.KATEGORILER:
                    return {"basarili": False, "mesaj": f"Geçersiz kategori: {deger}"}
                if anahtar == "hazirlama_suresi" and deger <= 0:
                    return {"basarili": False, "mesaj": "Süre pozitif olmalıdır."}
                if anahtar == "zorluk" and deger not in self.ZORLUK_SEVIYELERI:
                    return {"basarili": False, "mesaj": f"Geçersiz zorluk: {deger}"}
                alanlar.append(f"{anahtar} = ?")
                degerler.append(deger)

        if not alanlar:
            return {"basarili": False, "mesaj": "Güncellenecek geçerli alan bulunamadı."}

        # Tarifin var olup olmadığını kontrol et
        self.db.cursor.execute("SELECT 1 FROM tarifler WHERE tarif_id = ?", (tarif_id,))
        if not self.db.cursor.fetchone():
            return {"basarili": False, "mesaj": "Tarif bulunamadı."}

        degerler.append(tarif_id)
        self.db.cursor.execute(
            f"UPDATE tarifler SET {', '.join(alanlar)} WHERE tarif_id = ?", degerler
        )
        self.db.conn.commit()
        return {"basarili": True, "mesaj": "Tarif başarıyla güncellendi."}

    def getir(self, tarif_id: int) -> Optional[Dict]:
        """
        Bir tarifi tüm detaylarıyla getirir.
        Kullanıcı adı ve ortalama puan da sonuca eklenir.
        """
        self.db.cursor.execute("""
            SELECT t.*, k.ad || ' ' || k.soyad AS ekleyen,
                   (SELECT AVG(puan) FROM degerlendirmeler WHERE tarif_id = t.tarif_id) AS ort_puan,
                   (SELECT COUNT(*) FROM degerlendirmeler WHERE tarif_id = t.tarif_id) AS puan_sayisi
            FROM tarifler t
            JOIN kullanicilar k ON t.kullanici_id = k.kullanici_id
            WHERE t.tarif_id = ?
        """, (tarif_id,))
        satir = self.db.cursor.fetchone()
        return dict(satir) if satir else None

    def listele(self, kategori: str = None, max_sure: int = None) -> List[Dict]:
        """
        Tüm tarifleri listeler. Opsiyonel filtreler:
            kategori : Belirli bir kategorideki tarifler
            max_sure : Belirli bir süreden kısa tarifler (dakika)
        """
        sorgu = """
            SELECT t.*, k.ad || ' ' || k.soyad AS ekleyen,
                   (SELECT AVG(puan) FROM degerlendirmeler WHERE tarif_id = t.tarif_id) AS ort_puan,
                   (SELECT COUNT(*) FROM degerlendirmeler WHERE tarif_id = t.tarif_id) AS puan_sayisi
            FROM tarifler t
            JOIN kullanicilar k ON t.kullanici_id = k.kullanici_id
        """
        kosullar, parametreler = [], []
        if kategori:
            kosullar.append("t.kategori = ?")
            parametreler.append(kategori)
        if max_sure:
            kosullar.append("t.hazirlama_suresi <= ?")
            parametreler.append(max_sure)
        if kosullar:
            sorgu += " WHERE " + " AND ".join(kosullar)
        sorgu += " ORDER BY t.olusturma_tarihi DESC"

        self.db.cursor.execute(sorgu, parametreler)
        return [dict(satir) for satir in self.db.cursor.fetchall()]

    def ara(self, anahtar_kelime: str) -> List[Dict]:
        """Tarif adı ve açıklamada arama yapar (büyük/küçük harf duyarsız)."""
        desen = f"%{anahtar_kelime}%"
        self.db.cursor.execute("""
            SELECT t.*, k.ad || ' ' || k.soyad AS ekleyen,
                   (SELECT AVG(puan) FROM degerlendirmeler WHERE tarif_id = t.tarif_id) AS ort_puan
            FROM tarifler t
            JOIN kullanicilar k ON t.kullanici_id = k.kullanici_id
            WHERE LOWER(t.tarif_adi) LIKE LOWER(?) OR LOWER(t.aciklama) LIKE LOWER(?)
            ORDER BY t.olusturma_tarihi DESC
        """, (desen, desen))
        return [dict(satir) for satir in self.db.cursor.fetchall()]

    def sil(self, tarif_id: int) -> Dict:
        """Tarifi ve ilgili tüm malzeme/değerlendirmeleri siler."""
        self.db.cursor.execute("DELETE FROM malzemeler WHERE tarif_id = ?", (tarif_id,))
        self.db.cursor.execute("DELETE FROM degerlendirmeler WHERE tarif_id = ?", (tarif_id,))
        self.db.cursor.execute("DELETE FROM tarifler WHERE tarif_id = ?", (tarif_id,))
        silinen = self.db.cursor.rowcount
        self.db.conn.commit()
        if silinen > 0:
            return {"basarili": True, "mesaj": "Tarif ve tüm ilişkili veriler silindi."}
        return {"basarili": False, "mesaj": "Tarif bulunamadı."}

    def ortalama_puan(self, tarif_id: int) -> float:
        """Tarifin ortalama değerlendirme puanını hesaplar (0.0 - 5.0)."""
        self.db.cursor.execute(
            "SELECT AVG(puan) AS ort FROM degerlendirmeler WHERE tarif_id = ?", (tarif_id,)
        )
        sonuc = self.db.cursor.fetchone()["ort"]
        return round(sonuc, 2) if sonuc else 0.0

    def degerlendirmeler(self, tarif_id: int) -> List[Dict]:
        """Bir tarife yapılan tüm değerlendirmeleri kullanıcı adlarıyla getirir."""
        self.db.cursor.execute("""
            SELECT d.*, k.ad || ' ' || k.soyad AS kullanici_adi
            FROM degerlendirmeler d
            JOIN kullanicilar k ON d.kullanici_id = k.kullanici_id
            WHERE d.tarif_id = ?
            ORDER BY d.tarih DESC
        """, (tarif_id,))
        return [dict(satir) for satir in self.db.cursor.fetchall()]

    def malzemeye_gore_ara(self, malzeme_isimleri: List[str]) -> List[Dict]:
        """
        Verilen malzeme isimlerinden EN AZ BİRİNİ içeren tarifleri döndürür.
        """
        if not malzeme_isimleri:
            return []
            
        kosullar = []
        parametreler = []
        for isim in malzeme_isimleri:
            kosullar.append("m.malzeme_adi LIKE ?")
            parametreler.append(f"%{isim.strip()}%")
            
        kosul_str = " OR ".join(kosullar)
        
        sorgu = f"""
            SELECT DISTINCT t.*, k.ad || ' ' || k.soyad AS ekleyen,
                   (SELECT AVG(puan) FROM degerlendirmeler WHERE tarif_id = t.tarif_id) AS ort_puan,
                   (SELECT COUNT(*) FROM degerlendirmeler WHERE tarif_id = t.tarif_id) AS puan_sayisi
            FROM tarifler t
            JOIN kullanicilar k ON t.kullanici_id = k.kullanici_id
            JOIN malzemeler m ON t.tarif_id = m.tarif_id
            WHERE {kosul_str}
            ORDER BY t.olusturma_tarihi DESC
        """
        self.db.cursor.execute(sorgu, parametreler)
        return [dict(satir) for satir in self.db.cursor.fetchall()]
        
    def rastgele_getir(self) -> Optional[Dict]:
        """Rastgele bir tarif döndürür (Bugün Ne Pişirsem için)."""
        self.db.cursor.execute("SELECT tarif_id FROM tarifler ORDER BY RANDOM() LIMIT 1")
        satir = self.db.cursor.fetchone()
        if satir:
            return self.getir(satir["tarif_id"])
        return None


# ══════════════════════════════════════════════════════════════
#  ANA SINIF 3: MALZEME
# ══════════════════════════════════════════════════════════════

class Malzeme:
    """
    Malzeme sınıfı - Tariflerin malzemelerini yönetir.

    Her malzeme bir tarife aittir (bire-çok ilişki).

    Özellikler:
        malzeme_adi (str) : Malzemenin adı (ör. "Domates")
        miktar (str)      : Miktar değeri (ör. "2", "500", "1/2")
        birim (str)       : Ölçü birimi (ör. "adet", "gr", "su bardağı")

    Metodlar:
        ekle()    - Tarife yeni malzeme ekler
        getir()   - Tek bir malzemeyi getirir
        listele() - Bir tarifin tüm malzemelerini listeler
        guncelle()- Malzeme bilgilerini günceller
        sil()     - Malzemeyi siler
        topla()   - Bir tarifin toplam malzeme sayısını döndürür
    """

    def __init__(self, db: Veritabani):
        """Malzeme yöneticisini başlatır."""
        self.db = db

    def ekle(self, tarif_id: int, malzeme_adi: str, miktar: str, birim: str = "") -> Dict:
        """Bir tarife yeni malzeme ekler."""
        if not malzeme_adi or not malzeme_adi.strip():
            return {"basarili": False, "mesaj": "Malzeme adı boş olamaz."}
        if not miktar or not str(miktar).strip():
            return {"basarili": False, "mesaj": "Miktar belirtilmelidir."}

        # Tarifin varlığını doğrula
        self.db.cursor.execute("SELECT 1 FROM tarifler WHERE tarif_id = ?", (tarif_id,))
        if not self.db.cursor.fetchone():
            return {"basarili": False, "mesaj": "Tarif bulunamadı."}

        self.db.cursor.execute(
            "INSERT INTO malzemeler (tarif_id, malzeme_adi, miktar, birim) VALUES (?, ?, ?, ?)",
            (tarif_id, malzeme_adi.strip(), str(miktar).strip(), birim.strip())
        )
        self.db.conn.commit()
        return {"basarili": True, "malzeme_id": self.db.cursor.lastrowid,
                "mesaj": f"{malzeme_adi} eklendi."}

    def getir(self, malzeme_id: int) -> Optional[Dict]:
        """Tek bir malzemenin bilgilerini getirir."""
        self.db.cursor.execute("SELECT * FROM malzemeler WHERE malzeme_id = ?", (malzeme_id,))
        satir = self.db.cursor.fetchone()
        return dict(satir) if satir else None

    def listele(self, tarif_id: int) -> List[Dict]:
        """Belirli bir tarifin tüm malzemelerini listeler."""
        self.db.cursor.execute(
            "SELECT * FROM malzemeler WHERE tarif_id = ? ORDER BY malzeme_id", (tarif_id,)
        )
        return [dict(satir) for satir in self.db.cursor.fetchall()]

    def guncelle(self, malzeme_id: int, **kwargs) -> Dict:
        """Malzeme bilgilerini günceller."""
        alanlar, degerler = [], []
        for anahtar, deger in kwargs.items():
            if anahtar in ("malzeme_adi", "miktar", "birim"):
                alanlar.append(f"{anahtar} = ?")
                degerler.append(deger)
        if not alanlar:
            return {"basarili": False, "mesaj": "Güncellenecek alan bulunamadı."}
        degerler.append(malzeme_id)
        self.db.cursor.execute(
            f"UPDATE malzemeler SET {', '.join(alanlar)} WHERE malzeme_id = ?", degerler
        )
        self.db.conn.commit()
        return {"basarili": True, "mesaj": "Malzeme güncellendi."}

    def sil(self, malzeme_id: int) -> Dict:
        """Malzemeyi tarifinden siler."""
        self.db.cursor.execute("DELETE FROM malzemeler WHERE malzeme_id = ?", (malzeme_id,))
        silinen = self.db.cursor.rowcount
        self.db.conn.commit()
        if silinen > 0:
            return {"basarili": True, "mesaj": "Malzeme silindi."}
        return {"basarili": False, "mesaj": "Malzeme bulunamadı."}

    def topla(self, tarif_id: int) -> int:
        """Bir tarifin toplam malzeme sayısını döndürür."""
        self.db.cursor.execute(
            "SELECT COUNT(*) AS sayi FROM malzemeler WHERE tarif_id = ?", (tarif_id,)
        )
        return self.db.cursor.fetchone()["sayi"]


# ══════════════════════════════════════════════════════════════
#  YARDIMCI SINIF 2: İSTATİSTİK YÖNETİCİSİ
# ══════════════════════════════════════════════════════════════

class IstatistikYoneticisi:
    """
    Platform geneli istatistikleri hesaplar.
    Dashboard'daki istatistik kartları ve grafikler bu sınıfı kullanır.

    Metodlar:
        genel_istatistikler() - Toplam sayılar ve kategori dağılımı
        en_populer_tarifler() - En çok değerlendirilen / yüksek puanlı tarifler
        kategori_ortalamalari()- Her kategorinin ortalama puanı/süresi
    """

    def __init__(self, db: Veritabani):
        """İstatistik yöneticisini başlatır."""
        self.db = db

    def genel_istatistikler(self) -> Dict:
        """
        Platform genelindeki temel istatistikleri hesaplar.

        Döndürür (sözlük):
            toplam_kullanici, toplam_tarif, toplam_malzeme,
            toplam_degerlendirme, ortalama_puan,
            kategori_dagilimi (dict), zorluk_dagilimi (dict)
        """
        ist = {}

        # Toplam sayılar
        self.db.cursor.execute("SELECT COUNT(*) AS sayi FROM kullanicilar")
        ist["toplam_kullanici"] = self.db.cursor.fetchone()["sayi"]

        self.db.cursor.execute("SELECT COUNT(*) AS sayi FROM tarifler")
        ist["toplam_tarif"] = self.db.cursor.fetchone()["sayi"]

        self.db.cursor.execute("SELECT COUNT(*) AS sayi FROM malzemeler")
        ist["toplam_malzeme"] = self.db.cursor.fetchone()["sayi"]

        self.db.cursor.execute("SELECT COUNT(*) AS sayi FROM degerlendirmeler")
        ist["toplam_degerlendirme"] = self.db.cursor.fetchone()["sayi"]

        # Platform geneli ortalama puan
        self.db.cursor.execute("SELECT AVG(puan) AS ort FROM degerlendirmeler")
        ort = self.db.cursor.fetchone()["ort"]
        ist["ortalama_puan"] = round(ort, 2) if ort else 0.0

        # Kategori dağılımı
        self.db.cursor.execute(
            "SELECT kategori, COUNT(*) AS sayi FROM tarifler GROUP BY kategori ORDER BY sayi DESC"
        )
        ist["kategori_dagilimi"] = {s["kategori"]: s["sayi"] for s in self.db.cursor.fetchall()}

        # Zorluk dağılımı
        self.db.cursor.execute(
            "SELECT zorluk, COUNT(*) AS sayi FROM tarifler GROUP BY zorluk"
        )
        ist["zorluk_dagilimi"] = {s["zorluk"]: s["sayi"] for s in self.db.cursor.fetchall()}

        return ist

    def en_populer_tarifler(self, limit: int = 5) -> List[Dict]:
        """En yüksek ortalama puana sahip tarifleri döndürür (en az 1 puan olmalı)."""
        self.db.cursor.execute("""
            SELECT t.tarif_id, t.tarif_adi, t.kategori,
                   AVG(d.puan) AS ort_puan, COUNT(d.degerlendirme_id) AS puan_sayisi
            FROM tarifler t
            LEFT JOIN degerlendirmeler d ON t.tarif_id = d.tarif_id
            GROUP BY t.tarif_id
            HAVING puan_sayisi > 0
            ORDER BY ort_puan DESC, puan_sayisi DESC
            LIMIT ?
        """, (limit,))
        return [dict(satir) for satir in self.db.cursor.fetchall()]

    def kategori_ortalamalari(self) -> List[Dict]:
        """Her kategori için ortalama süre ve ortalama puan hesaplar."""
        self.db.cursor.execute("""
            SELECT t.kategori,
                   AVG(t.hazirlama_suresi) AS ort_sure,
                   AVG(d.puan) AS ort_puan,
                   COUNT(DISTINCT t.tarif_id) AS tarif_sayisi
            FROM tarifler t
            LEFT JOIN degerlendirmeler d ON t.tarif_id = d.tarif_id
            GROUP BY t.kategori
            ORDER BY tarif_sayisi DESC
        """)
        return [dict(satir) for satir in self.db.cursor.fetchall()]
