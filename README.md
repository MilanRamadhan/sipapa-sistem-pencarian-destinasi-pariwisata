# SIPAPA - Sistem Pencarian Destinasi Pariwisata

Proyek Akhir Mata Kuliah **Penelusuran Informasi**  
Sistem pencarian informasi untuk destinasi pariwisata Indonesia dari portal berita DetikTravel dan KompasTravel.

---

## 📋 Deskripsi Proyek

Proyek ini mengimplementasikan sistem Information Retrieval (IR) lengkap untuk mencari informasi destinasi wisata di Indonesia. Sistem ini melakukan:

1. **Web Crawling & Scraping** - Mengumpulkan data artikel pariwisata
2. **Preprocessing** - Membersihkan dan normalisasi teks
3. **Indexing** - Membangun inverted index
4. **Retrieval** - Implementasi 2 algoritma pencarian (TF-IDF & BM25)
5. **Evaluation** - Evaluasi performa dengan metrik IR standar

---

## 🗂️ Struktur Project

```
Project Akhir PI/
├── config.py                 # Konfigurasi: seeds, domains, keywords
├── crawling.py              # Script crawling URL
├── scraping.ipynb           # Notebook scraping konten artikel
├── preprocessing.ipynb      # Notebook preprocessing & cleaning
├── indexing.ipynb           # Notebook pembuatan inverted index
├── search.ipynb             # Implementasi TF-IDF & BM25
├── evaluation.ipynb         # Evaluasi & perbandingan algoritma
├── stopwords_id.txt         # Daftar stopwords Bahasa Indonesia
│
└── data/
    ├── urls.txt             # Hasil crawling (daftar URL)
    ├── scraped.csv          # Hasil scraping (konten artikel)
    ├── corpus_clean.csv     # Korpus bersih setelah preprocessing
    ├── corpus_clean.jsonl   # Korpus dalam format JSONL
    ├── doc_meta.csv         # Metadata dokumen
    ├── inverted_index.json  # Inverted index
    ├── ground_truth.json    # Relevance judgments untuk evaluasi
    └── evaluation_*.csv     # Hasil evaluasi algoritma
```

---

## 🚀 Tahapan Implementasi

### 1️⃣ **Crawling & Scraping**

**File**: `crawling.py`, `scraping.ipynb`

- **Crawling**: Mengunjungi website secara otomatis untuk mengumpulkan URL

  - Source: DetikTravel, KompasTravel
  - Async/concurrent crawling dengan `aiohttp`
  - Output: `data/urls.txt` (~10,000+ URLs)

- **Scraping**: Mengekstrak konten dari setiap URL
  - Ekstraksi: title, content, metadata
  - Output: `data/scraped.csv` (~4,852 artikel)

```bash
# Jalankan crawling
python crawling.py

# Jalankan scraping (buka notebook)
jupyter notebook scraping.ipynb
```

---

### 2️⃣ **Preprocessing**

**File**: `preprocessing.ipynb`

Tahapan preprocessing yang dilakukan:

1. **Cleaning**

   - Hapus duplikat berdasarkan URL
   - Buang dokumen kosong
   - Filter dokumen dengan minimal 40 kata

2. **Text Normalization**

   - Lowercase
   - Hapus URL dan karakter khusus
   - Tokenisasi

3. **Stopword Removal**

   - Hapus kata-kata umum (dan, atau, di, ke, dll)
   - Menggunakan `stopwords_id.txt`

4. **Stemming**

   - Konversi kata ke bentuk dasar
   - Menggunakan **Sastrawi** (stemmer Bahasa Indonesia)

5. **Filtering**
   - Filter berdasarkan keyword pariwisata
   - Hanya simpan dokumen relevan

**Output**:

- `data/corpus_clean.csv` (4,700 dokumen bersih)
- `data/corpus_clean.jsonl`

---

### 3️⃣ **Indexing**

**File**: `indexing.ipynb`

Membangun struktur data untuk pencarian efisien:

1. **Inverted Index**

   - Struktur: `term → {doc_id: term_frequency}`
   - Vocabulary size: ~37,662 terms unik
   - Format: JSON untuk portability

2. **Document Metadata**

   - doc_id, url, title, doc_length
   - Digunakan untuk ranking dan display

3. **Statistics**
   - Document Frequency (DF)
   - Inverse Document Frequency (IDF)
   - Average document length (avgdl)

**Output**:

- `data/inverted_index.json`
- `data/doc_meta.csv`

---

### 4️⃣ **Pencarian Informasi**

**File**: `search.ipynb`

Implementasi 2 algoritma pencarian:

#### **A. TF-IDF (Term Frequency - Inverse Document Frequency)**

Formula:

```
score(q, d) = Σ tf(t, d) × idf(t)
```

- **Kelebihan**: Sederhana, cepat, mudah diimplementasikan
- **Kekurangan**: Tidak mempertimbangkan panjang dokumen

#### **B. BM25 (Best Matching 25)**

Formula:

```
score(q, d) = Σ idf(t) × [tf(t,d) × (k₁ + 1)] / [tf(t,d) + k₁ × (1 - b + b × |d|/avgdl)]
```

Parameter:

- `k₁ = 1.5` (term frequency saturation)
- `b = 0.75` (length normalization)

- **Kelebihan**: Lebih robust, normalisasi panjang dokumen
- **Kekurangan**: Lebih kompleks, perlu tuning parameter

**Fitur**:

- Query preprocessing (lowercase, tokenize, stopwords, stem)
- Ranking berdasarkan relevansi
- Support untuk interactive search

---

### 5️⃣ **Evaluasi**

**File**: `evaluation.ipynb`

#### **Test Queries** (10 queries)

1. wisata pantai Bali
2. hotel murah Jakarta
3. gunung Bromo sunrise
4. kuliner Yogyakarta
5. tempat wisata Bandung
6. diving Bunaken
7. candi Borobudur
8. taman nasional komodo
9. danau Toba
10. rafting Sungai Ayung

#### **Metrik Evaluasi**

1. **Precision**

   ```
   Precision = |Retrieved ∩ Relevant| / |Retrieved|
   ```

   Proporsi hasil yang dikembalikan yang relevan

2. **Recall**

   ```
   Recall = |Retrieved ∩ Relevant| / |Relevant|
   ```

   Proporsi dokumen relevan yang berhasil ditemukan

3. **F1 Score**

   ```
   F1 = 2 × (Precision × Recall) / (Precision + Recall)
   ```

   Harmonic mean dari Precision dan Recall

4. **Mean Average Precision (MAP)**
   ```
   MAP = (1/|Q|) × Σ AP(q)
   ```
   Rata-rata precision untuk multiple queries

#### **Relevance Judgments**

Dokumen dianggap relevan jika mengandung minimal 1 keyword dari query.  
Ground truth disimpan di `data/ground_truth.json`

#### **Visualisasi**

- Bar chart: Perbandingan metrik rata-rata
- Per-query comparison: Performance untuk setiap query
- Export: PNG images untuk laporan

---

## 📊 Hasil Evaluasi

_(Akan diisi setelah running evaluation.ipynb)_

### Perbandingan TF-IDF vs BM25

| Metrik        | TF-IDF | BM25 | Winner |
| ------------- | ------ | ---- | ------ |
| Avg Precision | -      | -    | -      |
| Avg Recall    | -      | -    | -      |
| Avg F1 Score  | -      | -    | -      |
| MAP           | -      | -    | -      |

### Kesimpulan

_(Kesimpulan akan diisi setelah evaluasi)_

---

## 🛠️ Installation & Setup

### Requirements

```bash
# Python 3.8+
pip install pandas numpy
pip install beautifulsoup4 aiohttp
pip install Sastrawi
pip install matplotlib seaborn
pip install jupyter
```

### Setup Stopwords

Stopwords sudah disediakan di `stopwords_id.txt` (daftar kata umum Bahasa Indonesia)

### Run Project

1. **Crawling** (opsional, data sudah ada)

   ```bash
   python crawling.py
   ```

2. **Preprocessing**

   ```bash
   jupyter notebook preprocessing.ipynb
   # Run all cells
   ```

3. **Indexing**

   ```bash
   jupyter notebook indexing.ipynb
   # Run all cells
   ```

4. **Search**

   ```bash
   jupyter notebook search.ipynb
   # Run all cells
   ```

5. **Evaluation**
   ```bash
   jupyter notebook evaluation.ipynb
   # Run all cells
   ```

---

## 📚 Dependencies

- **pandas**: Data manipulation
- **numpy**: Numerical operations
- **beautifulsoup4**: HTML parsing
- **aiohttp**: Async HTTP requests
- **Sastrawi**: Indonesian stemming
- **matplotlib, seaborn**: Visualization
- **jupyter**: Interactive notebooks

---

## 🎯 Fitur Utama

✅ **Korpus Besar**: ~4,700 dokumen artikel pariwisata  
✅ **Preprocessing Lengkap**: Cleaning, tokenization, stopwords, stemming  
✅ **2 Algoritma IR**: TF-IDF & BM25  
✅ **Inverted Index**: Struktur data efisien untuk pencarian  
✅ **Evaluasi Komprehensif**: 4 metrik evaluasi standar  
✅ **Visualisasi**: Charts dan graphs untuk analisis  
✅ **Reproducible**: Semua code dalam Jupyter notebooks

---

## 📖 Referensi

1. Manning, C. D., Raghavan, P., & Schütze, H. (2008). _Introduction to Information Retrieval_. Cambridge University Press.
2. Robertson, S., & Zaragoza, H. (2009). _The Probabilistic Relevance Framework: BM25 and Beyond_. Foundations and Trends in Information Retrieval.
3. Sastrawi - Indonesian Stemmer: https://github.com/sastrawi/sastrawi

---

## 👥 Author

**Milan Ramadhan**  
Mata Kuliah: Penelusuran Informasi  
Semester 5

---

## 📝 License

Educational project for Information Retrieval course.

---

## 🔗 Links

- Repository: [sipapa-sistem-pencarian-destinasi-pariwisata](https://github.com/MilanRamadhan/sipapa-sistem-pencarian-destinasi-pariwisata)
- Source Data: DetikTravel, KompasTravel

---

## 📌 Notes

- Dataset dikumpulkan dari portal berita publik untuk tujuan edukasi
- Preprocessing dan indexing memakan waktu ~1 jam (tergantung hardware)
- Evaluasi menggunakan semi-automatic relevance judgments
- Untuk production use, disarankan manual annotation dan lebih banyak test queries
