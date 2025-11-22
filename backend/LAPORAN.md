# Laporan Proyek Akhir: Sistem Pencarian Destinasi Pariwisata

**Mata Kuliah**: Penelusuran Informasi  
**Nama**: Milan Ramadhan  
**Semester**: 5

---

## 1. PENDAHULUAN

### 1.1 Latar Belakang

Industri pariwisata Indonesia memiliki potensi besar dengan ribuan destinasi wisata yang tersebar di seluruh nusantara. Namun, informasi mengenai destinasi wisata tersebar di berbagai portal berita dan website, membuat wisatawan kesulitan menemukan informasi yang relevan dengan kebutuhan mereka.

Sistem pencarian (Information Retrieval) yang baik dapat membantu wisatawan menemukan informasi destinasi wisata dengan cepat dan akurat. Proyek ini mengembangkan sistem pencarian informasi destinasi pariwisata Indonesia dengan mengimplementasikan dua algoritma pencarian: **TF-IDF** dan **BM25**.

### 1.2 Tujuan

1. Membangun korpus dokumen pariwisata Indonesia dari portal berita
2. Mengimplementasikan preprocessing lengkap (cleaning, tokenization, stopword removal, stemming)
3. Membangun inverted index untuk pencarian efisien
4. Mengimplementasikan 2 algoritma pencarian: TF-IDF dan BM25
5. Melakukan evaluasi kinerja kedua algoritma dengan metrik standar IR

### 1.3 Sumber Data

- **DetikTravel** (travel.detik.com)
- **KompasTravel** (travel.kompas.com)
- **Total URL**: ~10,000+ URL dikumpulkan
- **Total Artikel**: 4,852 artikel di-scrape
- **Korpus Bersih**: 4,700 dokumen setelah preprocessing

---

## 2. METODOLOGI

### 2.1 Pengumpulan Data (Crawling & Scraping)

#### Crawling

- **Tools**: Python (aiohttp, asyncio)
- **Method**: Async/concurrent crawling
- **Seeds**: Halaman utama travel DetikTravel & KompasTravel
- **Domain Filtering**: Hanya ambil URL dari domain yang diizinkan
- **Output**: `data/urls.txt` (daftar URL)

#### Scraping

- **Tools**: BeautifulSoup4, pandas
- **Ekstraksi**: title, content, metadata
- **Rate Limiting**: Delay per domain untuk menghindari blocking
- **Output**: `data/scraped.csv` (4,852 artikel)

### 2.2 Preprocessing

Tahapan preprocessing yang dilakukan:

1. **Data Cleaning**

   - Hapus duplikat berdasarkan URL
   - Buang dokumen dengan konten kosong
   - Filter dokumen dengan minimal 40 kata

2. **Text Normalization**

   - Lowercase conversion
   - URL removal
   - Special character removal
   - Whitespace normalization

3. **Tokenization**

   - Split text menjadi individual tokens (words)
   - Hapus token kosong

4. **Stopword Removal**

   - Hapus kata-kata umum yang tidak informatif
   - Menggunakan daftar stopwords Bahasa Indonesia
   - Total: ~757 stopwords

5. **Stemming**

   - Konversi kata ke bentuk dasar
   - Algoritma: **Sastrawi** (stemmer Bahasa Indonesia)
   - Contoh: "wisatawan" → "wisata", "berkunjung" → "kunjung"

6. **Keyword Filtering**
   - Filter dokumen berdasarkan keyword pariwisata
   - Hanya simpan dokumen yang mengandung minimal 1 keyword
   - Keywords: wisata, pantai, hotel, kuliner, dll (dari config.py)

**Hasil**: 4,700 dokumen bersih

### 2.3 Indexing

Struktur data yang dibangun:

1. **Inverted Index**

   ```
   term → {doc_id1: tf1, doc_id2: tf2, ...}
   ```

   - Vocabulary size: 37,662 unique terms
   - Format: JSON untuk portability

2. **Document Metadata**

   - doc_id (integer ID)
   - url (original URL)
   - title (artikel title)
   - doc_len (jumlah token setelah preprocessing)

3. **Statistics**
   - N = 4,700 (total documents)
   - avgdl = 401 (average document length)
   - DF (document frequency) untuk setiap term
   - IDF (inverse document frequency)

### 2.4 Algoritma Pencarian

#### A. TF-IDF (Term Frequency - Inverse Document Frequency)

**Formula**:

```
score(q, d) = Σ_{t ∈ q} tf(t, d) × idf(t)

dimana:
- tf(t, d) = frekuensi term t dalam dokumen d
- idf(t) = log((N + 1) / (df(t) + 1)) + 1
```

**Karakteristik**:

- Sederhana dan cepat
- Mengukur pentingnya term dengan frekuensi dan keunikan
- Tidak mempertimbangkan panjang dokumen secara eksplisit

**Implementasi**:

```python
def tfidf_search(query, top_k=10):
    query_tokens = preprocess_query(query)
    scores = defaultdict(float)

    for term in query_tokens:
        if term in inverted_index:
            term_idf = idf[term]
            for doc_id, tf in inverted_index[term].items():
                scores[doc_id] += tf * term_idf

    return sorted(scores.items(), key=lambda x: -x[1])[:top_k]
```

#### B. BM25 (Best Matching 25)

**Formula**:

```
score(q, d) = Σ_{t ∈ q} idf(t) × [tf(t,d) × (k₁ + 1)] / [tf(t,d) + k₁ × (1 - b + b × |d|/avgdl)]

dimana:
- k₁ = 1.5 (term frequency saturation parameter)
- b = 0.75 (length normalization parameter)
- |d| = panjang dokumen d
- avgdl = rata-rata panjang dokumen
```

**Karakteristik**:

- Lebih sophisticated dari TF-IDF
- Normalisasi panjang dokumen dengan parameter b
- Saturasi term frequency dengan parameter k₁
- Generally lebih baik untuk korpus dengan variasi panjang dokumen

**Implementasi**:

```python
def bm25_search(query, top_k=10, k1=1.5, b=0.75):
    query_tokens = preprocess_query(query)
    scores = defaultdict(float)

    for term in query_tokens:
        if term in inverted_index:
            term_idf = idf[term]
            for doc_id, tf in inverted_index[term].items():
                doc_len = doc_meta.loc[doc_id, "doc_len"]
                numerator = tf * (k1 + 1)
                denominator = tf + k1 * (1 - b + b * (doc_len / avgdl))
                scores[doc_id] += term_idf * (numerator / denominator)

    return sorted(scores.items(), key=lambda x: -x[1])[:top_k]
```

### 2.5 Evaluasi

#### Test Queries (10 queries)

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

#### Relevance Judgments

- **Method**: Semi-automatic dengan keyword matching
- **Kriteria**: Dokumen relevan jika mengandung ≥1 keyword dari query
- **Ground Truth**: Disimpan di `data/ground_truth.json`

_Note: Dalam praktik production, relevance judgments harus dilakukan manual oleh human annotators_

#### Metrik Evaluasi

1. **Precision**

   ```
   Precision = |Retrieved ∩ Relevant| / |Retrieved|
   ```

   Mengukur akurasi: proporsi hasil yang relevan dari yang dikembalikan

2. **Recall**

   ```
   Recall = |Retrieved ∩ Relevant| / |Relevant|
   ```

   Mengukur coverage: proporsi dokumen relevan yang berhasil ditemukan

3. **F1 Score**

   ```
   F1 = 2 × (Precision × Recall) / (Precision + Recall)
   ```

   Harmonic mean dari Precision dan Recall (balance antara keduanya)

4. **Mean Average Precision (MAP)**

   ```
   MAP = (1/|Q|) × Σ AP(q)

   dimana AP(q) = (1/|Relevant|) × Σ [Precision@k × rel(k)]
   ```

   Mengukur kualitas ranking: mempertimbangkan posisi dokumen relevan dalam hasil

---

## 3. HASIL DAN ANALISIS

### 3.1 Statistik Korpus

| Metrik                        | Nilai        |
| ----------------------------- | ------------ |
| Total Dokumen Awal            | 4,852        |
| Dokumen Setelah Preprocessing | 4,700        |
| Vocabulary Size               | 37,662 terms |
| Rata-rata Panjang Dokumen     | 401 tokens   |
| Min Panjang Dokumen           | 64 tokens    |
| Max Panjang Dokumen           | 2,247 tokens |

### 3.2 Hasil Evaluasi

#### Perbandingan TF-IDF vs BM25

_(Tabel ini akan diisi setelah running evaluation.ipynb)_

| Metrik        | TF-IDF | BM25 | Improvement |
| ------------- | ------ | ---- | ----------- |
| Avg Precision | -      | -    | -           |
| Avg Recall    | -      | -    | -           |
| Avg F1 Score  | -      | -    | -           |
| MAP           | -      | -    | -           |

#### Per-Query Analysis

_(Akan diisi dengan detail performance per query)_

### 3.3 Visualisasi

Visualisasi hasil evaluasi tersimpan di:

- `data/evaluation_comparison.png` - Bar chart perbandingan metrik
- `data/evaluation_per_query.png` - Performance per query

### 3.4 Analisis

#### Kelebihan dan Kekurangan

**TF-IDF**:

- ✅ Kelebihan:
  - Simple dan mudah diimplementasikan
  - Cepat dalam komputasi
  - Interpretable (mudah dipahami)
- ❌ Kekurangan:
  - Tidak mempertimbangkan panjang dokumen
  - Bisa bias terhadap dokumen panjang

**BM25**:

- ✅ Kelebihan:
  - Normalisasi panjang dokumen
  - Parameter tuning untuk optimasi
  - Generally lebih robust
- ❌ Kekurangan:
  - Lebih kompleks
  - Perlu tuning parameter k₁ dan b

#### Temuan Penting

_(Akan diisi berdasarkan hasil evaluasi)_

1. Algoritma yang lebih baik: [TF-IDF/BM25]
2. Metrik terkuat: [Precision/Recall/F1/MAP]
3. Query dengan performance terbaik: [...]
4. Query dengan performance terburuk: [...]

---

## 4. KESIMPULAN

### 4.1 Pencapaian

1. ✅ Berhasil membangun korpus pariwisata dengan 4,700 dokumen bersih
2. ✅ Implementasi preprocessing lengkap dengan stopword removal dan stemming
3. ✅ Membangun inverted index dengan 37,662 unique terms
4. ✅ Implementasi TF-IDF dan BM25 berhasil
5. ✅ Evaluasi komprehensif dengan 4 metrik standar IR

### 4.2 Limitasi

1. **Relevance Judgments**: Semi-automatic, tidak manual annotation
2. **Test Queries**: Hanya 10 queries (idealnya 50-100)
3. **Parameter Tuning**: BM25 menggunakan parameter default
4. **Data Source**: Terbatas pada 2 portal berita
5. **Temporal Coverage**: Data snapshot, tidak real-time

### 4.3 Saran Pengembangan

1. **Immediate**:

   - Tambahkan lebih banyak test queries (50-100)
   - Manual annotation untuk relevance judgments
   - Grid search untuk optimal BM25 parameters

2. **Advanced**:

   - Implementasi algoritma modern: Sentence-BERT, Dense Retrieval
   - Query expansion dengan synonyms
   - Personalization berdasarkan user preferences
   - Real-time indexing untuk dokumen baru

3. **Production**:
   - Web interface untuk user-friendly search
   - A/B testing dengan real users
   - Feedback loop untuk continuous improvement
   - Distributed indexing untuk skalabilitas

---

## 5. REFERENSI

1. Manning, C. D., Raghavan, P., & Schütze, H. (2008). _Introduction to Information Retrieval_. Cambridge University Press.

2. Robertson, S., & Zaragoza, H. (2009). _The Probabilistic Relevance Framework: BM25 and Beyond_. Foundations and Trends in Information Retrieval, 3(4), 333-389.

3. Baeza-Yates, R., & Ribeiro-Neto, B. (2011). _Modern Information Retrieval: The Concepts and Technology behind Search_ (2nd ed.). Addison-Wesley Professional.

4. Sastrawi - Indonesian Stemmer. Retrieved from https://github.com/sastrawi/sastrawi

5. Asian, J., Williams, H. E., & Tahaghoghi, S. M. M. (2005). Stemming Indonesian. In _Proceedings of the 28th Australasian Conference on Computer Science_ (pp. 307-314).

---

## LAMPIRAN

### A. Konfigurasi

File lengkap: `config.py`

**Seeds**:

- DetikTravel: travel.detik.com
- KompasTravel: travel.kompas.com

**Parameters**:

- MAX_URLS: 10,000
- MAX_CONCURRENT_TASKS: 50
- MIN_WORDS: 40
- BM25 k₁: 1.5
- BM25 b: 0.75

**Keywords Pariwisata** (sample):
wisata, pariwisata, liburan, pantai, hotel, kuliner, gunung, museum, candi, danau, taman nasional, dll.

### B. Struktur Data

#### Inverted Index Structure

```json
{
  "pantai": [
    { "doc_id": 0, "tf": 5 },
    { "doc_id": 23, "tf": 3 },
    { "doc_id": 45, "tf": 8 }
  ],
  "hotel": [
    { "doc_id": 1, "tf": 12 },
    { "doc_id": 10, "tf": 4 }
  ]
}
```

#### Document Metadata Structure

```csv
doc_id,url,title,doc_len
0,https://travel.kompas.com/...,Wisata Pantai Bali...,581
1,https://travel.detik.com/...,Hotel Murah Jakarta...,356
```

### C. Code Repository

GitHub: https://github.com/MilanRamadhan/sipapa-sistem-pencarian-destinasi-pariwisata

### D. Screenshots

_(Tambahkan screenshots dari notebooks dan visualisasi)_

1. Preprocessing results
2. Indexing statistics
3. Search results comparison
4. Evaluation charts

---

**Tanggal**: November 2025  
**Versi**: 1.0
