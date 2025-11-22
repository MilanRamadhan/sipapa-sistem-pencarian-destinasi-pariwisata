import os
import re
import time
import requests
import pandas as pd
from bs4 import BeautifulSoup
from pathlib import Path
from urllib.parse import urlparse

# ============================
# PATH FILE
# ============================
BASE_DIR = Path(__file__).parent
URL_FILE = BASE_DIR / "data" / "urls.txt"
OUTPUT_FILE = BASE_DIR / "data" / "scraped.csv"

OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

# ============================
# PARAMETER SCRAPING
# ============================
REQUEST_TIMEOUT = 15  # detik
SLEEP_BETWEEN_REQUESTS = 0.2  # jeda antar request biar sopan
MIN_WORDS = 40  # minimal jumlah kata supaya artikel dianggap valid

# User-Agent biar nggak keliatan terlalu "robot"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

# ============================
# BACA URL DARI urls.txt
# ============================
def load_urls(path: Path) -> list:
    if not path.exists():
        raise FileNotFoundError(f"File URL tidak ditemukan: {path}")
    
    with path.open(encoding="utf-8") as f:
        raw = [line.strip() for line in f if line.strip()]
    
    # Hapus duplikat tapi jaga urutan
    seen = set()
    urls = []
    for u in raw:
        if u not in seen:
            seen.add(u)
            urls.append(u)
    
    print(f"[INFO] Total URL di {path.name}: {len(urls)}")
    return urls

# ============================
# FILTER: CUMA AMBIL URL ARTIKEL
# ============================
def is_article_url(url: str) -> bool:
    """
    Filter URL supaya:
    - Nggak ambil /copy/, /komentar/, /image/, /search/ (bukan artikel utama)
    - Nggak ambil homepage / halaman root
    """
    parsed = urlparse(url)
    path = parsed.path or ""

    # Buang path yang jelas bukan artikel
    blocked_fragments = [
        "/copy/",
        "/komentar/",
        "/image/",
        "/search/",
    ]
    if any(b in path for b in blocked_fragments):
        return False

    # Buang homepage dan path kosong
    if path in ["", "/"]:
        return False

    return True

# ============================
# CLEAN KONTEN ARTIKEL
# ============================
def clean_content(content: str, title: str) -> str:
    """
    Bersihkan konten artikel dari noise:
    - Judul duplikat di awal konten
    - 'Baca juga:' dan link-nya
    - Caption Instagram 'Sebuah kiriman dibagikan oleh'
    - Copyright footer
    - Editor/Tim Redaksi di awal
    - Whitespace berlebih
    """
    if not content:
        return ""
    
    # Hapus judul duplikat di awal (case-insensitive)
    if title:
        # Hapus judul yang muncul di awal konten
        lines = content.split('\n')
        cleaned_lines = []
        skip_count = 0
        
        for line in lines:
            line_lower = line.strip().lower()
            title_lower = title.strip().lower()
            
            # Skip jika line adalah judul atau judul duplikat
            if skip_count < 3 and (line_lower == title_lower or title_lower in line_lower and len(line_lower) < len(title_lower) + 20):
                skip_count += 1
                continue
            
            # Skip editor/tim redaksi di awal
            if skip_count < 2 and (line_lower in ['editor', 'tim redaksi', 'reporter']):
                skip_count += 1
                continue
                
            cleaned_lines.append(line)
        
        content = '\n'.join(cleaned_lines)
    
    # Hapus 'Baca juga:' beserta linknya (biasanya satu baris)
    content = re.sub(r'Baca juga:.*?(?=\n|$)', '', content, flags=re.IGNORECASE)
    
    # Hapus caption Instagram
    content = re.sub(r'Sebuah kiriman dibagikan oleh.*?(?=\n|$)', '', content, flags=re.IGNORECASE)
    
    # Hapus copyright footer
    content = re.sub(r'Copyright \d{4}.*?All Rights Reserved\.?', '', content, flags=re.IGNORECASE)
    content = re.sub(r'©.*?\d{4}.*?(?=\n|$)', '', content, flags=re.IGNORECASE)
    
    # Hapus caption gambar yang sering mengganggu (KOMPAS.COM/NAMA)
    content = re.sub(r'[A-Z]+\.[A-Z]+/[A-Z]+(?=[A-Z])', '', content)
    
    # Rapikan whitespace
    content = re.sub(r'\n\s*\n', '\n\n', content)  # max 2 newlines
    content = re.sub(r' +', ' ', content)  # single space
    content = content.strip()
    
    return content

# ============================
# EXTRACT GAMBAR ARTIKEL
# ============================
def extract_images(soup: BeautifulSoup) -> str:
    """
    Ekstrak URL gambar utama artikel:
    1. Dari meta og:image (Open Graph)
    2. Dari img tag pertama di article/content area
    """
    # Prioritas 1: Open Graph image
    og_image = soup.find("meta", attrs={"property": "og:image"})
    if og_image and og_image.get("content"):
        return og_image["content"].strip()
    
    # Prioritas 2: Twitter card image
    twitter_image = soup.find("meta", attrs={"name": "twitter:image"})
    if twitter_image and twitter_image.get("content"):
        return twitter_image["content"].strip()
    
    # Prioritas 3: Gambar pertama di area artikel
    # Coba cari di container artikel dulu
    article_containers = soup.find_all(["article", "div"], class_=lambda x: x and ('article' in x.lower() or 'content' in x.lower()))
    for container in article_containers:
        img = container.find("img", src=True)
        if img and img.get("src"):
            src = img["src"].strip()
            # Skip gambar kecil/icon (biasanya <100px atau base64)
            if not src.startswith('data:') and 'icon' not in src.lower() and 'logo' not in src.lower():
                return src
    
    # Fallback: gambar pertama di seluruh halaman
    img = soup.find("img", src=True)
    if img and img.get("src"):
        src = img["src"].strip()
        if not src.startswith('data:'):
            return src
    
    return ""

# ============================
# EXTRACT TEKS DARI HTML
# ============================
def extract_article(url: str, html: str) -> dict:
    """
    Ambil title + content (gabungan <p>) + image dari halaman.
    Untuk detikTravel & KompasTravel, ambil semua <p> sudah cukup bagus.
    """
    soup = BeautifulSoup(html, "html.parser")

    # Title
    title = None

    # Coba dari <meta property="og:title">
    og_title = soup.find("meta", attrs={"property": "og:title"})
    if og_title and og_title.get("content"):
        title = og_title["content"].strip()

    # Kalau belum ketemu, pakai <title>
    if not title:
        title_tag = soup.find("title")
        if title_tag:
            title = title_tag.get_text(strip=True)

    if not title:
        title = "No Title"

    # Kumpulin semua <p>
    paragraphs = [p.get_text(strip=True) for p in soup.find_all("p")]
    paragraphs = [p for p in paragraphs if p]
    content = "\n".join(paragraphs)
    
    # Bersihkan konten dari noise
    content = clean_content(content, title)
    
    # Ekstrak gambar artikel
    image_url = extract_images(soup)

    # Hitung jumlah kata, buat ngecek minimal
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

# ============================
# HTTP REQUEST
# ============================
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

# ============================
# SCRAPE SATU URL
# ============================
def scrape_one(url: str):
    print(f"[SCRAPE] {url}")
    html = fetch(url)
    if not html:
        return None

    article = extract_article(url, html)

    # Skip jika konten terlalu pendek
    if not article["content"] or article["word_count"] < MIN_WORDS:
        print(f"[SKIP - KONTEN PENDEK] {url}")
        return None

    print(f"[OK] {url} (≈ {article['word_count']} kata)")
    return article

# ============================
# MAIN: LOOP SCRAPING
# ============================
def scrape_all():
    urls = load_urls(URL_FILE)

    # Filter URL supaya cuma artikel utama
    article_urls = [u for u in urls if is_article_url(u)]
    print(f"[INFO] URL yang lolos filter pola artikel: {len(article_urls)}")

    results = []
    start_time = time.time()

    for idx, url in enumerate(article_urls, start=1):
        print(f"\n[{idx}/{len(article_urls)}]")
        data = scrape_one(url)
        if data:
            results.append(data)

        # Jeda kecil antar request
        time.sleep(SLEEP_BETWEEN_REQUESTS)

    elapsed = time.time() - start_time
    print(f"\n[INFO] Scraping selesai dalam {elapsed:.2f} detik.")
    print(f"[INFO] Total artikel valid: {len(results)}")

    return results

# ============================
# EKSEKUSI UTAMA
# ============================
if __name__ == "__main__":
    print(f"[INFO] Working Directory : {BASE_DIR}")
    print(f"[INFO] URL source       : {URL_FILE}")
    print(f"[INFO] Output CSV       : {OUTPUT_FILE}\n")

    results = scrape_all()

    if results:
        df = pd.DataFrame(results)
        df.to_csv(OUTPUT_FILE, index=False, encoding="utf-8-sig")
        print(f"\n[SUCCESS] Scraping selesai! File disimpan ke: {OUTPUT_FILE}")
        print(f"[INFO] Total data berhasil di-scrape: {len(results)}")

        # Preview
        print("\n[PREVIEW] 5 data pertama:")
        print(df.head())
    else:
        print("\n[WARNING] Tidak ada data yang berhasil di-scrape!")
