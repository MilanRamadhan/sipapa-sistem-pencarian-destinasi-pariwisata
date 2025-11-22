"""
Test scraping dengan cleaning dan ekstraksi gambar yang lebih baik.
Hanya scrape 100 URL pertama sebagai test.
"""
import os
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR = Path(__file__).parent
URL_FILE = BASE_DIR / "data" / "urls_test.txt"  # Test dengan 100 URL
OUTPUT_FILE = BASE_DIR / "data" / "scraped_test.csv"

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

REQUEST_TIMEOUT = 15
SLEEP_BETWEEN_REQUESTS = 0.2
MIN_WORDS = 40

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def load_urls(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"File URL tidak ditemukan: {path}")
    
    with path.open(encoding="utf-8") as f:
        raw = [line.strip() for line in f if line.strip()]
    
    seen = set()
    urls = []
    for u in raw:
        if u not in seen:
            seen.add(u)
            urls.append(u)
    
    print(f"[INFO] Total URL di {path.name}: {len(urls)}")
    return urls

def is_article_url(url: str) -> bool:
    parsed = urlparse(url)
    path = parsed.path or ""

    blocked_fragments = ["/copy/", "/komentar/", "/image/", "/search/"]
    if any(b in path for b in blocked_fragments):
        return False

    if path in ["", "/"]:
        return False

    return True

def clean_content(content: str, title: str) -> str:
    if not content:
        return ""
    
    if title:
        lines = content.split('\n')
        cleaned_lines = []
        skip_count = 0
        
        for line in lines:
            line_lower = line.strip().lower()
            title_lower = title.strip().lower()
            
            if skip_count < 3 and (line_lower == title_lower or title_lower in line_lower and len(line_lower) < len(title_lower) + 20):
                skip_count += 1
                continue
            
            if skip_count < 2 and (line_lower in ['editor', 'tim redaksi', 'reporter']):
                skip_count += 1
                continue
                
            cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
    
    content = re.sub(r'Baca juga:.*?(?=\n|$)', '', content, flags=re.IGNORECASE)
    content = re.sub(r'Sebuah kiriman dibagikan oleh.*?(?=\n|$)', '', content, flags=re.IGNORECASE)
    content = re.sub(r'Copyright \d{4}.*?All Rights Reserved\.?', '', content, flags=re.IGNORECASE)
    content = re.sub(r'©.*?\d{4}.*?(?=\n|$)', '', content, flags=re.IGNORECASE)
    content = re.sub(r'[A-Z]+\.[A-Z]+/[A-Z]+(?=[A-Z])', '', content)
    content = re.sub(r'\n\s*\n', '\n\n', content)
    content = re.sub(r' +', ' ', content)
    content = content.strip()
    
    return content

def extract_images(soup: BeautifulSoup) -> str:
    og_image = soup.find("meta", attrs={"property": "og:image"})
    if og_image and og_image.get("content"):
        return og_image["content"].strip()
    
    twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
    if twitter_image and twitter_image.get("content"):
        return twitter_image["content"].strip()
    
    article_containers = soup.find_all(["article", "div"], class_=lambda x: x and ('article' in x.lower() or 'content' in x.lower()))
    for container in article_containers:
        img = container.find("img", src=True)
        if img and img.get("src"):
            src = img["src"].strip()
            if not src.startswith('data:') and 'icon' not in src.lower() and 'logo' not in src.lower():
                return src
    
    img = soup.find("img", src=True)
    if img and img.get("src"):
        src = img["src"].strip()
        if not src.startswith('data:'):
            return src
    
    return ""

def extract_article(url: str, html: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    title = None

    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()

    if not title:
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

    if not title:
        title = "No Title"

    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    paragraphs = [p for p in paragraphs if p]
    content = "\n".join(paragraphs)
    content = clean_content(content, title)
    image_url = extract_images(soup)
    word_count = len(content.split())

    return {
        "url": url,
        "domain": urlparse(url).netloc,
        "title": title,
        "content": content,
        "image_url": image_url,
        "word_count": word_count,
        "timestamp": time.time(),
    }

def fetch(url: str):
    try:
        res = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        if res.status_code == 200:
            return res.text
        else:
            print(f"[STATUS {res.status_code}] {url}")
            return None
    except Exception as e:
        print(f"[ERROR] {url} -> {e}")
        return None

def scrape_one(url: str):
    print(f"[SCRAPE] {url}")
    html = fetch(url)
    if not html:
        return None

    article = extract_article(url, html)

    if not article["content"] or article["word_count"] < MIN_WORDS:
        print(f"[SKIP - KONTEN PENDEK] {url}")
        return None

    has_image = "Y" if article["image_url"] else "N"
    print(f"[OK] {url} (~{article['word_count']} kata) [Gambar: {has_image}]")
    return article

def scrape_all():
    urls = load_urls(URL_FILE)
    article_urls = [u for u in urls if is_article_url(u)]
    print(f"[INFO] URL yang lolos filter pola artikel: {len(article_urls)}")

    results = []
    start_time = time.time()

    for idx, url in enumerate(article_urls, start=1):
        print(f"\n[{idx}/{len(article_urls)}]")
        data = scrape_one(url)
        if data:
            results.append(data)

        time.sleep(SLEEP_BETWEEN_REQUESTS)

    elapsed = time.time() - start_time
    print(f"\n[INFO] Scraping selesai dalam {elapsed:.2f} detik.")
    print(f"[INFO] Total artikel valid: {len(results)}")
    
    with_images = sum(1 for r in results if r.get("image_url"))
    print(f"[INFO] Artikel dengan gambar: {with_images}/{len(results)} ({with_images/len(results)*100:.1f}%)")

    return results

if __name__ == "__main__":
    print(f"[INFO] TEST MODE - Scraping 100 URL pertama")
    print(f"[INFO] Working Directory : {BASE_DIR}")
    print(f"[INFO] URL source       : {URL_FILE}")
    print(f"[INFO] Output CSV       : {OUTPUT_FILE}\n")

    results = scrape_all()

    if results:
        df = pd.DataFrame(results)
        df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
        print(f"\n[SUCCESS] Scraping selesai! File disimpan ke: {OUTPUT_FILE}")
        print(f"[INFO] Total data berhasil di-scrape: {len(results)}")
        
        print("\n[PREVIEW] 3 data pertama:")
        for idx, row in df.head(3).iterrows():
            print(f"\n{idx+1}. {row['title']}")
            print(f"   URL: {row['url']}")
            print(f"   Image: {row['image_url'][:80] if row['image_url'] else 'Tidak ada'}")
            print(f"   Content preview: {row['content'][:150]}...")
    else:
        print("\n[WARNING] Tidak ada data yang berhasil di-scrape!")
