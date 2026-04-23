"""
╔══════════════════════════════════════════════════════════════╗
║          YEMEK TARİF PLATFORMU - MASAÜSTÜ UYGULAMASI         ║
╠══════════════════════════════════════════════════════════════╣
║  Çatı (Framework)  : PyQt5                                   ║
║  Tema              : Koyu çikolata + amber altın (Michelin)  ║
║  Ana sayfa sayısı  : 6 (Dashboard, Tarifler, Detay,          ║
║                         Yeni Tarif, Kullanıcılar, İstatistik)║
║  Özel Widget'lar   : Halka, ÇubukGrafik, Yıldız, TarifKartı  ║
║  Dosya             : app.py                                  ║
╚══════════════════════════════════════════════════════════════╝
"""

import sys
import math
import random
import os
import shutil
import uuid
from datetime import datetime
from typing import Dict

from PyQt5.QtWidgets import (
    QApplication, QWidget, QMainWindow, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox, QSpinBox, QScrollArea,
    QFrame, QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView, QDialog,
    QFormLayout, QMessageBox, QSizePolicy, QGraphicsDropShadowEffect,
    QListWidget, QListWidgetItem, QCheckBox, QFileDialog
)
from PyQt5.QtCore import (
    Qt, QTimer, QPropertyAnimation, QEasingCurve, QRect,
    pyqtSignal, QSize, QPointF, pyqtProperty
)
from PyQt5.QtGui import (
    QFont, QColor, QPainter, QPen, QBrush, QLinearGradient, QRadialGradient,
    QPainterPath, QFontDatabase, QPolygonF, QPdfWriter, QPageSize, QPixmap
)

from models import Veritabani, Kullanici, Tarif, Malzeme, IstatistikYoneticisi


# ══════════════════════════════════════════════════════════════════
#  RENK PALETİ — Koyu çikolata zemin, amber altın vurgu
#  ("Michelin restoranı" estetiği: sıcak, derin, rafine)
# ══════════════════════════════════════════════════════════════════
class C:
    # ─── Arka plan tonları (derinden yüzeye) ───
    BG      = "#0c0806"     # Ana arka plan (neredeyse siyah kahve)
    BG2     = "#13100c"     # Yan panel
    BG3     = "#080604"     # En koyu
    CARD    = "#1a1410"     # Kart arka planı
    CARD2   = "#231c16"     # Açık kart (hover/vurgu)
    CARD3   = "#2c241c"     # Daha açık
    HOVER   = "#342a20"     # Hover durumu
    BORDER  = "#2a2118"     # Birincil kenar
    BORDER2 = "#3d3022"     # İkincil kenar (vurgulu)

    # ─── Metin tonları ───
    TEXT    = "#f5ece0"     # Ana metin (sıcak krem)
    TEXT2   = "#a89985"     # İkincil metin (ılık gri)
    TEXT3   = "#6b5e50"     # Silik metin (etiketler)

    # ─── Vurgu renkleri ───
    GOLD    = "#d4a574"     # Birincil amber (ana vurgu)
    GOLD2   = "#e8c088"     # Açık altın
    GOLD3   = "#8a6a44"     # Koyu altın
    COPPER  = "#c17b5c"     # Yanık bakır (ikincil vurgu)

    SAGE    = "#9cae85"     # Adaçayı yeşili (pozitif/taze)
    SAGE2   = "#b5c79e"     # Açık adaçayı
    HERB    = "#7a9968"     # Koyu bitki yeşili

    WINE    = "#a0425c"     # Şarap kırmızısı (hata/uyarı)
    WINE2   = "#c05676"     # Açık şarap
    AMBER   = "#e8a658"     # Parlak amber (uyarı)

    # ─── Durum renkleri ───
    GREEN   = "#7a9968"     # Başarı
    RED     = "#a0425c"     # Hata
    YELLOW  = "#e8a658"     # Uyarı
    BLUE    = "#6b8aa8"     # Bilgi


# Kategori → renk eşlemesi (dashboard ve kartlar için)
KAT_RENK = {
    "Çorba":      "#c17b5c",    # Yanık bakır
    "Ana Yemek":  "#d4a574",    # Amber altın
    "Tatlı":      "#c05676",    # Şarap kırmızısı
    "Salata":     "#9cae85",    # Adaçayı
    "Aperatif":   "#e8a658",    # Parlak amber
    "Kahvaltı":   "#e8c088",    # Açık altın
    "İçecek":     "#6b8aa8",    # Taş mavisi
    "Hamur İşi":  "#b5927a",    # Fırınlanmış ekmek
}

# Zorluk → renk
ZOR_RENK = {"Kolay": C.SAGE, "Orta": C.GOLD, "Zor": C.WINE}

ORNEK_TARIFLER = [
    {
        "ad": "Fırında Somon Fileto",
        "kategori": "Ana Yemek",
        "sure": 40,
        "porsiyon": 2,
        "zorluk": "Orta",
        "aciklama": "Taze otlar ve limon dilimleriyle fırınlanmış, hafif ama gösterişli bir ana yemek.",
        "yapilis": (
            "1. Somonları kurulayın ve zeytinyağı, sarımsak, tuz, karabiber ile marine edin.\n"
            "2. Tepsiye yerleştirip üzerine limon dilimleri ve dereotu ekleyin.\n"
            "3. 200 derecede 25-30 dakika pişirin.\n"
            "4. Yanına roka salatası ile sıcak servis edin."
        ),
        "malzemeler": [
            ("Somon Fileto", "2", "Büyük Dilim"),
            ("Zeytinyağı", "3", "Yemek Kaşığı"),
            ("Limon", "1", "Adet"),
            ("Dereotu", "1", "Tutam"),
        ],
        "puan": 5,
        "yorum": "Balık sulu kalıyor, davet menüsü için çok şık.",
        "sunum": "Fırın patates ve roka salatasıyla birlikte servis edildiğinde restoran tabağı etkisi yaratır.",
        "yorumlar": [
            ("asya@menu.com", 5, "Limon ve dereotu dengesi çok iyi, hiç ağır olmadı."),
            ("emir@menu.com", 4, "Hafta sonu akşamı için çok şık ve pratik bir tarif."),
        ],
    },
    {
        "ad": "Kremalı Mantar Çorbası",
        "kategori": "Çorba",
        "sure": 30,
        "porsiyon": 4,
        "zorluk": "Kolay",
        "aciklama": "İpeksi dokusuyla içinizi ısıtacak klasik Fransız usulü mantar çorbası.",
        "yapilis": (
            "1. Soğan ve sarımsağı tereyağında soteleyin.\n"
            "2. Dilimlenmiş mantarları ekleyip suyunu çektirin.\n"
            "3. Unu kavurup et suyu ve kremayı ilave edin.\n"
            "4. 15 dakika kaynatıp blenderdan geçirerek servis edin."
        ),
        "malzemeler": [
            ("Kültür Mantarı", "400", "Gram"),
            ("Sıvı Krema", "200", "Mililitre"),
            ("Tereyağı", "2", "Yemek Kaşığı"),
            ("Et Suyu", "4", "Su Bardağı"),
        ],
        "puan": 4,
        "yorum": "Hafta içi için pratik ama sofrada çok güçlü duruyor.",
        "sunum": "Üzerine birkaç damla krema ve ince kıyılmış maydanoz ekleyerek servis edin.",
        "yorumlar": [
            ("zeynep@menu.com", 5, "Kıvamı tam oldu, ekmekle birlikte çok iyi gitti."),
            ("derya@menu.com", 4, "Blender sonrası ipeksi bir doku aldı, tekrar yaparım."),
        ],
    },
    {
        "ad": "San Sebastian Cheesecake",
        "kategori": "Tatlı",
        "sure": 60,
        "porsiyon": 6,
        "zorluk": "Zor",
        "aciklama": "İçi akışkan, üstü karamelize meşhur İspanyol cheesecake klasiği.",
        "yapilis": (
            "1. Krem peynir ve şekeri pürüzsüz olana kadar çırpın.\n"
            "2. Yumurtaları tek tek ekleyin.\n"
            "3. Krema, vanilya ve unu karışıma yedirin.\n"
            "4. 220 derecede yüksek ısıda 25 dakika pişirip dinlendirin."
        ),
        "malzemeler": [
            ("Krem Peynir", "600", "Gram"),
            ("Toz Şeker", "1.5", "Su Bardağı"),
            ("Sıvı Krema", "400", "Mililitre"),
            ("Yumurta", "4", "Adet"),
        ],
        "puan": 5,
        "yorum": "Dokusu tam yerinde, misafir sofralarında hep soruluyor.",
        "sunum": "Buzdolabında dinlendirdikten sonra sade bırakıp yoğun kahveyle servis edin.",
        "yorumlar": [
            ("asya@menu.com", 5, "Üst yanıklığı çok güzel oldu, içi de tam akışkan kaldı."),
            ("emir@menu.com", 4, "Bir gece dinlendirilince çok daha dengeli bir tat alıyor."),
        ],
    },
    {
        "ad": "Avokadolu Akdeniz Salatası",
        "kategori": "Salata",
        "sure": 15,
        "porsiyon": 2,
        "zorluk": "Kolay",
        "aciklama": "Narenciye soslu, taze otlarla desteklenmiş ferah bir salata tabağı.",
        "yapilis": (
            "1. Marul, roka, salatalık ve cherry domatesleri doğrayın.\n"
            "2. Avokado dilimlerini ve beyaz peyniri ekleyin.\n"
            "3. Zeytinyağı, limon suyu ve hardalı çırpıp sosu hazırlayın.\n"
            "4. Sosu gezdirip kabak çekirdeği ile servis edin."
        ),
        "malzemeler": [
            ("Avokado", "1", "Adet"),
            ("Roka", "1", "Demet"),
            ("Cherry Domates", "10", "Adet"),
            ("Beyaz Peynir", "80", "Gram"),
        ],
        "puan": 4,
        "yorum": "Hafif menüler için çok taze ve dengeli bir seçenek.",
        "sunum": "Geniş tabakta katmanlı sunum ve ekstra limon kabuğu rendesiyle servis edin.",
        "yorumlar": [
            ("zeynep@menu.com", 4, "Öğle menüsü için hafif ama doyurucu bir seçenek oldu."),
            ("derya@menu.com", 5, "Sosu çok dengeli, avokado ile şahane uydu."),
        ],
    },
    {
        "ad": "Menemen Tost Tabağı",
        "kategori": "Kahvaltı",
        "sure": 20,
        "porsiyon": 3,
        "zorluk": "Kolay",
        "aciklama": "Klasik menemeni çıtır ekmek ve eriyen kaşarla daha doyurucu hale getiren kahvaltı tabağı.",
        "yapilis": (
            "1. Biberleri soteleyip domatesleri ekleyin.\n"
            "2. Yumurtaları kırıp hafif sulu kalacak şekilde pişirin.\n"
            "3. Kaşarı ekleyip kapağı kapatın.\n"
            "4. Tost ekmekleriyle birlikte sıcak servis edin."
        ),
        "malzemeler": [
            ("Yumurta", "4", "Adet"),
            ("Domates", "3", "Adet"),
            ("Yeşil Biber", "2", "Adet"),
            ("Kaşar Peyniri", "100", "Gram"),
        ],
        "puan": 5,
        "yorum": "Kahvaltı bölümünü gerçekten canlandıran sıcak bir tarif.",
        "sunum": "Döküm tavada ve yanında kızarmış ekşi mayalı ekmekle servis edin.",
        "yorumlar": [
            ("asya@menu.com", 5, "Kahvaltı sayfasını bir anda canlı gösteren tarif bu oldu."),
            ("emir@menu.com", 4, "Kaşar eklenince çok daha doyurucu oldu."),
        ],
    },
    {
        "ad": "Naneli Ev Limonatası",
        "kategori": "İçecek",
        "sure": 10,
        "porsiyon": 4,
        "zorluk": "Kolay",
        "aciklama": "Taze nane ve bal dokunuşuyla ferahlatıcı yaz içeceği.",
        "yapilis": (
            "1. Limon suyu, bal ve soğuk suyu karıştırın.\n"
            "2. İnce kıyılmış naneyi ekleyin.\n"
            "3. Bol buz ve limon dilimleriyle sürahide servis edin."
        ),
        "malzemeler": [
            ("Limon", "4", "Adet"),
            ("Bal", "3", "Yemek Kaşığı"),
            ("Taze Nane", "8", "Yaprak"),
            ("Soğuk Su", "1", "Litre"),
        ],
        "puan": 4,
        "yorum": "İçecek kategorisini boş bırakmayan güzel bir başlangıç tarifi.",
        "sunum": "Bol buz, limon dilimi ve nane dalıyla cam sürahide sunun.",
        "yorumlar": [
            ("zeynep@menu.com", 4, "Bal ile yapılınca çok daha yumuşak içimli oldu."),
            ("derya@menu.com", 5, "Yaz menüsüne tam oturan ferah bir içecek."),
        ],
    },
    {
        "ad": "Çıtır Tavuk Taco",
        "kategori": "Aperatif",
        "sure": 35,
        "porsiyon": 4,
        "zorluk": "Orta",
        "aciklama": "Baharatlı tavuk, yoğurtlu sos ve renkli sebzelerle hazırlanan keyifli taco tabağı.",
        "yapilis": (
            "1. Tavukları baharatlayıp tavada kızartın.\n"
            "2. Tortillaları hafifçe ısıtın.\n"
            "3. Yoğurt, lime ve sarımsakla sos hazırlayın.\n"
            "4. Tavuk, marul ve mor lahana ile tacoları doldurup servis edin."
        ),
        "malzemeler": [
            ("Tavuk Göğsü", "500", "Gram"),
            ("Mini Tortilla", "8", "Adet"),
            ("Süzme Yoğurt", "4", "Yemek Kaşığı"),
            ("Mor Lahana", "1", "Kase"),
        ],
        "puan": 5,
        "yorum": "Atıştırmalık kategorisini tek başına güçlendiriyor.",
        "sunum": "Tahta servis tahtasında lime dilimleri ve acı sos eşliğinde servis edin.",
        "yorumlar": [
            ("asya@menu.com", 5, "Parti sofrasında en hızlı biten tarif bu oldu."),
            ("emir@menu.com", 4, "Yoğurtlu sos ferahlık kattı, dengesi çok iyi."),
        ],
    },
    {
        "ad": "Ispanaklı Kiş",
        "kategori": "Hamur İşi",
        "sure": 55,
        "porsiyon": 6,
        "zorluk": "Orta",
        "aciklama": "Kıtır tabanlı, peynirli ve ıspanaklı fırın kiş tarifi.",
        "yapilis": (
            "1. Hamuru kalıba yayıp ön pişirme yapın.\n"
            "2. Ispanağı soteleyin ve beyaz peynirle karıştırın.\n"
            "3. Yumurta ve krema karışımını ekleyin.\n"
            "4. Üzeri kızarana kadar fırında pişirin."
        ),
        "malzemeler": [
            ("Kiş Hamuru", "1", "Adet"),
            ("Ispanak", "300", "Gram"),
            ("Beyaz Peynir", "120", "Gram"),
            ("Yumurta", "3", "Adet"),
        ],
        "puan": 4,
        "yorum": "Çay saatine güçlü bir seçenek ekliyor.",
        "sunum": "Ilık dilimler halinde, yanında yeşil salata ile servis edin.",
        "yorumlar": [
            ("zeynep@menu.com", 5, "Misafir geldiğinde çok kurtarıcı bir tarif."),
            ("derya@menu.com", 4, "Tabanı kıtır kaldı, iç harcı da dengeliydi."),
        ],
    },
    {
        "ad": "Fırın Sütlaç",
        "kategori": "Tatlı",
        "sure": 50,
        "porsiyon": 5,
        "zorluk": "Kolay",
        "aciklama": "Üzeri hafif kızarmış, klasik ama her zaman sevilen ev yapımı sütlaç.",
        "yapilis": (
            "1. Pirinci haşlayın.\n"
            "2. Süt ve şekeri ekleyip koyulaşana kadar pişirin.\n"
            "3. Nişastayla kıvam verin.\n"
            "4. Kaselere pay edip fırında üzerini kızartın."
        ),
        "malzemeler": [
            ("Pirinç", "1", "Çay Bardağı"),
            ("Süt", "1", "Litre"),
            ("Toz Şeker", "1", "Su Bardağı"),
            ("Nişasta", "2", "Yemek Kaşığı"),
        ],
        "puan": 5,
        "yorum": "Tatlı bölümünü daha tanıdık ve sıcak bir hale getiriyor.",
        "sunum": "Tarçın ve fındık kırığı ile toprak kaselerde servis edin.",
        "yorumlar": [
            ("asya@menu.com", 5, "Tam anne usulü olmuş, kıvamı çok başarılı."),
            ("emir@menu.com", 5, "Yanık üst tabaka çok iyi bir kontrast verdi."),
        ],
    },
    {
        "ad": "Mercimek Köftesi",
        "kategori": "Aperatif",
        "sure": 25,
        "porsiyon": 6,
        "zorluk": "Kolay",
        "aciklama": "Çay saatlerinin vazgeçilmezi, bol yeşillikli ve dengeli mercimek köftesi.",
        "yapilis": (
            "1. Kırmızı mercimeği haşlayın.\n"
            "2. İnce bulgurla birleştirip demlendirin.\n"
            "3. Soğanlı salçalı harcı ekleyin.\n"
            "4. Yeşillikleri ilave edip şekil verin."
        ),
        "malzemeler": [
            ("Kırmızı Mercimek", "1", "Su Bardağı"),
            ("İnce Bulgur", "1.5", "Su Bardağı"),
            ("Taze Soğan", "4", "Dal"),
            ("Marul", "1", "Adet"),
        ],
        "puan": 4,
        "yorum": "Koleksiyona klasik bir ev lezzeti ekliyor.",
        "sunum": "Marul yaprakları üzerinde limon dilimleriyle servis edin.",
        "yorumlar": [
            ("zeynep@menu.com", 4, "Kısır sevenler için de çok güvenli bir seçenek."),
            ("derya@menu.com", 5, "Yeşillik oranı çok yerinde, taze bir lezzet oldu."),
        ],
    },
]

ORNEK_KULLANICILAR = [
    ("Misafir", "Tadim", "misafir@menu.com", "1234", "Uygulamayi hizlica gezmek isteyen ziyaretci profili."),
    ("Asya", "Kaya", "asya@menu.com", "1234", "Tatlı ve kahvaltı tariflerini sever."),
    ("Emir", "Demir", "emir@menu.com", "1234", "Ana yemek ve atıştırmalık avcısı."),
    ("Zeynep", "Acar", "zeynep@menu.com", "1234", "Ev mutfağı ve çorba tarifleri toplar."),
    ("Derya", "Tan", "derya@menu.com", "1234", "Ferah salata ve içecek tarifleri dener."),
]

HAFTA_GUNLERI = [
    ("Pazartesi", "Haftaya dengeli bir baslangic yap"),
    ("Sali", "Tempoyu koruyan pratik secim"),
    ("Carsamba", "Hafta ortasina guclu tabak"),
    ("Persembe", "Biraz daha rafine sunum zamani"),
    ("Cuma", "Keyifli kapanis aksami"),
    ("Cumartesi", "Misafirlik veya uzun sofra gunu"),
    ("Pazar", "Rahat ve sicak aile menusu"),
]

PLAN_OGUNLERI = ["Kahvalti", "Ogle", "Aksam", "Tatli Molasi", "Serin Mola"]


# ══════════════════════════════════════════════════════════════════
#  GLOBAL AKTİVİTE KAYDI (son yapılanlar listesi)
# ══════════════════════════════════════════════════════════════════
AKTIVITE = []

def log(mesaj: str, renk: str = None):
    """Aktivite günlüğüne yeni kayıt ekler (en çok 30 kayıt tutulur)."""
    AKTIVITE.insert(0, {
        "mesaj": mesaj,
        "zaman": datetime.now().strftime("%H:%M"),
        "renk": renk or C.TEXT2
    })
    if len(AKTIVITE) > 30:
        AKTIVITE.pop()


# ══════════════════════════════════════════════════════════════════
#  YARDIMCI ÜRETİCİ FONKSİYONLAR — Tutarlı stilde widget'lar
# ══════════════════════════════════════════════════════════════════

def btn_primary(metin: str, genislik: int = None, yukseklik: int = 42) -> QPushButton:
    """Amber altın dolgu - ana eylem butonu."""
    b = QPushButton(metin)
    b.setCursor(Qt.PointingHandCursor)
    b.setFixedHeight(yukseklik)
    if genislik:
        b.setFixedWidth(genislik)
    b.setStyleSheet(
        f"QPushButton{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        f"stop:0 {C.GOLD3},stop:1 {C.GOLD});color:#1a0f06;border:none;"
        f"border-radius:8px;font-size:13px;font-weight:bold;padding:0 18px;"
        f"letter-spacing:1px;outline:none;}}"
        f"QPushButton:hover{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
        f"stop:0 {C.GOLD},stop:1 {C.GOLD2});}}"
        f"QPushButton:focus{{outline:none;}}"
    )
    return b


def btn_ghost(metin: str, yukseklik: int = 38) -> QPushButton:
    """Saydam/çerçeveli ikincil buton."""
    b = QPushButton(metin)
    b.setCursor(Qt.PointingHandCursor)
    b.setFixedHeight(yukseklik)
    b.setStyleSheet(
        f"QPushButton{{background:transparent;color:{C.TEXT2};"
        f"border:1px solid {C.BORDER2};border-radius:8px;"
        f"font-size:12px;font-weight:bold;padding:0 16px;letter-spacing:1px;outline:none;}}"
        f"QPushButton:hover{{background:{C.CARD2};color:{C.GOLD2};"
        f"border-color:{C.GOLD3};}}"
        f"QPushButton:focus{{outline:none;}}"
    )
    return b


def btn_danger(metin: str) -> QPushButton:
    """Tehlikeli işlemler için şarap rengi buton."""
    b = QPushButton(metin)
    b.setCursor(Qt.PointingHandCursor)
    b.setFixedHeight(36)
    b.setStyleSheet(
        f"QPushButton{{background:transparent;color:{C.WINE2};"
        f"border:1px solid {C.WINE}40;border-radius:8px;"
        f"font-size:11px;font-weight:bold;padding:0 14px;outline:none;}}"
        f"QPushButton:hover{{background:{C.WINE}15;border-color:{C.WINE2};}}"
        f"QPushButton:focus{{outline:none;}}"
    )
    return b


def btn_renkli(metin: str, renk: str, yukseklik: int = 32) -> QPushButton:
    """Özelleştirilmiş renkli mini buton (kategori/filtre için)."""
    b = QPushButton(metin)
    b.setCursor(Qt.PointingHandCursor)
    b.setFixedHeight(yukseklik)
    b.setStyleSheet(
        f"QPushButton{{background:{renk}18;color:{renk};"
        f"border:1px solid {renk}35;border-radius:7px;"
        f"font-size:11px;font-weight:bold;padding:0 14px;outline:none;}}"
        f"QPushButton:hover{{background:{renk}28;}}"
        f"QPushButton:focus{{outline:none;}}"
    )
    return b


def etiket_baslik(metin: str, boyut: int = 22) -> QLabel:
    """Büyük başlık (serif tarzı)."""
    e = QLabel(metin)
    e.setStyleSheet(
        f"font-size:{boyut}px;font-weight:bold;color:{C.TEXT};"
        f"letter-spacing:-0.5px;"
    )
    return e


def etiket_kucuk(metin: str, renk: str = None) -> QLabel:
    """Küçük ikincil etiket (büyük harf + boşluklu)."""
    e = QLabel(metin.upper())
    e.setStyleSheet(
        f"font-size:9px;color:{renk or C.GOLD3};font-weight:bold;"
        f"letter-spacing:3px;"
    )
    return e


def form_input(placeholder: str = "", sifre: bool = False) -> QLineEdit:
    """Form alanları için tutarlı metin girişi."""
    le = QLineEdit()
    le.setPlaceholderText(placeholder)
    if sifre:
        le.setEchoMode(QLineEdit.Password)
    le.setFixedHeight(40)
    le.setStyleSheet(
        f"QLineEdit{{background:{C.BG};color:{C.TEXT};"
        f"border:1px solid {C.BORDER2};border-radius:8px;"
        f"padding:0 14px;font-size:13px;}}"
        f"QLineEdit:focus{{border-color:{C.GOLD};}}"
    )
    return le


def ayrac(dikey: bool = False) -> QFrame:
    """Ince çizgi ayracı."""
    f = QFrame()
    if dikey:
        f.setFixedWidth(1)
        f.setFrameShape(QFrame.VLine)
    else:
        f.setFixedHeight(1)
        f.setFrameShape(QFrame.HLine)
    f.setStyleSheet(f"background:{C.BORDER};border:none;")
    return f


# ══════════════════════════════════════════════════════════════════
#  ÖZEL WIDGET 1: TOAST BİLDİRİMİ
# ══════════════════════════════════════════════════════════════════
class Toast(QLabel):
    """
    Ekranın sağ alt köşesinde 3 saniye boyunca gösterilen bildirim.
    Başarı (yeşil), hata (şarap), bilgi (amber) olmak üzere üç türü vardır.
    """
    def __init__(self, ebeveyn, metin: str, tur: str = "basari"):
        super().__init__(ebeveyn)
        renk = {"basari": C.SAGE, "hata": C.WINE2, "bilgi": C.GOLD}.get(tur, C.GOLD)
        self.setText(metin)
        self.setStyleSheet(
            f"background:{C.CARD2};color:{renk};"
            f"border:none;border-radius:10px;"
            f"padding:14px 22px;font-size:12px;font-weight:bold;letter-spacing:0.5px;"
        )
        self.adjustSize()
        # Ana pencerenin sağ alt köşesine yerleştir
        x = ebeveyn.width() - self.width() - 30
        y = ebeveyn.height() - self.height() - 30
        self.move(x, y)
        self.show()
        QTimer.singleShot(2800, self.deleteLater)


# ══════════════════════════════════════════════════════════════════
#  ÖZEL WIDGET 2: HALKA GRAFİK (Donut Chart)
#  Kategori dağılımını dairesel dilimler halinde gösterir.
# ══════════════════════════════════════════════════════════════════
class HalkaGrafik(QWidget):
    """
    Kategori dağılımı için animasyonlu halka grafik.
    Her dilim bir kategoriyi temsil eder, rengi KAT_RENK'ten gelir.
    """
    def __init__(self, veri: dict = None):
        super().__init__()
        self.veri = veri or {}
        self.ilerleme = 0.0     # 0'dan 1'e animasyon değeri
        self.setMinimumSize(220, 220)

        # Açılış animasyonu
        self.zamanlayici = QTimer(self)
        self.zamanlayici.timeout.connect(self._anim)
        self.zamanlayici.start(16)    # ~60 FPS

    def _anim(self):
        """Her karede ilerleme değerini yumuşakça 1'e yaklaştırır."""
        self.ilerleme = min(1.0, self.ilerleme + 0.035)
        self.update()
        if self.ilerleme >= 1.0:
            self.zamanlayici.stop()

    def veri_guncelle(self, yeni_veri: dict):
        """Verileri yeniler ve animasyonu baştan başlatır."""
        self.veri = yeni_veri
        self.ilerleme = 0.0
        self.zamanlayici.start(16)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        boyut = min(w, h) - 30
        x, y = (w - boyut) // 2, (h - boyut) // 2
        kalinlik = 24

        # Zemin halkası
        pen = QPen(QColor(C.CARD2), kalinlik, Qt.SolidLine, Qt.RoundCap)
        p.setPen(pen)
        p.drawArc(x, y, boyut, boyut, 0, 360 * 16)

        toplam = sum(self.veri.values()) if self.veri else 0
        if toplam == 0:
            # Boş durumda ortaya bilgi yaz
            p.setPen(QColor(C.TEXT3))
            p.setFont(QFont("Segoe UI", 9, QFont.Bold))
            p.drawText(self.rect(), Qt.AlignCenter, "VERİ YOK")
            return

        # Dilimleri çiz (saat 12'den başla, saat yönünde)
        baslangic = 90 * 16     # Qt: 1/16 derece birim
        for kategori, deger in self.veri.items():
            oran = (deger / toplam) * self.ilerleme
            uzanti = int(-oran * 360 * 16)     # Saat yönü: negatif
            renk = QColor(KAT_RENK.get(kategori, C.GOLD))
            pen = QPen(renk, kalinlik, Qt.SolidLine, Qt.RoundCap)
            p.setPen(pen)
            p.drawArc(x, y, boyut, boyut, baslangic, uzanti)
            baslangic += uzanti

        # Ortadaki bilgi (toplam sayı)
        p.setPen(QColor(C.TEXT))
        p.setFont(QFont("Georgia", 26, QFont.Bold))
        p.drawText(self.rect().adjusted(0, -12, 0, -12),
                   Qt.AlignCenter, str(toplam))
        p.setPen(QColor(C.GOLD3))
        p.setFont(QFont("Segoe UI", 8, QFont.Bold))
        p.drawText(self.rect().adjusted(0, 26, 0, 26),
                   Qt.AlignCenter, "TOPLAM TARİF")


# ══════════════════════════════════════════════════════════════════
#  ÖZEL WIDGET 3: ÇUBUK GRAFİK (Bar Chart)
#  Zorluk dağılımı veya diğer kategorik veriler için.
# ══════════════════════════════════════════════════════════════════
class CubukGrafik(QWidget):
    """Dikey çubuk grafik — her kategori için bir çubuk, değer üstte yazılır."""
    def __init__(self, veri: dict = None):
        super().__init__()
        self.veri = veri or {}
        self.ilerleme = 0.0
        self.setMinimumHeight(200)
        self.zamanlayici = QTimer(self)
        self.zamanlayici.timeout.connect(self._anim)
        self.zamanlayici.start(16)

    def _anim(self):
        self.ilerleme = min(1.0, self.ilerleme + 0.04)
        self.update()
        if self.ilerleme >= 1.0:
            self.zamanlayici.stop()

    def veri_guncelle(self, yeni_veri: dict):
        self.veri = yeni_veri
        self.ilerleme = 0.0
        self.zamanlayici.start(16)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        if not self.veri:
            p.setPen(QColor(C.TEXT3))
            p.setFont(QFont("Segoe UI", 9, QFont.Bold))
            p.drawText(self.rect(), Qt.AlignCenter, "VERİ YOK")
            return

        w, h = self.width(), self.height()
        pad = 30
        alt = h - pad
        ust = 30
        mevcut_gen = w - 2 * pad
        cubuk_sayi = len(self.veri)
        aralik = mevcut_gen / cubuk_sayi if cubuk_sayi else 1
        cubuk_gen = min(aralik * 0.55, 40)

        maks = max(self.veri.values()) if self.veri else 1

        renkler = list(KAT_RENK.values())
        for i, (etiket, deger) in enumerate(self.veri.items()):
            # Kategori bazlı renk; yoksa dönen bir altın tonu
            renk = QColor(KAT_RENK.get(etiket, renkler[i % len(renkler)]))
            x = pad + i * aralik + (aralik - cubuk_gen) / 2
            yukseklik = (deger / maks) * (alt - ust) * self.ilerleme
            y = alt - yukseklik

            # Gradyan dolgulu çubuk
            grad = QLinearGradient(0, y, 0, alt)
            grad.setColorAt(0, renk)
            grad.setColorAt(1, QColor(renk.red() // 2, renk.green() // 2,
                                      renk.blue() // 2))
            p.setBrush(QBrush(grad))
            p.setPen(Qt.NoPen)
            p.drawRoundedRect(QRect(int(x), int(y), int(cubuk_gen),
                                    int(yukseklik)), 5, 5)

            # Üstte değer
            if self.ilerleme > 0.7:
                p.setPen(QColor(C.TEXT))
                p.setFont(QFont("Segoe UI", 10, QFont.Bold))
                p.drawText(QRect(int(x - 10), int(y - 22),
                                 int(cubuk_gen + 20), 20),
                           Qt.AlignCenter, str(deger))

            # Alt etiket
            p.setPen(QColor(C.TEXT2))
            p.setFont(QFont("Segoe UI", 8))
            p.drawText(QRect(int(x - aralik * 0.2), int(alt + 6),
                             int(cubuk_gen + aralik * 0.4), 18),
                       Qt.AlignCenter, etiket[:12])


# ══════════════════════════════════════════════════════════════════
#  ÖZEL WIDGET 4: YILDIZ DEĞERLENDİRME (Interactive)
#  1-5 yıldız arası puan veren, hover'da ön-izleme yapan widget.
# ══════════════════════════════════════════════════════════════════
class YildizDerecelendirme(QWidget):
    """
    Tıklanabilir 5 yıldız. Kullanıcı hover ile ön izleme görür,
    tıkladığında `puan_secildi` sinyali tetiklenir.
    """
    puan_secildi = pyqtSignal(int)

    def __init__(self, mevcut_puan: float = 0, salt_okunur: bool = False,
                 boyut: int = 28):
        super().__init__()
        self.puan = mevcut_puan
        self.hover_puan = 0
        self.salt_okunur = salt_okunur
        self.yildiz_boyutu = boyut
        self.setFixedHeight(boyut + 8)
        self.setFixedWidth(5 * (boyut + 4) + 4)
        if not salt_okunur:
            self.setCursor(Qt.PointingHandCursor)
            self.setMouseTracking(True)

    def mouseMoveEvent(self, e):
        if self.salt_okunur:
            return
        self.hover_puan = self._yildiz_index(e.x())
        self.update()

    def leaveEvent(self, _):
        self.hover_puan = 0
        self.update()

    def mousePressEvent(self, e):
        if self.salt_okunur:
            return
        secim = self._yildiz_index(e.x())
        if 1 <= secim <= 5:
            self.puan = secim
            self.puan_secildi.emit(secim)
            self.update()

    def _yildiz_index(self, x: int) -> int:
        """x piksel konumundan hangi yıldızın üzerinde olduğumuzu hesaplar."""
        genislik_per = (self.yildiz_boyutu + 4)
        idx = x // genislik_per + 1
        return max(1, min(5, idx))

    def puan_ayarla(self, yeni_puan: float):
        self.puan = yeni_puan
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        gosterilecek = self.hover_puan if self.hover_puan > 0 else self.puan

        for i in range(5):
            x = i * (self.yildiz_boyutu + 4) + 2
            y = 4
            merkez = QPointF(x + self.yildiz_boyutu / 2,
                             y + self.yildiz_boyutu / 2)

            # Aktif mi? (tamamen dolu, kısmi dolu veya boş)
            if (i + 1) <= gosterilecek:
                renk = QColor(C.GOLD2 if self.hover_puan else C.GOLD)
                dolgu = True
            elif (i + 1) - gosterilecek < 1 and (i + 1) - gosterilecek > 0:
                # Yarım yıldız (sadece salt okunur modda)
                renk = QColor(C.GOLD)
                dolgu = True
            else:
                renk = QColor(C.BORDER2)
                dolgu = False

            # 5 köşeli yıldız çiz
            yildiz = self._yildiz_yolu(merkez, self.yildiz_boyutu / 2)
            if dolgu:
                p.setBrush(QBrush(renk))
                p.setPen(QPen(renk, 1))
            else:
                p.setBrush(Qt.NoBrush)
                p.setPen(QPen(renk, 1.5))
            p.drawPath(yildiz)

    def _yildiz_yolu(self, merkez: QPointF, yaricap: float) -> QPainterPath:
        """5 köşeli bir yıldız yolu oluşturur (klasik yıldız şekli)."""
        yol = QPainterPath()
        ic_yaricap = yaricap * 0.4
        for i in range(10):
            aci = -math.pi / 2 + i * math.pi / 5
            r = yaricap if i % 2 == 0 else ic_yaricap
            x = merkez.x() + r * math.cos(aci)
            y = merkez.y() + r * math.sin(aci)
            if i == 0:
                yol.moveTo(x, y)
            else:
                yol.lineTo(x, y)
        yol.closeSubpath()
        return yol


# ══════════════════════════════════════════════════════════════════
#  ÖZEL WIDGET 5: İSTATİSTİK KARTI (Stat Card)
# ══════════════════════════════════════════════════════════════════
class StatKart(QFrame):
    """
    Sayı + etiket gösteren kart. Üstte ince renk şeridi, altta
    büyük değer, en altta etiket.
    """
    def __init__(self, etiket: str, deger: str, renk: str, ikon: str = "●"):
        super().__init__()
        self.setFixedHeight(130)
        self.renk = renk
        self.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;"
            f"border-radius:14px;}}"
        )

        # Üstteki renk şeridi manuel çizilecek (paintEvent)
        self.etiket_metin = etiket
        self.deger_metin = deger
        self.ikon_metin = ikon

        l = QVBoxLayout(self)
        l.setContentsMargins(22, 20, 22, 20)
        l.setSpacing(8)

        # İkon + etiket satırı
        ust = QHBoxLayout()
        ust.setSpacing(10)
        ic = QLabel(ikon)
        ic.setStyleSheet(
            f"font-size:16px;color:{renk};background:{renk}18;"
            f"border-radius:8px;padding:6px 10px;"
        )
        tl = QLabel(etiket.upper())
        tl.setStyleSheet(
            f"font-size:9px;color:{C.TEXT3};font-weight:bold;"
            f"letter-spacing:2.5px;background:transparent;"
        )
        ust.addWidget(ic)
        ust.addWidget(tl)
        ust.addStretch()
        l.addLayout(ust)
        l.addStretch()

        # Büyük değer
        self.deger_lbl = QLabel(deger)
        self.deger_lbl.setStyleSheet(
            f"font-size:34px;font-weight:bold;color:{C.TEXT};"
            f"background:transparent;letter-spacing:-1px;"
            f"font-family:Georgia;"
        )
        l.addWidget(self.deger_lbl)

    def deger_guncelle(self, yeni_deger: str):
        self.deger_lbl.setText(yeni_deger)

    def paintEvent(self, e):
        super().paintEvent(e)
        # Üstte 3 piksellik renkli şerit (kartın tepesine)
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)
        grad = QLinearGradient(0, 0, self.width(), 0)
        grad.setColorAt(0, QColor(self.renk))
        grad.setColorAt(1, QColor(self.renk).lighter(130))
        p.setBrush(QBrush(grad))
        p.setPen(Qt.NoPen)
        yol = QPainterPath()
        yol.addRoundedRect(0, 0, self.width(), 4, 2, 2)
        p.drawPath(yol)


# ══════════════════════════════════════════════════════════════════
#  ÖZEL WIDGET 6: ŞEF AMBLEMİ (Custom Logo Illustration)
#  Hoşgeldin ekranında gösterilen çatal-bıçak-tabak kompozisyonu.
# ══════════════════════════════════════════════════════════════════
class SefAmblemi(QWidget):
    """
    El çizimi 'elit restoran' amblemi: tabak + çaprazlanmış çatal-bıçak +
    dekoratif daire çerçeve. Altın çizgili, hafif animasyonlu.
    """
    def __init__(self):
        super().__init__()
        self.setMinimumSize(200, 200)
        self.setMaximumSize(240, 240)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.faz = 0.0
        self.zamanlayici = QTimer(self)
        self.zamanlayici.timeout.connect(self._tick)
        self.zamanlayici.start(30)

    def _tick(self):
        """Hafif dönüş animasyonu için faz değişkenini günceller."""
        self.faz += 0.012
        if self.faz > math.tau:
            self.faz -= math.tau
        self.update()

    def paintEvent(self, _):
        p = QPainter(self)
        p.setRenderHint(QPainter.Antialiasing)

        w, h = self.width(), self.height()
        cx, cy = w / 2, h / 2
        yaricap = min(w, h) / 2 - 20

        # ─── Arka plan yumuşak glow ───
        rad = QRadialGradient(cx, cy, yaricap * 1.2)
        rad.setColorAt(0, QColor(212, 165, 116, 30))      # GOLD @ 30/255
        rad.setColorAt(1, QColor(212, 165, 116, 0))
        p.setBrush(QBrush(rad))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(cx, cy), yaricap * 1.04, yaricap * 1.04)

        # ─── Dış dekoratif halka (ince, kesik) ───
        pen = QPen(QColor(C.GOLD), 1.2)
        pen.setStyle(Qt.DashLine)
        p.setPen(pen)
        p.setBrush(Qt.NoBrush)
        p.drawEllipse(QPointF(cx, cy), yaricap - 2, yaricap - 2)

        # ─── İç dekoratif halka (çift çizgi) ───
        pen = QPen(QColor(C.GOLD2), 1.8)
        p.setPen(pen)
        p.drawEllipse(QPointF(cx, cy), yaricap - 12, yaricap - 12)
        pen = QPen(QColor(C.GOLD3), 1)
        p.setPen(pen)
        p.drawEllipse(QPointF(cx, cy), yaricap - 18, yaricap - 18)

        # ─── Dönerek yanıp sönen ışık noktaları (8 adet) ───
        for i in range(8):
            aci = i * math.tau / 8 + self.faz
            x = cx + (yaricap - 8) * math.cos(aci)
            y = cy + (yaricap - 8) * math.sin(aci)
            parlaklik = (math.sin(self.faz * 3 + i) + 1) / 2     # 0..1 arası
            alpha = int(80 + parlaklik * 140)
            p.setBrush(QBrush(QColor(232, 192, 136, alpha)))
            p.setPen(Qt.NoPen)
            p.drawEllipse(QPointF(x, y), 3.5, 3.5)

        # ─── Tabak (iç içe iki daire) ───
        tabak_r = yaricap - 34
        pen = QPen(QColor(C.GOLD2), 2.5)
        p.setPen(pen)
        p.drawEllipse(QPointF(cx, cy), tabak_r, tabak_r)
        pen = QPen(QColor(C.GOLD3), 1.2)
        p.setPen(pen)
        p.drawEllipse(QPointF(cx, cy), tabak_r - 12, tabak_r - 12)

        # ─── Çaprazlanmış çatal ve bıçak ───
        # Not: Sap ile ağız/dişler, ortadaki M rozetinin DIŞINDAN başlar.
        # Sap rozetten aşağıya (+y), ağız/dişler rozetten yukarıya (-y) uzanır.
        p.save()
        p.translate(cx, cy)

        sap_baslangic = 22              # M rozeti 16px → 22'den sonra güvenli
        sap_bitis = int(tabak_r - 26)   # tabak kenarına yaklaşmadan dur
        agiz_baslangic = -22            # rozet dışından yukarı
        agiz_ucu = int(-tabak_r + 26)   # tabak kenarına yaklaşmadan dur

        # ─── BIÇAK — -45° (sol-alttan sağ-üste) ───
        p.save()
        p.rotate(-45)

        # Sap: kalın çizgi
        pen = QPen(QColor(C.GOLD2), 3.5)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.drawLine(0, sap_baslangic, 0, sap_bitis)

        # Sap topuzu (sap ucunda küçük altın düğme)
        p.setBrush(QBrush(QColor(C.GOLD)))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(0, sap_bitis), 3.2, 3.2)

        # Bıçak ağzı: simetrik, yaprak biçimli — asimetrik tip yok
        p.setBrush(QBrush(QColor(C.GOLD2)))
        p.setPen(Qt.NoPen)
        agiz_yol = QPainterPath()
        agiz_yol.moveTo(-3, agiz_baslangic)
        agiz_yol.lineTo(3, agiz_baslangic)
        agiz_yol.lineTo(3, agiz_baslangic + (agiz_ucu - agiz_baslangic) * 0.35)
        agiz_yol.lineTo(0, agiz_ucu)
        agiz_yol.lineTo(-3, agiz_baslangic + (agiz_ucu - agiz_baslangic) * 0.35)
        agiz_yol.closeSubpath()
        p.drawPath(agiz_yol)

        # Ağız üzerinde ince parlama çizgisi
        pen = QPen(QColor(C.GOLD), 0.8)
        p.setPen(pen)
        p.drawLine(0, agiz_baslangic + 3, 0, agiz_ucu - 4)
        p.restore()

        # ─── ÇATAL — +45° (sağ-alttan sol-üste) ───
        p.save()
        p.rotate(45)

        # Sap
        pen = QPen(QColor(C.GOLD2), 3.5)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        p.drawLine(0, sap_baslangic, 0, sap_bitis)

        # Sap topuzu
        p.setBrush(QBrush(QColor(C.GOLD)))
        p.setPen(Qt.NoPen)
        p.drawEllipse(QPointF(0, sap_bitis), 3.2, 3.2)

        # Çatal boynu (sapı dişlere bağlayan ince dörtgen)
        boyun_alt = -18                     # rozet dışında
        boyun_ust = agiz_baslangic - 4
        p.setBrush(QBrush(QColor(C.GOLD2)))
        p.setPen(Qt.NoPen)
        boyun = QPolygonF([
            QPointF(-4, boyun_alt),
            QPointF(4, boyun_alt),
            QPointF(4.5, boyun_ust),
            QPointF(-4.5, boyun_ust),
        ])
        p.drawPolygon(boyun)

        # 4 diş — simetrik, sivri uçlu
        pen = QPen(QColor(C.GOLD2), 2.2)
        pen.setCapStyle(Qt.RoundCap)
        p.setPen(pen)
        for dx in (-5, -2, 2, 5):
            p.drawLine(dx, boyun_ust, dx, agiz_ucu + 2)
        p.restore()

        p.restore()

        # ─── Merkez amblemi (küçük altın kare + "M") ───
        p.setBrush(QBrush(QColor(C.GOLD)))
        p.setPen(Qt.NoPen)
        merkez = QPainterPath()
        merkez.addRoundedRect(int(cx - 16), int(cy - 16), 32, 32, 6, 6)
        p.drawPath(merkez)
        p.setPen(QColor("#1a0f06"))
        p.setFont(QFont("Georgia", 18, QFont.Bold))
        p.drawText(QRect(int(cx - 16), int(cy - 16), 32, 32),
                   Qt.AlignCenter, "M")


# ══════════════════════════════════════════════════════════════════
#  ÖZEL WIDGET 7: CANLI SAAT
# ══════════════════════════════════════════════════════════════════
class CanliSaat(QLabel):
    """Her saniye güncellenen dijital saat + tarih."""
    def __init__(self):
        super().__init__()
        self.setStyleSheet(
            f"color:{C.TEXT2};font-size:12px;font-weight:bold;"
            f"letter-spacing:2px;font-family:Georgia;"
        )
        self.zamanlayici = QTimer(self)
        self.zamanlayici.timeout.connect(self._guncelle)
        self.zamanlayici.start(1000)
        self._guncelle()

    def _guncelle(self):
        simdi = datetime.now()
        self.setText(simdi.strftime("  %H:%M  ·  %d %b %Y").upper())

class MutfakZamanlayici(QWidget):
    def __init__(self):
        super().__init__()
        self.kalan_saniye = 0
        self.calisiyor = False
        
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._geri_sayim)
        
        l = QHBoxLayout(self)
        l.setContentsMargins(0, 0, 0, 0)
        l.setSpacing(10)
        
        self.dk_spin = QSpinBox()
        self.dk_spin.setRange(1, 180)
        self.dk_spin.setValue(30)
        self.dk_spin.setSuffix(" dk")
        self.dk_spin.setFixedHeight(30)
        self.dk_spin.setStyleSheet(
            f"QSpinBox{{background:transparent;color:{C.TEXT};border:1px solid {C.BORDER2};border-radius:4px;padding:2px;font-size:11px;}}"
        )
        
        self.zaman_lbl = QLabel("00:00")
        self.zaman_lbl.setStyleSheet(f"color:{C.GOLD};font-size:14px;font-weight:bold;font-family:Georgia;")
        self.zaman_lbl.hide()
        
        self.basla_btn = QPushButton("▶")
        self.basla_btn.setFixedSize(30, 30)
        self.basla_btn.setCursor(Qt.PointingHandCursor)
        self.basla_btn.setStyleSheet(f"QPushButton{{background:{C.CARD2};color:{C.TEXT};border:1px solid {C.BORDER};border-radius:4px;}} QPushButton:hover{{background:{C.GOLD};color:#000;}}")
        self.basla_btn.clicked.connect(self._basla_dur)
        
        ikon = QLabel("⏱")
        ikon.setStyleSheet(f"color:{C.TEXT3};font-size:14px;")
        l.addWidget(ikon)
        l.addWidget(self.dk_spin)
        l.addWidget(self.zaman_lbl)
        l.addWidget(self.basla_btn)
        
    def _basla_dur(self):
        if self.calisiyor:
            self.timer.stop()
            self.calisiyor = False
            self.basla_btn.setText("▶")
            self.dk_spin.show()
            self.zaman_lbl.hide()
        else:
            if self.kalan_saniye <= 0:
                self.kalan_saniye = self.dk_spin.value() * 60
            self.dk_spin.hide()
            self.zaman_lbl.show()
            self.calisiyor = True
            self.basla_btn.setText("⏹")
            self._goster()
            self.timer.start(1000)
            
    def _geri_sayim(self):
        self.kalan_saniye -= 1
        self._goster()
        if self.kalan_saniye <= 0:
            self.timer.stop()
            self.calisiyor = False
            self.kalan_saniye = 0
            self.basla_btn.setText("▶")
            self.dk_spin.show()
            self.zaman_lbl.hide()
            # Parent window toast
            if hasattr(self.window(), "_toast_goster"):
                self.window()._toast_goster("Süre doldu! Yemeğiniz hazır olabilir.", "bilgi")
            else:
                Toast(self.window(), "Süre doldu! Yemeğiniz hazır olabilir.", "bilgi")
            
    def _goster(self):
        dk = self.kalan_saniye // 60
        sn = self.kalan_saniye % 60
        self.zaman_lbl.setText(f"{dk:02d}:{sn:02d}")



# ══════════════════════════════════════════════════════════════════
#  GLOBAL VERİ YÖNETİCİSİ (Singleton mantığıyla)
# ══════════════════════════════════════════════════════════════════
class VeriYoneticisi:
    """
    Tüm uygulama boyunca tek bir veritabanı bağlantısı kullanılır.
    Bu sınıf o bağlantıyı ve yönetici nesneleri tutar.
    """
    def __init__(self):
        self.db = Veritabani("tarif_platformu.db")
        self.kullanici = Kullanici(self.db)
        self.tarif = Tarif(self.db)
        self.malzeme = Malzeme(self.db)
        self.istatistik = IstatistikYoneticisi(self.db)
        self.aktif_kullanici = None    # Giriş yapan kişi (sözlük)


# ══════════════════════════════════════════════════════════════════
#  GİRİŞ / KAYIT EKRANI
# ══════════════════════════════════════════════════════════════════
class GirisEkrani(QWidget):
    """
    Rafine açılış ekranı: sol vitrin + sağda üç modlu giriş/kayıt kartı.
    Modlar: ÜYE GİRİŞİ, ADMİN GİRİŞİ, ÜYE KAYIT.
    """
    giris_basarili = pyqtSignal(dict)

    def __init__(self, veri: VeriYoneticisi):
        super().__init__()
        self.veri = veri
        self.aktif_mod = "uye"   # "uye" | "admin" | "kayit"
        self.setStyleSheet(f"background:{C.BG};")

        kok_l = QVBoxLayout(self)
        kok_l.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        scroll.setStyleSheet(
            f"QScrollArea{{background:{C.BG};border:none;}}"
            f"QScrollBar:vertical{{width:8px;background:transparent;}}"
            f"QScrollBar::handle:vertical{{background:{C.BORDER2};border-radius:4px;}}"
        )
        kok_l.addWidget(scroll)

        govde = QWidget()
        govde.setStyleSheet(f"background:{C.BG};")
        scroll.setWidget(govde)

        dis = QHBoxLayout(govde)
        dis.setContentsMargins(28, 28, 28, 28)
        dis.setSpacing(20)

        # ═══ SOL PANEL: Vitrin ═══
        sol = QFrame()
        sol.setObjectName("girisSolPanel")
        sol.setMinimumWidth(640)
        sol.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        sol.setStyleSheet(
            f"QFrame#girisSolPanel{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {C.BG2},stop:0.45 {C.CARD},stop:1 {C.BG});"
            f"border:1px solid {C.BORDER};border-radius:28px;}}"
        )
        sol_l = QVBoxLayout(sol)
        sol_l.setContentsMargins(34, 30, 34, 30)
        sol_l.setSpacing(18)

        vitrin = QLabel("MENU MASTERCLASS")
        vitrin.setStyleSheet(
            f"color:{C.GOLD2};font-size:10px;font-weight:bold;letter-spacing:6px;background:transparent;"
        )
        sol_l.addWidget(vitrin)

        amblem = SefAmblemi()
        sol_l.addWidget(amblem, 0, Qt.AlignLeft)

        baslik = QLabel("Mutfaga\nsahne isigi ver.")
        baslik.setMaximumWidth(640)
        baslik.setStyleSheet(
            f"color:{C.TEXT};font-size:44px;font-weight:bold;font-family:Georgia;"
            f"line-height:50px;background:transparent;"
        )
        sol_l.addWidget(baslik)

        aciklama = QLabel(
            "Haftalik menuler, favoriler, alisveris akisi ve sunumu guclu tarif vitrini "
            "tek bir masaustu deneyiminde birlesiyor."
        )
        aciklama.setWordWrap(True)
        aciklama.setMaximumWidth(700)
        aciklama.setStyleSheet(
            f"color:{C.TEXT2};font-size:13px;line-height:22px;background:transparent;"
        )
        sol_l.addWidget(aciklama)

        ist_sat = QHBoxLayout()
        ist_sat.setSpacing(12)
        self.ac_stat_tarif = StatKart("Tarif", "0", C.GOLD, "D")
        self.ac_stat_puan = StatKart("Ortalama", "0.0", C.COPPER, "*")
        self.ac_stat_kullanici = StatKart("Uye", "0", C.SAGE, "U")
        ist_sat.addWidget(self.ac_stat_tarif)
        ist_sat.addWidget(self.ac_stat_puan)
        ist_sat.addWidget(self.ac_stat_kullanici)
        sol_l.addLayout(ist_sat)

        onizleme = QGridLayout()
        onizleme.setHorizontalSpacing(14)
        onizleme.setVerticalSpacing(14)
        onizleme.addWidget(self._onizleme_karti(
            "HEMEN BASLA", "Tek tikla uye ol",
            "Birkac alanla yeni bir uye hesabi ac, tariflerinle bulus.", C.GOLD
        ), 0, 0)
        onizleme.addWidget(self._onizleme_karti(
            "AKILLI AKIS", "Tariften alisverise kesintisiz gecis",
            "Planladigin gunlerin malzemelerini tek listede toparla.", C.SAGE
        ), 0, 1)
        onizleme.addWidget(self._onizleme_karti(
            "ADMIN MODU", "Tarif, kullanici ve yorumlari yonet",
            "Admin girisi ile platformdaki tum icerigi duzenleyip silme yetkisine sahipsin.", C.WINE2
        ), 1, 0, 1, 2)
        sol_l.addLayout(onizleme)
        sol_l.addStretch()

        # ═══ SAĞ PANEL: Form Kartı ═══
        sag = QFrame()
        sag.setObjectName("girisSagPanel")
        sag.setMinimumWidth(410)
        sag.setMaximumWidth(470)
        sag.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        sag.setStyleSheet(
            f"QFrame#girisSagPanel{{background:{C.CARD};border:1px solid {C.BORDER};border-radius:28px;}}"
        )
        golge = QGraphicsDropShadowEffect(self)
        golge.setBlurRadius(38)
        golge.setOffset(0, 18)
        golge.setColor(QColor(0, 0, 0, 120))
        sag.setGraphicsEffect(golge)

        sag_l = QVBoxLayout(sag)
        sag_l.setContentsMargins(28, 28, 28, 28)
        sag_l.setSpacing(12)

        self.mini_lbl = QLabel("GIRIS YAP")
        self.mini_lbl.setStyleSheet(
            f"color:{C.GOLD2};font-size:10px;font-weight:bold;letter-spacing:4px;background:transparent;"
        )
        sag_l.addWidget(self.mini_lbl)

        self.bas_lbl = QLabel("Mutfagina\nhos geldin.")
        self.bas_lbl.setWordWrap(True)
        self.bas_lbl.setStyleSheet(
            f"color:{C.TEXT};font-size:30px;font-weight:bold;font-family:Georgia;background:transparent;"
        )
        sag_l.addWidget(self.bas_lbl)

        self.alt_lbl = QLabel("Uye hesabinla giris yap ve tariflerinle bulus.")
        self.alt_lbl.setWordWrap(True)
        self.alt_lbl.setStyleSheet(
            f"color:{C.TEXT2};font-size:12px;line-height:19px;background:transparent;"
        )
        sag_l.addWidget(self.alt_lbl)

        # ─── MOD SEKMELERI ───
        sekme_kap = QFrame()
        sekme_kap.setStyleSheet(
            f"QFrame{{background:{C.BG}80;border:1px solid {C.BORDER2};border-radius:12px;}}"
        )
        sekme_l = QHBoxLayout(sekme_kap)
        sekme_l.setContentsMargins(4, 4, 4, 4)
        sekme_l.setSpacing(4)

        self.uye_sekme_btn = QPushButton("UYE")
        self.admin_sekme_btn = QPushButton("ADMIN")
        for btn in (self.uye_sekme_btn, self.admin_sekme_btn):
            btn.setCursor(Qt.PointingHandCursor)
            btn.setFixedHeight(34)
        self.uye_sekme_btn.clicked.connect(lambda: self._mod_degistir("uye"))
        self.admin_sekme_btn.clicked.connect(lambda: self._mod_degistir("admin"))
        sekme_l.addWidget(self.uye_sekme_btn, 1)
        sekme_l.addWidget(self.admin_sekme_btn, 1)
        sag_l.addWidget(sekme_kap)

        # ═══ GİRİŞ FORMU (uye/admin modunda görünür) ═══
        self.giris_form = QFrame()
        self.giris_form.setStyleSheet("QFrame{background:transparent;border:none;}")
        gf_l = QVBoxLayout(self.giris_form)
        gf_l.setContentsMargins(0, 0, 0, 0)
        gf_l.setSpacing(10)

        gf_l.addWidget(self._label_olustur("E-POSTA"))
        self.eposta_inp = self._line_edit_olustur("ornek@menu.com")
        gf_l.addWidget(self.eposta_inp)

        gf_l.addWidget(self._label_olustur("SIFRE"))
        self.sifre_inp = self._line_edit_olustur("********", sifre=True)
        self.sifre_inp.returnPressed.connect(self._giris_dene)
        gf_l.addWidget(self.sifre_inp)

        self.giris_btn = btn_primary("GIRIS YAP", genislik=None, yukseklik=46)
        self.giris_btn.clicked.connect(self._giris_dene)
        gf_l.addWidget(self.giris_btn)

        # Demo hesap paneli
        self.demo_panel = QFrame()
        self.demo_panel.setStyleSheet(
            f"QFrame{{background:{C.BG}80;border:1px dashed {C.BORDER2};border-radius:12px;}}"
        )
        demo_l = QVBoxLayout(self.demo_panel)
        demo_l.setContentsMargins(14, 10, 14, 10)
        demo_l.setSpacing(5)

        self.demo_etiket = QLabel("DEMO HESAP")
        self.demo_etiket.setStyleSheet(
            f"color:{C.GOLD2};font-size:9px;font-weight:bold;letter-spacing:3px;"
            f"background:transparent;border:none;"
        )
        demo_l.addWidget(self.demo_etiket)

        self.demo_bilgi_lbl = QLabel("")
        self.demo_bilgi_lbl.setStyleSheet(
            f"color:{C.TEXT2};font-size:10px;line-height:15px;background:transparent;border:none;"
            f"font-family:Georgia;"
        )
        self.demo_bilgi_lbl.setWordWrap(True)
        demo_l.addWidget(self.demo_bilgi_lbl)

        self.demo_doldur_btn = QPushButton("HAZIR DEMO ILE DOLDUR")
        self.demo_doldur_btn.setCursor(Qt.PointingHandCursor)
        self.demo_doldur_btn.setFixedHeight(28)
        self.demo_doldur_btn.setStyleSheet(
            f"QPushButton{{background:transparent;color:{C.GOLD};border:1px solid {C.GOLD}60;"
            f"border-radius:8px;font-size:10px;font-weight:bold;letter-spacing:2px;}}"
            f"QPushButton:hover{{background:{C.GOLD}15;border-color:{C.GOLD};}}"
        )
        self.demo_doldur_btn.clicked.connect(self._demo_doldur)
        demo_l.addWidget(self.demo_doldur_btn)
        gf_l.addWidget(self.demo_panel)

        # "Hesabın yok mu? ÜYE OL" linki (sadece üye modunda)
        self.uye_ol_link = QPushButton("Hesabin yok mu?   UYE OL  →")
        self.uye_ol_link.setCursor(Qt.PointingHandCursor)
        self.uye_ol_link.setFixedHeight(34)
        self.uye_ol_link.setStyleSheet(
            f"QPushButton{{background:transparent;color:{C.TEXT2};"
            f"border:none;font-size:11px;letter-spacing:1px;font-weight:bold;}}"
            f"QPushButton:hover{{color:{C.GOLD};}}"
        )
        self.uye_ol_link.clicked.connect(self._kayit_moduna_gec)
        gf_l.addWidget(self.uye_ol_link, 0, Qt.AlignCenter)

        sag_l.addWidget(self.giris_form)

        # ═══ KAYIT FORMU (varsayılan gizli) ═══
        self.kayit_form = QFrame()
        self.kayit_form.setStyleSheet("QFrame{background:transparent;border:none;}")
        kf_l = QVBoxLayout(self.kayit_form)
        kf_l.setContentsMargins(0, 0, 0, 0)
        kf_l.setSpacing(10)

        # Ad + Soyad yan yana
        ad_soyad_wrap = QWidget()
        ad_soyad_wrap.setStyleSheet("background:transparent;")
        as_l = QHBoxLayout(ad_soyad_wrap)
        as_l.setContentsMargins(0, 0, 0, 0)
        as_l.setSpacing(10)

        ad_col = QVBoxLayout()
        ad_col.setSpacing(5)
        ad_col.addWidget(self._label_olustur("AD"))
        self.ad_inp = self._line_edit_olustur("Adin")
        ad_col.addWidget(self.ad_inp)
        as_l.addLayout(ad_col, 1)

        soyad_col = QVBoxLayout()
        soyad_col.setSpacing(5)
        soyad_col.addWidget(self._label_olustur("SOYAD"))
        self.soyad_inp = self._line_edit_olustur("Soyadin")
        soyad_col.addWidget(self.soyad_inp)
        as_l.addLayout(soyad_col, 1)

        kf_l.addWidget(ad_soyad_wrap)

        kf_l.addWidget(self._label_olustur("E-POSTA"))
        self.kayit_eposta_inp = self._line_edit_olustur("ornek@menu.com")
        kf_l.addWidget(self.kayit_eposta_inp)

        kf_l.addWidget(self._label_olustur("SIFRE"))
        self.kayit_sifre_inp = self._line_edit_olustur("En az 4 karakter", sifre=True)
        kf_l.addWidget(self.kayit_sifre_inp)

        kf_l.addWidget(self._label_olustur("SIFRE (TEKRAR)"))
        self.sifre2_inp = self._line_edit_olustur("Sifreni tekrar gir", sifre=True)
        self.sifre2_inp.returnPressed.connect(self._kayit_ol)
        kf_l.addWidget(self.sifre2_inp)

        self.kayit_btn = btn_primary("UYE OL", genislik=None, yukseklik=46)
        self.kayit_btn.clicked.connect(self._kayit_ol)
        kf_l.addWidget(self.kayit_btn)

        # "Zaten üye misin? GİRİŞ YAP" linki
        self.giris_link = QPushButton("←  Zaten uye misin?   GIRIS YAP")
        self.giris_link.setCursor(Qt.PointingHandCursor)
        self.giris_link.setFixedHeight(34)
        self.giris_link.setStyleSheet(
            f"QPushButton{{background:transparent;color:{C.TEXT2};"
            f"border:none;font-size:11px;letter-spacing:1px;font-weight:bold;}}"
            f"QPushButton:hover{{color:{C.GOLD};}}"
        )
        self.giris_link.clicked.connect(lambda: self._mod_degistir("uye"))
        kf_l.addWidget(self.giris_link, 0, Qt.AlignCenter)

        sag_l.addWidget(self.kayit_form)
        self.kayit_form.hide()

        sag_l.addStretch()

        dis.addWidget(sol, 1)
        dis.addWidget(sag)
        dis.setStretch(0, 5)
        dis.setStretch(1, 2)

        self._giris_istatistiklerini_yenile()
        self._mod_degistir("uye")

    # ══════════════════════════════════════════════════════════════
    #  YARDIMCI WİDGET'LAR
    # ══════════════════════════════════════════════════════════════
    def _label_olustur(self, metin: str) -> QLabel:
        lbl = QLabel(metin)
        lbl.setStyleSheet(
            f"color:{C.TEXT3};font-size:9px;font-weight:bold;letter-spacing:2px;"
            f"background:transparent;border:none;"
        )
        return lbl

    def _line_edit_olustur(self, placeholder: str, sifre: bool = False) -> QLineEdit:
        inp = QLineEdit()
        inp.setPlaceholderText(placeholder)
        if sifre:
            inp.setEchoMode(QLineEdit.Password)
        inp.setFixedHeight(40)
        extra = "letter-spacing:2px;" if sifre else ""
        inp.setStyleSheet(
            f"QLineEdit{{background:{C.BG};color:{C.TEXT};border:1px solid {C.BORDER2};"
            f"border-radius:10px;padding:0 14px;font-size:13px;{extra}}}"
            f"QLineEdit:focus{{border-color:{C.GOLD};}}"
        )
        return inp

    def _onizleme_karti(self, ust_metin: str, baslik: str, alt_metin: str, renk: str) -> QFrame:
        kart = QFrame()
        kart.setObjectName("acilisOnizlemeKarti")
        kart.setStyleSheet(
            f"QFrame#acilisOnizlemeKarti{{background:{C.BG}90;border:1px solid {C.BORDER};border-radius:18px;}}"
        )
        l = QVBoxLayout(kart)
        l.setContentsMargins(18, 16, 18, 16)
        l.setSpacing(8)

        ust = QLabel(ust_metin)
        ust.setStyleSheet(
            f"color:{renk};font-size:9px;font-weight:bold;letter-spacing:3px;background:transparent;border:none;"
        )
        l.addWidget(ust)

        bas = QLabel(baslik)
        bas.setWordWrap(True)
        bas.setStyleSheet(
            f"color:{C.TEXT};font-size:17px;font-weight:bold;font-family:Georgia;background:transparent;border:none;"
        )
        l.addWidget(bas)

        alt = QLabel(alt_metin)
        alt.setWordWrap(True)
        alt.setStyleSheet(
            f"color:{C.TEXT2};font-size:11px;line-height:18px;background:transparent;border:none;"
        )
        l.addWidget(alt)
        return kart

    # ══════════════════════════════════════════════════════════════
    #  MOD YÖNETİMİ
    # ══════════════════════════════════════════════════════════════
    def _sekme_stilleri(self):
        aktif_uye = (
            f"QPushButton{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {C.GOLD},stop:1 {C.COPPER});color:#1a0f06;"
            f"border:none;border-radius:9px;font-size:11px;font-weight:bold;"
            f"letter-spacing:3px;}}"
        )
        aktif_admin = (
            f"QPushButton{{background:qlineargradient(x1:0,y1:0,x2:1,y2:0,"
            f"stop:0 {C.WINE2},stop:1 {C.COPPER});color:#f5ece0;"
            f"border:none;border-radius:9px;font-size:11px;font-weight:bold;"
            f"letter-spacing:3px;}}"
        )
        pasif = (
            f"QPushButton{{background:transparent;color:{C.TEXT2};"
            f"border:none;border-radius:9px;font-size:11px;font-weight:bold;"
            f"letter-spacing:3px;}}"
            f"QPushButton:hover{{color:{C.TEXT};}}"
        )
        return aktif_uye, aktif_admin, pasif

    def _mod_degistir(self, mod: str):
        """Login modlarına geçiş yapar. Geçerli modlar: 'uye' veya 'admin'."""
        self.aktif_mod = mod
        self.kayit_form.hide()
        self.giris_form.show()
        aktif_uye, aktif_admin, pasif = self._sekme_stilleri()

        if mod == "uye":
            self.uye_sekme_btn.setStyleSheet(aktif_uye)
            self.admin_sekme_btn.setStyleSheet(pasif)
            self.mini_lbl.setText("UYE GIRISI")
            self.bas_lbl.setText("Mutfagina\nhos geldin.")
            self.alt_lbl.setText("Uye hesabinla giris yap ve tariflerinle bulus.")
            self.giris_btn.setText("UYE GIRISI")
            self.demo_panel.show()
            self.uye_ol_link.show()
            self.demo_etiket.setText("DEMO UYE HESABI")
            self.demo_bilgi_lbl.setText(
                "E-posta: sef@menu.com   ·   Sifre: 1234\n"
                "Normal uye: tarif ekleme, favori, plan, alisveris."
            )
        else:   # admin
            self.uye_sekme_btn.setStyleSheet(pasif)
            self.admin_sekme_btn.setStyleSheet(aktif_admin)
            self.mini_lbl.setText("ADMIN GIRISI")
            self.bas_lbl.setText("Admin\nkontrol paneli.")
            self.alt_lbl.setText("Tam yetki ile giris yap: tarif, kullanici ve yorum silebilirsin.")
            self.giris_btn.setText("ADMIN GIRISI")
            self.demo_panel.show()
            self.uye_ol_link.hide()   # admin için kayıt yok
            self.demo_etiket.setText("DEMO ADMIN HESABI")
            self.demo_bilgi_lbl.setText(
                "E-posta: admin@menu.com   ·   Sifre: admin1234\n"
                "Admin: tarif/kullanici/yorum silme (tam yetki)."
            )

    def _kayit_moduna_gec(self):
        """Üye kayıt formuna geçiş."""
        self.aktif_mod = "kayit"
        self.giris_form.hide()
        self.kayit_form.show()
        _, _, pasif = self._sekme_stilleri()
        self.uye_sekme_btn.setStyleSheet(pasif)
        self.admin_sekme_btn.setStyleSheet(pasif)
        self.mini_lbl.setText("YENI UYE KAYIT")
        self.bas_lbl.setText("Hesap\nolustur.")
        self.alt_lbl.setText(
            "Birkac alanda yeni bir uye hesabi actir. "
            "Tariflerini ekle, favorileri kaydet, planlarini yap."
        )
        self.ad_inp.setFocus()

    def _demo_doldur(self):
        """Seçili moda göre demo e-posta/şifreyi doldurur."""
        if self.aktif_mod == "uye":
            self.eposta_inp.setText("sef@menu.com")
            self.sifre_inp.setText("1234")
        elif self.aktif_mod == "admin":
            self.eposta_inp.setText("admin@menu.com")
            self.sifre_inp.setText("admin1234")
        self.sifre_inp.setFocus()

    def _varsayilan_hesabi_hazirla(self):
        """Çıkış sonrası tüm formları temizler ve üye modunu gösterir."""
        self.eposta_inp.clear()
        self.sifre_inp.clear()
        self.ad_inp.clear()
        self.soyad_inp.clear()
        self.kayit_eposta_inp.clear()
        self.kayit_sifre_inp.clear()
        self.sifre2_inp.clear()
        self._mod_degistir("uye")
        self.eposta_inp.setFocus()

    def _giris_istatistiklerini_yenile(self):
        tarifler = self.veri.tarif.listele()
        kullanicilar = self.veri.kullanici.listele()
        ortalama = 0.0
        if tarifler:
            puanlar = [t.get("ort_puan") or 0 for t in tarifler if t.get("ort_puan")]
            ortalama = sum(puanlar) / len(puanlar) if puanlar else 0.0
        self.ac_stat_tarif.deger_guncelle(str(len(tarifler)))
        self.ac_stat_puan.deger_guncelle(f"{ortalama:.1f}")
        self.ac_stat_kullanici.deger_guncelle(str(len(kullanicilar)))

    # ══════════════════════════════════════════════════════════════
    #  GİRİŞ & KAYIT İŞLEMLERİ
    # ══════════════════════════════════════════════════════════════
    def _giris_dene(self):
        email = self.eposta_inp.text().strip().lower()
        sifre = self.sifre_inp.text()

        if not email or not sifre:
            Toast(self, "E-posta ve sifre zorunludur.", "hata")
            return

        kullanici = self.veri.kullanici.giris_yap(email, sifre)
        if not kullanici:
            Toast(self, "E-posta veya sifre hatali.", "hata")
            self.sifre_inp.clear()
            self.sifre_inp.setFocus()
            return

        kul_rolu = kullanici.get("rol", "uye")

        if self.aktif_mod == "admin" and kul_rolu != "admin":
            Toast(self, "Bu hesap admin degil. 'UYE' sekmesinden giris yapin.", "hata")
            return

        if self.aktif_mod == "uye" and kul_rolu == "admin":
            Toast(self, "Admin hesabiyla giris yapildi.", "bilgi")

        rol_metni = "Admin" if kul_rolu == "admin" else "Uye"
        log(f"{kullanici['ad']} ({rol_metni}) giris yapti",
            C.WINE2 if kul_rolu == "admin" else C.SAGE)
        self.giris_basarili.emit(kullanici)

    def _kayit_ol(self):
        """Yeni üye kaydı: formu doğrula, veritabanına ekle, otomatik giriş yap."""
        ad = self.ad_inp.text().strip()
        soyad = self.soyad_inp.text().strip()
        email = self.kayit_eposta_inp.text().strip().lower()
        sifre = self.kayit_sifre_inp.text()
        sifre2 = self.sifre2_inp.text()

        # Doğrulamalar
        if not ad:
            Toast(self, "Ad alani zorunludur.", "hata")
            self.ad_inp.setFocus()
            return
        if not email:
            Toast(self, "E-posta zorunludur.", "hata")
            self.kayit_eposta_inp.setFocus()
            return
        if "@" not in email or "." not in email:
            Toast(self, "Gecerli bir e-posta girin (ornek@domain.com).", "hata")
            self.kayit_eposta_inp.setFocus()
            return
        if len(sifre) < 4:
            Toast(self, "Sifre en az 4 karakter olmalidir.", "hata")
            self.kayit_sifre_inp.setFocus()
            return
        if sifre != sifre2:
            Toast(self, "Sifreler eslesmiyor. Lutfen tekrar deneyin.", "hata")
            self.sifre2_inp.clear()
            self.sifre2_inp.setFocus()
            return

        # Veritabanına ekle (rol='uye' varsayılan)
        sonuc = self.veri.kullanici.ekle(ad, soyad, email, sifre, rol="uye")
        if not sonuc["basarili"]:
            Toast(self, sonuc["mesaj"], "hata")
            return

        log(f"Yeni uye kayit oldu: {ad} {soyad}", C.SAGE)

        # Otomatik giriş
        kullanici = self.veri.kullanici.giris_yap(email, sifre)
        if not kullanici:
            # Güvenli geri dönüş: form bilgilerini giriş ekranına taşı
            Toast(self, "Kayit tamam. Lutfen sifrenizle giris yapin.", "bilgi")
            self._mod_degistir("uye")
            self.eposta_inp.setText(email)
            self.sifre_inp.setFocus()
            return

        # İstatistikleri tazele (yeni üye sayısı için)
        self._giris_istatistiklerini_yenile()
        self.giris_basarili.emit(kullanici)



# ══════════════════════════════════════════════════════════════════
#  TARİF KARTI — Liste görünümünde kullanılır
# ══════════════════════════════════════════════════════════════════
class TarifKarti(QFrame):
    """
    Bir tarifi özet halinde gösteren hoverable kart.
    Tıklandığında detay sayfasını açan sinyal yayar.
    """
    tiklandi = pyqtSignal(int)    # tarif_id

    def __init__(self, tarif_dict: dict):
        super().__init__()
        self.tarif_id = tarif_dict["tarif_id"]
        self.kategori = tarif_dict.get("kategori", "Ana Yemek")
        self.setFixedHeight(170)
        self.setCursor(Qt.PointingHandCursor)
        self.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;"
            f"border-radius:14px;}}"
            f"QFrame:hover{{background:{C.CARD2};}}"
        )

        l = QHBoxLayout(self)
        l.setContentsMargins(24, 20, 24, 20)
        l.setSpacing(18)

        # Sol renk şeridi (kategori rengine göre)
        renk_ser = QFrame()
        renk_ser.setFixedWidth(4)
        renk = KAT_RENK.get(self.kategori, C.GOLD)
        renk_ser.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            f"stop:0 {renk},stop:1 {renk}60);border-radius:2px;border:none;"
        )
        l.addWidget(renk_ser)

        # Sol kolon: tarif adı + kategori rozeti + açıklama
        sol_kap = QVBoxLayout()
        sol_kap.setSpacing(8)

        ust_sat = QHBoxLayout()
        ust_sat.setSpacing(10)
        ad_lbl = QLabel(tarif_dict["tarif_adi"])
        ad_lbl.setStyleSheet(
            f"color:{C.TEXT};font-size:18px;font-weight:bold;"
            f"font-family:Georgia;background:transparent;border:none;"
        )
        ust_sat.addWidget(ad_lbl)
        # Kategori rozeti
        kat_lbl = QLabel(self.kategori.upper())
        kat_lbl.setStyleSheet(
            f"color:{renk};background:{renk}15;padding:4px 10px;"
            f"border-radius:6px;font-size:9px;font-weight:bold;"
            f"letter-spacing:1.5px;border:none;"
        )
        ust_sat.addWidget(kat_lbl)
        ust_sat.addStretch()
        sol_kap.addLayout(ust_sat)

        aciklama = tarif_dict.get("aciklama") or "Açıklama girilmemiş."
        if len(aciklama) > 100:
            aciklama = aciklama[:100] + "…"
        ack_lbl = QLabel(aciklama)
        ack_lbl.setWordWrap(True)
        ack_lbl.setStyleSheet(
            f"color:{C.TEXT2};font-size:11px;line-height:18px;"
            f"background:transparent;border:none;"
        )
        sol_kap.addWidget(ack_lbl)
        sol_kap.addStretch()

        # Alt satır: meta bilgiler
        meta = QHBoxLayout()
        meta.setSpacing(18)
        # Hazırlama süresi
        sure_text = f"⏱  {tarif_dict['hazirlama_suresi']} dk"
        zor = tarif_dict.get("zorluk", "Orta")
        zor_renk = ZOR_RENK.get(zor, C.GOLD)
        for metin, renk_m in [
            (sure_text, C.TEXT2),
            (f"◉  {zor}", zor_renk),
            (f"♦  {tarif_dict.get('porsiyon', 4)} porsiyon", C.TEXT2),
            (f"👤  {tarif_dict.get('ekleyen', '—')}", C.TEXT3),
        ]:
            e = QLabel(metin)
            e.setStyleSheet(
                f"color:{renk_m};font-size:10px;font-weight:bold;"
                f"background:transparent;border:none;letter-spacing:0.5px;"
            )
            meta.addWidget(e)
        meta.addStretch()
        sol_kap.addLayout(meta)

        l.addLayout(sol_kap, 1)

        # Sağ kolon: ortalama puan (büyük yıldız + sayı)
        sag_kap = QVBoxLayout()
        sag_kap.setAlignment(Qt.AlignCenter)
        sag_kap.setSpacing(6)

        puan = tarif_dict.get("ort_puan") or 0
        sayisi = tarif_dict.get("puan_sayisi") or 0

        puan_lbl = QLabel(f"{puan:.1f}" if puan else "—")
        puan_lbl.setAlignment(Qt.AlignCenter)
        puan_lbl.setStyleSheet(
            f"color:{C.GOLD};font-size:30px;font-weight:bold;"
            f"font-family:Georgia;background:transparent;border:none;"
        )
        sag_kap.addWidget(puan_lbl)

        # 5 mini yıldız
        mini_yld = YildizDerecelendirme(puan, salt_okunur=True, boyut=14)
        mini_yld.setStyleSheet("background:transparent;border:none;")
        sag_yld = QHBoxLayout()
        sag_yld.addStretch()
        sag_yld.addWidget(mini_yld)
        sag_yld.addStretch()
        sag_kap.addLayout(sag_yld)

        sayisi_lbl = QLabel(f"{sayisi} değerlendirme" if sayisi else "Değerlendirme yok")
        sayisi_lbl.setAlignment(Qt.AlignCenter)
        sayisi_lbl.setStyleSheet(
            f"color:{C.TEXT3};font-size:10px;background:transparent;"
            f"border:none;letter-spacing:0.5px;"
        )
        sag_kap.addWidget(sayisi_lbl)

        sag_w = QWidget()
        sag_w.setFixedWidth(140)
        sag_w.setStyleSheet("background:transparent;border:none;")
        sag_w.setLayout(sag_kap)
        l.addWidget(sag_w)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            self.tiklandi.emit(self.tarif_id)


# ══════════════════════════════════════════════════════════════════
#  ANA PENCERE
# ══════════════════════════════════════════════════════════════════
class AnaPencere(QMainWindow):
    """
    Uygulamanın ana penceresi.
    Sol: Navigasyon kenar çubuğu (sidebar)
    Sağ: QStackedWidget içinde sayfalar
    Üst: Mini üst çubuk (kullanıcı + saat)
    """
    def __init__(self, veri: VeriYoneticisi):
        super().__init__()
        self.veri = veri
        self.setWindowTitle("Menü — Yemek Tarif Platformu")
        self.setGeometry(50, 50, 1380, 860)
        self.setStyleSheet(f"background:{C.BG};")

        # Giriş ekranı ve ana içeriği bir stacked widget'ta tut
        self.merkez = QStackedWidget()
        self.setCentralWidget(self.merkez)

        self.giris = GirisEkrani(veri)
        self.giris.giris_basarili.connect(self._giris_tamam)
        self.merkez.addWidget(self.giris)

        # Ana içerik (kullanıcı giriş yaptıktan sonra oluşturulacak)
        self.ana_icerik = None

    def _giris_tamam(self, kullanici: dict):
        """Giriş başarılı olduğunda ana arayüzü oluştur."""
        self.veri.aktif_kullanici = kullanici
        if self.ana_icerik is not None:
            self.merkez.removeWidget(self.ana_icerik)
            self.ana_icerik.deleteLater()
            self.ana_icerik = None
        self.ana_icerik = self._ana_arayuz()
        self.merkez.addWidget(self.ana_icerik)
        self.merkez.setCurrentWidget(self.ana_icerik)
        selam = "Hosgeldin Admin" if self._admin_mi() else f"Hosgeldiniz, {kullanici['ad']}!"
        QTimer.singleShot(100, lambda: Toast(self, selam, "basari"))

    def _admin_mi(self) -> bool:
        """Aktif kullanıcı admin rolüne sahipse True döner."""
        k = self.veri.aktif_kullanici
        return bool(k and k.get("rol") == "admin")

    # ─── Ana Arayüz Konteyneri ───
    def _ana_arayuz(self) -> QWidget:
        w = QWidget()
        ana_l = QHBoxLayout(w)
        ana_l.setContentsMargins(0, 0, 0, 0)
        ana_l.setSpacing(0)

        # Sayfa yığını (StackedWidget) üst çubuk tarafından bağlanacağı için önce oluşturulmalı
        self.sayfalar = QStackedWidget()

        # ─── Sol Sidebar ───
        sidebar = self._sidebar_olustur()
        ana_l.addWidget(sidebar)

        # ─── Sağ: Üst çubuk + sayfa içeriği ───
        sag_kap = QWidget()
        sag_kap.setStyleSheet(f"background:{C.BG};")
        sag_l = QVBoxLayout(sag_kap)
        sag_l.setContentsMargins(0, 0, 0, 0)
        sag_l.setSpacing(0)

        # Üst çubuk
        sag_l.addWidget(self._ust_cubuk_olustur())

        self.dashboard_w = self._sayfa_dashboard()
        self.tarifler_w = self._sayfa_tarifler()
        self.detay_w = self._sayfa_detay_konteyner()
        self.yeni_tarif_w = self._sayfa_yeni_tarif()
        self.kullanicilar_w = self._sayfa_kullanicilar()
        self.istatistik_w = self._sayfa_istatistik()
        self.favoriler_w = self._sayfa_favoriler()
        self.plan_w = self._sayfa_haftalik_plan()
        self.alisveris_w = self._sayfa_alisveris()

        self.sayfalar.addWidget(self.dashboard_w)
        self.sayfalar.addWidget(self.tarifler_w)
        self.sayfalar.addWidget(self.detay_w)
        self.sayfalar.addWidget(self.yeni_tarif_w)
        self.sayfalar.addWidget(self.kullanicilar_w)
        self.sayfalar.addWidget(self.istatistik_w)
        self.sayfalar.addWidget(self.favoriler_w)
        self.sayfalar.addWidget(self.plan_w)
        self.sayfalar.addWidget(self.alisveris_w)

        sag_l.addWidget(self.sayfalar, 1)
        ana_l.addWidget(sag_kap, 1)

        # İlk açılışta Dashboard (Gösterge Paneli) verilerini yükle
        self._sayfa_degistir(0)

        return w

    # ─── SIDEBAR ───
    def _sidebar_olustur(self) -> QWidget:
        sb = QWidget()
        sb.setFixedWidth(240)
        sb.setStyleSheet(
            f"background:{C.BG2};border-right:none;"
        )
        l = QVBoxLayout(sb)
        l.setContentsMargins(20, 28, 20, 24)
        l.setSpacing(6)

        # Marka adı
        marka = QLabel("Menü")
        marka.setStyleSheet(
            f"color:{C.TEXT};font-size:30px;font-weight:bold;"
            f"font-family:Georgia;letter-spacing:-1px;padding-left:8px;"
        )
        l.addWidget(marka)
        alt_mrk = QLabel("MASTERCLASS")
        alt_mrk.setStyleSheet(
            f"color:{C.GOLD};font-size:8px;font-weight:bold;"
            f"letter-spacing:5px;padding-left:10px;"
        )
        l.addWidget(alt_mrk)

        l.addSpacing(28)

        # Menü başlığı
        l.addWidget(etiket_kucuk("  NAVİGASYON"))
        l.addSpacing(8)

        # Menü butonları
        self.nav_btns = []
        menuler = [
            ("Gösterge Paneli", "◈", 0),
            ("Tarifler", "♦", 1),
            ("Favorilerim", "💖", 6),
            ("Haftalik Plan", "=", 7),
            ("Alışveriş Listesi", "🛒", 8),
            ("Yeni Tarif", "✛", 3),
            ("Kullanıcılar", "◉", 4),
            ("İstatistikler", "▦", 5),
        ]
        for metin, ikon, indeks in menuler:
            btn = self._sidebar_btn(metin, ikon, indeks)
            self.nav_btns.append((btn, indeks))
            l.addWidget(btn)

        l.addStretch()

        # Alt kısım: aktif kullanıcı bilgisi + çıkış
        l.addWidget(ayrac())
        l.addSpacing(14)

        kul = self.veri.aktif_kullanici
        baş_harf = kul["ad"][0].upper() if kul else "?"
        kul_kap = QHBoxLayout()
        kul_kap.setSpacing(10)
        avatar = QLabel(baş_harf)
        avatar.setFixedSize(38, 38)
        avatar.setAlignment(Qt.AlignCenter)
        # Admin için farklı renk
        if self._admin_mi():
            avatar.setStyleSheet(
                f"background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                f"stop:0 {C.WINE2},stop:1 {C.COPPER});"
                f"color:#f5ece0;border-radius:19px;font-size:15px;"
                f"font-weight:bold;font-family:Georgia;"
            )
        else:
            avatar.setStyleSheet(
                f"background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
                f"stop:0 {C.GOLD},stop:1 {C.COPPER});"
                f"color:#1a0f06;border-radius:19px;font-size:15px;"
                f"font-weight:bold;font-family:Georgia;"
            )
        kul_kap.addWidget(avatar)
        kul_bilgi = QVBoxLayout()
        kul_bilgi.setSpacing(2)
        kul_adi_metin = f"{kul['ad']} {kul['soyad']}".strip() if kul else "—"
        kul_adi = QLabel(kul_adi_metin)
        kul_adi.setStyleSheet(
            f"color:{C.TEXT};font-size:12px;font-weight:bold;"
        )
        # Admin ise e-posta yerine ADMIN rozeti
        if self._admin_mi():
            kul_email = QLabel("◆ ADMIN · TAM YETKI")
            kul_email.setStyleSheet(
                f"color:{C.WINE2};font-size:9px;font-weight:bold;letter-spacing:2px;"
            )
        else:
            kul_email = QLabel(kul['email'] if kul else "")
            kul_email.setStyleSheet(f"color:{C.TEXT3};font-size:10px;")
        kul_bilgi.addWidget(kul_adi)
        kul_bilgi.addWidget(kul_email)
        kul_kap.addLayout(kul_bilgi, 1)
        l.addLayout(kul_kap)

        l.addSpacing(12)

        cikis_btn = btn_ghost("ÇIKIŞ YAP")
        cikis_btn.clicked.connect(self._cikis_yap)
        l.addWidget(cikis_btn)

        self._aktif_sayfa_guncelle(0)
        return sb

    def _sidebar_btn(self, metin: str, ikon: str, indeks: int) -> QPushButton:
        b = QPushButton(f"  {ikon}   {metin}")
        b.setCursor(Qt.PointingHandCursor)
        b.setFixedHeight(42)
        b.setStyleSheet(
            f"QPushButton{{background:transparent;color:{C.TEXT2};"
            f"border:none;border-radius:8px;text-align:left;"
            f"padding-left:14px;font-size:13px;font-weight:bold;"
            f"letter-spacing:0.5px;outline:none;}}"
            f"QPushButton:hover{{background:{C.CARD};color:{C.TEXT};}}"
            f"QPushButton:focus{{outline:none;}}"
        )
        b.clicked.connect(lambda: self._sayfa_degistir(indeks))
        return b

    def _aktif_sayfa_guncelle(self, indeks: int):
        """Sidebar'da aktif butonu vurgular."""
        for btn, idx in self.nav_btns:
            if idx == indeks:
                btn.setStyleSheet(
                    f"QPushButton{{background:{C.GOLD}18;color:{C.GOLD2};"
                    f"border:none;border-radius:8px;text-align:left;"
                    f"padding-left:14px;font-size:13px;font-weight:bold;"
                    f"letter-spacing:0.5px;"
                    f"border-left:none;outline:none;}}"
                    f"QPushButton:focus{{outline:none;}}"
                )
            else:
                btn.setStyleSheet(
                    f"QPushButton{{background:transparent;color:{C.TEXT2};"
                    f"border:none;border-radius:8px;text-align:left;"
                    f"padding-left:14px;font-size:13px;font-weight:bold;"
                    f"letter-spacing:0.5px;outline:none;}}"
                    f"QPushButton:hover{{background:{C.CARD};color:{C.TEXT};}}"
                    f"QPushButton:focus{{outline:none;}}"
                )

    def _sayfa_degistir(self, indeks: int):
        self.sayfalar.setCurrentIndex(indeks)
        self._aktif_sayfa_guncelle(indeks)
        # Sayfa açılınca veri yenile
        if indeks == 0:
            self._dashboard_yenile()
        elif indeks == 1:
            self._tarifler_yenile()
        elif indeks == 4:
            self._kullanicilar_yenile()
        elif indeks == 5:
            self._istatistik_yenile()
        elif indeks == 6:
            self._favoriler_yenile()
        elif indeks == 7:
            self._haftalik_plan_yenile()
        elif indeks == 8:
            self._alisveris_yenile()

    def _cikis_yap(self):
        """Aktif kullanıcıyı sıfırla, giriş ekranına dön."""
        self.veri.aktif_kullanici = None
        if self.ana_icerik is not None:
            self.merkez.removeWidget(self.ana_icerik)
            self.ana_icerik.deleteLater()
            self.ana_icerik = None
        self.giris._giris_istatistiklerini_yenile()
        self.giris._varsayilan_hesabi_hazirla()
        log("Oturum kapatıldı", C.WINE2)
        self.merkez.setCurrentWidget(self.giris)

    # ══════════════════════════════════════════════════════════════
    #  ADMIN SİLME İŞLEMLERİ (Sadece rol='admin' olan kullanıcılar için)
    # ══════════════════════════════════════════════════════════════
    def _admin_onay_al(self, baslik: str, metin: str) -> bool:
        """Admin silme işlemleri için onay diyaloğu."""
        cvp = QMessageBox.question(
            self, baslik, metin,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        return cvp == QMessageBox.Yes

    def _admin_tarif_sil(self, tarif_id: int, tarif_adi: str):
        """Admin: bir tarifi (ve bağlı tüm malzeme/yorumlarını) siler."""
        if not self._admin_mi():
            Toast(self, "Bu islem icin admin yetkisi gerekli.", "hata")
            return
        if not self._admin_onay_al(
            "Tarifi Sil",
            f"'{tarif_adi}' tarifi ve butun malzemeleri/yorumlari silinecek.\n\nEmin misiniz?"
        ):
            return
        sonuc = self.veri.tarif.sil(tarif_id)
        if sonuc["basarili"]:
            log(f"[ADMIN] Tarif silindi: {tarif_adi}", C.WINE2)
            Toast(self, f"'{tarif_adi}' silindi.", "basari")
            self._sayfa_degistir(1)  # Tarifler sayfasına dön
            self._tarifler_yenile()
        else:
            Toast(self, sonuc["mesaj"], "hata")

    def _admin_yorum_sil(self, degerlendirme_id: int, tarif_id: int):
        """Admin: bir yorumu/değerlendirmeyi siler."""
        if not self._admin_mi():
            Toast(self, "Bu islem icin admin yetkisi gerekli.", "hata")
            return
        if not self._admin_onay_al(
            "Yorumu Sil",
            "Bu yorum ve puan kalıcı olarak silinecek.\n\nEmin misiniz?"
        ):
            return
        sonuc = self.veri.kullanici.degerlendirme_sil(degerlendirme_id)
        if sonuc["basarili"]:
            log(f"[ADMIN] Yorum silindi (#{degerlendirme_id})", C.WINE2)
            Toast(self, "Yorum silindi.", "basari")
            self._tarif_detay_ac(tarif_id)   # Detay sayfasını tazele
        else:
            Toast(self, sonuc["mesaj"], "hata")

    def _admin_kullanici_sil(self, kullanici_id: int, kullanici_adi: str):
        """Admin: bir kullanıcıyı ve bağlı tüm verileri siler."""
        if not self._admin_mi():
            Toast(self, "Bu islem icin admin yetkisi gerekli.", "hata")
            return
        # Admin kendi hesabını silemez (güvenlik)
        if self.veri.aktif_kullanici and kullanici_id == self.veri.aktif_kullanici["kullanici_id"]:
            Toast(self, "Kendi hesabinizi silemezsiniz.", "hata")
            return
        if not self._admin_onay_al(
            "Kullaniciyi Sil",
            f"'{kullanici_adi}' kullanicisinin TUM verileri silinecek:\n"
            f"• Tarifler ve malzemeleri\n• Yorumlar ve favoriler\n• Haftalik plan, alisveris listesi\n\n"
            f"Bu islem geri alinamaz. Emin misiniz?"
        ):
            return
        sonuc = self.veri.kullanici.sil(kullanici_id, zorla=True)
        if sonuc["basarili"]:
            log(f"[ADMIN] Kullanici silindi: {kullanici_adi}", C.WINE2)
            Toast(self, f"'{kullanici_adi}' silindi.", "basari")
            self._kullanicilar_yenile()
        else:
            Toast(self, sonuc["mesaj"], "hata")

    # ─── ÜST ÇUBUK ───
    def _ust_cubuk_olustur(self) -> QWidget:
        c = QWidget()
        c.setFixedHeight(60)
        c.setStyleSheet(
            f"background:{C.BG};border-bottom:none;"
        )
        l = QHBoxLayout(c)
        l.setContentsMargins(30, 0, 30, 0)
        l.setSpacing(16)

        # Sol: sayfa başlığı (dinamik)
        self.sayfa_basligi = QLabel("GÖSTERGE PANELİ")
        self.sayfa_basligi.setStyleSheet(
            f"color:{C.GOLD};font-size:11px;font-weight:bold;"
            f"letter-spacing:4px;"
        )
        l.addWidget(self.sayfa_basligi)

        # Dinamik başlık güncellemesi için sinyal
        self.sayfalar_baslik_eslesme = [
            "GÖSTERGE PANELİ", "TARİFLER", "TARİF DETAYI",
            "YENİ TARİF", "KULLANICILAR", "İSTATİSTİKLER", "FAVORİLERİM",
            "HAFTALIK PLAN", "ALIŞVERİŞ LİSTESİ"
        ]
        # currentChanged sinyaline bağla
        def baslik_guncelle(idx):
            if 0 <= idx < len(self.sayfalar_baslik_eslesme):
                self.sayfa_basligi.setText(self.sayfalar_baslik_eslesme[idx])
        self.sayfalar.currentChanged.connect(baslik_guncelle)

        l.addStretch()

        # Sağ: Zamanlayıcı ve Canlı saat
        saag_kutu = QHBoxLayout()
        saag_kutu.setSpacing(20)
        saag_kutu.addWidget(MutfakZamanlayici())
        saag_kutu.addWidget(CanliSaat())
        l.addLayout(saag_kutu)
        return c

    # ══════════════════════════════════════════════════════════════
    #  SAYFA 1: DASHBOARD
    # ══════════════════════════════════════════════════════════════
    def _sayfa_dashboard(self) -> QWidget:
        kap = QScrollArea()
        kap.setWidgetResizable(True)
        kap.setStyleSheet(f"QScrollArea{{background:{C.BG};border:none;}}"
                          "QScrollBar:vertical{width:8px;background:transparent;}")
        ic = QWidget()
        ic.setStyleSheet(f"background:{C.BG};")
        l = QVBoxLayout(ic)
        l.setContentsMargins(34, 28, 34, 28)
        l.setSpacing(22)

        # ─── Hoşgeldin kartı ───
        hs_kart = QFrame()
        hs_kart.setFixedHeight(140)
        hs_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;"
            f"border-radius:16px;}}"
        )
        hsl = QHBoxLayout(hs_kart)
        hsl.setContentsMargins(34, 22, 34, 22)

        # Sol renk şeridi (amber)
        ser = QFrame()
        ser.setFixedWidth(3)
        ser.setStyleSheet(
            f"background:qlineargradient(x1:0,y1:0,x2:0,y2:1,"
            f"stop:0 {C.GOLD},stop:1 {C.COPPER});border:none;border-radius:2px;"
        )
        hsl.addWidget(ser)
        hsl.addSpacing(22)

        metin_kap = QVBoxLayout()
        metin_kap.setSpacing(6)
        ust_et = QLabel("GÜNAYDIN" if datetime.now().hour < 12
                        else ("İYİ GÜNLER" if datetime.now().hour < 18
                              else "İYİ AKŞAMLAR"))
        ust_et.setStyleSheet(
            f"color:{C.GOLD};font-size:10px;font-weight:bold;"
            f"letter-spacing:4px;background:transparent;border:none;"
        )
        metin_kap.addWidget(ust_et)

        ad = self.veri.aktif_kullanici["ad"] if self.veri.aktif_kullanici else "Şef"
        self.hs_baslik = QLabel(f"Hoşgeldin, {ad}")
        self.hs_baslik.setStyleSheet(
            f"color:{C.TEXT};font-size:30px;font-weight:bold;"
            f"font-family:Georgia;letter-spacing:-0.5px;"
            f"background:transparent;border:none;"
        )
        metin_kap.addWidget(self.hs_baslik)

        self.hs_alt = QLabel("Mutfağında bugün ne pişecek?")
        self.hs_alt.setStyleSheet(
            f"color:{C.TEXT2};font-size:13px;background:transparent;"
            f"border:none;font-family:Georgia;font-style:italic;"
        )
        metin_kap.addWidget(self.hs_alt)
        hsl.addLayout(metin_kap, 1)

        # Sağda hızlı buton
        btn_kutu = QVBoxLayout()
        btn_kutu.setSpacing(10)
        hizli_btn = btn_primary("+ YENİ TARİF", genislik=170, yukseklik=44)
        hizli_btn.clicked.connect(lambda: self._sayfa_degistir(3))
        rastgele_btn = btn_ghost("Bugün Ne Pişirsem?", yukseklik=44)
        rastgele_btn.setMinimumWidth(190)
        def rastgele_ac():
            rt = self.veri.tarif.rastgele_getir()
            if rt:
                self._tarif_detay_ac(rt["tarif_id"])
            else:
                Toast(self, "Henüz hiç tarif yok.", "hata")
        rastgele_btn.clicked.connect(rastgele_ac)
        btn_kutu.addWidget(hizli_btn)
        btn_kutu.addWidget(rastgele_btn)
        hsl.addLayout(btn_kutu)

        l.addWidget(hs_kart)

        # ─── İstatistik kartları (4'lü) ───
        kartlar_kap = QHBoxLayout()
        kartlar_kap.setSpacing(18)

        self.k_tarif = StatKart("TOPLAM TARİF", "0", C.GOLD, "♦")
        self.k_malzeme = StatKart("MALZEME", "0", C.COPPER, "◈")
        self.k_kullanici = StatKart("KULLANICI", "0", C.SAGE, "◉")
        self.k_puan = StatKart("ORTALAMA PUAN", "0.0", C.WINE2, "★")

        kartlar_kap.addWidget(self.k_tarif)
        kartlar_kap.addWidget(self.k_malzeme)
        kartlar_kap.addWidget(self.k_kullanici)
        kartlar_kap.addWidget(self.k_puan)
        l.addLayout(kartlar_kap)

        # ─── Grafikler satırı (halka + çubuk) ───
        graf_sat = QHBoxLayout()
        graf_sat.setSpacing(18)

        # Sol: Halka grafik kartı
        halka_kart = QFrame()
        halka_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;"
            f"border-radius:14px;}}"
        )
        hkl = QVBoxLayout(halka_kart)
        hkl.setContentsMargins(24, 20, 24, 20)
        hkl.setSpacing(12)
        hkl.addWidget(etiket_kucuk("KATEGORİ DAĞILIMI"))
        h_bsl = QLabel("Tarif Türleri")
        h_bsl.setStyleSheet(
            f"color:{C.TEXT};font-size:18px;font-weight:bold;"
            f"font-family:Georgia;background:transparent;border:none;"
        )
        hkl.addWidget(h_bsl)
        self.halka = HalkaGrafik({})
        self.halka.setStyleSheet("background:transparent;border:none;")
        hkl.addWidget(self.halka, 1)

        # Legend (kategoriler renkleriyle)
        self.legend_kap = QVBoxLayout()
        self.legend_kap.setSpacing(6)
        legend_w = QWidget()
        legend_w.setStyleSheet("background:transparent;border:none;")
        legend_w.setLayout(self.legend_kap)
        hkl.addWidget(legend_w)

        graf_sat.addWidget(halka_kart, 1)

        # Sağ: Çubuk grafik kartı
        cubuk_kart = QFrame()
        cubuk_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;"
            f"border-radius:14px;}}"
        )
        ckl = QVBoxLayout(cubuk_kart)
        ckl.setContentsMargins(24, 20, 24, 20)
        ckl.setSpacing(12)
        ckl.addWidget(etiket_kucuk("ZORLUK DAĞILIMI"))
        c_bsl = QLabel("Tarif Zorlukları")
        c_bsl.setStyleSheet(
            f"color:{C.TEXT};font-size:18px;font-weight:bold;"
            f"font-family:Georgia;background:transparent;border:none;"
        )
        ckl.addWidget(c_bsl)
        self.cubuk = CubukGrafik({})
        self.cubuk.setStyleSheet("background:transparent;border:none;")
        ckl.addWidget(self.cubuk, 1)
        graf_sat.addWidget(cubuk_kart, 1)

        l.addLayout(graf_sat)

        # ─── Popüler tarifler + son aktiviteler ───
        alt_sat = QHBoxLayout()
        alt_sat.setSpacing(18)

        # Popüler tarifler
        pop_kart = QFrame()
        pop_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;"
            f"border-radius:14px;}}"
        )
        pkl = QVBoxLayout(pop_kart)
        pkl.setContentsMargins(24, 20, 24, 20)
        pkl.setSpacing(10)
        pkl.addWidget(etiket_kucuk("EN YÜKSEK PUANLILAR"))
        p_bsl = QLabel("Şef Seçimi")
        p_bsl.setStyleSheet(
            f"color:{C.TEXT};font-size:18px;font-weight:bold;"
            f"font-family:Georgia;background:transparent;border:none;"
        )
        pkl.addWidget(p_bsl)
        self.pop_liste = QVBoxLayout()
        self.pop_liste.setSpacing(8)
        pop_icw = QWidget()
        pop_icw.setStyleSheet("background:transparent;border:none;")
        pop_icw.setLayout(self.pop_liste)
        pkl.addWidget(pop_icw)
        pkl.addStretch()
        alt_sat.addWidget(pop_kart, 1)

        # Son aktiviteler
        akt_kart = QFrame()
        akt_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;"
            f"border-radius:14px;}}"
        )
        akl = QVBoxLayout(akt_kart)
        akl.setContentsMargins(24, 20, 24, 20)
        akl.setSpacing(10)
        akl.addWidget(etiket_kucuk("SON AKTİVİTELER"))
        a_bsl = QLabel("Mutfak Günlüğü")
        a_bsl.setStyleSheet(
            f"color:{C.TEXT};font-size:18px;font-weight:bold;"
            f"font-family:Georgia;background:transparent;border:none;"
        )
        akl.addWidget(a_bsl)
        self.akt_liste = QVBoxLayout()
        self.akt_liste.setSpacing(8)
        akt_icw = QWidget()
        akt_icw.setStyleSheet("background:transparent;border:none;")
        akt_icw.setLayout(self.akt_liste)
        akl.addWidget(akt_icw)
        akl.addStretch()
        alt_sat.addWidget(akt_kart, 1)

        l.addLayout(alt_sat)

        kap.setWidget(ic)
        return kap

    def _dashboard_yenile(self):
        """Dashboard'daki tüm bileşenleri günceller."""
        ist = self.veri.istatistik.genel_istatistikler()
        self.k_tarif.deger_guncelle(str(ist["toplam_tarif"]))
        self.k_malzeme.deger_guncelle(str(ist["toplam_malzeme"]))
        self.k_kullanici.deger_guncelle(str(ist["toplam_kullanici"]))
        self.k_puan.deger_guncelle(f"{ist['ortalama_puan']:.1f}")
        if ist["toplam_tarif"] > 0:
            populer_kat = next(iter(ist["kategori_dagilimi"]), "tarif koleksiyonu")
            self.hs_alt.setText(
                f"{ist['toplam_tarif']} tarif seni bekliyor. Bugünün öne çıkan kategorisi: {populer_kat}."
            )
        else:
            self.hs_alt.setText("Mutfağında bugün ne pişecek?")

        self.halka.veri_guncelle(ist["kategori_dagilimi"])
        self.cubuk.veri_guncelle(ist["zorluk_dagilimi"])

        # Legend güncelle
        while self.legend_kap.count():
            ch = self.legend_kap.takeAt(0).widget()
            if ch:
                ch.deleteLater()
        for kat, sayi in ist["kategori_dagilimi"].items():
            renk = KAT_RENK.get(kat, C.GOLD)
            sat = QHBoxLayout()
            sat.setSpacing(10)
            dot = QLabel("●")
            dot.setStyleSheet(
                f"color:{renk};font-size:14px;background:transparent;border:none;"
            )
            et = QLabel(f"{kat}")
            et.setStyleSheet(
                f"color:{C.TEXT2};font-size:11px;background:transparent;border:none;"
            )
            sa = QLabel(str(sayi))
            sa.setStyleSheet(
                f"color:{C.TEXT};font-size:11px;font-weight:bold;"
                f"background:transparent;border:none;"
            )
            sat.addWidget(dot)
            sat.addWidget(et)
            sat.addStretch()
            sat.addWidget(sa)
            sat_w = QWidget()
            sat_w.setStyleSheet("background:transparent;border:none;")
            sat_w.setLayout(sat)
            self.legend_kap.addWidget(sat_w)

        # Popüler tarifler
        while self.pop_liste.count():
            ch = self.pop_liste.takeAt(0).widget()
            if ch:
                ch.deleteLater()
        pop = self.veri.istatistik.en_populer_tarifler(5)
        if not pop:
            bos = QLabel("Henüz değerlendirilmiş tarif yok.")
            bos.setStyleSheet(
                f"color:{C.TEXT3};font-size:11px;background:transparent;border:none;"
            )
            self.pop_liste.addWidget(bos)
        for t in pop:
            sat = self._populer_satir(t)
            self.pop_liste.addWidget(sat)

        # Aktiviteler
        while self.akt_liste.count():
            ch = self.akt_liste.takeAt(0).widget()
            if ch:
                ch.deleteLater()
        if not AKTIVITE:
            bos = QLabel("Aktivite kaydı boş.")
            bos.setStyleSheet(
                f"color:{C.TEXT3};font-size:11px;background:transparent;border:none;"
            )
            self.akt_liste.addWidget(bos)
        for akt in AKTIVITE[:7]:
            sat = QHBoxLayout()
            sat.setSpacing(12)
            zaman = QLabel(akt["zaman"])
            zaman.setStyleSheet(
                f"color:{C.TEXT3};font-size:10px;font-weight:bold;"
                f"background:transparent;border:none;min-width:45px;"
            )
            msg = QLabel(akt["mesaj"])
            msg.setStyleSheet(
                f"color:{akt['renk']};font-size:11px;"
                f"background:transparent;border:none;"
            )
            sat.addWidget(zaman)
            sat.addWidget(msg)
            sat.addStretch()
            sw = QWidget()
            sw.setStyleSheet("background:transparent;border:none;")
            sw.setLayout(sat)
            self.akt_liste.addWidget(sw)

    def _populer_satir(self, tarif: dict) -> QWidget:
        """Popüler tarifler listesindeki tek satır (tıklanabilir)."""
        w = QFrame()
        w.setCursor(Qt.PointingHandCursor)
        w.setStyleSheet(
            f"QFrame{{background:{C.BG};border:none;"
            f"border-radius:8px;}}"
            f"QFrame:hover{{background:{C.CARD2};}}"
        )
        l = QHBoxLayout(w)
        l.setContentsMargins(14, 10, 14, 10)
        l.setSpacing(12)

        renk = KAT_RENK.get(tarif["kategori"], C.GOLD)
        dot = QLabel("●")
        dot.setStyleSheet(
            f"color:{renk};font-size:16px;background:transparent;border:none;"
        )
        l.addWidget(dot)

        ad = QLabel(tarif["tarif_adi"])
        ad.setStyleSheet(
            f"color:{C.TEXT};font-size:12px;font-weight:bold;"
            f"background:transparent;border:none;"
        )
        l.addWidget(ad)

        # Kategori mini rozet
        kat = QLabel(tarif["kategori"])
        kat.setStyleSheet(
            f"color:{renk};font-size:9px;background:transparent;border:none;"
            f"letter-spacing:1px;"
        )
        l.addWidget(kat)
        l.addStretch()

        puan_t = QLabel(f"★ {tarif['ort_puan']:.1f}")
        puan_t.setStyleSheet(
            f"color:{C.GOLD};font-size:13px;font-weight:bold;"
            f"background:transparent;border:none;font-family:Georgia;"
        )
        l.addWidget(puan_t)

        # Tıklanınca detay
        def tikla(_, tid=tarif["tarif_id"]):
            self._tarif_detay_ac(tid)
        w.mousePressEvent = tikla
        return w


    # ══════════════════════════════════════════════════════════════
    #  SAYFA 2: TARİFLER LİSTESİ
    # ══════════════════════════════════════════════════════════════
    def _sayfa_tarifler(self) -> QWidget:
        """
        Tüm tarifleri listeleyen sayfa.
        Üstte: Arama kutusu + kategori filtre butonları
        Altta: TarifKarti'ları barındıran scroll alanı
        """
        kap = QWidget()
        kap.setStyleSheet(f"background:{C.BG};")
        l = QVBoxLayout(kap)
        l.setContentsMargins(30, 24, 30, 24)
        l.setSpacing(18)

        # ─── Üst başlık satırı ───
        bas_sat = QHBoxLayout()
        bas_sat.setSpacing(14)

        baslik_kap = QVBoxLayout()
        baslik_kap.setSpacing(2)
        bas = QLabel("Tarif Koleksiyonu")
        bas.setStyleSheet(
            f"color:{C.TEXT};font-size:26px;font-weight:bold;"
            f"font-family:Georgia;letter-spacing:-0.5px;"
        )
        baslik_kap.addWidget(bas)
        alt_bas = QLabel("SEÇİLMİŞ YEMEK TARİFLERİ")
        alt_bas.setStyleSheet(
            f"color:{C.GOLD3};font-size:9px;font-weight:bold;letter-spacing:4px;"
        )
        baslik_kap.addWidget(alt_bas)
        bas_sat.addLayout(baslik_kap)
        bas_sat.addStretch()

        # Sağdaki "Yeni Tarif" kısayol butonu
        yeni_btn = btn_primary("+ YENİ TARİF", yukseklik=40)
        yeni_btn.setFixedWidth(160)
        yeni_btn.clicked.connect(lambda: self._sayfa_degistir(3))
        bas_sat.addWidget(yeni_btn)
        l.addLayout(bas_sat)

        vitrin = QFrame()
        vitrin.setStyleSheet(
            f"QFrame{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {C.CARD2},stop:0.55 {C.CARD},stop:1 {C.BG2});"
            f"border:none;border-radius:18px;}}"
        )
        vitrin_l = QHBoxLayout(vitrin)
        vitrin_l.setContentsMargins(26, 24, 26, 24)
        vitrin_l.setSpacing(24)

        vitrin_sol = QVBoxLayout()
        vitrin_sol.setSpacing(10)
        vitrin_sol.addWidget(etiket_kucuk("BUGUNUN MENUSU", C.GOLD2))

        self.tr_vitrin_baslik = QLabel("Mutfağını yeni tariflerle doldur")
        self.tr_vitrin_baslik.setStyleSheet(
            f"color:{C.TEXT};font-size:28px;font-weight:bold;"
            f"font-family:Georgia;background:transparent;border:none;"
        )
        self.tr_vitrin_baslik.setWordWrap(True)
        vitrin_sol.addWidget(self.tr_vitrin_baslik)

        self.tr_vitrin_alt = QLabel(
            "Koleksiyondaki öne çıkan tarifler burada görünecek."
        )
        self.tr_vitrin_alt.setStyleSheet(
            f"color:{C.TEXT2};font-size:12px;line-height:20px;"
            f"background:transparent;border:none;"
        )
        self.tr_vitrin_alt.setWordWrap(True)
        vitrin_sol.addWidget(self.tr_vitrin_alt)

        chip_sat = QHBoxLayout()
        chip_sat.setSpacing(10)
        self.tr_chip_toplam = QLabel("")
        self.tr_chip_sure = QLabel("")
        self.tr_chip_kolay = QLabel("")
        for chip, renk in [
            (self.tr_chip_toplam, C.GOLD),
            (self.tr_chip_sure, C.COPPER),
            (self.tr_chip_kolay, C.SAGE),
        ]:
            chip.setStyleSheet(
                f"color:{renk};background:{renk}15;border:none;"
                f"border-radius:9px;padding:8px 12px;font-size:11px;font-weight:bold;"
            )
            chip_sat.addWidget(chip)
        chip_sat.addStretch()
        vitrin_sol.addLayout(chip_sat)

        secim_btn = btn_ghost("One Cikani Ac", yukseklik=40)
        secim_btn.setFixedWidth(160)
        secim_btn.clicked.connect(self._tarif_one_cikan_ac)
        vitrin_sol.addWidget(secim_btn, 0, Qt.AlignLeft)
        vitrin_sol.addStretch()
        vitrin_l.addLayout(vitrin_sol, 3)

        vitrin_sag = QVBoxLayout()
        vitrin_sag.setSpacing(10)
        vitrin_sag.addWidget(etiket_kucuk("ONE CIKAN TARIFLER", C.GOLD3))
        self.tr_vitrin_kartlari = QVBoxLayout()
        self.tr_vitrin_kartlari.setSpacing(10)
        vitrin_sag.addLayout(self.tr_vitrin_kartlari)
        vitrin_sag.addStretch()
        vitrin_l.addLayout(vitrin_sag, 2)
        l.addWidget(vitrin)

        # ─── Arama + filtre çubuğu ───
        filt_kap = QFrame()
        filt_kap.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;"
            f"border-radius:12px;}}"
        )
        filt_l = QVBoxLayout(filt_kap)
        filt_l.setContentsMargins(20, 18, 20, 18)
        filt_l.setSpacing(14)

        # Arama satırı
        ara_sat = QHBoxLayout()
        ara_sat.setSpacing(10)
        ikon_lbl = QLabel("🔍")
        ikon_lbl.setStyleSheet(f"font-size:16px;color:{C.GOLD};border:none;background:transparent;")
        ara_sat.addWidget(ikon_lbl)

        self.tr_arama = form_input("Tarif adı, açıklama veya malzemede ara…")
        self.tr_arama.textChanged.connect(self._tarifler_yenile)
        ara_sat.addWidget(self.tr_arama, 1)
        filt_l.addLayout(ara_sat)

        # Kategori filtre butonları
        self.tr_aktif_kategori = None    # None = tümü
        filt_btn_sat = QHBoxLayout()
        filt_btn_sat.setSpacing(8)

        tumu_btn = btn_renkli("TÜMÜ", C.GOLD)
        tumu_btn.clicked.connect(lambda: self._kategori_sec(None))
        filt_btn_sat.addWidget(tumu_btn)

        for kat in Tarif.KATEGORILER:
            renk = KAT_RENK.get(kat, C.GOLD)
            b = btn_renkli(kat.upper(), renk)
            b.clicked.connect(lambda _, k=kat: self._kategori_sec(k))
            filt_btn_sat.addWidget(b)
        filt_btn_sat.addStretch()
        filt_l.addLayout(filt_btn_sat)
        l.addWidget(filt_kap)

        # ─── Sonuç etiketi ───
        self.tr_sonuc_lbl = QLabel("")
        self.tr_sonuc_lbl.setStyleSheet(
            f"color:{C.TEXT3};font-size:10px;font-weight:bold;letter-spacing:2px;"
        )
        l.addWidget(self.tr_sonuc_lbl)

        # ─── Scroll alan: TarifKartı'ları ───
        self.tr_scroll = QScrollArea()
        self.tr_scroll.setWidgetResizable(True)
        self.tr_scroll.setStyleSheet(
            f"QScrollArea{{background:{C.BG};border:none;}}"
            f"QScrollBar:vertical{{width:8px;background:transparent;}}"
            f"QScrollBar::handle:vertical{{background:{C.BORDER2};"
            f"border-radius:4px;min-height:20px;}}"
        )

        ic = QWidget()
        ic.setStyleSheet(f"background:{C.BG};")
        self.tr_liste_l = QVBoxLayout(ic)
        self.tr_liste_l.setContentsMargins(0, 0, 0, 0)
        self.tr_liste_l.setSpacing(10)
        self.tr_liste_l.addStretch()

        self.tr_scroll.setWidget(ic)
        l.addWidget(self.tr_scroll, 1)
        return kap

    def _kategori_sec(self, kategori):
        """Kategori filtre butonuna tıklandığında çalışır."""
        self.tr_aktif_kategori = kategori
        self._tarifler_yenile()

    def _tarif_vitrin_karti(self, tarif: dict) -> QWidget:
        """Tarif vitrini için kompakt, tıklanabilir kart."""
        renk = KAT_RENK.get(tarif.get("kategori"), C.GOLD)
        w = QFrame()
        w.setCursor(Qt.PointingHandCursor)
        w.setStyleSheet(
            f"QFrame{{background:{C.BG};border:none;"
            f"border-radius:12px;}}"
            f"QFrame:hover{{background:{C.CARD2};}}"
        )
        l = QVBoxLayout(w)
        l.setContentsMargins(16, 14, 16, 14)
        l.setSpacing(6)

        ust = QHBoxLayout()
        ust.setSpacing(8)
        kat = QLabel(tarif.get("kategori", "Tarif").upper())
        kat.setStyleSheet(
            f"color:{renk};background:{renk}18;border:none;"
            f"border-radius:7px;padding:3px 8px;font-size:9px;font-weight:bold;"
        )
        ust.addWidget(kat)
        ust.addStretch()
        puan = tarif.get("ort_puan") or 0
        puan_lbl = QLabel(f"★ {puan:.1f}" if puan else "Yeni")
        puan_lbl.setStyleSheet(
            f"color:{C.GOLD2};font-size:10px;font-weight:bold;background:transparent;"
        )
        ust.addWidget(puan_lbl)
        l.addLayout(ust)

        ad = QLabel(tarif["tarif_adi"])
        ad.setStyleSheet(
            f"color:{C.TEXT};font-size:13px;font-weight:bold;"
            f"font-family:Georgia;background:transparent;border:none;"
        )
        ad.setWordWrap(True)
        l.addWidget(ad)

        meta = QLabel(
            f"{tarif.get('hazirlama_suresi', 0)} dk  •  "
            f"{tarif.get('porsiyon', 0)} porsiyon  •  "
            f"{tarif.get('zorluk', 'Orta')}"
        )
        meta.setStyleSheet(
            f"color:{C.TEXT3};font-size:10px;background:transparent;border:none;"
        )
        l.addWidget(meta)

        def tikla(_event, tid=tarif["tarif_id"]):
            self._tarif_detay_ac(tid)

        w.mousePressEvent = tikla
        return w

    def _tarif_vitrin_yenile(self, gosterilen_tarifler: list, tum_tarifler: list):
        """Tarif sayfasındaki üst vitrin alanını günceller."""
        while self.tr_vitrin_kartlari.count():
            item = self.tr_vitrin_kartlari.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        kaynak = gosterilen_tarifler or tum_tarifler
        if not kaynak:
            self.tr_vitrin_baslik.setText("Koleksiyon henüz boş")
            self.tr_vitrin_alt.setText("İlk tarifi eklediğinizde bu alan önerilerle dolacak.")
            self.tr_chip_toplam.setText("0 tarif")
            self.tr_chip_sure.setText("Ortalama süre yok")
            self.tr_chip_kolay.setText("0 kolay seçim")
            bos = QLabel("Öne çıkan tarif görünmüyor.")
            bos.setStyleSheet(f"color:{C.TEXT3};font-size:11px;background:transparent;")
            self.tr_vitrin_kartlari.addWidget(bos)
            return

        istatistik_kaynagi = tum_tarifler or kaynak
        ort_sure = round(
            sum(t.get("hazirlama_suresi", 0) for t in kaynak) / len(kaynak)
        )
        kolay_sayisi = sum(1 for t in kaynak if t.get("zorluk") == "Kolay")
        kat_sayilari = {}
        for tarif in istatistik_kaynagi:
            kategori = tarif.get("kategori", "Tarif")
            kat_sayilari[kategori] = kat_sayilari.get(kategori, 0) + 1
        populer_kat = max(kat_sayilari, key=kat_sayilari.get)

        if self.tr_aktif_kategori:
            self.tr_vitrin_baslik.setText(f"{self.tr_aktif_kategori} tarifleri vitrinde")
        elif self.tr_arama.text().strip():
            self.tr_vitrin_baslik.setText("Arama sonuçlarından seçilen lezzetler")
        else:
            self.tr_vitrin_baslik.setText("Bu hafta menüde öne çıkanlar")

        self.tr_vitrin_alt.setText(
            f"{len(kaynak)} tarif incelenmeye hazır. Koleksiyonun en güçlü kategorisi "
            f"{populer_kat.lower()} ve ortalama hazırlık süresi {ort_sure} dakika."
        )
        self.tr_chip_toplam.setText(f"{len(kaynak)} tarif")
        self.tr_chip_sure.setText(f"Ort. {ort_sure} dk")
        self.tr_chip_kolay.setText(f"{kolay_sayisi} kolay seçim")

        secilenler = sorted(
            kaynak,
            key=lambda t: (
                -(t.get("ort_puan") or 0),
                -(t.get("puan_sayisi") or 0),
                t.get("hazirlama_suresi", 999),
            ),
        )[:3]
        for tarif in secilenler:
            self.tr_vitrin_kartlari.addWidget(self._tarif_vitrin_karti(tarif))

    def _tarif_one_cikan_ac(self):
        """Vitrindeki ilk uygun tarifi detay sayfasında açar."""
        tarifler = self.veri.istatistik.en_populer_tarifler(limit=1)
        if tarifler:
            self._tarif_detay_ac(tarifler[0]["tarif_id"])
            return
        tum_tarifler = self.veri.tarif.listele()
        if tum_tarifler:
            self._tarif_detay_ac(tum_tarifler[0]["tarif_id"])

    def _onerilen_tarifler(self, tarif: dict, limit: int = 3) -> list:
        """Aynı kategori veya benzer zorluktan öneriler döndürür."""
        tum_tarifler = self.veri.tarif.listele()
        adaylar = [t for t in tum_tarifler if t["tarif_id"] != tarif["tarif_id"]]
        ayni_kategori = [t for t in adaylar if t.get("kategori") == tarif.get("kategori")]
        ayni_zorluk = [t for t in adaylar if t.get("zorluk") == tarif.get("zorluk")]
        secilenler = ayni_kategori + [t for t in ayni_zorluk if t not in ayni_kategori]
        if len(secilenler) < limit:
            for tarif_adayi in adaylar:
                if tarif_adayi not in secilenler:
                    secilenler.append(tarif_adayi)
                if len(secilenler) >= limit:
                    break
        return secilenler[:limit]

    def _tarifler_yenile(self):
        """
        Arama ve kategori durumuna göre tarif listesini yeniden oluşturur.
        Tüm mevcut kartları temizler, yenilerini ekler.
        """
        # Önceki kartları kaldır (son stretch hariç)
        while self.tr_liste_l.count() > 1:
            item = self.tr_liste_l.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Arama metnini oku
        arama = self.tr_arama.text().strip() if hasattr(self, "tr_arama") else ""
        tum_tarifler = self.veri.tarif.listele()

        # Veritabanından tarifleri çek
        if arama:
            tarifler = self.veri.tarif.ara(arama)
            malzeme_sonuclari = self.veri.tarif.malzemeye_gore_ara([arama])
            eklenen_idler = {t["tarif_id"] for t in tarifler}
            for mt in malzeme_sonuclari:
                if mt["tarif_id"] not in eklenen_idler:
                    tarifler.append(mt)
                    eklenen_idler.add(mt["tarif_id"])
            
            if self.tr_aktif_kategori:
                tarifler = [t for t in tarifler if t["kategori"] == self.tr_aktif_kategori]
        else:
            tarifler = self.veri.tarif.listele(kategori=self.tr_aktif_kategori)

        self._tarif_vitrin_yenile(tarifler, tum_tarifler)

        # Sonuç etiketi
        if self.tr_aktif_kategori:
            self.tr_sonuc_lbl.setText(
                f"{len(tarifler)} SONUÇ · {self.tr_aktif_kategori.upper()} KATEGORİSİ"
            )
        else:
            self.tr_sonuc_lbl.setText(f"{len(tarifler)} TARİF LİSTELENDİ")

        if not tarifler:
            # Boş durum
            bos = QFrame()
            bos.setStyleSheet(
                f"QFrame{{background:{C.CARD};border:none;"
                f"border-radius:14px;}}"
            )
            bos_l = QVBoxLayout(bos)
            bos_l.setContentsMargins(30, 50, 30, 50)
            bos_l.setAlignment(Qt.AlignCenter)

            sem = QLabel("∅")
            sem.setAlignment(Qt.AlignCenter)
            sem.setStyleSheet(
                f"color:{C.GOLD3};font-size:48px;background:transparent;border:none;"
            )
            bos_l.addWidget(sem)
            msg = QLabel("Kriterlere uygun tarif bulunamadı")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet(
                f"color:{C.TEXT2};font-size:14px;background:transparent;border:none;"
            )
            bos_l.addWidget(msg)
            alt = QLabel("Farklı anahtar kelime veya kategori deneyin.")
            alt.setAlignment(Qt.AlignCenter)
            alt.setStyleSheet(
                f"color:{C.TEXT3};font-size:11px;background:transparent;border:none;"
            )
            bos_l.addWidget(alt)
            self.tr_liste_l.insertWidget(self.tr_liste_l.count() - 1, bos)
            return

        # Tarifleri kart olarak ekle
        for t in tarifler:
            kart = TarifKarti(t)
            kart.tiklandi.connect(self._tarif_detay_ac)
            self.tr_liste_l.insertWidget(self.tr_liste_l.count() - 1, kart)


    # ══════════════════════════════════════════════════════════════
    #  SAYFA 3: TARİF DETAYI
    # ══════════════════════════════════════════════════════════════
    def _sayfa_detay_konteyner(self) -> QWidget:
        """
        Detay sayfası için boş konteyner oluşturur.
        İçerik, bir kart tıklandığında _tarif_detay_ac(tid) ile doldurulur.
        """
        self.detay_scroll = QScrollArea()
        self.detay_scroll.setWidgetResizable(True)
        self.detay_scroll.setStyleSheet(
            f"QScrollArea{{background:{C.BG};border:none;}}"
            f"QScrollBar:vertical{{width:8px;background:transparent;}}"
            f"QScrollBar::handle:vertical{{background:{C.BORDER2};border-radius:4px;}}"
        )
        # İçerik dolduran yer tutucu widget
        bos = QWidget()
        bos.setStyleSheet(f"background:{C.BG};")
        self.detay_scroll.setWidget(bos)
        return self.detay_scroll

    def _tarif_detay_ac(self, tarif_id: int):
        """
        Belirtilen tarifin detay sayfasını oluşturur ve ona geçer.
        Malzemeleri, değerlendirmeleri ve yıldız derecelendirme widget'ını içerir.
        """
        tarif = self.veri.tarif.getir(tarif_id)
        if not tarif:
            Toast(self, "Tarif bulunamadı.", "hata")
            return

        malzemeler = self.veri.malzeme.listele(tarif_id)
        degerlendirmeler = self.veri.tarif.degerlendirmeler(tarif_id)
        ort_puan = self.veri.tarif.ortalama_puan(tarif_id)
        renk = KAT_RENK.get(tarif["kategori"], C.GOLD)

        # Ana içerik widget
        ic = QWidget()
        ic.setStyleSheet(f"background:{C.BG};")
        ana_l = QVBoxLayout(ic)
        ana_l.setContentsMargins(30, 24, 30, 30)
        ana_l.setSpacing(20)

        # ─── Geri dönüş butonu ve Favoriler ───
        geri_sat = QHBoxLayout()
        geri_btn = btn_ghost("← TARİFLERE DÖN", yukseklik=34)
        geri_btn.setFixedWidth(170)
        geri_btn.clicked.connect(lambda: self._sayfa_degistir(1))
        geri_sat.addWidget(geri_btn)
        geri_sat.addStretch()

        pdf_btn = btn_ghost("📄 PDF İndir", yukseklik=34)
        pdf_btn.clicked.connect(lambda: self._pdf_indir(tarif_id))
        geri_sat.addWidget(pdf_btn)

        if self.veri.aktif_kullanici:
            kid = self.veri.aktif_kullanici["kullanici_id"]
            is_fav = self.veri.kullanici.favori_mi(kid, tarif_id)
            fav_metin = "💖 Favorilerde" if is_fav else "🤍 Favoriye Ekle"
            fav_btn = btn_ghost(fav_metin, yukseklik=34)
            def favori_tikla():
                res = self.veri.kullanici.favori_ekle_cikar(kid, tarif_id)
                if res["basarili"]:
                    if res["durum"] == "eklendi":
                        fav_btn.setText("💖 Favorilerde")
                    else:
                        fav_btn.setText("🤍 Favoriye Ekle")
                    Toast(self, res["mesaj"], "basari")
            fav_btn.clicked.connect(favori_tikla)
            geri_sat.addWidget(fav_btn)

        # Admin için tarif silme butonu
        if self._admin_mi():
            sil_btn = QPushButton("🗑  TARİFİ SİL")
            sil_btn.setCursor(Qt.PointingHandCursor)
            sil_btn.setFixedHeight(34)
            sil_btn.setStyleSheet(
                f"QPushButton{{background:transparent;color:{C.WINE2};"
                f"border:1px solid {C.WINE2}80;border-radius:8px;"
                f"padding:0 14px;font-size:11px;font-weight:bold;letter-spacing:1px;}}"
                f"QPushButton:hover{{background:{C.WINE2}20;border-color:{C.WINE2};color:#f5ece0;}}"
            )
            sil_btn.clicked.connect(lambda: self._admin_tarif_sil(tarif_id, tarif["tarif_adi"]))
            geri_sat.addWidget(sil_btn)

        ana_l.addLayout(geri_sat)

        # ─── GÖRSEL EKLENTİSİ ───
        gorsel_yolu = tarif.get("gorsel_yolu")
        if gorsel_yolu:
            tam_yol = os.path.join(os.path.dirname(os.path.abspath(__file__)), gorsel_yolu)
            if os.path.exists(tam_yol):
                resim_lbl = QLabel()
                resim_lbl.setFixedHeight(220)
                pixmap = QPixmap(tam_yol)
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(800, 220, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
                    resim_lbl.setPixmap(pixmap)
                    resim_lbl.setAlignment(Qt.AlignCenter)
                    resim_lbl.setStyleSheet(f"background:{C.CARD}; border-radius:16px; margin-bottom:10px;")
                    ana_l.addWidget(resim_lbl)

        # ─── HERO KART: Tarif başlığı + meta ───
        hero = QFrame()
        hero.setStyleSheet(
            f"QFrame{{background:qlineargradient(x1:0,y1:0,x2:1,y2:1,"
            f"stop:0 {C.CARD2},stop:1 {C.CARD});"
            f"border:none;border-radius:16px;}}"
        )
        hero_l = QVBoxLayout(hero)
        hero_l.setContentsMargins(30, 24, 30, 24)
        hero_l.setSpacing(10)

        # Üst: kategori rozeti + büyük başlık
        kat_lbl = QLabel(tarif["kategori"].upper())
        kat_lbl.setFixedWidth(100)
        kat_lbl.setAlignment(Qt.AlignCenter)
        kat_lbl.setStyleSheet(
            f"color:{renk};background:{renk}18;padding:5px 10px;"
            f"border-radius:7px;font-size:9px;font-weight:bold;"
            f"letter-spacing:2px;border:none;"
        )
        hero_l.addWidget(kat_lbl)

        ad_lbl = QLabel(tarif["tarif_adi"])
        ad_lbl.setStyleSheet(
            f"color:{C.TEXT};font-size:36px;font-weight:bold;"
            f"font-family:Georgia;background:transparent;border:none;"
            f"letter-spacing:-1px;"
        )
        hero_l.addWidget(ad_lbl)

        # Açıklama
        if tarif.get("aciklama"):
            ack = QLabel(tarif["aciklama"])
            ack.setWordWrap(True)
            ack.setStyleSheet(
                f"color:{C.TEXT2};font-size:13px;line-height:20px;"
                f"background:transparent;border:none;font-style:italic;"
            )
            hero_l.addWidget(ack)

        # Meta satırı: sure/porsiyon/zorluk/ortalama puan
        meta_kap = QHBoxLayout()
        meta_kap.setSpacing(30)
        meta_kap.setContentsMargins(0, 14, 0, 0)
        for ikon, etk, deger, r in [
            ("⏱",  "SÜRE",      f"{tarif['hazirlama_suresi']} dk",   C.GOLD),
            ("♦",  "PORSİYON",  f"{tarif.get('porsiyon', 4)} kişi",  C.COPPER),
            ("◉",  "ZORLUK",    tarif.get('zorluk', 'Orta'),
                                 ZOR_RENK.get(tarif.get('zorluk', 'Orta'), C.GOLD)),
            ("★",  "PUAN",      f"{ort_puan:.1f} / 5.0" if ort_puan else "—", C.GOLD),
            ("👤", "EKLEYEN",   tarif.get('ekleyen', '—'),           C.TEXT2),
        ]:
            kap = QVBoxLayout()
            kap.setSpacing(2)
            ust = QLabel(f"{ikon}  {etk}")
            ust.setStyleSheet(
                f"color:{C.TEXT3};font-size:9px;font-weight:bold;"
                f"letter-spacing:2px;background:transparent;border:none;"
            )
            kap.addWidget(ust)
            alt = QLabel(deger)
            alt.setStyleSheet(
                f"color:{r};font-size:15px;font-weight:bold;"
                f"font-family:Georgia;background:transparent;border:none;"
            )
            kap.addWidget(alt)
            meta_kap.addLayout(kap)
        meta_kap.addStretch()
        hero_l.addLayout(meta_kap)
        ana_l.addWidget(hero)

        bilgi_sat = QHBoxLayout()
        bilgi_sat.setSpacing(20)

        ozet_kart = QFrame()
        ozet_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;border-radius:14px;}}"
        )
        ozet_l = QVBoxLayout(ozet_kart)
        ozet_l.setContentsMargins(22, 18, 22, 18)
        ozet_l.setSpacing(10)
        ozet_l.addWidget(etiket_kucuk("SEF NOTU", C.GOLD))
        ozet_l.addWidget(ayrac())

        sunum_yazi = tarif.get("sunum") or (
            "Sunum önerisi eklenmemiş; bu tarifi sade tabakta taze otlarla tamamlayabilirsiniz."
        )
        sunum_lbl = QLabel(sunum_yazi)
        sunum_lbl.setWordWrap(True)
        sunum_lbl.setStyleSheet(
            f"color:{C.TEXT2};font-size:11px;line-height:18px;background:transparent;border:none;"
        )
        ozet_l.addWidget(sunum_lbl)

        yorum_ozet = QLabel(
            f"{len(degerlendirmeler)} yorum  •  Ortalama {ort_puan:.1f}" if degerlendirmeler
            else "Henüz yorum yok  •  İlk değerlendirmeyi siz bırakın"
        )
        yorum_ozet.setStyleSheet(
            f"color:{C.GOLD2};font-size:11px;font-weight:bold;background:transparent;border:none;"
        )
        ozet_l.addWidget(yorum_ozet)
        
        if self.veri.aktif_kullanici:
            ozet_l.addSpacing(10)
            ozet_l.addWidget(ayrac())
            ozet_l.addWidget(etiket_kucuk("KİŞİSEL ŞEF NOTUNUZ", C.GOLD3))
            mevcut_not = self.veri.kullanici.not_getir(self.veri.aktif_kullanici["kullanici_id"], tarif_id)
            not_inp = QTextEdit()
            not_inp.setPlaceholderText("Bu tarif için gizli püf noktalarınızı buraya yazın...")
            not_inp.setPlainText(mevcut_not)
            not_inp.setFixedHeight(60)
            not_inp.setStyleSheet(
                f"QTextEdit{{background:{C.BG};color:{C.TEXT2};"
                f"border:1px solid {C.BORDER2};border-radius:8px;padding:8px;font-size:11px;}}"
                f"QTextEdit:focus{{border-color:{C.GOLD};}}"
            )
            ozet_l.addWidget(not_inp)
            not_kaydet_btn = btn_ghost("Notu Kaydet", yukseklik=28)
            def not_kaydet_tikla():
                self.veri.kullanici.not_kaydet(self.veri.aktif_kullanici["kullanici_id"], tarif_id, not_inp.toPlainText())
                Toast(self, "Şef notunuz başarıyla kaydedildi.", "basari")
            not_kaydet_btn.clicked.connect(not_kaydet_tikla)
            ozet_l.addWidget(not_kaydet_btn, 0, Qt.AlignRight)

        bilgi_sat.addWidget(ozet_kart, 1)

        oner_kart = QFrame()
        oner_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;border-radius:14px;}}"
        )
        oner_l = QVBoxLayout(oner_kart)
        oner_l.setContentsMargins(22, 18, 22, 18)
        oner_l.setSpacing(10)
        oner_l.addWidget(etiket_kucuk("BENZER TARIFLER", C.GOLD))
        oner_l.addWidget(ayrac())
        oneriler = self._onerilen_tarifler(tarif, limit=3)
        if oneriler:
            for onerilen in oneriler:
                sat = QFrame()
                sat.setCursor(Qt.PointingHandCursor)
                sat.setStyleSheet(
                    f"QFrame{{background:{C.BG};border:none;border-radius:10px;}}"
                    f"QFrame:hover{{background:{C.CARD2};}}"
                )
                sat_l = QHBoxLayout(sat)
                sat_l.setContentsMargins(12, 10, 12, 10)
                sat_l.setSpacing(10)
                nokta = QLabel("●")
                nokta.setStyleSheet(f"color:{KAT_RENK.get(onerilen['kategori'], C.GOLD)};font-size:12px;")
                sat_l.addWidget(nokta)
                isim = QLabel(onerilen["tarif_adi"])
                isim.setStyleSheet(
                    f"color:{C.TEXT};font-size:11px;font-weight:bold;background:transparent;border:none;"
                )
                sat_l.addWidget(isim, 1)
                meta = QLabel(f"{onerilen.get('hazirlama_suresi', 0)} dk")
                meta.setStyleSheet(f"color:{C.TEXT3};font-size:10px;background:transparent;border:none;")
                sat_l.addWidget(meta)

                def oner_tikla(_event, tid=onerilen["tarif_id"]):
                    self._tarif_detay_ac(tid)

                sat.mousePressEvent = oner_tikla
                oner_l.addWidget(sat)
        else:
            bos_oner = QLabel("Gösterilecek benzer tarif bulunamadı.")
            bos_oner.setStyleSheet(
                f"color:{C.TEXT3};font-size:11px;font-style:italic;background:transparent;border:none;"
            )
            oner_l.addWidget(bos_oner)
        bilgi_sat.addWidget(oner_kart, 1)
        ana_l.addLayout(bilgi_sat)

        # ─── ORTA: Malzemeler (sol) + Yapılışı (sağ) ───
        orta_sat = QHBoxLayout()
        orta_sat.setSpacing(20)

        # Sol: Malzemeler kartı
        mal_kart = QFrame()
        mal_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;"
            f"border-radius:14px;}}"
        )
        mal_kart.setFixedWidth(340)
        mal_l = QVBoxLayout(mal_kart)
        mal_l.setContentsMargins(22, 20, 22, 22)
        mal_l.setSpacing(10)

        mal_bas = QHBoxLayout()
        mal_bas.addWidget(etiket_kucuk("MALZEMELER", C.GOLD))
        
        # PORSİYON HESAPLAYICI
        self.guncel_porsiyon = tarif.get("porsiyon", 4)
        if not isinstance(self.guncel_porsiyon, int):
            self.guncel_porsiyon = 4
        self.orijinal_porsiyon = self.guncel_porsiyon
        
        mal_bas.addStretch()
        
        btn_azalt = QPushButton("−")
        btn_azalt.setFixedSize(22, 22)
        btn_azalt.setStyleSheet(f"background:{C.CARD2};color:{C.GOLD};border-radius:11px;font-weight:bold;font-size:12px;border:none;")
        btn_azalt.setCursor(Qt.PointingHandCursor)
        
        self.lbl_porsiyon_goster = QLabel(f"{self.guncel_porsiyon} Kişilik")
        self.lbl_porsiyon_goster.setStyleSheet(f"color:{C.TEXT};font-size:11px;font-weight:bold;padding:0 5px;")
        
        btn_artir = QPushButton("+")
        btn_artir.setFixedSize(22, 22)
        btn_artir.setStyleSheet(btn_azalt.styleSheet())
        btn_artir.setCursor(Qt.PointingHandCursor)
        
        mal_bas.addWidget(btn_azalt)
        mal_bas.addWidget(self.lbl_porsiyon_goster)
        mal_bas.addWidget(btn_artir)
        mal_bas.addSpacing(15)

        say = QLabel(f"{len(malzemeler)} adet")
        say.setStyleSheet(
            f"color:{C.TEXT3};font-size:9px;background:transparent;border:none;"
        )
        mal_bas.addWidget(say)
        mal_l.addLayout(mal_bas)
        mal_l.addWidget(ayrac())
        mal_l.addSpacing(4)

        self.malzeme_etiketleri = []

        if malzemeler:
            for m in malzemeler:
                sat = QHBoxLayout()
                sat.setSpacing(10)
                nokta = QLabel("◆")
                nokta.setStyleSheet(
                    f"color:{C.GOLD};font-size:8px;background:transparent;border:none;"
                )
                sat.addWidget(nokta)
                ad = QLabel(m["malzeme_adi"])
                ad.setStyleSheet(
                    f"color:{C.TEXT};font-size:12px;background:transparent;border:none;"
                )
                sat.addWidget(ad)
                sat.addStretch()
                mik = QLabel(f"{m['miktar']} {m['birim']}".strip())
                mik.setStyleSheet(
                    f"color:{C.GOLD2};font-size:12px;font-weight:bold;"
                    f"font-family:Georgia;background:transparent;border:none;"
                )
                sat.addWidget(mik)
                mal_l.addLayout(sat)
                self.malzeme_etiketleri.append((mik, m['miktar'], m['birim']))
                
            def _miktar_sayiya_cevir(s):
                try:
                    s = s.replace(",", ".")
                    if "/" in s:
                        parcalar = s.split("/")
                        if len(parcalar) == 2:
                            return float(parcalar[0]) / float(parcalar[1])
                    return float(s)
                except:
                    return None
                    
            def _sayiyi_metne_cevir(num):
                if num.is_integer():
                    return str(int(num))
                return f"{num:.1f}".replace(".", ",")

            def _porsiyon_guncelle(artis):
                self.guncel_porsiyon += artis
                if self.guncel_porsiyon < 1:
                    self.guncel_porsiyon = 1
                self.lbl_porsiyon_goster.setText(f"{self.guncel_porsiyon} Kişilik")
                
                oran = self.guncel_porsiyon / self.orijinal_porsiyon
                for lbl, orj_mik, birim in self.malzeme_etiketleri:
                    sayi = _miktar_sayiya_cevir(orj_mik)
                    if sayi is not None:
                        yeni_sayi = sayi * oran
                        lbl.setText(f"{_sayiyi_metne_cevir(yeni_sayi)} {birim}".strip())
                    else:
                        lbl.setText(f"{orj_mik} {birim}".strip())
                        
            btn_azalt.clicked.connect(lambda: _porsiyon_guncelle(-1))
            btn_artir.clicked.connect(lambda: _porsiyon_guncelle(1))
        else:
            bos_mal = QLabel("Bu tarife henüz malzeme eklenmemiş.")
            bos_mal.setStyleSheet(
                f"color:{C.TEXT3};font-size:11px;font-style:italic;"
                f"background:transparent;border:none;padding:18px 0;"
            )
            bos_mal.setAlignment(Qt.AlignCenter)
            mal_l.addWidget(bos_mal)
        mal_l.addStretch()
        
        if self.veri.aktif_kullanici and malzemeler:
            listeye_ekle_btn = btn_ghost("🛒 Tümünü Listeye Ekle", yukseklik=28)
            def _listeye_ekle():
                res = self.veri.kullanici.alisveris_listesine_ekle(self.veri.aktif_kullanici["kullanici_id"], malzemeler)
                if res["basarili"]:
                    Toast(self, "Malzemeler alışveriş listenize eklendi.", "basari")
                else:
                    Toast(self, "Bir hata oluştu.", "hata")
            listeye_ekle_btn.clicked.connect(_listeye_ekle)
            mal_l.addWidget(listeye_ekle_btn)
            
        orta_sat.addWidget(mal_kart)

        # Sağ: Yapılışı kartı
        yap_kart = QFrame()
        yap_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;"
            f"border-radius:14px;}}"
        )
        yap_l = QVBoxLayout(yap_kart)
        yap_l.setContentsMargins(24, 20, 24, 22)
        yap_l.setSpacing(10)
        yap_l.addWidget(etiket_kucuk("HAZIRLANIŞI", C.GOLD))
        yap_l.addWidget(ayrac())
        yap_l.addSpacing(6)

        yap_metin = tarif.get("yapilis") or "Yapılış adımları girilmemiş."
        yap_lbl = QLabel(yap_metin)
        yap_lbl.setWordWrap(True)
        yap_lbl.setStyleSheet(
            f"color:{C.TEXT};font-size:12px;line-height:22px;"
            f"background:transparent;border:none;"
        )
        yap_l.addWidget(yap_lbl)
        yap_l.addStretch()
        orta_sat.addWidget(yap_kart, 1)
        ana_l.addLayout(orta_sat)

        # ─── DERECELENDİRME KARTI ───
        der_kart = QFrame()
        der_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;"
            f"border-radius:14px;}}"
        )
        der_l = QVBoxLayout(der_kart)
        der_l.setContentsMargins(24, 22, 24, 22)
        der_l.setSpacing(14)

        der_bas_sat = QHBoxLayout()
        der_bas_sat.addWidget(etiket_kucuk("DEĞERLENDİR", C.GOLD))
        der_bas_sat.addStretch()
        der_l.addLayout(der_bas_sat)

        if self.veri.aktif_kullanici:
            # Mevcut puanı (varsa) kontrol et
            kid = self.veri.aktif_kullanici["kullanici_id"]
            mevcut_puan = 0
            for d in degerlendirmeler:
                if d["kullanici_id"] == kid:
                    mevcut_puan = d["puan"]
                    break

            aciklama_txt = (
                f"Mevcut puanınız: {mevcut_puan}/5" if mevcut_puan
                else "Bu tarife puan vererek değerlendirin."
            )
            ack = QLabel(aciklama_txt)
            ack.setStyleSheet(
                f"color:{C.TEXT2};font-size:11px;background:transparent;border:none;"
            )
            der_l.addWidget(ack)

            # Yıldız widget (etkileşimli)
            yld_sat = QHBoxLayout()
            yld_sat.setSpacing(16)
            yld_widget = YildizDerecelendirme(mevcut_puan, salt_okunur=False, boyut=32)
            yld_widget.setStyleSheet("background:transparent;border:none;")
            yld_sat.addWidget(yld_widget)

            # Ad Soyad alanı
            ad_soyad_inp = QLineEdit()
            ad_soyad_inp.setPlaceholderText("Ad Soyad...")
            ad_soyad_inp.setFixedHeight(40)
            ad_soyad_inp.setFixedWidth(150)
            ad_soyad_inp.setStyleSheet(
                f"QLineEdit{{background:{C.BG};color:{C.TEXT};"
                f"border:none;border-radius:8px;"
                f"padding:0 14px;font-size:12px;}}"
                f"QLineEdit:focus{{background:{C.BG2};}}"
            )
            yld_sat.addWidget(ad_soyad_inp)

            # Yorum alanı
            yorum_inp = QLineEdit()
            yorum_inp.setPlaceholderText("Opsiyonel yorum ekleyin…")
            yorum_inp.setFixedHeight(40)
            yorum_inp.setStyleSheet(
                f"QLineEdit{{background:{C.BG};color:{C.TEXT};"
                f"border:none;border-radius:8px;"
                f"padding:0 14px;font-size:12px;}}"
                f"QLineEdit:focus{{background:{C.BG2};}}"
            )
            yld_sat.addWidget(yorum_inp, 1)

            gonder_btn = btn_primary("PUAN VER", yukseklik=40)
            gonder_btn.setFixedWidth(130)
            yld_sat.addWidget(gonder_btn)
            der_l.addLayout(yld_sat)

            def puan_gonder():
                secili_puan = yld_widget.puan
                if secili_puan < 1:
                    Toast(self, "Lütfen önce yıldız seçin.", "bilgi")
                    return
                ad_soyad = ad_soyad_inp.text().strip()
                if not ad_soyad:
                    Toast(self, "Lütfen ad ve soyadınızı girin.", "bilgi")
                    return
                yorum_metni = yorum_inp.text().strip()
                birlestirilmis_yorum = f"{ad_soyad} - {yorum_metni}" if yorum_metni else f"{ad_soyad} tarafından puanlandı."
                
                sonuc = self.veri.kullanici.tarif_degerlendir(
                    kid, tarif_id, int(secili_puan), birlestirilmis_yorum
                )
                if sonuc["basarili"]:
                    Toast(self, sonuc["mesaj"], "basari")
                    log(f"Değerlendirme: {tarif['tarif_adi']} ({int(secili_puan)}/5)", C.GOLD)
                    # Detay sayfasını yenile
                    self._tarif_detay_ac(tarif_id)
                else:
                    Toast(self, sonuc["mesaj"], "hata")
            gonder_btn.clicked.connect(puan_gonder)
        else:
            giris_uyari = QLabel("Puan vermek için giriş yapmanız gerekir.")
            giris_uyari.setStyleSheet(
                f"color:{C.TEXT3};font-size:11px;font-style:italic;"
                f"background:transparent;border:none;"
            )
            der_l.addWidget(giris_uyari)
        ana_l.addWidget(der_kart)

        # ─── YORUMLAR LİSTESİ ───
        yor_kart = QFrame()
        yor_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;"
            f"border-radius:14px;}}"
        )
        yor_l = QVBoxLayout(yor_kart)
        yor_l.setContentsMargins(24, 22, 24, 22)
        yor_l.setSpacing(12)

        yor_bas = QHBoxLayout()
        yor_bas.addWidget(etiket_kucuk(
            f"DEĞERLENDİRMELER · {len(degerlendirmeler)}", C.GOLD
        ))
        yor_bas.addStretch()
        yor_l.addLayout(yor_bas)
        yor_l.addWidget(ayrac())

        if degerlendirmeler:
            for d in degerlendirmeler:
                sat = QFrame()
                sat.setStyleSheet(
                    f"QFrame{{background:{C.BG};border:none;"
                    f"border-radius:10px;}}"
                )
                sat_l = QVBoxLayout(sat)
                sat_l.setContentsMargins(14, 10, 14, 10)
                sat_l.setSpacing(6)

                ust = QHBoxLayout()
                
                yorum_metni_ham = d.get("yorum", "")
                gosterilecek_isim = d["kullanici_adi"]
                gosterilecek_yorum = yorum_metni_ham

                if " - " in yorum_metni_ham:
                    parcalar = yorum_metni_ham.split(" - ", 1)
                    gosterilecek_isim = parcalar[0]
                    gosterilecek_yorum = parcalar[1]
                elif " tarafından puanlandı." in yorum_metni_ham:
                    gosterilecek_isim = yorum_metni_ham.replace(" tarafından puanlandı.", "")
                    gosterilecek_yorum = ""

                isim = QLabel(gosterilecek_isim)
                isim.setStyleSheet(
                    f"color:{C.TEXT};font-size:12px;font-weight:bold;"
                    f"background:transparent;border:none;"
                )
                ust.addWidget(isim)
                ust.addStretch()
                # Yıldızları metin olarak
                yld_metin = "★" * d["puan"] + "☆" * (5 - d["puan"])
                yld = QLabel(yld_metin)
                yld.setStyleSheet(
                    f"color:{C.GOLD};font-size:13px;background:transparent;border:none;"
                )
                ust.addWidget(yld)

                # Admin için yorum silme butonu (×)
                if self._admin_mi():
                    yorum_sil_btn = QPushButton("×")
                    yorum_sil_btn.setCursor(Qt.PointingHandCursor)
                    yorum_sil_btn.setFixedSize(22, 22)
                    yorum_sil_btn.setToolTip("Yorumu sil (admin)")
                    yorum_sil_btn.setStyleSheet(
                        f"QPushButton{{background:transparent;color:{C.WINE2};"
                        f"border:1px solid {C.WINE2}60;border-radius:11px;"
                        f"font-size:14px;font-weight:bold;}}"
                        f"QPushButton:hover{{background:{C.WINE2};color:#f5ece0;border-color:{C.WINE2};}}"
                    )
                    deg_id = d["degerlendirme_id"]
                    yorum_sil_btn.clicked.connect(
                        lambda _=False, did=deg_id, tid=tarif_id: self._admin_yorum_sil(did, tid)
                    )
                    ust.addWidget(yorum_sil_btn)

                sat_l.addLayout(ust)

                if gosterilecek_yorum:
                    y = QLabel(gosterilecek_yorum)
                    y.setWordWrap(True)
                    y.setStyleSheet(
                        f"color:{C.TEXT2};font-size:11px;line-height:17px;"
                        f"background:transparent;border:none;font-style:italic;"
                    )
                    sat_l.addWidget(y)
                yor_l.addWidget(sat)
        else:
            bos_yor = QLabel("Henüz değerlendirme yapılmamış. İlk yorumu siz yapın!")
            bos_yor.setAlignment(Qt.AlignCenter)
            bos_yor.setStyleSheet(
                f"color:{C.TEXT3};font-size:11px;font-style:italic;"
                f"background:transparent;border:none;padding:16px;"
            )
            yor_l.addWidget(bos_yor)
        ana_l.addWidget(yor_kart)
        ana_l.addStretch()

        # Scroll alana yeni içeriği yerleştir
        self.detay_scroll.setWidget(ic)

        # Detay sayfasına geç
        self.sayfalar.setCurrentIndex(2)
        self._aktif_sayfa_guncelle(2)


    # ══════════════════════════════════════════════════════════════
    #  SAYFA 4: YENİ TARİF EKLEME FORMU
    # ══════════════════════════════════════════════════════════════
    def _sayfa_yeni_tarif(self) -> QWidget:
        """
        Yeni tarif oluşturma formu.
        Tarif bilgileri + dinamik malzeme satırları (ekle/kaldır).
        """
        kap = QScrollArea()
        kap.setWidgetResizable(True)
        kap.setStyleSheet(
            f"QScrollArea{{background:{C.BG};border:none;}}"
            f"QScrollBar:vertical{{width:8px;background:transparent;}}"
            f"QScrollBar::handle:vertical{{background:{C.BORDER2};border-radius:4px;}}"
        )

        ic = QWidget()
        ic.setStyleSheet(f"background:{C.BG};")
        ana_l = QVBoxLayout(ic)
        ana_l.setContentsMargins(30, 24, 30, 30)
        ana_l.setSpacing(20)

        # Başlık
        bas_kap = QVBoxLayout()
        bas_kap.setSpacing(2)
        bas = QLabel("Yeni Tarif Oluştur")
        bas.setStyleSheet(
            f"color:{C.TEXT};font-size:26px;font-weight:bold;"
            f"font-family:Georgia;letter-spacing:-0.5px;"
        )
        bas_kap.addWidget(bas)
        alt = QLabel("TARİF BİLGİLERİNİ GİRİN")
        alt.setStyleSheet(
            f"color:{C.GOLD3};font-size:9px;font-weight:bold;letter-spacing:4px;"
        )
        bas_kap.addWidget(alt)
        ana_l.addLayout(bas_kap)

        # ─── Ana bilgi kartı ───
        bilgi_kart = QFrame()
        bilgi_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;"
            f"border-radius:14px;}}"
        )
        bilgi_l = QVBoxLayout(bilgi_kart)
        bilgi_l.setContentsMargins(24, 22, 24, 22)
        bilgi_l.setSpacing(14)

        bilgi_l.addWidget(etiket_kucuk("TARİF BİLGİLERİ", C.GOLD))
        bilgi_l.addWidget(ayrac())
        self.secilen_gorsel_yolu = ""

        # Görsel seçimi
        gorsel_kap = QHBoxLayout()
        self.lbl_gorsel_ad = QLabel("Görsel seçilmedi")
        self.lbl_gorsel_ad.setStyleSheet(f"color:{C.TEXT3};font-size:11px;font-style:italic;")
        btn_gorsel = btn_ghost("Fotoğraf Seç", yukseklik=28)
        
        def _gorsel_sec():
            dosya, _ = QFileDialog.getOpenFileName(self, "Fotoğraf Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg)")
            if dosya:
                self.secilen_gorsel_yolu = dosya
                self.lbl_gorsel_ad.setText(os.path.basename(dosya))
                
        btn_gorsel.clicked.connect(_gorsel_sec)
        gorsel_kap.addWidget(self.lbl_gorsel_ad)
        gorsel_kap.addStretch()
        gorsel_kap.addWidget(btn_gorsel)
        bilgi_l.addLayout(gorsel_kap)

        # Tarif adı
        lbl_ad = QLabel("Tarif Adı")
        lbl_ad.setStyleSheet(f"color:{C.TEXT2};font-size:11px;font-weight:bold;")
        bilgi_l.addWidget(lbl_ad)
        self.yt_ad = form_input("Ör: Karnıyarık")
        bilgi_l.addWidget(self.yt_ad)

        # Açıklama
        lbl_ack = QLabel("Açıklama")
        lbl_ack.setStyleSheet(f"color:{C.TEXT2};font-size:11px;font-weight:bold;")
        bilgi_l.addWidget(lbl_ack)
        self.yt_aciklama = QTextEdit()
        self.yt_aciklama.setPlaceholderText("Kısa bir tanıtım…")
        self.yt_aciklama.setFixedHeight(70)
        self.yt_aciklama.setStyleSheet(
            f"QTextEdit{{background:{C.BG};color:{C.TEXT};"
            f"border:none;border-radius:8px;"
            f"padding:10px;font-size:12px;}}"
            f"QTextEdit:focus{{background:{C.BG2};}}"
        )
        bilgi_l.addWidget(self.yt_aciklama)

        # Yapılışı
        lbl_yap = QLabel("Hazırlanışı")
        lbl_yap.setStyleSheet(f"color:{C.TEXT2};font-size:11px;font-weight:bold;")
        bilgi_l.addWidget(lbl_yap)
        self.yt_yapilis = QTextEdit()
        self.yt_yapilis.setPlaceholderText("Adım adım tarifi yazın…")
        self.yt_yapilis.setFixedHeight(100)
        self.yt_yapilis.setStyleSheet(
            f"QTextEdit{{background:{C.BG};color:{C.TEXT};"
            f"border:none;border-radius:8px;"
            f"padding:10px;font-size:12px;}}"
            f"QTextEdit:focus{{background:{C.BG2};}}"
        )
        bilgi_l.addWidget(self.yt_yapilis)

        # Satır: Kategori + Zorluk + Süre + Porsiyon
        param_sat = QHBoxLayout()
        param_sat.setSpacing(14)

        # Kategori seçimi
        kat_kap = QVBoxLayout()
        kat_kap.setSpacing(4)
        kat_lbl = QLabel("Kategori")
        kat_lbl.setStyleSheet(f"color:{C.TEXT2};font-size:11px;font-weight:bold;")
        kat_kap.addWidget(kat_lbl)
        self.yt_kategori = QComboBox()
        self.yt_kategori.addItems(Tarif.KATEGORILER)
        self.yt_kategori.setFixedHeight(40)
        self.yt_kategori.setStyleSheet(
            f"QComboBox{{background:{C.BG};color:{C.TEXT};"
            f"border:none;border-radius:8px;"
            f"padding:0 12px;font-size:12px;}}"
            f"QComboBox:focus{{background:{C.BG2};}}"
            f"QComboBox::drop-down{{border:none;}}"
            f"QComboBox QAbstractItemView{{background:{C.CARD};"
            f"color:{C.TEXT};selection-background-color:{C.GOLD3};"
            f"border:none;border-radius:6px;}}"
        )
        kat_kap.addWidget(self.yt_kategori)
        param_sat.addLayout(kat_kap)

        # Zorluk seçimi
        zor_kap = QVBoxLayout()
        zor_kap.setSpacing(4)
        zor_lbl = QLabel("Zorluk")
        zor_lbl.setStyleSheet(f"color:{C.TEXT2};font-size:11px;font-weight:bold;")
        zor_kap.addWidget(zor_lbl)
        self.yt_zorluk = QComboBox()
        self.yt_zorluk.addItems(Tarif.ZORLUK_SEVIYELERI)
        self.yt_zorluk.setCurrentText("Orta")
        self.yt_zorluk.setFixedHeight(40)
        self.yt_zorluk.setStyleSheet(self.yt_kategori.styleSheet())
        zor_kap.addWidget(self.yt_zorluk)
        param_sat.addLayout(zor_kap)

        # Süre (dakika)
        sure_kap = QVBoxLayout()
        sure_kap.setSpacing(4)
        sure_lbl = QLabel("Süre (dk)")
        sure_lbl.setStyleSheet(f"color:{C.TEXT2};font-size:11px;font-weight:bold;")
        sure_kap.addWidget(sure_lbl)
        self.yt_sure = QSpinBox()
        self.yt_sure.setRange(1, 999)
        self.yt_sure.setValue(30)
        self.yt_sure.setSuffix(" dk")
        self.yt_sure.setFixedHeight(40)
        self.yt_sure.setStyleSheet(
            f"QSpinBox{{background:{C.BG};color:{C.TEXT};"
            f"border:none;border-radius:8px;"
            f"padding:0 12px;font-size:12px;}}"
            f"QSpinBox:focus{{background:{C.BG2};}}"
            f"QSpinBox::up-button,QSpinBox::down-button{{width:16px;}}"
        )
        sure_kap.addWidget(self.yt_sure)
        param_sat.addLayout(sure_kap)

        # Porsiyon
        por_kap = QVBoxLayout()
        por_kap.setSpacing(4)
        por_lbl = QLabel("Porsiyon")
        por_lbl.setStyleSheet(f"color:{C.TEXT2};font-size:11px;font-weight:bold;")
        por_kap.addWidget(por_lbl)
        self.yt_porsiyon = QSpinBox()
        self.yt_porsiyon.setRange(1, 50)
        self.yt_porsiyon.setValue(4)
        self.yt_porsiyon.setSuffix(" kişi")
        self.yt_porsiyon.setFixedHeight(40)
        self.yt_porsiyon.setStyleSheet(self.yt_sure.styleSheet())
        por_kap.addWidget(self.yt_porsiyon)
        param_sat.addLayout(por_kap)
        bilgi_l.addLayout(param_sat)

        ana_l.addWidget(bilgi_kart)

        # ─── Malzeme kartı (dinamik satırlar) ───
        mal_kart = QFrame()
        mal_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;"
            f"border-radius:14px;}}"
        )
        mal_l = QVBoxLayout(mal_kart)
        mal_l.setContentsMargins(24, 22, 24, 22)
        mal_l.setSpacing(12)

        mal_bas_sat = QHBoxLayout()
        mal_bas_sat.addWidget(etiket_kucuk("MALZEMELER", C.GOLD))
        mal_bas_sat.addStretch()
        mal_ekle_btn = btn_ghost("+ MALZEME EKLE", yukseklik=32)
        mal_ekle_btn.setFixedWidth(150)
        mal_ekle_btn.clicked.connect(self._yt_malzeme_satir_ekle)
        mal_bas_sat.addWidget(mal_ekle_btn)
        mal_l.addLayout(mal_bas_sat)
        mal_l.addWidget(ayrac())

        # Dinamik malzeme satırları için konteyner
        self.yt_malzeme_kap = QVBoxLayout()
        self.yt_malzeme_kap.setSpacing(8)
        mal_l.addLayout(self.yt_malzeme_kap)
        self.yt_malzeme_satirlari = []   # (ad_inp, miktar_inp, birim_inp, sat_widget)

        # Varsayılan 2 boş satır ekle
        self._yt_malzeme_satir_ekle()
        self._yt_malzeme_satir_ekle()

        ana_l.addWidget(mal_kart)

        # ─── Mesaj etiketi + Kaydet butonu ───
        self.yt_mesaj = QLabel("")
        self.yt_mesaj.setAlignment(Qt.AlignCenter)
        self.yt_mesaj.setStyleSheet(
            f"color:{C.WINE2};font-size:11px;font-weight:bold;"
        )
        ana_l.addWidget(self.yt_mesaj)

        btn_sat = QHBoxLayout()
        btn_sat.addStretch()
        kaydet = btn_primary("TARİFİ KAYDET", yukseklik=48)
        kaydet.setFixedWidth(220)
        kaydet.clicked.connect(self._yt_kaydet)
        btn_sat.addWidget(kaydet)
        btn_sat.addStretch()
        ana_l.addLayout(btn_sat)
        ana_l.addStretch()

        kap.setWidget(ic)
        return kap

    def _yt_malzeme_satir_ekle(self):
        """Yeni tarif formuna bir malzeme girdi satırı ekler."""
        sat = QFrame()
        sat.setStyleSheet(
            f"QFrame{{background:{C.BG};border:none;"
            f"border-radius:8px;}}"
        )
        sl = QHBoxLayout(sat)
        sl.setContentsMargins(10, 6, 10, 6)
        sl.setSpacing(8)

        ad_inp = form_input("Malzeme adı")
        ad_inp.setFixedHeight(34)
        sl.addWidget(ad_inp, 2)

        mik_inp = form_input("Miktar")
        mik_inp.setFixedHeight(34)
        mik_inp.setFixedWidth(80)
        sl.addWidget(mik_inp)

        birim_inp = form_input("Birim (ör: gr, adet)")
        birim_inp.setFixedHeight(34)
        birim_inp.setFixedWidth(120)
        sl.addWidget(birim_inp)

        sil_btn = QPushButton("✕")
        sil_btn.setCursor(Qt.PointingHandCursor)
        sil_btn.setFixedSize(30, 30)
        sil_btn.setStyleSheet(
            f"QPushButton{{background:transparent;color:{C.WINE2};"
            f"border:none;font-size:14px;font-weight:bold;}}"
            f"QPushButton:hover{{color:{C.WINE};}}"
        )
        sil_btn.clicked.connect(lambda: self._yt_malzeme_satir_sil(sat))
        sl.addWidget(sil_btn)

        kayit = (ad_inp, mik_inp, birim_inp, sat)
        self.yt_malzeme_satirlari.append(kayit)
        self.yt_malzeme_kap.addWidget(sat)

    def _yt_malzeme_satir_sil(self, sat_widget):
        """Malzeme satırını listeden ve arayüzden kaldırır."""
        self.yt_malzeme_satirlari = [
            s for s in self.yt_malzeme_satirlari if s[3] is not sat_widget
        ]
        sat_widget.deleteLater()

    def _yt_kaydet(self):
        """Yeni tarif formundaki verileri veritabanına kaydeder."""
        ad = self.yt_ad.text().strip()
        if not ad:
            self.yt_mesaj.setText("Tarif adı boş olamaz.")
            return

        if not self.veri.aktif_kullanici:
            self.yt_mesaj.setText("Lütfen önce giriş yapın.")
            return

        # Görseli kopyala
        kaydedilecek_gorsel = ""
        if hasattr(self, "secilen_gorsel_yolu") and self.secilen_gorsel_yolu:
            gorsel_klasor = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gorseller")
            if not os.path.exists(gorsel_klasor):
                os.makedirs(gorsel_klasor)
            uzanti = os.path.splitext(self.secilen_gorsel_yolu)[1]
            yeni_ad = f"tarif_{uuid.uuid4().hex[:8]}{uzanti}"
            hedef_yol = os.path.join(gorsel_klasor, yeni_ad)
            try:
                shutil.copy2(self.secilen_gorsel_yolu, hedef_yol)
                kaydedilecek_gorsel = f"gorseller/{yeni_ad}"
            except Exception:
                pass # Kopyalama basarisiz olursa görsel eklenmez

        # Tarifi ekle
        sonuc = self.veri.tarif.tarif_ekle(
            tarif_adi=ad,
            kategori=self.yt_kategori.currentText(),
            hazirlama_suresi=self.yt_sure.value(),
            kullanici_id=self.veri.aktif_kullanici["kullanici_id"],
            porsiyon=self.yt_porsiyon.value(),
            zorluk=self.yt_zorluk.currentText(),
            aciklama=self.yt_aciklama.toPlainText().strip(),
            yapilis=self.yt_yapilis.toPlainText().strip(),
            gorsel_yolu=kaydedilecek_gorsel
        )

        if not sonuc["basarili"]:
            self.yt_mesaj.setText(sonuc["mesaj"])
            return

        tarif_id = sonuc["tarif_id"]

        # Malzemeleri ekle
        eklenen = 0
        for ad_inp, mik_inp, birim_inp, _ in self.yt_malzeme_satirlari:
            m_ad = ad_inp.text().strip()
            m_mik = mik_inp.text().strip()
            if m_ad and m_mik:
                self.veri.malzeme.ekle(tarif_id, m_ad, m_mik, birim_inp.text().strip())
                eklenen += 1

        # Formu temizle
        self.yt_ad.clear()
        self.yt_aciklama.clear()
        self.yt_yapilis.clear()
        self.yt_sure.setValue(30)
        self.yt_porsiyon.setValue(4)
        self.yt_kategori.setCurrentIndex(0)
        self.yt_zorluk.setCurrentText("Orta")
        self.yt_mesaj.setText("")
        if hasattr(self, "secilen_gorsel_yolu"):
            self.secilen_gorsel_yolu = ""
            self.lbl_gorsel_ad.setText("Görsel seçilmedi")

        # Malzeme satırlarını temizle, 2 boş satır ekle
        for _, _, _, w in self.yt_malzeme_satirlari:
            w.deleteLater()
        self.yt_malzeme_satirlari.clear()
        self._yt_malzeme_satir_ekle()
        self._yt_malzeme_satir_ekle()

        log(f"Yeni tarif: {ad} (+{eklenen} malzeme)", C.SAGE)
        Toast(self, sonuc["mesaj"], "basari")
        # Tarifler sayfasına geç
        self._sayfa_degistir(1)

    # ══════════════════════════════════════════════════════════════
    #  SAYFA 5: KULLANICILAR
    # ══════════════════════════════════════════════════════════════
    def _sayfa_kullanicilar(self) -> QWidget:
        """Kayıtlı kullanıcıları tablo halinde listeleyen sayfa."""
        kap = QWidget()
        kap.setStyleSheet(f"background:{C.BG};")
        l = QVBoxLayout(kap)
        l.setContentsMargins(30, 24, 30, 24)
        l.setSpacing(18)

        bas_kap = QVBoxLayout()
        bas_kap.setSpacing(2)
        bas = QLabel("Kullanıcılar")
        bas.setStyleSheet(
            f"color:{C.TEXT};font-size:26px;font-weight:bold;"
            f"font-family:Georgia;letter-spacing:-0.5px;"
        )
        bas_kap.addWidget(bas)
        alt = QLabel("KAYITLI ÜYELER")
        alt.setStyleSheet(
            f"color:{C.GOLD3};font-size:9px;font-weight:bold;letter-spacing:4px;"
        )
        bas_kap.addWidget(alt)
        l.addLayout(bas_kap)

        # Tablo
        self.kul_tablo = QTableWidget()
        # Admin moduna göre sütun sayısı ayarlanacak (_kullanicilar_yenile içinde)
        self.kul_tablo.setColumnCount(6)
        self.kul_tablo.setHorizontalHeaderLabels(
            ["ID", "Ad", "Soyad", "E-posta", "Rol", "İşlem"]
        )
        self.kul_tablo.horizontalHeader().setStretchLastSection(True)
        self.kul_tablo.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.kul_tablo.verticalHeader().setVisible(False)
        self.kul_tablo.setEditTriggers(QTableWidget.NoEditTriggers)
        self.kul_tablo.setSelectionBehavior(QTableWidget.SelectRows)
        self.kul_tablo.setAlternatingRowColors(False)
        self.kul_tablo.setStyleSheet(
            f"QTableWidget{{background:{C.CARD};color:{C.TEXT};"
            f"border:none;border-radius:12px;"
            f"font-size:12px;gridline-color:transparent;}}"
            f"QTableWidget::item{{padding:10px 14px;}}"
            f"QTableWidget::item:selected{{background:{C.GOLD3}40;color:{C.TEXT};}}"
            f"QHeaderView::section{{background:{C.BG2};color:{C.GOLD};"
            f"border:none;border-bottom:none;"
            f"padding:10px 14px;font-size:10px;font-weight:bold;"
            f"letter-spacing:2px;}}"
        )
        l.addWidget(self.kul_tablo, 1)
        return kap

    def _kullanicilar_yenile(self):
        """Kullanıcılar tablosunu veritabanından günceller. Admin ise silme butonu gösterir."""
        kullanicilar = self.veri.kullanici.listele()
        admin_mi = self._admin_mi()
        # Sütun sayısını role göre ayarla
        self.kul_tablo.setColumnCount(6 if admin_mi else 5)
        if admin_mi:
            self.kul_tablo.setHorizontalHeaderLabels(
                ["ID", "Ad", "Soyad", "E-posta", "Rol", "İşlem"]
            )
        else:
            self.kul_tablo.setHorizontalHeaderLabels(
                ["ID", "Ad", "Soyad", "E-posta", "Rol"]
            )
        self.kul_tablo.setRowCount(len(kullanicilar))
        for i, k in enumerate(kullanicilar):
            self.kul_tablo.setItem(i, 0, QTableWidgetItem(str(k["kullanici_id"])))
            self.kul_tablo.setItem(i, 1, QTableWidgetItem(k["ad"]))
            self.kul_tablo.setItem(i, 2, QTableWidgetItem(k["soyad"]))
            self.kul_tablo.setItem(i, 3, QTableWidgetItem(k["email"]))
            rol_metin = "ADMIN" if k.get("rol") == "admin" else "ÜYE"
            rol_item = QTableWidgetItem(rol_metin)
            if k.get("rol") == "admin":
                rol_item.setForeground(QColor(C.WINE2))
            self.kul_tablo.setItem(i, 4, rol_item)

            if admin_mi:
                # Kendi hesabın için silme butonu çıkmasın
                if self.veri.aktif_kullanici and k["kullanici_id"] == self.veri.aktif_kullanici["kullanici_id"]:
                    kendi_item = QTableWidgetItem("— (sen)")
                    kendi_item.setForeground(QColor(C.TEXT3))
                    self.kul_tablo.setItem(i, 5, kendi_item)
                else:
                    sil_btn = QPushButton("Sil")
                    sil_btn.setCursor(Qt.PointingHandCursor)
                    sil_btn.setStyleSheet(
                        f"QPushButton{{background:transparent;color:{C.WINE2};"
                        f"border:1px solid {C.WINE2}60;border-radius:6px;"
                        f"padding:4px 14px;font-size:10px;font-weight:bold;letter-spacing:1px;}}"
                        f"QPushButton:hover{{background:{C.WINE2};color:#f5ece0;border-color:{C.WINE2};}}"
                    )
                    kul_id = k["kullanici_id"]
                    kul_ad = f"{k['ad']} {k['soyad']}".strip()
                    sil_btn.clicked.connect(
                        lambda _=False, kid=kul_id, knm=kul_ad: self._admin_kullanici_sil(kid, knm)
                    )
                    self.kul_tablo.setCellWidget(i, 5, sil_btn)

    # ══════════════════════════════════════════════════════════════
    #  SAYFA 6: İSTATİSTİKLER
    # ══════════════════════════════════════════════════════════════
    def _sayfa_istatistik(self) -> QWidget:
        """
        Detaylı istatistik sayfası:
        - Genel özet kartları (üst)
        - Kategori ortalamaları tablosu (orta)
        - En popüler tarifler listesi (alt)
        """
        kap = QScrollArea()
        kap.setWidgetResizable(True)
        kap.setStyleSheet(
            f"QScrollArea{{background:{C.BG};border:none;}}"
            f"QScrollBar:vertical{{width:8px;background:transparent;}}"
            f"QScrollBar::handle:vertical{{background:{C.BORDER2};border-radius:4px;}}"
        )

        ic = QWidget()
        ic.setStyleSheet(f"background:{C.BG};")
        ana_l = QVBoxLayout(ic)
        ana_l.setContentsMargins(30, 24, 30, 30)
        ana_l.setSpacing(20)

        bas_kap = QVBoxLayout()
        bas_kap.setSpacing(2)
        bas = QLabel("İstatistikler")
        bas.setStyleSheet(
            f"color:{C.TEXT};font-size:26px;font-weight:bold;"
            f"font-family:Georgia;letter-spacing:-0.5px;"
        )
        bas_kap.addWidget(bas)
        alt = QLabel("PLATFORM ANALİTİKLERİ")
        alt.setStyleSheet(
            f"color:{C.GOLD3};font-size:9px;font-weight:bold;letter-spacing:4px;"
        )
        bas_kap.addWidget(alt)
        ana_l.addLayout(bas_kap)

        # ─── Özet kartları (4'lü grid) ───
        ozet_sat = QHBoxLayout()
        ozet_sat.setSpacing(14)
        self.is_kartlar = []
        bilgiler = [
            ("Toplam Tarif",         "0", C.GOLD,  "📖"),
            ("Toplam Kullanıcı",     "0", C.SAGE,  "👥"),
            ("Toplam Değerlendirme", "0", C.COPPER,"★"),
            ("Ortalama Puan",        "—", C.WINE2, "◆"),
        ]
        for etk, dgr, rnk, ikn in bilgiler:
            k = StatKart(etk, dgr, rnk, ikn)
            ozet_sat.addWidget(k)
            self.is_kartlar.append(k)
        ana_l.addLayout(ozet_sat)

        # ─── Kategori ortalamaları tablosu ───
        kat_kart = QFrame()
        kat_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;"
            f"border-radius:14px;}}"
        )
        kat_l = QVBoxLayout(kat_kart)
        kat_l.setContentsMargins(24, 22, 24, 22)
        kat_l.setSpacing(12)
        kat_l.addWidget(etiket_kucuk("KATEGORİ ANALİZİ", C.GOLD))
        kat_l.addWidget(ayrac())

        self.is_kat_tablo = QTableWidget()
        self.is_kat_tablo.setColumnCount(4)
        self.is_kat_tablo.setHorizontalHeaderLabels(
            ["Kategori", "Tarif Sayısı", "Ort. Süre (dk)", "Ort. Puan"]
        )
        self.is_kat_tablo.horizontalHeader().setStretchLastSection(True)
        self.is_kat_tablo.horizontalHeader().setSectionResizeMode(
            QHeaderView.Stretch
        )
        self.is_kat_tablo.verticalHeader().setVisible(False)
        self.is_kat_tablo.setEditTriggers(QTableWidget.NoEditTriggers)
        self.is_kat_tablo.setSelectionBehavior(QTableWidget.SelectRows)
        self.is_kat_tablo.setStyleSheet(
            f"QTableWidget{{background:{C.BG};color:{C.TEXT};"
            f"border:none;font-size:12px;gridline-color:transparent;}}"
            f"QTableWidget::item{{padding:10px 14px;}}"
            f"QTableWidget::item:selected{{background:{C.GOLD3}40;color:{C.TEXT};}}"
            f"QHeaderView::section{{background:{C.CARD};color:{C.GOLD};"
            f"border:none;border-bottom:none;"
            f"padding:10px 14px;font-size:10px;font-weight:bold;"
            f"letter-spacing:2px;}}"
        )
        kat_l.addWidget(self.is_kat_tablo)
        ana_l.addWidget(kat_kart)

        # ─── En popüler tarifler kartı ───
        pop_kart = QFrame()
        pop_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;"
            f"border-radius:14px;}}"
        )
        pop_l = QVBoxLayout(pop_kart)
        pop_l.setContentsMargins(24, 22, 24, 22)
        pop_l.setSpacing(12)
        pop_l.addWidget(etiket_kucuk("EN POPÜLER TARİFLER", C.GOLD))
        pop_l.addWidget(ayrac())

        self.is_pop_liste = QVBoxLayout()
        self.is_pop_liste.setSpacing(8)
        pop_l.addLayout(self.is_pop_liste)
        ana_l.addWidget(pop_kart)

        ana_l.addStretch()
        kap.setWidget(ic)
        return kap

    def _istatistik_yenile(self):
        """İstatistik sayfasını veritabanından günceller."""
        ist = self.veri.istatistik.genel_istatistikler()

        # Özet kartları güncelle
        degerler = [
            str(ist.get("toplam_tarif", 0)),
            str(ist.get("toplam_kullanici", 0)),
            str(ist.get("toplam_degerlendirme", 0)),
            f"{ist.get('ortalama_puan', 0):.1f}",
        ]
        for kart, deger in zip(self.is_kartlar, degerler):
            kart.deger_guncelle(deger)

        # Kategori tablosu
        kat_ort = self.veri.istatistik.kategori_ortalamalari()
        self.is_kat_tablo.setRowCount(len(kat_ort))
        for i, k in enumerate(kat_ort):
            self.is_kat_tablo.setItem(i, 0, QTableWidgetItem(k["kategori"]))
            self.is_kat_tablo.setItem(
                i, 1, QTableWidgetItem(str(k["tarif_sayisi"]))
            )
            ort_sure = k.get("ort_sure") or 0
            self.is_kat_tablo.setItem(
                i, 2, QTableWidgetItem(f"{ort_sure:.0f}")
            )
            ort_puan = k.get("ort_puan") or 0
            self.is_kat_tablo.setItem(
                i, 3, QTableWidgetItem(f"{ort_puan:.1f}" if ort_puan else "—")
            )

        # Popüler tarifler
        while self.is_pop_liste.count():
            item = self.is_pop_liste.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        populer = self.veri.istatistik.en_populer_tarifler(limit=8)
        if populer:
            for sira, t in enumerate(populer, 1):
                w = self._populer_satir(t)
                # Sıra numarası ekle
                self.is_pop_liste.addWidget(w)
        else:
            bos = QLabel("Henüz değerlendirme yapılmamış.")
            bos.setAlignment(Qt.AlignCenter)
            bos.setStyleSheet(
                f"color:{C.TEXT3};font-size:11px;font-style:italic;"
                f"background:transparent;border:none;padding:16px;"
            )
            self.is_pop_liste.addWidget(bos)

    # ══════════════════════════════════════════════════════════════
    #  SAYFA 7: FAVORİLERİM
    # ══════════════════════════════════════════════════════════════
    def _sayfa_haftalik_plan(self) -> QWidget:
        kap = QScrollArea()
        kap.setWidgetResizable(True)
        kap.setStyleSheet(f"QScrollArea{{background:{C.BG};border:none;}}")

        ic = QWidget()
        ic.setStyleSheet(f"background:{C.BG};")
        l = QVBoxLayout(ic)
        l.setContentsMargins(30, 24, 30, 30)
        l.setSpacing(20)

        ust_kart = QFrame()
        ust_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border:none;border-radius:18px;}}"
        )
        ust_l = QVBoxLayout(ust_kart)
        ust_l.setContentsMargins(28, 24, 28, 24)
        ust_l.setSpacing(14)

        bas = QLabel("Haftalik Menu Plani")
        bas.setStyleSheet(
            f"color:{C.TEXT};font-size:30px;font-weight:bold;font-family:Georgia;background:transparent;"
        )
        ust_l.addWidget(bas)

        alt = QLabel(
            "Her gun icin tarif secin, not dusun ve tek tikla dengeli bir haftalik akis olusturun."
        )
        alt.setWordWrap(True)
        alt.setStyleSheet(
            f"color:{C.TEXT2};font-size:12px;line-height:20px;background:transparent;"
        )
        ust_l.addWidget(alt)

        aksiyon = QHBoxLayout()
        aksiyon.setSpacing(10)
        oto_btn = btn_primary("Akilli Plan Olustur", genislik=190, yukseklik=44)
        oto_btn.clicked.connect(self._haftalik_plan_akilli_olustur)
        kaydet_btn = btn_ghost("Plani Kaydet", yukseklik=44)
        kaydet_btn.clicked.connect(self._haftalik_plan_kaydet)
        alisveris_btn = btn_ghost("Malzemeleri Listeye Aktar", yukseklik=44)
        alisveris_btn.clicked.connect(self._haftalik_plan_alisverise_aktar)
        temizle_btn = btn_ghost("Plani Temizle", yukseklik=44)
        temizle_btn.clicked.connect(self._haftalik_plan_temizle_ui)
        aksiyon.addWidget(oto_btn)
        aksiyon.addWidget(kaydet_btn)
        aksiyon.addWidget(alisveris_btn)
        aksiyon.addWidget(temizle_btn)
        aksiyon.addStretch()
        ust_l.addLayout(aksiyon)
        l.addWidget(ust_kart)

        ist_sat = QHBoxLayout()
        ist_sat.setSpacing(16)
        self.hp_k_gun = StatKart("Planlanan Gun", "0", C.GOLD, "7")
        self.hp_k_sure = StatKart("Toplam Sure", "0 dk", C.COPPER, "S")
        self.hp_k_denge = StatKart("Kategori Cesidi", "0", C.SAGE, "K")
        ist_sat.addWidget(self.hp_k_gun)
        ist_sat.addWidget(self.hp_k_sure)
        ist_sat.addWidget(self.hp_k_denge)
        l.addLayout(ist_sat)

        self.hp_ozet = QLabel("Plan olusturmak icin bir tarif secin ya da akilli oneriyi kullanin.")
        self.hp_ozet.setWordWrap(True)
        self.hp_ozet.setStyleSheet(
            f"color:{C.TEXT2};font-size:12px;line-height:20px;padding:2px 2px 8px 2px;"
        )
        l.addWidget(self.hp_ozet)

        self.hp_gunleri = {}
        grid = QGridLayout()
        grid.setHorizontalSpacing(16)
        grid.setVerticalSpacing(16)
        for idx, (gun, slogan) in enumerate(HAFTA_GUNLERI):
            kart = self._haftalik_plan_karti_olustur(gun, slogan)
            self.hp_gunleri[gun] = kart
            grid.addWidget(kart["kapsayici"], idx // 2, idx % 2)
        l.addLayout(grid)
        l.addStretch()

        kap.setWidget(ic)
        return kap

    def _haftalik_plan_karti_olustur(self, gun: str, slogan: str) -> Dict:
        kart = QFrame()
        kart.setObjectName("haftalikPlanKarti")
        kart.setStyleSheet(
            f"QFrame#haftalikPlanKarti{{background:{C.CARD};border:1px solid {C.BORDER};border-radius:16px;}}"
        )
        l = QVBoxLayout(kart)
        l.setContentsMargins(20, 18, 20, 18)
        l.setSpacing(10)

        bas = QLabel(gun)
        bas.setStyleSheet(
            f"color:{C.TEXT};font-size:22px;font-weight:bold;font-family:Georgia;background:transparent;border:none;"
        )
        l.addWidget(bas)

        alt = QLabel(slogan)
        alt.setWordWrap(True)
        alt.setStyleSheet(
            f"color:{C.TEXT3};font-size:11px;line-height:18px;background:transparent;border:none;"
        )
        l.addWidget(alt)

        ogun = QComboBox()
        ogun.addItems(PLAN_OGUNLERI)
        ogun.setFixedHeight(38)
        ogun.setStyleSheet(
            f"QComboBox{{background:{C.BG};color:{C.TEXT};border:1px solid {C.BORDER2};"
            f"border-radius:10px;padding:6px 10px;font-size:11px;selection-background-color:{C.CARD2};"
            f"selection-color:{C.TEXT};}}"
            f"QComboBox:hover{{border-color:{C.GOLD3};}}"
            f"QComboBox:focus{{border-color:{C.GOLD};color:{C.TEXT};}}"
            f"QComboBox::drop-down{{border:none;width:26px;}}"
            f"QComboBox QAbstractItemView{{background:{C.CARD};color:{C.TEXT};"
            f"border:1px solid {C.BORDER2};selection-background-color:{C.GOLD3};"
            f"selection-color:{C.TEXT};outline:none;}}"
        )
        l.addWidget(ogun)

        tarif = QComboBox()
        tarif.setFixedHeight(40)
        tarif.setStyleSheet(
            f"QComboBox{{background:{C.BG};color:{C.TEXT};border:1px solid {C.BORDER2};"
            f"border-radius:10px;padding:6px 10px;font-size:12px;selection-background-color:{C.CARD2};"
            f"selection-color:{C.TEXT};}}"
            f"QComboBox:hover{{border-color:{C.GOLD3};}}"
            f"QComboBox:focus{{border-color:{C.GOLD};color:{C.TEXT};}}"
            f"QComboBox::drop-down{{border:none;width:26px;}}"
            f"QComboBox QAbstractItemView{{background:{C.CARD};color:{C.TEXT};"
            f"border:1px solid {C.BORDER2};selection-background-color:{C.GOLD3};"
            f"selection-color:{C.TEXT};outline:none;}}"
        )
        tarif.currentIndexChanged.connect(lambda _, g=gun: self._haftalik_plan_kartini_guncelle(g))
        l.addWidget(tarif)

        meta = QLabel("Tarif secildiginde sure, kategori ve zorluk burada gorunur.")
        meta.setWordWrap(True)
        meta.setStyleSheet(
            f"color:{C.TEXT2};font-size:11px;line-height:18px;background:transparent;border:none;"
        )
        l.addWidget(meta)

        not_inp = QLineEdit()
        not_inp.setPlaceholderText("Gun icin kisa not...")
        not_inp.setFixedHeight(38)
        not_inp.setStyleSheet(
            f"QLineEdit{{background:{C.BG};color:{C.TEXT};border:1px solid {C.BORDER2};"
            f"border-radius:10px;padding:0 10px;font-size:11px;}}"
        )
        not_inp.textChanged.connect(lambda _=None: self._haftalik_plan_istatistik_guncelle())
        l.addWidget(not_inp)

        return {
            "kapsayici": kart,
            "ogun": ogun,
            "tarif": tarif,
            "meta": meta,
            "not": not_inp,
        }

    def _haftalik_plan_tariflerini_doldur(self):
        tarifler = self.veri.tarif.listele()
        self.hp_tarif_haritasi = {t["tarif_id"]: t for t in tarifler}
        sirali = sorted(
            tarifler,
            key=lambda t: (
                -(t.get("ort_puan") or 0),
                t.get("hazirlama_suresi", 999),
                t["tarif_adi"].lower()
            )
        )
        for kart in self.hp_gunleri.values():
            combo = kart["tarif"]
            mevcut_id = combo.currentData()
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("Tarif secin", None)
            for tarif in sirali:
                combo.addItem(f"{tarif['tarif_adi']}  |  {tarif['kategori']}", tarif["tarif_id"])
            hedef_idx = combo.findData(mevcut_id)
            combo.setCurrentIndex(hedef_idx if hedef_idx >= 0 else 0)
            combo.blockSignals(False)

    def _haftalik_plan_kartini_guncelle(self, gun: str):
        kart = self.hp_gunleri[gun]
        tarif_id = kart["tarif"].currentData()
        tarif = self.hp_tarif_haritasi.get(tarif_id)
        if not tarif:
            kart["meta"].setText("Tarif secildiginde sure, kategori ve zorluk burada gorunur.")
        else:
            puan = tarif.get("ort_puan") or 0
            puan_metin = f"{puan:.1f}" if puan else "Yeni"
            kart["meta"].setText(
                f"{tarif['kategori']}  |  {tarif.get('hazirlama_suresi', 0)} dk  |  "
                f"{tarif.get('zorluk', 'Orta')}  |  Puan {puan_metin}"
            )
        self._haftalik_plan_istatistik_guncelle()

    def _haftalik_plan_istatistik_guncelle(self):
        secili = []
        toplam_sure = 0
        kategoriler = set()
        for kart in self.hp_gunleri.values():
            tarif = self.hp_tarif_haritasi.get(kart["tarif"].currentData())
            if not tarif:
                continue
            secili.append(tarif)
            toplam_sure += tarif.get("hazirlama_suresi", 0)
            kategoriler.add(tarif.get("kategori", "Diger"))
        self.hp_k_gun.deger_guncelle(str(len(secili)))
        self.hp_k_sure.deger_guncelle(f"{toplam_sure} dk")
        self.hp_k_denge.deger_guncelle(str(len(kategoriler)))

        if not secili:
            self.hp_ozet.setText("Plan olusturmak icin bir tarif secin ya da akilli oneriyi kullanin.")
        else:
            en_kisa = min(secili, key=lambda t: t.get("hazirlama_suresi", 999))
            en_uzun = max(secili, key=lambda t: t.get("hazirlama_suresi", 0))
            self.hp_ozet.setText(
                f"Bu hafta {len(secili)} gun planlandi. En hizli tabak {en_kisa['tarif_adi']} "
                f"({en_kisa.get('hazirlama_suresi', 0)} dk), en uzun hazirlik ise "
                f"{en_uzun['tarif_adi']} ({en_uzun.get('hazirlama_suresi', 0)} dk)."
            )

    def _haftalik_plan_yenile(self):
        if not self.veri.aktif_kullanici:
            return
        self._haftalik_plan_tariflerini_doldur()
        kayitlar = {
            kayit["gun"]: kayit
            for kayit in self.veri.kullanici.haftalik_plan_getir(self.veri.aktif_kullanici["kullanici_id"])
        }
        for gun, kart in self.hp_gunleri.items():
            kayit = kayitlar.get(gun)
            kart["ogun"].blockSignals(True)
            kart["tarif"].blockSignals(True)
            kart["not"].blockSignals(True)
            if kayit:
                idx = kart["tarif"].findData(kayit["tarif_id"])
                kart["tarif"].setCurrentIndex(idx if idx >= 0 else 0)
                ogun_idx = kart["ogun"].findText(kayit.get("ogun", "Aksam"))
                kart["ogun"].setCurrentIndex(ogun_idx if ogun_idx >= 0 else 2)
                kart["not"].setText(kayit.get("not_metni", ""))
            else:
                kart["tarif"].setCurrentIndex(0)
                kart["ogun"].setCurrentIndex(2 if kart["ogun"].count() > 2 else 0)
                kart["not"].clear()
            kart["tarif"].blockSignals(False)
            kart["ogun"].blockSignals(False)
            kart["not"].blockSignals(False)
            self._haftalik_plan_kartini_guncelle(gun)

    def _haftalik_plan_akilli_olustur(self):
        tarifler = self.veri.tarif.listele()
        if not tarifler:
            Toast(self, "Plan olusturmak icin once tarif eklenmeli.", "hata")
            return

        secilenler = []
        kategori_sayisi = {}
        kullanilan = set()
        havuz = sorted(
            tarifler,
            key=lambda t: (
                -(t.get("ort_puan") or 0),
                t.get("hazirlama_suresi", 999),
                t["tarif_adi"].lower()
            )
        )
        for _gun, _slogan in HAFTA_GUNLERI:
            adaylar = sorted(
                havuz,
                key=lambda t: (
                    kategori_sayisi.get(t.get("kategori", "Diger"), 0),
                    1 if t["tarif_id"] in kullanilan else 0,
                    -(t.get("ort_puan") or 0),
                    t.get("hazirlama_suresi", 999)
                )
            )
            secilen = adaylar[0]
            secilenler.append(secilen)
            kullanilan.add(secilen["tarif_id"])
            kategori = secilen.get("kategori", "Diger")
            kategori_sayisi[kategori] = kategori_sayisi.get(kategori, 0) + 1

        for idx, (gun, _slogan) in enumerate(HAFTA_GUNLERI):
            tarif = secilenler[idx]
            kart = self.hp_gunleri[gun]
            hedef = kart["tarif"].findData(tarif["tarif_id"])
            kart["tarif"].setCurrentIndex(hedef if hedef >= 0 else 0)
            if tarif["kategori"] == "Kahvaltı":
                kart["ogun"].setCurrentText("Kahvalti")
            elif tarif["kategori"] == "Tatlı":
                kart["ogun"].setCurrentText("Tatli Molasi")
            elif tarif["kategori"] == "İçecek":
                kart["ogun"].setCurrentText("Serin Mola")
            else:
                kart["ogun"].setCurrentText("Aksam")
            kart["not"].setText(f"{tarif['kategori']} dengesi icin secildi.")
            self._haftalik_plan_kartini_guncelle(gun)
        Toast(self, "Haftalik plan akilli sekilde olusturuldu.", "basari")

    def _haftalik_plan_kaydet(self):
        if not self.veri.aktif_kullanici:
            return
        kid = self.veri.aktif_kullanici["kullanici_id"]
        for gun, kart in self.hp_gunleri.items():
            self.veri.kullanici.haftalik_plan_kaydet(
                kid,
                gun,
                kart["tarif"].currentData(),
                kart["ogun"].currentText(),
                kart["not"].text().strip()
            )
        log("Haftalik menu plani guncellendi", C.GOLD)
        Toast(self, "Haftalik plan kaydedildi.", "basari")

    def _haftalik_plan_temizle_ui(self):
        if not self.veri.aktif_kullanici:
            return
        self.veri.kullanici.haftalik_plan_temizle(self.veri.aktif_kullanici["kullanici_id"])
        self._haftalik_plan_yenile()
        Toast(self, "Haftalik plan temizlendi.", "bilgi")

    def _haftalik_plan_alisverise_aktar(self):
        if not self.veri.aktif_kullanici:
            return
        malzemeler = []
        for kart in self.hp_gunleri.values():
            tarif_id = kart["tarif"].currentData()
            if tarif_id:
                malzemeler.extend(self.veri.malzeme.listele(tarif_id))
        if not malzemeler:
            Toast(self, "Listeye aktarilacak planli tarif bulunamadi.", "hata")
            return
        sonuc = self.veri.kullanici.alisveris_listesine_ekle(
            self.veri.aktif_kullanici["kullanici_id"], malzemeler
        )
        if sonuc["basarili"]:
            Toast(self, "Plan malzemeleri alisveris listesine eklendi.", "basari")
        else:
            Toast(self, sonuc["mesaj"], "hata")

    def _sayfa_favoriler(self) -> QWidget:
        kap = QWidget()
        kap.setStyleSheet(f"background:{C.BG};")
        l = QVBoxLayout(kap)
        l.setContentsMargins(30, 24, 30, 24)
        l.setSpacing(18)

        bas_kap = QVBoxLayout()
        bas_kap.setSpacing(2)
        bas = QLabel("Favorilerim")
        bas.setStyleSheet(
            f"color:{C.TEXT};font-size:26px;font-weight:bold;"
            f"font-family:Georgia;letter-spacing:-0.5px;"
        )
        bas_kap.addWidget(bas)
        alt = QLabel("KAYDETTİĞİNİZ TARİFLER")
        alt.setStyleSheet(
            f"color:{C.GOLD3};font-size:9px;font-weight:bold;letter-spacing:4px;"
        )
        bas_kap.addWidget(alt)
        l.addLayout(bas_kap)

        self.fav_scroll = QScrollArea()
        self.fav_scroll.setWidgetResizable(True)
        self.fav_scroll.setStyleSheet(
            f"QScrollArea{{background:{C.BG};border:none;}}"
            f"QScrollBar:vertical{{width:8px;background:transparent;}}"
            f"QScrollBar::handle:vertical{{background:{C.BORDER2};border-radius:4px;}}"
        )

        ic = QWidget()
        ic.setStyleSheet(f"background:{C.BG};")
        self.fav_liste_l = QVBoxLayout(ic)
        self.fav_liste_l.setContentsMargins(0, 0, 0, 0)
        self.fav_liste_l.setSpacing(10)
        self.fav_liste_l.addStretch()

        self.fav_scroll.setWidget(ic)
        l.addWidget(self.fav_scroll, 1)
        return kap

    def _favoriler_yenile(self):
        while self.fav_liste_l.count() > 1:
            item = self.fav_liste_l.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self.veri.aktif_kullanici:
            return

        kid = self.veri.aktif_kullanici["kullanici_id"]
        favoriler = self.veri.kullanici.favorilerim(kid)

        if not favoriler:
            bos = QFrame()
            bos.setStyleSheet(
                f"QFrame{{background:{C.CARD};border:none;"
                f"border-radius:14px;}}"
            )
            bos_l = QVBoxLayout(bos)
            bos_l.setContentsMargins(30, 50, 30, 50)
            bos_l.setAlignment(Qt.AlignCenter)

            sem = QLabel("💖")
            sem.setAlignment(Qt.AlignCenter)
            sem.setStyleSheet(
                f"color:{C.GOLD3};font-size:48px;background:transparent;border:none;"
            )
            bos_l.addWidget(sem)
            msg = QLabel("Henüz hiç favori tarifiniz yok.")
            msg.setAlignment(Qt.AlignCenter)
            msg.setStyleSheet(
                f"color:{C.TEXT2};font-size:14px;background:transparent;border:none;"
            )
            bos_l.addWidget(msg)
            self.fav_liste_l.insertWidget(self.fav_liste_l.count() - 1, bos)
            return

        for t in favoriler:
            kart = TarifKarti(t)
            kart.tiklandi.connect(self._tarif_detay_ac)
            self.fav_liste_l.insertWidget(self.fav_liste_l.count() - 1, kart)

    # ══════════════════════════════════════════════════════════════
    #  SAYFA 8: ALIŞVERİŞ LİSTESİ
    # ══════════════════════════════════════════════════════════════
    def _sayfa_alisveris(self) -> QWidget:
        kap = QWidget()
        kap.setStyleSheet(f"background:{C.BG};")
        l = QVBoxLayout(kap)
        l.setContentsMargins(30, 24, 30, 24)
        l.setSpacing(18)

        bas_sat = QHBoxLayout()
        bas_kap = QVBoxLayout()
        bas_kap.setSpacing(2)
        bas = QLabel("Alışveriş Listesi")
        bas.setStyleSheet(f"color:{C.TEXT};font-size:26px;font-weight:bold;font-family:Georgia;letter-spacing:-0.5px;")
        bas_kap.addWidget(bas)
        alt = QLabel("ALINACAK MALZEMELER")
        alt.setStyleSheet(f"color:{C.GOLD3};font-size:9px;font-weight:bold;letter-spacing:4px;")
        bas_kap.addWidget(alt)
        bas_sat.addLayout(bas_kap)
        bas_sat.addStretch()
        
        self.al_temizle_btn = btn_ghost("Alınanları Temizle")
        self.al_temizle_btn.clicked.connect(self._alisveris_alinanlari_temizle)
        self.tum_temizle_btn = btn_ghost("Tümünü Temizle")
        self.tum_temizle_btn.clicked.connect(self._alisveris_tumunu_temizle)
        self.al_disa_aktar_btn = btn_ghost("TXT Disa Aktar")
        self.al_disa_aktar_btn.clicked.connect(self._alisveris_txt_disa_aktar)
        bas_sat.addWidget(self.al_disa_aktar_btn)
        bas_sat.addWidget(self.al_temizle_btn)
        bas_sat.addWidget(self.tum_temizle_btn)
        l.addLayout(bas_sat)

        self.al_ozet_kart = QFrame()
        self.al_ozet_kart.setStyleSheet(
            f"QFrame{{background:{C.CARD};border-radius:14px;border:1px solid {C.BORDER};}}"
        )
        ozet_l = QVBoxLayout(self.al_ozet_kart)
        ozet_l.setContentsMargins(20, 18, 20, 18)
        ozet_l.setSpacing(12)
        ozet_l.addWidget(etiket_kucuk("AKILLI OZET", C.GOLD))
        self.al_ozet_metin = QLabel("Liste henuz dolmadi.")
        self.al_ozet_metin.setWordWrap(True)
        self.al_ozet_metin.setStyleSheet(
            f"color:{C.TEXT};font-size:13px;line-height:20px;background:transparent;border:none;"
        )
        ozet_l.addWidget(self.al_ozet_metin)
        self.al_birlesik_liste = QLabel("")
        self.al_birlesik_liste.setWordWrap(True)
        self.al_birlesik_liste.setStyleSheet(
            f"color:{C.TEXT2};font-size:12px;line-height:20px;background:transparent;border:none;"
        )
        ozet_l.addWidget(self.al_birlesik_liste)
        l.addWidget(self.al_ozet_kart)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(f"QScrollArea{{background:{C.BG};border:none;}}")
        ic = QWidget()
        ic.setStyleSheet(f"background:{C.BG};")
        self.al_liste_l = QVBoxLayout(ic)
        self.al_liste_l.setContentsMargins(0, 0, 0, 0)
        self.al_liste_l.setSpacing(10)
        self.al_liste_l.addStretch()
        scroll.setWidget(ic)
        l.addWidget(scroll, 1)
        return kap

    def _alisveris_yenile(self):
        while self.al_liste_l.count() > 1:
            item = self.al_liste_l.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
                
        if not self.veri.aktif_kullanici:
            return
            
        kid = self.veri.aktif_kullanici["kullanici_id"]
        liste = self.veri.kullanici.alisveris_listesi_getir(kid)
        ozet = self.veri.kullanici.alisveris_ozeti_getir(kid)
        self.al_ozet_metin.setText(
            f"{ozet['benzersiz_urun']} benzersiz urun, "
            f"{ozet['bekleyen_kalem']} bekleyen kalem ve "
            f"{ozet['alinan_kalem']} tamamlanan kalem bulunuyor."
        )
        birlesik_satirlar = []
        for urun in ozet["birlesik_liste"][:6]:
            durum = "✓" if urun["tamamlandi_mi"] else "*"
            miktar = f"{urun['miktar']} {urun['birim']}".strip()
            tekrar = f" · {urun['kayit_sayisi']} kayit" if urun["kayit_sayisi"] > 1 else ""
            birlesik_satirlar.append(f"{durum} {urun['malzeme_adi']} - {miktar}{tekrar}".rstrip(" -"))
        if len(ozet["birlesik_liste"]) > 6:
            birlesik_satirlar.append(f"+{len(ozet['birlesik_liste']) - 6} urun daha")
        self.al_birlesik_liste.setText(
            "\n".join(birlesik_satirlar) if birlesik_satirlar else "Henuz listelenecek urun yok."
        )
        
        if not liste:
            bos = QLabel("Alışveriş listeniz boş.")
            bos.setStyleSheet(f"color:{C.TEXT3};font-size:14px;padding:30px;")
            bos.setAlignment(Qt.AlignCenter)
            self.al_liste_l.insertWidget(self.al_liste_l.count() - 1, bos)
            return
            
        for urun in liste:
            sat = QFrame()
            sat.setStyleSheet(f"QFrame{{background:{C.CARD};border-radius:8px;}}")
            sat_l = QHBoxLayout(sat)
            sat_l.setContentsMargins(16, 12, 16, 12)
            
            cb = QCheckBox()
            cb.setStyleSheet(
                f"QCheckBox::indicator{{width:18px;height:18px;border-radius:4px;border:2px solid {C.BORDER2};}}"
                f"QCheckBox::indicator:checked{{background-color:{C.GOLD};border-color:{C.GOLD};}}"
            )
            cb.setChecked(bool(urun["alindi_mi"]))
            
            ad = QLabel(urun["malzeme_adi"])
            ad.setStyleSheet(f"color:{C.TEXT};font-size:13px;")
            if urun["alindi_mi"]:
                ad.setStyleSheet(f"color:{C.TEXT3};font-size:13px;text-decoration:line-through;")
                
            mik = QLabel(f"{urun['miktar']} {urun['birim']}")
            mik.setStyleSheet(f"color:{C.GOLD2};font-size:13px;font-weight:bold;")
            if urun["alindi_mi"]:
                mik.setStyleSheet(f"color:{C.TEXT3};font-size:13px;font-weight:bold;text-decoration:line-through;")
            
            def durum_degis(state, uid=urun["id"]):
                alindi = bool(state)
                self.veri.kullanici.alisveris_durum_guncelle(uid, alindi)
                self._alisveris_yenile()
                
            cb.stateChanged.connect(durum_degis)
            
            sat_l.addWidget(cb)
            sat_l.addWidget(ad, 1)
            sat_l.addWidget(mik)
            self.al_liste_l.insertWidget(self.al_liste_l.count() - 1, sat)

    def _alisveris_alinanlari_temizle(self):
        if self.veri.aktif_kullanici:
            self.veri.kullanici.alisveris_listesi_temizle(self.veri.aktif_kullanici["kullanici_id"], sadece_alinanlar=True)
            self._alisveris_yenile()
            
    def _alisveris_tumunu_temizle(self):
        if self.veri.aktif_kullanici:
            self.veri.kullanici.alisveris_listesi_temizle(self.veri.aktif_kullanici["kullanici_id"], sadece_alinanlar=False)
            self._alisveris_yenile()

    # ─── PDF İNDİRME FONKSİYONU ───
    def _alisveris_txt_disa_aktar(self):
        if not self.veri.aktif_kullanici:
            return
        kid = self.veri.aktif_kullanici["kullanici_id"]
        varsayilan = f"alisveris-listesi-{datetime.now().strftime('%Y%m%d-%H%M')}.txt"
        dosya_yolu, _ = QFileDialog.getSaveFileName(
            self, "Alisveris Listesini Kaydet", varsayilan, "Metin Dosyalari (*.txt)"
        )
        if not dosya_yolu:
            return
        metin = self.veri.kullanici.alisveris_metni_olustur(kid, sadece_bekleyenler=False)
        try:
            with open(dosya_yolu, "w", encoding="utf-8") as dosya:
                dosya.write(metin + "\n")
            Toast(self, "Alisveris listesi disa aktarildi.", "basari")
        except OSError as hata:
            QMessageBox.warning(self, "Kaydetme Hatasi", f"Dosya kaydedilemedi:\n{hata}")

    def _pdf_indir(self, tarif_id: int):
        tarif = self.veri.tarif.getir(tarif_id)
        malzemeler = self.veri.malzeme.listele(tarif_id)
        if not tarif:
            return
            
        import os
        from PyQt5.QtWidgets import QFileDialog
        
        dosya_yolu, _ = QFileDialog.getSaveFileName(
            self, "PDF Olarak Kaydet", f"{tarif['tarif_adi']}.pdf", "PDF Dosyaları (*.pdf)"
        )
        if not dosya_yolu:
            return
            
        yazici = QPdfWriter(dosya_yolu)
        yazici.setPageSize(QPageSize(QPageSize.A4))
        yazici.setResolution(300)
        
        ressam = QPainter(yazici)
        
        # Temel stil değişkenleri
        bg_color = QColor(C.BG)
        card_color = QColor(C.CARD)
        text_color = QColor(C.TEXT)
        text_color2 = QColor(C.TEXT2)
        gold_color = QColor(C.GOLD)
        
        ressam.fillRect(0, 0, yazici.width(), yazici.height(), bg_color)
        
        f_baslik = QFont("Georgia", 24, QFont.Bold)
        f_altbaslik = QFont("Georgia", 14, QFont.Bold)
        f_normal = QFont("Segoe UI", 10)
        
        y = 300
        x_sol = 300
        
        ressam.setPen(gold_color)
        ressam.setFont(f_baslik)
        ressam.drawText(x_sol, y, tarif["tarif_adi"])
        y += 200
        
        ressam.setPen(text_color2)
        ressam.setFont(f_normal)
        meta_metin = f"Kategori: {tarif['kategori']}  |  Zorluk: {tarif.get('zorluk', 'Orta')}  |  Süre: {tarif.get('hazirlama_suresi', 0)} dk  |  Porsiyon: {tarif.get('porsiyon', 4)} kişi"
        ressam.drawText(x_sol, y, meta_metin)
        y += 400
        
        ressam.setPen(gold_color)
        ressam.setFont(f_altbaslik)
        ressam.drawText(x_sol, y, "MALZEMELER")
        y += 200
        
        ressam.setPen(text_color)
        ressam.setFont(f_normal)
        for m in malzemeler:
            ressam.drawText(x_sol + 50, y, f"• {m['malzeme_adi']} - {m['miktar']} {m['birim']}")
            y += 150
            
        y += 200
        ressam.setPen(gold_color)
        ressam.setFont(f_altbaslik)
        ressam.drawText(x_sol, y, "YAPILIŞI")
        y += 200
        
        ressam.setPen(text_color)
        ressam.setFont(f_normal)
        yapilis_adim = tarif.get("yapilis", "").split("\n")
        for adim in yapilis_adim:
            if not adim.strip(): continue
            # Çok uzun satırları kesmek için basit bir yöntem kullanılabilir ama QPdfWriter da bu çok iyi sonuç vermeyebilir
            # Basit satır yazdırma:
            rect = QRect(x_sol + 50, y, yazici.width() - 800, 1000)
            ressam.drawText(rect, Qt.AlignLeft | Qt.TextWordWrap, adim.strip())
            y += 300 # tahmini yükseklik artışı
            
        ressam.end()
        Toast(self, "Tarif başarıyla PDF olarak kaydedildi.", "basari")


# ══════════════════════════════════════════════════════════════════
#  UYGULAMA GİRİŞ NOKTASI
# ══════════════════════════════════════════════════════════════════
def ornek_verileri_yukle(veri: VeriYoneticisi):
    """Eksikse demo şef hesabını, admin hesabını ve örnek tarifleri ekler."""
    kullanicilar = veri.kullanici.listele()
    sef = next((k for k in kullanicilar if k["email"] == "sef@menu.com"), None)

    if not sef:
        sonuc = veri.kullanici.ekle(
            "Şef", "Michelin", "sef@menu.com", "1234", "Baş Aşçı", rol="uye"
        )
        if sonuc["basarili"]:
            sef_id = sonuc["kullanici_id"]
        else:
            mevcut = veri.kullanici.giris_yap("sef@menu.com", "1234")
            sef_id = mevcut["kullanici_id"] if mevcut else None
    else:
        sef_id = sef["kullanici_id"]

    # ─── ADMIN hesabı seed (rol='admin', sifre='admin1234') ───
    admin = next((k for k in veri.kullanici.listele() if k["email"] == "admin@menu.com"), None)
    if not admin:
        veri.kullanici.ekle(
            "Platform", "Admin", "admin@menu.com", "admin1234",
            "Tam yetkili yonetici hesabi.", rol="admin"
        )
    elif admin.get("rol") != "admin":
        # Eski veritabanında admin@menu.com varsa ama rol yoksa güncelle
        veri.db.cursor.execute(
            "UPDATE kullanicilar SET rol='admin' WHERE email='admin@menu.com'"
        )
        veri.db.conn.commit()

    if not sef_id:
        return

    kullanici_haritasi = {k["email"]: k["kullanici_id"] for k in veri.kullanici.listele()}
    for ad, soyad, email, sifre, bio in ORNEK_KULLANICILAR:
        if email not in kullanici_haritasi:
            sonuc = veri.kullanici.ekle(ad, soyad, email, sifre, bio)
            if sonuc["basarili"]:
                kullanici_haritasi[email] = sonuc["kullanici_id"]
    kullanici_haritasi["sef@menu.com"] = sef_id

    var_olan_tarifler = {t["tarif_adi"] for t in veri.tarif.listele()}
    for tarif in ORNEK_TARIFLER:
        if tarif["ad"] in var_olan_tarifler:
            continue

        sonuc = veri.tarif.tarif_ekle(
            tarif_adi=tarif["ad"],
            kategori=tarif["kategori"],
            hazirlama_suresi=tarif["sure"],
            kullanici_id=sef_id,
            porsiyon=tarif["porsiyon"],
            zorluk=tarif["zorluk"],
            aciklama=tarif["aciklama"],
            yapilis=tarif["yapilis"],
        )
        if not sonuc["basarili"]:
            continue

        tarif_id = sonuc["tarif_id"]
        for malzeme_adi, miktar, birim in tarif["malzemeler"]:
            veri.malzeme.ekle(tarif_id, malzeme_adi, miktar, birim)
        veri.kullanici.tarif_degerlendir(
            sef_id, tarif_id, tarif["puan"], tarif["yorum"]
        )
        for email, puan, yorum in tarif.get("yorumlar", []):
            kullanici_id = kullanici_haritasi.get(email)
            if kullanici_id:
                veri.kullanici.tarif_degerlendir(kullanici_id, tarif_id, puan, yorum)
        var_olan_tarifler.add(tarif["ad"])

    mevcut_tarifler = {t["tarif_adi"]: t["tarif_id"] for t in veri.tarif.listele()}
    for tarif in ORNEK_TARIFLER:
        tarif_id = mevcut_tarifler.get(tarif["ad"])
        if not tarif_id:
            continue
        veri.kullanici.tarif_degerlendir(
            sef_id, tarif_id, tarif["puan"], tarif["yorum"]
        )
        for email, puan, yorum in tarif.get("yorumlar", []):
            kullanici_id = kullanici_haritasi.get(email)
            if kullanici_id:
                veri.kullanici.tarif_degerlendir(kullanici_id, tarif_id, puan, yorum)


if __name__ == "__main__":
    app = QApplication(sys.argv)

    # Genel font ayarı
    font = QFont("Segoe UI", 10)
    app.setFont(font)

    veri = VeriYoneticisi()
    
    # Arayüz açılmadan önce tarif listesini kontrol et ve doldur
    ornek_verileri_yukle(veri)
    
    pencere = AnaPencere(veri)
    pencere.show()

    log("Platform başlatıldı", C.GOLD)
    sys.exit(app.exec_())
