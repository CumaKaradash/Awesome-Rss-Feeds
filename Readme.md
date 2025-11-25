# RSS Beslemeleri Koleksiyonu
---
## Proje Hakkında

Bu proje, popüler web siteleri ve servisler için kullanılabilir RSS/Atom beslemelerinin kapsamlı bir koleksiyonudur. Haber siteleri, sosyal medya platformları, teknoloji blogları ve daha fazlası için düzenli olarak güncellenen RSS kaynakları sunmaktadır.

## İçindekiler

- [Özellikler](#-özellikler)
- [Desteklenen Servisler](#-desteklenen-servisler)
- [Kullanım](#-kullanım)
- [Katkıda Bulunma](#-katkıda-bulunma)
- [Güncellemeler](#-güncellemeler)
- [Lisans](#-lisans)

##  Özellikler

-  Kategorilere ayrılmış RSS kaynakları
-  Düzenli olarak güncellenen bağlantılar
-  Türkçe ve global kaynaklar
-  Kolay entegrasyon
-  Mobil uyumlu beslemeler

##  Desteklenen Servisler

###  Haber Siteleri

#### Global Kaynaklar
- **Google Haberler**: `https://news.google.com/rss`
- **BBC News**: `http://feeds.bbci.co.uk/news/rss.xml`
- **CNN**: `https://rss.cnn.com/rss/edition.rss`
- **Reuters**: `https://www.reuters.com/tools/rss`

#### Türkçe Kaynaklar
- **Hürriyet**: `https://www.hurriyet.com.tr/rss`
- **Milliyet**: `https://www.milliyet.com.tr/rss/rssnew/anasayfaRss.xml`
- **Anadolu Ajansı**: `https://www.aa.com.tr/tr/rss/default?cat=guncel`
- **TRT Haber**: `https://www.trthaber.com/rss`

### Teknoloji ve Yazılım
- **Stack Overflow**: `https://stackoverflow.com/feeds`
- **GitHub**: `https://github.com/{KULLANICI_ADI}.atom`
- **Adobe Blog**: `https://blog.adobe.com/en/feed.xml`

### Oyun ve Dijital Platformlar
- **Steam**: `https://store.steampowered.com/feeds/news.xml`
- **Epic Games**: `https://www.epicgames.com/store/en-US/feed.xml`

### Video ve Medya
- **YouTube**: `https://www.youtube.com/feeds/videos.xml?channel_id={KANAL_ID}`
- **Spotify**: Podcast bazlı RSS adresleri podcast sayfalarından elde edilebilir

[Tüm liste için tıklayın](feeds.md)

##  Kullanım

### RSS Okuyucu için
1. İstediğiniz servisin RSS adresini kopyalayın
2. RSS okuyucunuza yapıştırın
3. Özelleştirilebilir beslemeler için `{PARAMETRE}` değerlerini değiştirin

### API Entegrasyonu için
```python
import feedparser

# RSS beslemesini okuma
feed = feedparser.parse('RSS_ADRESİ')

# Başlıkları listeleme
for entry in feed.entries:
    print(entry.title)
```

##  Lisans

Bu proje [MIT Lisansı](LICENSE) ile lisanslanmıştır.

##  Projeye Destek Ol

Eğer bu proje işinize yaradıysa, ⭐ vermeyi unutmayın!
