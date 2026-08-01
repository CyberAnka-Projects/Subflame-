# Subflame

Subfinder tabanlı, Türkçe arayüzlü alt alan adı keşif ve canlılık kontrolü aracı.

[![Subflame ana arayüz](https://github.com/CyberAnka-Projects/Subflame-/blob/main/docs/arayuz.png)

Subflame; hedef alan adlarının alt alan adlarını toplar, HTTP/HTTPS canlılık kontrolünden geçirir, kategori bazında sınıflandırır ve sonuçları Excel veya metin dosyası olarak dışa aktarır.

> Uyarı: Bu araç yalnızca sahibi olduğunuz veya test yetkisi bulunan sistemlerde kullanılmalıdır. İzinsiz kullanım sorumluluğu kullanıcıya aittir.

## Özellikler

- Subfinder tabanlı alt alan adı keşfi (tekli alan adı veya dosyadan çoklu alan adı)
- HTTP/HTTPS canlılık kontrolü: durum kodu, sunucu ve sayfa başlığı tespiti
- Otomatik kategorilendirme: Yönetim, API, Veri, Ağ, Medya, Yedek
- Kategoriye göre renkli akordeon sonuç paneli
- Anahtar kelime ve port bazlı filtreleme (ör. `api`, `admin`, `443`)
- Excel (.xls) ve metin (.txt) dışa aktarma
- Ayarlanabilir iş parçacığı, zaman aşımı ve maksimum süre
- Duraklatma, durdurma ve devam etme kontrolü

## Gereksinimler

- Python 3.8 veya üzeri
- [subfinder](https://github.com/projectdiscovery/subfinder) (Go aracı)

Python bağımlılıkları (`customtkinter`, `Pillow`, `requests`, `urllib3`, `xlsxwriter`) ilk çalıştırmada otomatik kurulur; ayrıca kurulum gerekmez.

## Kurulum

Yalnızca `subfinder` aracını kurmanız yeterlidir:

```bash
# Linux / macOS
go install -v github.com/projectdiscovery/subfinder/v2/cmd/subfinder@latest

# Alternatif (Debian/Ubuntu)
sudo apt install subfinder
```

Windows'ta subfinder `%USERPROFILE%\go\bin\subfinder.exe` yoluna kurulur. Kurulu exe dosyasını arayüzdeki `SUBFINDER SEÇ` butonuyla manuel olarak da seçebilirsiniz.

## Kullanım

```bash
python3 subflame.py
```

1. Hedef alan adını girin (ör. `ornek.com`) veya satır satır alan adları içeren bir `.txt` dosyası verin.
2. `BAŞLAT` ile alt alan adı keşfini çalıştırın.
3. Tarama sonrası `CANLI DOMAİN TARA` ile canlı hostları tespit edin.
4. Sonuçları `KAYDET` veya `CANLI DOMAİNLERİ KAYDET` ile dışa aktarın.

## Ekran Görüntüleri

[![Karşılama Ekranı](https://github.com/CyberAnka-Projects/Subflame-/blob/main/docs/karsilama.png)

[![Tarama sonucu](https://github.com/CyberAnka-Projects/Subflame-/blob/main/docs/tarama.png)


## Teknik Detaylar

- Alt alan adı keşfi: subfinder (8.8.8.8, 1.1.1.1, 9.9.9.9, 208.67.222.222 genel DNS sunucuları)
- Canlılık kontrolü: 80/443 portlarına soket bağlantısı ve HTTP isteği
- Arayüz: CustomTkinter ve Pillow (GIF animasyonu, logo, arka plan)
- Dışa aktarma: xlsxwriter (Excel) ve düz metin

## Klasör Yapısı

```
├── subflame.py          # Ana uygulama
├── requirements.txt     # Bağımlılık listesi (opsiyonel, elle kurulum için)
├── docs/                # Ekran görüntüleri
│   ├── arayuz.png
│   ├── tarama.png
│   ├── canli-tarama.png
│   └── excel.png
├── LICENSE              # MIT Lisansı
└── README.md
```

## Lisans

Bu proje MIT Lisansı ile lisanslanmıştır. Ayrıntılar için [LICENSE](LICENSE) dosyasına bakın.
