import { searchArticles } from "@/lib/api";
import SearchBar from "@/components/SearchBar";
import SafeImage from "@/components/SafeImage";

export default async function HomePage() {
  // Ambil artikel "unggulan" untuk ditampilkan di landing
  const articles = await searchArticles("wisata", "tfidf", 7);
  const [hero, secondary, ...others] = articles;

  // Potong snippet secondary sampai kata "kepada" + ...
  if (secondary) {
    const kepadaIndex = secondary.snippet.indexOf("kepada");
    if (kepadaIndex !== -1) {
      secondary.snippet = secondary.snippet.substring(0, kepadaIndex + 6) + "...";
    }
  }

  return (
    <main className="min-h-screen px-4 py-6">
      {/* HEADER */}
      <header className="max-w-6xl mx-auto border-b border-neutral-300 pb-4 mb-6">
        <div className="flex items-center justify-between mb-3 gap-4">
          <button className="text-xs tracking-[0.2em] uppercase text-neutral-500">SIPAPA DAILY</button>

          <h1 className="heading-serif text-4xl md:text-5xl font-black text-center flex-1" style={{ fontFamily: "var(--font-playfair)" }}>
            Sipapa Travel Times
          </h1>

          <div className="text-xs text-neutral-500 text-right hidden md:block">
            {new Date().toLocaleDateString("id-ID", {
              weekday: "long",
              year: "numeric",
              month: "long",
              day: "numeric",
            })}
          </div>
        </div>

        <div className="flex flex-wrap items-center justify-between gap-3 mt-2">
          <nav className="flex flex-wrap gap-4 text-xs uppercase tracking-wide text-neutral-600">
            <span className="cursor-pointer hover:text-black">Destinasi</span>
            <span className="cursor-pointer hover:text-black">Pantai</span>
            <span className="cursor-pointer hover:text-black">Gunung</span>
            <span className="cursor-pointer hover:text-black">Kuliner</span>
            <span className="cursor-pointer hover:text-black">Budaya & Festival</span>
            <span className="cursor-pointer hover:text-black">Semua</span>
          </nav>

          <SearchBar />
        </div>
      </header>

      {/* MAIN CONTENT */}
      <section className="max-w-6xl mx-auto">
        <div className="grid md:grid-cols-3 gap-6">
          {/* HERO ARTICLE KIRI - Lebih compact */}
          {hero && (
            <article className="md:col-span-2 border-b md:border-b-0 md:border-r border-neutral-300 pr-0 md:pr-6 pb-6 md:pb-0">
              <p className="text-[10px] uppercase tracking-[0.2em] text-neutral-500 mb-3">DESTINASI UNGGULAN</p>
              <a href={`/detail/${hero.doc_id}`} className="cursor-pointer block hover:opacity-80 transition-opacity">
                <h1 className="heading-serif text-2xl md:text-3xl font-bold mb-3 leading-tight">{hero.title}</h1>
              </a>
              <p className="text-sm text-neutral-700 leading-relaxed mb-3 line-clamp-4">{hero.snippet}</p>
              <a href={`/detail/${hero.doc_id}`} className="text-xs font-semibold tracking-[0.15em] uppercase text-blue-700 hover:underline">
                BACA SELENGKAPNYA →
              </a>
              {hero.image_url && (
                <div className="mt-4 overflow-hidden rounded-sm">
                  <SafeImage src={hero.image_url} alt={hero.title} className="w-full h-auto object-cover" />
                </div>
              )}
            </article>
          )}

          {/* ARTICLE BESAR KANAN - Background hitam dengan gambar */}
          {secondary && (
            <article className="bg-black text-white p-4 rounded-md flex flex-col min-h-[350px] md:min-h-[420px]">
              <p className="text-[9px] uppercase tracking-[0.25em] text-neutral-400 mb-1">SPOT REKOMENDASI</p>
              <a href={`/detail/${secondary.doc_id}`} className="cursor-pointer block hover:opacity-90 transition-opacity">
                <h2 className="heading-serif text-lg md:text-xl font-bold mb-2 leading-tight">{secondary.title}</h2>
              </a>
              <p className="text-sm text-neutral-300 leading-[1.5] flex-1">{secondary.snippet}</p>
              <a href={`/detail/${secondary.doc_id}`} className="text-[10px] font-semibold tracking-wide uppercase text-white hover:text-gray-300 transition-colors mt-2">
                JELAJAHI DESTINASI →
              </a>
            </article>
          )}
        </div>

        {/* STRIP ARTIKEL KECIL DI BAWAH - Grid 5 kolom dengan gambar */}
        <section className="mt-6 border-t border-neutral-300 pt-5">
          <div className="grid gap-4 md:grid-cols-5">
            {others.map((art) => (
              <article key={art.doc_id} className="group pb-3">
                {art.image_url && (
                  <div className="mb-3 overflow-hidden rounded-sm">
                    <SafeImage src={art.image_url} alt={art.title} className="w-full h-28 object-cover hover:scale-105 transition-transform duration-300" />
                  </div>
                )}
                <p className="text-[10px] uppercase tracking-[0.2em] text-neutral-500 mb-2">TRAVEL</p>
                <a href={`/detail/${art.doc_id}`} className="cursor-pointer block">
                  <h3 className="heading-serif text-sm font-bold leading-snug mb-2 line-clamp-3 group-hover:text-blue-700 transition-colors">{art.title}</h3>
                </a>
                <p className="text-xs text-neutral-600 line-clamp-2 mb-2">{art.snippet}</p>
                <a href={`/detail/${art.doc_id}`} className="text-[11px] uppercase tracking-[0.16em] text-blue-700 hover:underline font-semibold">
                  BACA →
                </a>
              </article>
            ))}
          </div>
        </section>
      </section>
    </main>
  );
}
