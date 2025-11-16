# config.py

SEEDS = [
    # ===== detikTravel =====
    "https://travel.detik.com/",
    "https://travel.detik.com/domestic-destination",
    "https://travel.detik.com/international-destination",
    "https://travel.detik.com/travel-news",
    "https://travel.detik.com/travel-tips",
    "https://travel.detik.com/travel-deals",
    "https://travel.detik.com/travel-food",

    # Bisa juga pakai halaman tag/keyword populer
    "https://travel.detik.com/tag/wisata",
    "https://travel.detik.com/tag/destinasi",
    "https://travel.detik.com/tag/liburan",
    "https://travel.detik.com/tag/hotel",
    "https://travel.detik.com/tag/pantai",

    # ===== Kompas Travel =====
    "https://travel.kompas.com/",
    "https://travel.kompas.com/read",
    "https://travel.kompas.com/search?q=wisata",
    "https://travel.kompas.com/search?q=liburan",
    "https://travel.kompas.com/search?q=hotel",
    "https://travel.kompas.com/search?q=kuliner",
]

# Batasan crawler (boleh disamain aja dengan yang lama)
MAX_URLS = 10_000
MAX_CONCURRENT_TASKS = 50
PER_DOMAIN_DELAY = 1.0
REQUEST_TIMEOUT = 20
MAX_RETRIES = 2

# Kata kunci biar yang ke-keep bener-bener konten pariwisata
KEYWORD_FILTER = [
    # Umum pariwisata
    "wisata", "pariwisata", "liburan", "jalan-jalan", "travelling",
    "tour", "tourism", "travel", "trip", "backpacker",
    "destinasi", "destinasi wisata", "tempat wisata",
    "obyek wisata", "objek wisata", "spot wisata",

    # Jenis destinasi
    "pantai", "laut", "pulau", "snorkeling", "diving",
    "gunung", "pendakian", "hiking", "camping", "campground",
    "hutan", "taman nasional", "cagar alam",
    "desa wisata", "kampung wisata",
    "air terjun", "curug", "danau", "telaga",

    # Akomodasi & fasilitas
    "hotel", "resort", "villa", "guest house", "homestay",
    "penginapan", "hostel", "akomodasi", "airbnb",
    "booking", "reservasi", "check-in", "check in",

    # Transportasi & akses
    "tiket pesawat", "bandara", "airport",
    "kereta api", "stasiun", "bus wisata", "kapal", "pelabuhan",
    "akses menuju lokasi", "rute perjalanan", "itinerary",

    # Aktivitas & pengalaman
    "city tour", "walking tour", "tur", "paket wisata",
    "itinerary", "one day trip", "open trip", "paket liburan",
    "kuliner", "kulineran", "makanan khas", "jajanan lokal",
    "festival", "event", "acara budaya", "karnaval", "upacara adat",

    # Konteks Indonesia (biar makin relevan)
    "nusantara", "indonesia", "lokal", "domestik",
    "wisatawan lokal", "wisatawan mancanegara",
    "objek wisata indonesia", "destinasi indonesia",

    # Info praktis
    "harga tiket", "jam operasional", "jam buka",
    "tips liburan", "tips wisata", "panduan wisata",
    "rekomendasi wisata", "tempat hits", "tempat instagramable",
]

ALLOWED_DOMAINS = [
    # Fokus ke dua portal utama
    "travel.detik.com",
    "detik.com",          # jaga-jaga kalau ada subpath travel di detik.com biasa
    "travel.kompas.com",
    "kompas.com",         # kadang artikel travel nyelip di kompas.com umum
]
