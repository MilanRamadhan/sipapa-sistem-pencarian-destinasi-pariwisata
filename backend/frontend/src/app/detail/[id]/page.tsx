import { getDocument } from "@/lib/api";
import SafeImage from "@/components/SafeImage";
import BackButton from "@/components/BackButton";

type DetailParams = {
  id: string;
};

type DetailPageProps = {
  params: Promise<DetailParams>;
};

// 🔎 Heuristik simpel buat nebak heading (subjudul)
function isLikelyHeading(line: string): boolean {
  const text = line.trim();
  if (!text) return false;

  // Jangan treat kalimat yang diakhiri titik / tanda tanya / seru sebagai heading
  if (/[.?!]$/.test(text)) return false;

  // Skip kalau ada URL / @
  if (/@|http/.test(text)) return false;

  const words = text.split(/\s+/);
  if (words.length < 2 || words.length > 10) return false;

  // Hitung kata yang huruf pertamanya kapital
  const capitalizedCount = words.filter((w) => /^[A-ZÀ-Ý]/.test(w)).length;

  // Harus ada minimal 2 kata kapital dan proporsinya lumayan
  if (capitalizedCount < 2) return false;
  if (capitalizedCount / words.length < 0.4) return false;

  return true;
}

export default async function DetailPage(props: DetailPageProps) {
  // ⬅️ WAJIB: await dulu props.params
  const { id } = await props.params;

  const doc = await getDocument(id);

  if (!doc) {
    return (
      <main className="min-h-screen bg-neutral-50 text-neutral-900">
        <div className="max-w-4xl mx-auto px-4 py-8">
          <BackButton />

          <div className="mt-6">
            <h1 className="heading-serif text-2xl font-bold mb-2">Artikel tidak ditemukan</h1>
            <p className="text-sm text-neutral-600">
              Maaf, detail artikel untuk ID <code>{id}</code> tidak tersedia.
            </p>
          </div>
        </div>
      </main>
    );
  }

  return (
    <main className="min-h-screen bg-neutral-50 text-neutral-900">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <BackButton />

        <header className="mt-4 mb-6 border-b border-neutral-300 pb-4">
          <p className="text-[10px] uppercase tracking-[0.2em] text-neutral-500 mb-2">Travel · Artikel</p>
          <h1 className="heading-serif text-3xl md:text-4xl font-bold leading-tight mb-3">{doc.title}</h1>
          <div className="text-[11px] text-neutral-500 space-x-2">
            {doc.url && (
              <span>
                Sumber asli:{" "}
                <a href={doc.url} target="_blank" rel="noreferrer" className="underline">
                  {doc.url.replace(/^https?:\/\//, "")}
                </a>
              </span>
            )}
            {doc.doc_len && <span>· Perkiraan panjang: {doc.doc_len} kata</span>}
          </div>
        </header>

        {doc.image_url && (
          <figure className="mb-6">
            <SafeImage src={doc.image_url} alt={doc.title} className="w-full h-auto rounded-sm" />
          </figure>
        )}

        <article className="text-sm leading-relaxed text-neutral-800">
          {doc.content ? (
            doc.content
              .split(/\n+/) // pisah per paragraf
              .map((rawLine: string, idx: number) => {
                const line = rawLine.trim();
                if (!line) return null;

                if (isLikelyHeading(line)) {
                  // 🧱 Subjudul (H2)
                  return (
                    <h2 key={idx} className="heading-serif text-xl md:text-2xl font-semibold mt-6 mb-3">
                      {line}
                    </h2>
                  );
                }

                // 📄 Paragraf biasa
                return (
                  <p key={idx} className="mb-3">
                    {line}
                  </p>
                );
              })
          ) : (
            <p>Konten artikel tidak tersedia.</p>
          )}
        </article>
      </div>
    </main>
  );
}
