// أرشيف تثبّت: commonly circulated citations as the tool checked them (data/archive.json via /api/archive).
// Everything shown is copied from the archive record: Mushaf text, the scholars' gradings verbatim, links.
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
let lang = "ar";
try { const s = localStorage.getItem("tathabbut-lang"); if (["ar", "en", "ur", "id"].includes(s)) lang = s; } catch (e) { /* ignore */ }
const num = (n) => (lang === "ar" ? String(n).replace(/\d/g, (d) => "٠١٢٣٤٥٦٧٨٩"[d]) : String(n));

const T = {
  ar: {
    title: "أرشيف تثبّت", tagline: "أحاديث وآيات متداولة، ومعها ما قاله علماء الحديث المعتمدون بنصه ومصدره",
    navCheck: "الفحص", navArchive: "الأرشيف", navBot: "إجابة روبوت", navDev: "للمطورين",
    searchLabel: "ابحث في الأرشيف", searchPh: "اكتب كلمة من الحديث أو الآية",
    footer: "فريق قيد الأوابد · تحدي الذكاء الاصطناعي في خدمة المحتوى الإسلامي",
    credit: "المصادر من الحزمة العلمية للتحدي: مصحف مجمع الملك فهد، والموسوعة الحديثية في الدرر السنية.",
    filters: { all: "الكل", supported: "تؤيده المصادر", not_supported: "لا تؤيده المصادر المعتمدة", verify: "يحتاج مزيدًا من التحقق", quran: "آيات" },
    stats: { total: "استشهادًا", supported: "تؤيده المصادر", not_supported: "لا تؤيده المصادر", quran: "آية" },
    tier: { documented: "مطابق للمصحف", supported: "تؤيده المصادر", not_supported: "لا تؤيده المصادر المعتمدة", verify: "يحتاج مزيدًا من التحقق", refer: "يُحال إلى مختص" },
    tierLbl: "حالة الدليل", hadith: "حديث", quran: "آية",
    verdict: { accepted: "صحيح أو حسن عند", weak: "ضعيف عند", fabricated: "موضوع أو لا أصل له عند" },
    sahihayn: "في الصحيحين:", longer: "حكمٌ على رواية أطول أو لفظ مقارب، لا يُبنى عليه", gradings: (n) => `أحكام العلماء بنصها (${num(n)})`, died: (y) => `ت ${num(y)}هـ`,
    wrote: (a, b) => `كُتب «${a}»، وفي المصحف «${b}»`, wrongRef: (r) => `العزو المكتوب لا يطابق موضع الآية؛ موضعها ${r}`,
    notFound: "لم نجد له أصلًا في المصادر المعتمدة، ويُحال إلى مختص.",
    check: "افحصه بنفسك الآن", source: "المصدر", count: (n, m) => `${num(n)} من ${num(m)}`,
    note: (d) => `فُحصت هذه الاستشهادات آليًا في ${d}، والأحكام منقولة بنصها من الموسوعة الحديثية مع روابطها. لم تراجعها المختصة الشرعية في الفريق بعد، والأداة لا ترجّح بين الأحكام.`,
    empty: "لا نتائج. جرّب كلمة أخرى، أو افحص النص بنفسك من صفحة الفحص.",
  },
  en: {
    title: "Tathabbut archive", tagline: "Commonly circulated hadith and verses, with what the approved hadith scholars said, verbatim and sourced",
    navCheck: "Check", navArchive: "Archive", navBot: "Chatbot answer", navDev: "Developers",
    searchLabel: "Search the archive", searchPh: "Type a word from the hadith or verse",
    footer: "Team Qayd al-Awabid · AI Challenge: Serving Islamic Content",
    credit: "Sources from the challenge's scientific package: the King Fahd Complex Mushaf and Dorar's hadith encyclopedia.",
    filters: { all: "All", supported: "Supported", not_supported: "Not supported", verify: "Needs verification", quran: "Verses" },
    stats: { total: "citations", supported: "supported", not_supported: "not supported", quran: "verses" },
    tier: { documented: "Matches the Mushaf", supported: "Supported by the sources", not_supported: "Not supported by the approved sources", verify: "Needs more verification", refer: "Refer to a specialist" },
    tierLbl: "Evidence status", hadith: "Hadith", quran: "Verse",
    verdict: { accepted: "Authentic or good according to", weak: "Weak according to", fabricated: "Fabricated or baseless according to" },
    sahihayn: "In the two Sahihs:", longer: "graded on a longer or near wording; not counted", gradings: (n) => `The scholars' gradings, verbatim (${n})`, died: (y) => `d. ${y} AH`,
    wrote: (a, b) => `Written «${a}»; the Mushaf has «${b}»`, wrongRef: (r) => `The written reference is wrong; the verse is at ${r}`,
    notFound: "No source was found in the approved references; refer to a specialist.",
    check: "Check it yourself now", source: "Source", count: (n, m) => `${n} of ${m}`,
    note: (d) => `Checked automatically on ${d}. Gradings are quoted verbatim from Dorar with their links. Not yet reviewed by the team's Sharia reviewer; the tool never weighs one grading against another.`,
    empty: "No results. Try another word, or check the text yourself on the Check page.",
  },
};
T.ur = { ...T.en,
  title: "تثبّت آرکائیو", tagline: "رائج احادیث و آیات، معتمد علمائے حدیث کے اقوال کے ساتھ، اصل متن اور ماخذ سمیت",
  navCheck: "جانچ", navArchive: "آرکائیو", navBot: "چیٹ بوٹ کا جواب", navDev: "ڈویلپرز",
  searchLabel: "آرکائیو میں تلاش کریں", searchPh: "حدیث یا آیت کا کوئی لفظ لکھیں",
  filters: { all: "سب", supported: "مآخذ سے تائید", not_supported: "تائید نہیں", verify: "مزید تحقیق درکار", quran: "آیات" },
  stats: { total: "حوالے", supported: "تائید", not_supported: "تائید نہیں", quran: "آیات" },
  tier: { documented: "مصحف کے مطابق", supported: "مآخذ سے تائید", not_supported: "معتمد مآخذ سے تائید نہیں", verify: "مزید تحقیق درکار", refer: "ماہر کے حوالے" },
  tierLbl: "دلیل کی حیثیت", hadith: "حدیث", quran: "آیت",
  verdict: { accepted: "صحیح یا حسن، بقول", weak: "ضعیف، بقول", fabricated: "موضوع یا بے اصل، بقول" },
  sahihayn: "صحیحین میں:", gradings: (n) => `علماء کے احکام اصل متن میں (${n})`, died: (y) => `وفات ${y}ھ`,
  longer: "طویل یا ملتی جلتی روایت پر حکم؛ اس پر بنیاد نہیں",
  check: "خود ابھی جانچیں", source: "ماخذ", count: (n, m) => `${m} میں سے ${n}`,
  note: (d) => `یہ حوالے ${d} کو خودکار طور پر جانچے گئے؛ احکام الدرر سے اصل متن میں روابط سمیت منقول ہیں۔ ٹیم کی شرعی ماہر نے ابھی ان کا جائزہ نہیں لیا، اور آلہ کسی حکم کو ترجیح نہیں دیتا۔`,
  empty: "کوئی نتیجہ نہیں۔ کوئی اور لفظ آزمائیں، یا جانچ کے صفحے پر خود متن جانچیں۔",
};
T.id = { ...T.en,
  title: "Arsip Tathabbut", tagline: "Hadis dan ayat yang beredar, beserta penilaian ulama hadis yang diakui, teks asli dan sumbernya",
  navCheck: "Periksa", navArchive: "Arsip", navBot: "Jawaban chatbot", navDev: "Pengembang",
  searchLabel: "Cari di arsip", searchPh: "Ketik kata dari hadis atau ayat",
  filters: { all: "Semua", supported: "Didukung", not_supported: "Tidak didukung", verify: "Perlu verifikasi", quran: "Ayat" },
  stats: { total: "kutipan", supported: "didukung", not_supported: "tidak didukung", quran: "ayat" },
  tier: { documented: "Sesuai Mushaf", supported: "Didukung sumber", not_supported: "Tidak didukung sumber yang diakui", verify: "Perlu verifikasi lanjut", refer: "Dirujuk ke ahli" },
  tierLbl: "Status dalil", hadith: "Hadis", quran: "Ayat",
  verdict: { accepted: "Shahih atau hasan menurut", weak: "Dha'if menurut", fabricated: "Maudhu' atau tidak berdasar menurut" },
  sahihayn: "Dalam Shahihain:", gradings: (n) => `Penilaian ulama, teks asli (${n})`, died: (y) => `w. ${y} H`,
  longer: "dinilai pada riwayat lebih panjang atau lafaz mirip; tidak dihitung",
  check: "Periksa sendiri sekarang", source: "Sumber", count: (n, m) => `${n} dari ${m}`,
  note: (d) => `Diperiksa otomatis pada ${d}. Penilaian dikutip apa adanya dari Dorar beserta tautannya. Belum ditinjau oleh peninjau syariah tim; alat ini tidak mengunggulkan satu penilaian atas yang lain.`,
  empty: "Tidak ada hasil. Coba kata lain, atau periksa teks sendiri di halaman Periksa.",
};
const LANGS = ["ar", "en", "ur", "id"];
const arData = () => lang === "ar" || lang === "ur";
const t = () => T[lang];
let data = { entries: [] }, filter = "all";
const CLS = { documented: "ok", supported: "ok", not_supported: "warn", verify: "warn", refer: "warn" };

function matches(e) {
  if (filter === "quran" && e.type !== "quran") return false;
  if (filter === "verify" && !["verify", "refer"].includes(e.tier)) return false;
  if (["supported", "not_supported"].includes(filter) && e.tier !== filter) return false;
  const q = $("q").value.trim().replace(/[ًٌٍَُِّْٰـ]/g, "");
  if (!q) return true;
  const hay = (e.quote + " " + e.text + " " + ((e.quran || {}).mushaf_text || "")).replace(/[ًٌٍَُِّْٰـ]/g, "");
  return hay.includes(q) || hay.toLowerCase().includes(q.toLowerCase());
}

function card(e, i) {
  const fab = e.hadith && (e.hadith.verdicts || []).some((v) => v.verdict === "fabricated");
  const cls = e.tier === "not_supported" && fab ? "bad" : CLS[e.tier] || "warn";
  let h = `<li class="entry"><div class="entry-no">${num(i + 1)}</div><div>
    <p class="entry-kind">${esc(e.type === "quran" ? t().quran : t().hadith)}
      <span class="tier ${cls}">${esc(t().tierLbl)}: ${esc(t().tier[e.tier] || "")}</span></p>
    <p class="arch-quote"><bdi dir="${e.lang === "en" ? "ltr" : "rtl"}">«${esc(e.quote)}»</bdi></p>`;
  if (e.quran) {
    const q = e.quran;
    h += `<div class="mushaf arch-mushaf"><p class="mushaf-head">${esc(arData() ? `سورة ${q.surah_name_ar}، ${q.ref}` : `${q.surah_name_en} ${q.ref}`)}</p>
      <p class="ayat" lang="ar" dir="rtl">${esc(q.mushaf_text)}</p></div>`;
    for (const d of (q.diff || []).slice(0, 3)) if (d.quoted || d.mushaf) h += `<p class="line warn">${esc(t().wrote(d.quoted || "—", d.mushaf || "—"))}</p>`;
    if (q.reference_ok === false) h += `<p class="line warn">${esc(t().wrongRef(q.ref))}</p>`;
  }
  if (e.hadith) {
    const hd = e.hadith, vcls = { accepted: "ok", weak: "warn", fabricated: "bad" };
    if ((hd.verdicts || []).length) {
      h += `<div class="verdicts">` + hd.verdicts.map((v) =>
        `<p class="line ${vcls[v.verdict]}"><b>${esc(t().verdict[v.verdict])}</b> ${esc((arData() ? v.scholars_ar : v.scholars_en).join(arData() ? "، " : ", "))}</p>`).join("") + `</div>`;
    }
    if ((hd.sahihayn || []).length) {
      h += `<p class="line ok">${esc(t().sahihayn)} ` + hd.sahihayn.map((x) =>
        `<a href="${esc(x.url)}" target="_blank" rel="noopener">${esc(arData() ? `${x.book} (${num(x.number)})` : `${x.book_en || x.book} (no. ${x.number})`)}</a>`).join(arData() ? "، " : ", ") + `</p>`;
    }
    if ((hd.gradings || []).length) {
      h += `<details class="arch-grades"><summary>${esc(t().gradings(hd.gradings.length))}</summary><ul>` + hd.gradings.map((g) =>
        `<li><p class="ag-head"><b>${esc(arData() ? g.scholar_ar : g.scholar_en)}</b> <span class="fine">${esc(t().died(g.died_ah))}</span>`
        + (g.match && g.match !== "same" ? ` <span class="ag-tag">${esc(t().longer)}</span>` : "") + `</p>
          <p class="ag-grade">«<bdi dir="rtl">${esc(g.grade)}</bdi>» · <a href="${esc(g.url)}" target="_blank" rel="noopener"><bdi dir="rtl">${esc(g.book)}${g.number ? " " + esc(g.number) : ""}</bdi></a></p>
          <p class="fine ag-text" dir="rtl">${esc((g.text || "").slice(0, 160))}${(g.text || "").length > 160 ? "…" : ""}</p></li>`).join("") + `</ul></details>`;
    } else if (e.tier === "refer") h += `<p class="refer">${esc(t().notFound)}</p>`;
  }
  const src = (e.quran && e.quran.url) || (e.hadith && e.hadith.search_url);
  h += `<p class="copy-row"><a class="primary arch-check" href="/?q=${encodeURIComponent(e.text)}">${esc(t().check)}</a>`
    + (src ? ` <a href="${esc(src)}" target="_blank" rel="noopener">${esc(t().source)}</a>` : "") + `</p>`;
  return h + `</div></li>`;
}

function render() {
  const shown = data.entries.filter(matches);
  $("list").innerHTML = shown.map(card).join("") || `<li class="fine">${esc(t().empty)}</li>`;
  $("count").textContent = t().count(shown.length, data.entries.length);
  $("filters").innerHTML = Object.entries(t().filters).map(([k, v]) =>
    `<button type="button" class="chip" data-f="${k}" aria-pressed="${k === filter}">${esc(v)}</button>`).join("");
  const es = data.entries;
  const st = { total: es.length, supported: es.filter((e) => e.tier === "supported").length,
    not_supported: es.filter((e) => e.tier === "not_supported").length, quran: es.filter((e) => e.type === "quran").length };
  $("stats").innerHTML = Object.entries(st).map(([k, v]) => `<div><dt>${esc(num(v))}</dt><dd>${esc(t().stats[k])}</dd></div>`).join("");
  const day = data.checked_at ? new Date(data.checked_at).toLocaleDateString({ ar: "ar-SA-u-ca-islamic-umalqura", ur: "ur-PK-u-ca-islamic-umalqura", id: "id-ID", en: "en-GB" }[lang], { year: "numeric", month: "long", day: "numeric" }) : "—";
  $("note").textContent = t().note(day);
}

function applyLang() {
  document.documentElement.lang = lang;
  document.documentElement.dir = arData() ? "rtl" : "ltr";
  document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = t()[el.dataset.i18n]; });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => { el.placeholder = t()[el.dataset.i18nPh]; });
  $("lang").value = lang;
  document.title = { ar: "أرشيف تثبّت · استشهادات متداولة ومصادرها", ur: "تثبّت آرکائیو", id: "Arsip Tathabbut" }[lang] || "Tathabbut archive · circulated citations and their sources";
  render();
}

$("filters").addEventListener("click", (e) => {
  const b = e.target.closest("button[data-f]");
  if (!b) return;
  filter = b.dataset.f;
  render();
});
$("q").addEventListener("input", render);
$("lang").addEventListener("change", () => {
  lang = LANGS.includes($("lang").value) ? $("lang").value : "ar";
  try { localStorage.setItem("tathabbut-lang", lang); } catch (e) { /* ignore */ }
  applyLang();
});
fetch("/api/archive").then((r) => r.json()).then((d) => {
  data = d;
  // Fabricated and not-supported first, then what needs checking, then supported: what a visitor most needs to see.
  const order = { not_supported: 0, verify: 1, refer: 2, documented: 3, supported: 4 };
  data.entries.sort((a, b) => (order[a.tier] ?? 5) - (order[b.tier] ?? 5));
  applyLang();
}).catch(() => { $("count").textContent = "—"; });
applyLang();
