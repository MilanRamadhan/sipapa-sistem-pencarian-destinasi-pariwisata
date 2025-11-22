# Perbaikan Tampilan Artikel & Ekstraksi Gambar

## Masalah yang Diperbaiki

### ❌ Masalah Sebelumnya:

1. **Judul duplikat** - Judul artikel muncul 2x di awal konten
2. **Teks "Baca juga:"** - Link promosi internal masih terikut
3. **Caption Instagram** - "Sebuah kiriman dibagikan oleh..."
4. **Copyright footer** - "Copyright 2008 - 2025 PT. Kompas..."
5. **Editor/Tim Redaksi** - Metadata editor di awal artikel
6. **Gambar tidak muncul** - Tidak ada ekstraksi & tampilan gambar

### ✅ Solusi yang Diterapkan:

1. **Cleaning konten otomatis** - Hapus semua noise
2. **Ekstraksi gambar artikel** - Dari meta og:image & img tags
3. **Tampilan gambar di frontend** - Gambar utama ditampilkan
4. **Whitespace normalisasi** - Max 2 newlines, single space

---

## File yang Dimodifikasi

### 1. Backend - Scraping (`scraping.ipynb`)

**Fungsi baru:**

- `clean_content(content, title)` - Bersihkan konten dari noise
- `extract_images(soup)` - Ekstrak URL gambar dari artikel
- Kolom `image_url` ditambahkan ke hasil scraping

### 2. Backend - Search Engine (`search_engine.py`)

**Perubahan:**

- Load `image_url` dari `corpus_clean.csv`
- `get_document()` mengembalikan field `image_url`

### 3. Frontend - Detail Page (`frontend/src/app/detail/[id]/page.tsx`)

**Perubahan:**

- Tampilkan gambar jika `doc.image_url` tersedia
- Error handling jika gambar gagal load

### 4. Backend - Preprocessing (`preprocessing.ipynb`)

**Perubahan:**

- Kolom `image_url` disimpan ke `corpus_clean.csv`

---

## Script Utility Baru

### 1. `clean_existing_data.py`

Membersihkan data `scraped.csv` yang sudah ada tanpa scraping ulang.

**Fungsi cleaning:**

- Hapus judul duplikat (hingga 2x di 5 baris pertama)
- Hapus "Editor", "Tim Redaksi", "Penulis", "Reporter"
- Hapus "Baca juga:" dengan regex multiline
- Hapus caption Instagram
- Hapus copyright footer (berbagai format)
- Hapus caption gambar (KOMPAS.COM/NAMA, DETIK.COM/NAMA)
- Normalisasi whitespace

**Cara pakai:**

```bash
cd backend
python clean_existing_data.py
```

**Output:** `data/scraped_cleaned.csv`

### 2. `quick_corpus_clean.py`

Generate `corpus_clean.csv` dari `scraped.csv` dengan cepat.

**Cara pakai:**

```bash
cd backend
python quick_corpus_clean.py
```

### 3. `scrape_articles.py`

Script standalone untuk scraping dengan cleaning & gambar.

**Cara pakai:**

```bash
cd backend
python scrape_articles.py
```

### 4. `test_scraping.py`

Test scraping 100 URL pertama.

**Cara pakai:**

```bash
cd backend
python test_scraping.py
```

---

## Workflow yang Sudah Dijalankan

```
1. scraped.csv (4,852 artikel lama)
   ↓
2. clean_existing_data.py
   → Cleaning: judul duplikat, "Baca juga:", copyright, dll
   ↓
3. scraped_cleaned.csv (4,852 artikel bersih)
   ↓
4. Copy ke scraped.csv
   ↓
5. quick_corpus_clean.py
   → Format untuk search engine
   ↓
6. corpus_clean.csv (4,852 dengan image_url)
   ↓
7. Backend restart → Load data baru
   ↓
8. Frontend → Tampilkan konten bersih
```

---

## Hasil Akhir

### Sebelum:

```
Desa Megulungkidul di Purworejo Didorong Kembangkan Paket Wisata Edukasi
Desa Megulungkidul di Purworejo Didorong Kembangkan Paket Wisata Edukasi
Tim Redaksi
PURWOREJO, KOMPAS.com- Desa Megulungkidul...
Baca juga:5 Desa Wisata Penyangga Borobudur...
Sebuah kiriman dibagikan oleh Kompas Travel (@kompas.travel)
...
Copyright 2008 - 2025 PT. Kompas Cyber Media...
```

### Sesudah:

```
PURWOREJO, KOMPAS.com- Desa Megulungkidul di Kecamatan Pituruh,
Kabupaten Purworejo, Jawa Tengah, punya potensi wisata edukasi.

Potensi tersebut diharapkan dapat terus dikembangkan sehingga menjadi
daya tarik wisata baru di wilayah Purworejo bagian barat...
```

---

## Testing

### Test Endpoint Backend:

```bash
# Test API running
curl http://localhost:5000/

# Test document detail
curl http://localhost:5000/document/1 | python -m json.tool

# Test search
curl "http://localhost:5000/search?query=pantai+bali&algo=bm25"
```

### Verifikasi Frontend:

1. Buka http://localhost:3000
2. Cari artikel (contoh: "wisata Bali")
3. Klik salah satu hasil
4. Verifikasi:
   - ✅ Tidak ada judul duplikat
   - ✅ Tidak ada "Baca juga:"
   - ✅ Tidak ada copyright footer
   - ✅ Gambar muncul (jika tersedia)
   - ✅ Konten rapi dan bersih

---

## Catatan

### Image URL

- Data lama (4,852 artikel) tidak punya gambar karena tidak di-scrape
- Kolom `image_url` kosong (`""`) untuk data lama
- Jika mau re-scrape semua dengan gambar, jalankan:
  ```bash
  cd backend
  python scrape_articles.py  # Scrape 10,000 URL dengan gambar
  ```
  ⚠️ **Warning:** Proses ini memakan waktu ~30-60 menit

### Performance

- Cleaning 4,852 artikel: ~5 detik
- Generate corpus_clean: ~2 detik
- Backend restart: ~3 detik
- **Total: < 15 detik** untuk update data

### Next Steps (Opsional)

1. **Re-scrape dengan gambar:**
   - Backup data lama
   - Jalankan `scrape_articles.py`
   - Update preprocessing
2. **Tambah field metadata:**
   - Tanggal publikasi
   - Kategori artikel
   - Tags/keywords
3. **Improve cleaning:**
   - ML-based content extraction
   - Better caption detection
   - Author extraction

---

## Troubleshooting

### Backend tidak load data baru

```bash
# Restart backend
ps aux | grep "python.*api.py" | awk '{print $2}' | xargs kill
cd backend && python api.py
```

### Konten masih ada noise

```bash
# Re-run cleaning dengan update terbaru
cd backend
python clean_existing_data.py
cp data/scraped_cleaned.csv data/scraped.csv
python quick_corpus_clean.py
# Restart backend
```

### Frontend tidak tampilkan gambar

- Cek apakah `image_url` ada di response API
- Cek console browser untuk error CORS/loading
- Pastikan URL gambar valid (bukan data:// atau broken link)

---

**Status:** ✅ Selesai - Konten bersih & siap produksi!
