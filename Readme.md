# RSS Beslemeleri Koleksiyonu (Awesome RSS Feeds)

## Proje Hakkında

Bu proje, sadece popüler haber sitelerini değil, aynı zamanda akademik araştırmaları, mühendislik bloglarını ve teknik dökümanları takip etmek isteyenler için küratörlüğü yapılmış kapsamlı bir RSS/Atom koleksiyonudur.

Sıradan bir link listesi olmanın ötesinde, araştırmacılar ve yazılım mühendisleri için özelleştirilmiş kaynaklar ve Python entegrasyon kodları içerir.

## İçindekiler

- [Özellikler](#özellikler)
- [Kategoriler](#kategoriler)
- [Hızlı Kurulum (OPML)](#hızlı-kurulum-opml)
- [Geliştirici Kullanımı (Python)](#geliştirici-kullanımı-python)
- [Katkıda Bulunma](#katkıda-bulunma)
- [Lisans](#lisans)

## Özellikler

- 📚 **Akademik Odak**: arXiv, Nature, Science ve IEEE kaynakları
- 🔧 **Teknik Derinlik**: Netflix, Uber, Google AI gibi şirketlerin mühendislik blogları
- 📥 **Toplu İçe Aktarma**: .opml dosyası ile yüzlerce kaynağı tek tıkla okuyucunuza ekleme imkanı
- 🤖 **Bot Korumalı Script**: Cloudflare veya bot korumasına takılmadan veri çeken örnek kodlar
- 🇹🇷 **Yerel ve Global**: Türkçe haber kaynakları ve global otoriteler bir arada

## Kategoriler

Detaylı liste için [feeds.md](feeds.md) dosyasına bakınız. Öne çıkan başlıklar:

- **Akademik & Bilim**: NASA, CERN, arXiv (CS/Physics)
- **Engineering Blogs**: Big Tech şirketlerinin teknik makaleleri
- **Haberler**: Yerel ve Global ajanslar
- **Teknoloji**: Hacker News, Stack Overflow
- **Sosyal Medya & Eğlence**: YouTube, Reddit, Steam

## Hızlı Kurulum (OPML)

RSS okuyucunuza (Feedly, Inoreader, Thunderbird vb.) tek tek link eklemekle uğraşmayın:

1. Bu depodaki `feeds.opml` dosyasını indirin
2. RSS okuyucunuzun "Import OPML" seçeneğini kullanın
3. Tüm kategoriler otomatik olarak listenize eklenecektir

## Geliştirici Kullanımı (Python)

Modern web siteleri (özellikle Cloudflare arkasındakiler), basit urllib veya feedparser isteklerini "bot" olarak algılayıp engelleyebilir. Aşağıdaki yöntem ile tarayıcı gibi davranarak veri çekebilirsiniz.

### Gereksinimler

```bash
pip install feedparser requests
```

### Örnek Kod

```python
import feedparser
import requests
from io import BytesIO

def fetch_rss(url):
    # User-Agent header'ı ekleyerek gerçek bir tarayıcı taklidi yapıyoruz
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()  # HTTP hatalarını yakala
        
        feed = feedparser.parse(BytesIO(response.content))
        
        print(f"Kaynak: {feed.feed.get('title', 'Bilinmeyen Kaynak')}")
        for entry in feed.entries[:5]:
            print(f"- {entry.title} ({entry.link})")
            
    except Exception as e:
        print(f"Hata oluştu: {e}")

# Test: Netflix Mühendislik Blogu
fetch_rss('https://netflixtechblog.com/feed')
```

Daha gelişmiş bir script için depodaki `fetcher.py` dosyasına göz atın.

## Katkıda Bulunma

1. Fork yapın
2. Yeni bir dal (branch) oluşturun (`git checkout -b feature/YeniKaynak`)
3. Değişikliklerinizi commit edin (`git commit -m 'Yeni AI blogları eklendi'`)
4. Dalınızı pushlayın (`git push origin feature/YeniKaynak`)
5. Bir Pull Request oluşturun

## Lisans

Bu proje MIT Lisansı ile lisanslanmıştır.

---

**Not**: Projeye katkıda bulunmak veya yeni RSS kaynakları önermek için issues bölümünü kullanabilirsiniz.
