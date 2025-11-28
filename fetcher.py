import feedparser
import requests
from io import BytesIO
import time
import sys
import json
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Optional, List, Dict
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib

class RSSFetcher:
    """
    Gelişmiş RSS/Atom feed çekici.
    Özellikler:
    - User-Agent rotation
    - Retry mekanizması
    - Cache desteği
    - OPML parse
    - Paralel indirme
    - Rate limiting
    """
    
    def __init__(self, cache_enabled=True, max_workers=5):
        self.cache = {} if cache_enabled else None
        self.max_workers = max_workers
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        ]
        self.request_times = []  # Rate limiting için
        
    def _get_cache_key(self, url: str) -> str:
        """URL'den cache key oluştur"""
        return hashlib.md5(url.encode()).hexdigest()
    
    def _check_rate_limit(self, max_requests_per_minute=30):
        """Rate limiting kontrolü"""
        now = time.time()
        # Son 1 dakikadaki istekleri filtrele
        self.request_times = [t for t in self.request_times if now - t < 60]
        
        if len(self.request_times) >= max_requests_per_minute:
            sleep_time = 60 - (now - self.request_times[0])
            print(f"⏳ Rate limit aşıldı. {sleep_time:.1f} saniye bekleniyor...")
            time.sleep(sleep_time)
        
        self.request_times.append(now)
    
    def fetch_feed(self, url: str, retries=3, use_cache=True) -> Optional[feedparser.FeedParserDict]:
        """
        RSS beslemesini güvenli ve sağlam bir şekilde çeker.
        """
        # Cache kontrolü
        if use_cache and self.cache is not None:
            cache_key = self._get_cache_key(url)
            if cache_key in self.cache:
                print(f"💾 Cache'den yükleniyor: {url}")
                return self.cache[cache_key]
        
        headers = {
            'User-Agent': self.user_agents[0],  # İlk user agent'ı kullan
            'Accept': 'application/rss+xml, application/xml, application/atom+xml, text/xml;q=0.9, */*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.9,tr;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
        }

        for attempt in range(retries):
            try:
                # Rate limiting
                self._check_rate_limit()
                
                print(f"📡 Bağlanılıyor: {url} (Deneme {attempt+1}/{retries})")
                
                # Her denemede farklı User-Agent kullan
                if attempt > 0:
                    headers['User-Agent'] = self.user_agents[attempt % len(self.user_agents)]
                
                response = requests.get(
                    url, 
                    headers=headers, 
                    timeout=15,
                    allow_redirects=True
                )
                
                response.raise_for_status()
                
                # Content-Type kontrolü
                content_type = response.headers.get('Content-Type', '')
                if 'xml' not in content_type and 'rss' not in content_type and 'atom' not in content_type:
                    print(f"⚠️ Uyarı: Beklenmeyen Content-Type: {content_type}")
                
                feed = feedparser.parse(BytesIO(response.content))
                
                if feed.bozo:
                    print(f"⚠️ XML Uyarısı: {feed.bozo_exception}")
                
                # Başarılı sonucu cache'e kaydet
                if self.cache is not None:
                    self.cache[self._get_cache_key(url)] = feed
                
                return feed

            except requests.exceptions.HTTPError as e:
                if e.response.status_code in [404, 410]:  # Not Found, Gone
                    print(f"❌ Feed bulunamadı (HTTP {e.response.status_code})")
                    break
                elif e.response.status_code == 403:
                    print(f"⛔ Erişim engellendi (HTTP 403). User-Agent değiştiriliyor...")
                elif e.response.status_code == 429:
                    print(f"⏰ Çok fazla istek (HTTP 429). Bekleniyor...")
                    time.sleep(5 * (attempt + 1))
                else:
                    print(f"❌ HTTP Hatası: {e}")
                    
            except requests.exceptions.Timeout:
                print(f"⏱️ Zaman aşımı. Tekrar deneniyor...")
                time.sleep(2 * (attempt + 1))
                
            except requests.exceptions.ConnectionError as e:
                print(f"🔌 Bağlantı hatası: {e}")
                time.sleep(3 * (attempt + 1))
                
            except Exception as e:
                print(f"❌ Beklenmeyen hata: {e}")
                break
        
        return None
    
    def parse_opml(self, opml_file: str) -> Dict[str, List[Dict]]:
        """
        OPML dosyasını parse eder ve kategorilere göre feed'leri döndürür.
        """
        try:
            tree = ET.parse(opml_file)
            root = tree.getroot()
            
            categories = {}
            
            for outline in root.findall('.//outline[@text]'):
                # Kategori mi yoksa feed mi?
                if outline.find('outline') is not None:
                    # Bu bir kategori
                    category_name = outline.get('text') or outline.get('title')
                    categories[category_name] = []
                    
                    for feed_outline in outline.findall('outline[@xmlUrl]'):
                        feed_info = {
                            'title': feed_outline.get('text'),
                            'url': feed_outline.get('xmlUrl'),
                            'type': feed_outline.get('type', 'rss')
                        }
                        categories[category_name].append(feed_info)
                        
            return categories
            
        except Exception as e:
            print(f"❌ OPML parse hatası: {e}")
            return {}
    
    def fetch_multiple(self, urls: List[str], show_progress=True) -> Dict[str, feedparser.FeedParserDict]:
        """
        Birden fazla feed'i paralel olarak çeker.
        """
        results = {}
        
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_url = {executor.submit(self.fetch_feed, url): url for url in urls}
            
            for future in as_completed(future_to_url):
                url = future_to_url[future]
                try:
                    feed = future.result()
                    results[url] = feed
                    if show_progress:
                        status = "✅" if feed else "❌"
                        print(f"{status} {url}")
                except Exception as e:
                    print(f"❌ {url}: {e}")
                    results[url] = None
        
        return results
    
    def export_to_json(self, feed: feedparser.FeedParserDict, output_file: str):
        """
        Feed'i JSON formatında dışa aktarır.
        """
        if not feed:
            print("❌ Dışa aktarılacak veri yok.")
            return
        
        data = {
            'feed_info': {
                'title': feed.feed.get('title', ''),
                'link': feed.feed.get('link', ''),
                'description': feed.feed.get('description', ''),
                'updated': feed.feed.get('updated', '')
            },
            'entries': []
        }
        
        for entry in feed.entries:
            entry_data = {
                'title': entry.get('title', ''),
                'link': entry.get('link', ''),
                'published': entry.get('published', ''),
                'summary': entry.get('summary', '')[:200]  # İlk 200 karakter
            }
            data['entries'].append(entry_data)
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ JSON'a aktarıldı: {output_file}")

def display_feed_summary(feed: Optional[feedparser.FeedParserDict], show_entries=5):
    """Feed özetini ekrana yazdırır."""
    if not feed:
        print("❌ Veri çekilemedi.\n")
        return

    print("\n" + "="*70)
    print(f"📰 Başlık: {feed.feed.get('title', 'Başlık Yok')}")
    print(f"🔗 Link:   {feed.feed.get('link', 'Link Yok')}")
    
    description = feed.feed.get('description', 'Açıklama Yok')
    if len(description) > 100:
        description = description[:100] + "..."
    print(f"📝 Açıklama: {description}")
    
    if hasattr(feed.feed, 'updated'):
        print(f"🕒 Güncelleme: {feed.feed.updated}")
    
    print(f"📊 Toplam İçerik: {len(feed.entries)}")
    print("="*70 + "\n")

    print(f"Son {min(show_entries, len(feed.entries))} İçerik:")
    for i, entry in enumerate(feed.entries[:show_entries], 1):
        print(f"\n{i}. {entry.title}")
        print(f"   👉 {entry.link}")
        
        if hasattr(entry, 'published'):
            print(f"   📅 {entry.published}")
        
        if hasattr(entry, 'summary'):
            summary = entry.summary[:150].replace('\n', ' ')
            print(f"   📄 {summary}...")
        
        print("-" * 70)

def main():
    """Ana program"""
    fetcher = RSSFetcher(cache_enabled=True, max_workers=5)
    
    # Tek feed test
    print("=== TEK FEED TEST ===\n")
    test_urls = [
        "https://netflixtechblog.com/feed",
        "http://export.arxiv.org/rss/cs",
        "https://news.ycombinator.com/rss"
    ]
    
    for url in test_urls:
        feed = fetcher.fetch_feed(url)
        display_feed_summary(feed, show_entries=3)
        print("\n" + "="*70 + "\n")
    
    # Paralel fetch test
    print("\n\n=== PARALEL FETCH TEST ===\n")
    results = fetcher.fetch_multiple(test_urls)
    
    success_count = sum(1 for feed in results.values() if feed)
    print(f"\n✅ Başarılı: {success_count}/{len(test_urls)}")
    
    # JSON export örneği
    if results.get(test_urls[0]):
        fetcher.export_to_json(results[test_urls[0]], 'netflix_feed.json')

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️ Program kullanıcı tarafından durduruldu.")
        sys.exit(0)
