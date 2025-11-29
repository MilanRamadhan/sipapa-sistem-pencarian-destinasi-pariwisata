import { getDocument } from "@/lib/api";
import SafeImage from "@/components/SafeImage";
import BackButton from "@/components/BackButton";

type DetailParams = {
  id: string;
};

type DetailPageProps = {
  params: Promise<DetailParams>;
};

// -------------------------
// DETECT SUBHEADINGS (H2)
// -------------------------
function isLikelyHeading(line: string): boolean {
  const text = line.trim();
  if (!text) return false;

  // Jangan dianggap heading kalau diakhiri tanda titik/tanya/seru
  if (/[.?!]$/.test(text)) return false;

  // Skip kalau ada URL atau @
  if (/http|@/i.test(text)) return false;

  const words = text.split(/\s+/);
  if (words.length < 2 || words.length > 12) return false;

  // Hitung kata yang huruf pertamanya kapital (A-Z)
  const capitalized = words.filter((w) => /^[A-Z]/.test(w)).length;

  if (capitalized < 2) return false;
  if (capitalized / words.length < 0.35) return false;

  return true;
}

// -----------------------------
// DETECT LEAD PARAGRAPH BOLD
// (e.g. "JAKARTA, KOMPAS.com - ...")
// -----------------------------
function isLeadParagraph(line: string): boolean {
  const text = line.trim();
  if (!text) return false;

  // pattern kota + KOMPAS.com di awal
  return /^([A-Z]+,\s*)?KOMPAS\.com\b/.test(text);
}

// -----------------------------
// DETECT PHOTO CREDITS (skip)
// -----------------------------
function isPhotoCredit(line: string): boolean {
  const lower = line.trim().toLowerCase();

  // contoh: "KOMPAS.com/M LUKMAN PABRIYANTO ...."
  if (lower.startsWith("kompas.com/")) return true;
  if (lower.startsWith("kompas.com /")) return true;

  // sering ada kata "dok." atau "dokumentasi" + kompas.com
  if (lower.includes("kompas.com") && lower.includes("dok")) return true;

  // kalau baris pendek tapi ada "kompas.com" dan "foto"
  if (lower.includes("kompas.com") && lower.includes("foto")) return true;

  return false;
}

export default async function DetailPage(props: DetailPageProps) {
  // ⬅️ tetap pakai pola yang sudah jalan di project kamu
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
            doc.content.split(/\n+/).map((rawLine: string, idx: number) => {
              const line = rawLine.trim();
              if (!line) return null;

              // 1) skip credit foto
              if (isPhotoCredit(line)) {
                return null;
              }

              // 2) subjudul -> H2
              if (isLikelyHeading(line)) {
                return (
                  <h2 key={idx} className="heading-serif text-xl md:text-2xl font-semibold mt-6 mb-3">
                    {line}
                  </h2>
                );
              }

              // 3) lead paragraph (JAKARTA, KOMPAS.com ...) -> hanya prefix yang bold
              if (isLeadParagraph(line)) {
                // Extract prefix (JAKARTA, KOMPAS.com -) dan sisanya
                const match = line.match(/^([A-Z]+,\s*KOMPAS\.com\s*[-–—]?\s*)/);
                if (match) {
                  const prefix = match[1];
                  const rest = line.substring(prefix.length);
                  return (
                    <p key={idx} className="mb-3">
                      <span className="font-bold">{prefix}</span>
                      {rest}
                    </p>
                  );
                }
                // Fallback jika pattern tidak match persis
                return (
                  <p key={idx} className="mb-3">
                    {line}
                  </p>
                );
              }

              // 4) paragraf biasa
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
