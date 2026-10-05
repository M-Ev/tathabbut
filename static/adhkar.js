// الأذكار الموثّقة: adhkar, du'as and verses, each hadith dhikr checked with Tathabbut itself (data/adhkar.json,
// scripts/build_adhkar.py); verses from the Mushaf file (/api/adhkar, /api/mushaf, /api/asma). The reader's
// progress, favourites, worship log and tasbih counts stay in their own browser (localStorage); nothing is sent.
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const LANGS = ["ar", "en", "ur", "id", "bn", "tr", "fr", "es", "hi", "zh", "ja"];
let lang = "ar";
try { const s = localStorage.getItem("tathabbut-lang"); if (LANGS.includes(s)) lang = s; } catch (e) { /* ignore */ }
const RTL = ["ar", "ur"];
const num = (n) => (lang === "ar" ? String(n).replace(/\d/g, (d) => "٠١٢٣٤٥٦٧٨٩"[d]) : String(n));
const store = {
  get(k, d) { try { const v = localStorage.getItem("tth-" + k); return v ? JSON.parse(v) : d; } catch (e) { return d; } },
  set(k, v) { try { localStorage.setItem("tth-" + k, JSON.stringify(v)); } catch (e) { /* the page works without it */ } },
};

const T = {
  ar: {
    title: "الأذكار الموثّقة", tagline: "كل ذكر هنا فحصه تثبّت: مصدره، وحكم العلماء المعتمدين عليه بنصه",
    home: "الرئيسية", mushaf: "المصحف", beta: "تجريبي", tracker: "متابعة العبادات", trackerSub: "تتبع صلواتك وأذكارك ونوافلك",
    asma: "أسماء الله الحسنى", fav: "أذكاري", favSub: "ما حفظته بالنجمة", tasbih: "تسابيح", ayah: "آية وتفسير", more: "المزيد",
    count: (n) => `${num(n)} مرات`, tapCount: "اضغط للعدّ", done: "تم",
    source: "المصدر", grading: "الحكم", narration: "نص الرواية في الموسوعة الحديثية", others: "أحكام أخرى وجدها تثبّت على لفظه",
    dorar: "ابحث في الدرر بنفسك", evidence: "الدليل على قراءتها هنا",
    excluded: (n) => `لم تُعرض هنا (${num(n)})`,
    excludedWhy: "أذكار متداولة في هذا الباب لم نجد لها في نتائج الموسوعة الحديثية حكمًا مقبولًا من العلماء المعتمدين على رواية فيها لفظها كاملًا وتذكر هذا الوقت أو الحال. وهذا ليس حكمًا عليها: قد تثبت عند غيرهم أو بلفظ آخر، فابحث بنفسك أو اسأل أهل العلم.",
    empty: "لا شيء هنا بعد.", favEmpty: "اضغط ☆ بجانب أي ذكر ليظهر هنا.",
    resume: (s, a) => `أكمل من ${s}، الآية ${num(a)}`, progress: (p) => `قرأت ${num(p)}٪ من المصحف`, markHere: "وصلت هنا",
    mushafNote: "نص مصحف مجمع الملك فهد. اضغط على آية لتحفظ موضع قراءتك على جهازك، وتُحسب منه نسبة ما قرأت.",
    tasks: { fajr: "الفجر", dhuhr: "الظهر", asr: "العصر", maghrib: "المغرب", isha: "العشاء", rawatib: "السنن الرواتب", witr: "الوتر", duha: "الضحى", morning: "أذكار الصباح", evening: "أذكار المساء", quran: "ورد القرآن" },
    groups: { fard: "الصلوات الخمس", nafl: "النوافل", dhikr: "الأذكار والقرآن" },
    today: "اليوم", week: "آخر سبعة أيام", savedLocal: "تُحفظ على جهازك فقط، ولا تُرسل إلى أي خادم.",
    reset: "تصفير", target: "الهدف", ayahOfDay: "آية اليوم", prev: "السابقة", next: "التالية",
    tafsir: "اقرأ تفسيرها في قرآنبيديا (التفاسير المعتمدة في الحزمة العلمية)", meaning: "معنى الآية",
    asmaVerse: "ورد في", note: (d, ok, all) => `فُحصت الأذكار آليًا بتثبّت في ${d}: عُرض منها ${num(ok)} من ${num(all)}. الأحكام منقولة بنصها من الموسوعة الحديثية مع روابطها، ولم تراجعها المختصة الشرعية في الفريق بعد.`,
    footer: "فريق قيد الأوابد · تحدي الذكاء الاصطناعي في خدمة المحتوى الإسلامي",
  },
  en: {
    title: "Verified adhkar", tagline: "Every dhikr here was checked by Tathabbut: its source, and the approved scholars' grading verbatim",
    home: "Home", mushaf: "The Mushaf", beta: "beta", tracker: "Worship tracker", trackerSub: "Track your prayers, adhkar and voluntary prayers",
    asma: "The Names of Allah", fav: "My adhkar", favSub: "Starred items", tasbih: "Tasbih", ayah: "A verse and its tafsir", more: "More",
    count: (n) => `${n} times`, tapCount: "Tap to count", done: "Done",
    source: "Source", grading: "Grading", narration: "The narration in Dorar's encyclopedia", others: "Other gradings Tathabbut found on its wording",
    dorar: "Search Dorar yourself", evidence: "Evidence for reciting it here",
    excluded: (n) => `Not shown here (${n})`,
    excludedWhy: "Commonly circulated adhkar of this kind for which Dorar's results had no accepted grading by the approved scholars on a narration with the whole wording that names this time or situation. This is not a grading: they may be established elsewhere or in another wording; search yourself or ask a scholar.",
    empty: "Nothing here yet.", favEmpty: "Tap ☆ beside any dhikr to keep it here.",
    resume: (s, a) => `Continue from ${s}, verse ${a}`, progress: (p) => `You have read ${p}% of the Mushaf`, markHere: "I stopped here",
    mushafNote: "The King Fahd Complex Mushaf text. Tap a verse to keep your place on this device; your progress is counted from it.",
    tasks: { fajr: "Fajr", dhuhr: "Dhuhr", asr: "Asr", maghrib: "Maghrib", isha: "Isha", rawatib: "Sunnah prayers", witr: "Witr", duha: "Duha", morning: "Morning adhkar", evening: "Evening adhkar", quran: "Quran reading" },
    groups: { fard: "The five prayers", nafl: "Voluntary prayers", dhikr: "Adhkar and Quran" },
    today: "Today", week: "Last seven days", savedLocal: "Kept on this device only; never sent to a server.",
    reset: "Reset", target: "Target", ayahOfDay: "Verse of the day", prev: "Previous", next: "Next",
    tafsir: "Read its tafsir on Quranpedia (tafsirs in the challenge's package)", meaning: "Meaning",
    asmaVerse: "In", note: (d, ok, all) => `Checked automatically with Tathabbut on ${d}: ${ok} of ${all} shown. Gradings are quoted verbatim from Dorar with their links; not yet reviewed by the team's Sharia reviewer.`,
    footer: "Team Qayd al-Awabid · AI Challenge: Serving Islamic Content",
  },
};
const NAV_ADHKAR = { ar: "الأذكار الموثّقة", en: "Verified adhkar", ur: "مستند اذکار", id: "Zikir terverifikasi", bn: "যাচাইকৃত যিকির", tr: "Doğrulanmış zikirler", fr: "Invocations vérifiées", es: "Adhkar verificados", hi: "प्रमाणित अज़कार", zh: "经核实的记念词", ja: "検証済みのズィクル" };
if (typeof DK_I18N !== "undefined") for (const [k, v] of Object.entries(DK_I18N)) T[k] = { ...T.en, ...v, tagline: T.en.tagline };
const t = () => T[lang] || T.en;
const navWord = (k) => {
  if (k === "navAdhkar") return NAV_ADHKAR[lang];
  const own = { navCheck: ["الفحص", "Check"], navArchive: ["الأرشيف", "Archive"], navBot: ["اسأل الثقات", "Ask the trusted"], navPillars: ["أركان الإسلام", "Pillars of Islam"], navDev: ["للمطورين", "Developers"] }[k];
  const pack = lang === "ar" ? null : (typeof T_EXTRA !== "undefined" && T_EXTRA[lang]) || (typeof T_MORE !== "undefined" && T_MORE[lang]);
  return (pack && pack[k]) || (own ? own[lang === "ar" ? 0 : 1] : "");
};

let DATA = null, CATS = {};
const catName = (k) => (lang === "ar" ? (CATS[k] || {}).ar : (t().cats && t().cats[k]) || (CATS[k] || {}).en) || k;

// ---------- cards ----------
function srcLine(s) {
  return `<a href="${esc(s.url)}" target="_blank" rel="noopener" lang="ar">${esc(s.book)} (${esc(num(s.number))})</a> · <span lang="ar">${esc(s.scholar_ar)}: ${esc(s.grade)}</span>`;
}
function counter(id, n) {
  if (!n) return "";
  return `<button type="button" class="dk-count" data-id="${esc(id)}" data-n="${n}" aria-label="${esc(t().tapCount)}"><b>${num(n)}</b><span>${esc(t().count(n))}</span></button>`;
}
function star(id) {
  const on = store.get("fav", []).includes(id);
  return `<button type="button" class="dk-star" data-id="${esc(id)}" aria-pressed="${on}" aria-label="${esc(t().fav)}">${on ? "★" : "☆"}</button>`;
}
function hadithCard(x, place) {
  const s = place.source;
  const others = (x.check.narrations || []).filter((n) => n.url !== s.url).slice(0, 5)
    .map((n) => `<li lang="ar">${esc(n.scholar_ar)}: ${esc(n.grade)} · <a href="${esc(n.url)}" target="_blank" rel="noopener">${esc(n.book)} (${esc(n.number)})</a></li>`).join("");
  return `<article class="dk" id="d-${esc(x.id)}">
    <div class="dk-top">${star(x.id)}${counter(x.id + ":" + place.category, place.count)}</div>
    <p class="dk-text" lang="ar" dir="rtl">${esc(x.text)}</p>
    <p class="dk-src"><span class="lbl">${esc(t().source)}</span>${srcLine(s)}</p>
    <details class="dk-more"><summary>${esc(t().narration)}</summary>
      <p class="dk-narr" lang="ar" dir="rtl">«${esc(s.text)}»</p>
      ${others ? `<p class="lbl">${esc(t().others)}</p><ul class="dk-others">${others}</ul>` : ""}
      <p class="fine"><a href="${esc(x.check.search_url)}" target="_blank" rel="noopener">${esc(t().dorar)}</a></p>
    </details></article>`;
}
function verseText(v) {
  return v.ayat.map((a) => `${esc(a.text)} <span class="ayah-no">﴿${num(a.ayah)}﴾</span>`).join(" ");
}
function quranCard(x, place) {
  const ref = `[${esc(lang === "ar" ? x.surah_ar : x.surah_en)}: ${num(x.ayah_from)}${x.ayah_to !== x.ayah_from ? "–" + num(x.ayah_to) : ""}]`;
  const ev = place.evidence;
  return `<article class="dk dk-q" id="q-${esc(x.id)}">
    <div class="dk-top">${star("q:" + x.id)}${counter("q:" + x.id + ":" + place.category, place.count)}</div>
    <p class="dk-verse quran" lang="ar" dir="rtl">${verseText(x)}</p>
    <p class="fine">${ref}</p>
    ${x.meaning ? `<p class="pl-meaning" dir="auto"><span class="lbl">${esc(t().meaning)}</span>${esc(x.meaning.text)} <span class="fine">(${esc(x.meaning.name)})</span></p>` : ""}
    ${ev ? `<details class="dk-more"><summary>${esc(t().evidence)}</summary><p class="dk-narr" lang="ar" dir="rtl">«${esc(ev.source.text)}»</p>
      <p class="dk-src">${srcLine(ev.source)}</p></details>` : ""}
  </article>`;
}
function bindCards(root) {
  root.querySelectorAll(".dk-count").forEach((b) => {
    b.onclick = () => {
      let n = Number(b.dataset.left ?? b.dataset.n);
      n = n > 0 ? n - 1 : Number(b.dataset.n);
      b.dataset.left = n;
      b.querySelector("b").textContent = n ? num(n) : "✓";
      b.closest(".dk").classList.toggle("is-done", n === 0);
      if (navigator.vibrate) try { navigator.vibrate(8); } catch (e) { /* ignore */ }
    };
  });
  root.querySelectorAll(".dk-star").forEach((b) => {
    b.onclick = () => {
      const f = store.get("fav", []); const id = b.dataset.id; const i = f.indexOf(id);
      if (i >= 0) f.splice(i, 1); else f.push(id);
      store.set("fav", f); b.textContent = i >= 0 ? "☆" : "★"; b.setAttribute("aria-pressed", String(i < 0));
    };
  });
}

// ---------- views ----------
function tile(href, title, sub, extra) {
  return `<a class="dk-tile" href="${href}"><b>${esc(title)}</b>${sub ? `<span>${esc(sub)}</span>` : ""}${extra || ""}</a>`;
}
function viewHome() {
  const m = store.get("mushaf", { max: 0 });
  const pct = DATA_MUSHAF_TOTAL ? Math.floor((m.max || 0) * 100 / DATA_MUSHAF_TOTAL) : 0;
  const cats = (DATA ? DATA.categories : []).map((c) => tile(`#c/${c.key}`, catName(c.key), "")).join("");
  return `<div class="dk-tiles dk-tiles-main">
      ${tile("#mushaf", t().mushaf, t().beta, `<span class="dk-bar"><i style="width:${pct}%"></i></span><span class="dk-pct">${num(pct)}${lang === "ar" ? "٪" : "%"}</span>`)}
      ${tile("#tracker", t().tracker, t().trackerSub)}
      ${tile("#asma", t().asma, "")}
      ${tile("#fav", t().fav, t().favSub)}
    </div>
    <div class="dk-tiles">${cats}${tile("#tasbih", t().tasbih, "")}${tile("#ayah", t().ayah, "")}</div>`;
}
function viewCategory(key) {
  if (!DATA) return `<p>${esc(t().empty)}</p>`;
  const cards = [];
  for (const x of DATA.quran) for (const p of x.shown || []) if (p.category === key) cards.push(quranCard(x, p));
  for (const x of DATA.hadith) if (!x.id.startsWith("ev_")) for (const p of x.shown || []) if (p.category === key) cards.push(hadithCard(x, p));
  const out = DATA.hadith.filter((x) => !x.id.startsWith("ev_") && x.categories.includes(key) && !(x.shown || []).some((p) => p.category === key));
  const ex = out.length ? `<details class="dk-excluded"><summary>${esc(t().excluded(out.length))}</summary><p class="fine">${esc(t().excludedWhy)}</p>
      <ul>${out.map((x) => `<li><span lang="ar" dir="rtl">${esc(x.text)}</span> · <a href="${esc((x.check || {}).search_url || "#")}" target="_blank" rel="noopener">${esc(t().dorar)}</a></li>`).join("")}</ul></details>` : "";
  return `<h2 class="pl-h">${esc(catName(key))}</h2>${cards.join("") || `<p>${esc(t().empty)}</p>`}${ex}`;
}
function viewFav() {
  const f = store.get("fav", []);
  if (!f.length || !DATA) return `<h2 class="pl-h">${esc(t().fav)}</h2><p>${esc(t().favEmpty)}</p>`;
  const cards = [];
  for (const id of f) {
    if (id.startsWith("q:")) { const x = DATA.quran.find((y) => y.id === id.slice(2)); if (x && x.shown && x.shown[0]) cards.push(quranCard(x, x.shown[0])); }
    else { const x = DATA.hadith.find((y) => y.id === id); if (x && x.shown && x.shown[0]) cards.push(hadithCard(x, x.shown[0])); }
  }
  return `<h2 class="pl-h">${esc(t().fav)}</h2>${cards.join("")}`;
}

let DATA_MUSHAF_TOTAL = 6236, SURAHS = null;
async function viewMushaf(n) {
  if (!SURAHS) { const r = await fetch("/api/mushaf"); const d = await r.json(); SURAHS = d.surahs; DATA_MUSHAF_TOTAL = d.total; }
  const m = store.get("mushaf", { s: 1, a: 1, max: 0 });
  const pct = Math.floor((m.max || 0) * 100 / DATA_MUSHAF_TOTAL);
  if (!n) {
    const s = SURAHS.find((x) => x.n === m.s) || SURAHS[0];
    return `<h2 class="pl-h">${esc(t().mushaf)} <span class="dk-beta">${esc(t().beta)}</span></h2>
      <p class="fine">${esc(t().mushafNote)}</p>
      <p><span class="dk-bar dk-bar-big"><i style="width:${pct}%"></i></span> ${esc(t().progress(pct))}</p>
      ${m.max ? `<p><a class="primary-link" href="#mushaf/${m.s}">${esc(t().resume(lang === "ar" ? s.ar : s.tr, m.a))}</a></p>` : ""}
      <ol class="dk-surahs">${SURAHS.map((x) => `<li><a href="#mushaf/${x.n}"><span class="n">${num(x.n)}</span><b lang="ar" dir="rtl">${esc(x.ar)}</b><span>${esc(x.tr)} · ${num(x.ayat)}</span></a></li>`).join("")}</ol>`;
  }
  const r = await fetch(`/api/mushaf/${n}?lang=${lang}`); const d = await r.json();
  const before = SURAHS.filter((x) => x.n < n).reduce((a, x) => a + x.ayat, 0);
  return `<h2 class="pl-h" lang="ar">سورة ${esc(d.surah_ar)}</h2>
    <div class="dk-mushaf quran" lang="ar" dir="rtl">${d.ayat.map((a) => `<span class="dk-ayah${m.s === n && m.a === a.ayah ? " is-here" : ""}" data-a="${a.ayah}" data-g="${before + a.ayah}" role="button" tabindex="0">${esc(a.text)} <span class="ayah-no">﴿${num(a.ayah)}﴾</span></span>`).join(" ")}</div>
    ${d.meaning_name ? `<details class="dk-more"><summary>${esc(t().meaning)} (${esc(d.meaning_name)})</summary><ol class="dk-meanings" dir="auto">${d.ayat.map((a) => `<li value="${a.ayah}">${esc(a.meaning || "")}</li>`).join("")}</ol></details>` : ""}
    <p class="dk-pager">${n > 1 ? `<a href="#mushaf/${n - 1}">${esc(t().prev)}</a>` : ""} <a href="#mushaf">${esc(t().mushaf)}</a> ${n < 114 ? `<a href="#mushaf/${n + 1}">${esc(t().next)}</a>` : ""}</p>`;
}
function bindMushaf(root, n) {
  root.querySelectorAll(".dk-ayah").forEach((el) => {
    const mark = () => {
      const m = store.get("mushaf", { max: 0 }); const g = Number(el.dataset.g);
      store.set("mushaf", { s: n, a: Number(el.dataset.a), max: Math.max(m.max || 0, g) });
      root.querySelectorAll(".dk-ayah.is-here").forEach((x) => x.classList.remove("is-here")); el.classList.add("is-here");
      logToday("quran", true);
    };
    el.onclick = mark; el.onkeydown = (e) => { if (e.key === "Enter") mark(); };
  });
}

const TASKS = { fard: ["fajr", "dhuhr", "asr", "maghrib", "isha"], nafl: ["rawatib", "witr", "duha"], dhikr: ["morning", "evening", "quran"] };
const dayKey = (d) => d.toISOString().slice(0, 10);
function logToday(k, v) { const L = store.get("track", {}); const d = dayKey(new Date()); L[d] = L[d] || {}; L[d][k] = v; store.set("track", L); }
function viewTracker() {
  const L = store.get("track", {}); const today = L[dayKey(new Date())] || {};
  const all = Object.values(TASKS).flat();
  const week = [...Array(7)].map((_, i) => { const d = new Date(); d.setDate(d.getDate() - (6 - i)); const x = L[dayKey(d)] || {};
    const n = all.filter((k) => x[k]).length; return `<li title="${dayKey(d)}"><i style="height:${Math.round(n * 100 / all.length)}%"></i><span>${d.toLocaleDateString(lang === "ar" ? "ar-SA" : lang, { weekday: "short" })}</span></li>`; }).join("");
  return `<h2 class="pl-h">${esc(t().tracker)}</h2><p class="fine">${esc(t().savedLocal)}</p>
    <h3 class="dk-h3">${esc(t().today)}</h3>
    ${Object.entries(TASKS).map(([g, ks]) => `<fieldset class="dk-track"><legend>${esc(t().groups[g])}</legend>${ks.map((k) =>
      `<label><input type="checkbox" data-k="${k}" ${today[k] ? "checked" : ""}> ${esc(t().tasks[k])}</label>`).join("")}</fieldset>`).join("")}
    <h3 class="dk-h3">${esc(t().week)}</h3><ol class="dk-week">${week}</ol>`;
}
function bindTracker(root) { root.querySelectorAll(".dk-track input").forEach((c) => (c.onchange = () => { logToday(c.dataset.k, c.checked); render(); })); }

let ASMA = null;
async function viewAsma() {
  if (!ASMA) ASMA = await (await fetch(`/api/asma?lang=${lang}`)).json();
  const h = DATA && DATA.hadith.find((x) => x.id === "asma_99");
  const hp = h && h.shown && h.shown[0];
  return `<h2 class="pl-h">${esc(t().asma)}</h2>
    ${hp ? `<figure class="pl-hadith"><blockquote lang="ar" dir="rtl">«${esc(hp.source.text)}»</blockquote><figcaption>${srcLine(hp.source)}</figcaption></figure>` : ""}
    <p class="fine" lang="ar">${esc(ASMA.note_ar)}</p>
    <ol class="dk-asma">${ASMA.names.map((x) => `<li><details><summary><b lang="ar">${esc(x.name)}</b></summary>
      <p class="quran" lang="ar" dir="rtl">${verseText(x.verse)}</p><p class="fine">${esc(t().asmaVerse)} [${esc(lang === "ar" ? x.verse.surah_ar : x.verse.surah_en)}: ${num(x.ayah)}]</p>
      ${x.verse.meaning ? `<p class="pl-meaning" dir="auto">${esc(x.verse.meaning.text)}</p>` : ""}</details></li>`).join("")}</ol>`;
}

const PHRASES = ["سبحان الله", "الحمد لله", "الله أكبر", "لا إله إلا الله", "أستغفر الله", "سبحان الله وبحمده", "لا حول ولا قوة إلا بالله"];
function viewTasbih() {
  const s = store.get("tasbih", { p: 0, n: 0, target: 33 });
  return `<h2 class="pl-h">${esc(t().tasbih)}</h2>
    <div class="dk-phrases" role="group">${PHRASES.map((p, i) => `<button type="button" class="chip" data-p="${i}" aria-pressed="${s.p === i}" lang="ar">${esc(p)}</button>`).join("")}</div>
    <div class="dk-tasbih"><button type="button" id="tb" class="dk-bead"><span lang="ar">${esc(PHRASES[s.p])}</span><b>${num(s.n)}</b><small>${esc(t().target)}: ${num(s.target)}</small></button></div>
    <p class="dk-pager"><button type="button" class="pbtn" data-target="33">33</button> <button type="button" class="pbtn" data-target="100">100</button> <button type="button" class="pbtn" id="tb-reset">${esc(t().reset)}</button></p>`;
}
function bindTasbih(root) {
  const s = store.get("tasbih", { p: 0, n: 0, target: 33 }); const save = () => { store.set("tasbih", s); };
  root.querySelector("#tb").onclick = () => { s.n += 1; save(); root.querySelector("#tb b").textContent = num(s.n);
    if (s.n % s.target === 0 && navigator.vibrate) try { navigator.vibrate([30, 40, 30]); } catch (e) { /* ignore */ } else if (navigator.vibrate) try { navigator.vibrate(6); } catch (e) { /* ignore */ } };
  root.querySelector("#tb-reset").onclick = () => { s.n = 0; save(); render(); };
  root.querySelectorAll("[data-target]").forEach((b) => (b.onclick = () => { s.target = Number(b.dataset.target); save(); render(); }));
  root.querySelectorAll("[data-p]").forEach((b) => (b.onclick = () => { s.p = Number(b.dataset.p); s.n = 0; save(); render(); }));
}

async function viewAyah(g) {
  if (!SURAHS) { const d = await (await fetch("/api/mushaf")).json(); SURAHS = d.surahs; DATA_MUSHAF_TOTAL = d.total; }
  const day = Math.floor(Date.now() / 86400000);
  let idx = g ? Number(g) : (day * 37) % DATA_MUSHAF_TOTAL + 1;
  idx = ((idx - 1 + DATA_MUSHAF_TOTAL) % DATA_MUSHAF_TOTAL) + 1;
  let s = 0, a = idx; while (a > SURAHS[s].ayat) { a -= SURAHS[s].ayat; s++; }
  const n = SURAHS[s].n;
  const d = await (await fetch(`/api/mushaf/${n}?lang=${lang}&ayah=${a}`)).json();
  const v = d.ayat[0];
  const meaning = v.meaning ? `<p class="pl-meaning" dir="auto"><span class="lbl">${esc(t().meaning)}</span>${esc(v.meaning)} <span class="fine">(${esc(d.meaning_name)})</span></p>` : "";
  return `<h2 class="pl-h">${esc(g ? t().ayah : t().ayahOfDay)}</h2>
    <p class="dk-verse quran" lang="ar" dir="rtl">${esc(v.text)} <span class="ayah-no">﴿${num(a)}﴾</span></p>
    <p class="fine">[${esc(lang === "ar" ? d.surah_ar : d.surah_en)}: ${num(a)}]</p>${meaning}
    <p><a href="https://quranpedia.net/ayahs/${n}/${a}" target="_blank" rel="noopener">${esc(t().tafsir)}</a></p>
    <p class="dk-pager"><a href="#ayah/${idx - 1}">${esc(t().prev)}</a> <a href="#ayah/${idx + 1}">${esc(t().next)}</a></p>`;
}

// ---------- router ----------
async function render() {
  document.documentElement.lang = lang;
  document.documentElement.dir = RTL.includes(lang) ? "rtl" : "ltr";
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    const k = el.dataset.i18n; el.textContent = k.startsWith("nav") ? navWord(k) : (t()[k] ?? el.textContent);
  });
  document.title = `${t().title} · ${lang === "ar" ? "تثبّت" : "Tathabbut"}`;
  const [route, arg] = (location.hash.slice(1) || "home").split("/");
  const v = $("view");
  const titles = { mushaf: t().mushaf, tracker: t().tracker, asma: t().asma, fav: t().fav, tasbih: t().tasbih, ayah: t().ayah, c: arg ? catName(arg) : "" };
  $("crumbs").innerHTML = route === "home" ? "" : `<a href="#home">${esc(t().home)}</a> › <span>${esc(titles[route] || "")}</span>`;
  try {
    if (route === "c") { v.innerHTML = viewCategory(arg); bindCards(v); }
    else if (route === "fav") { v.innerHTML = viewFav(); bindCards(v); }
    else if (route === "mushaf") { v.innerHTML = await viewMushaf(arg ? Number(arg) : 0); if (arg) bindMushaf(v, Number(arg)); }
    else if (route === "tracker") { v.innerHTML = viewTracker(); bindTracker(v); }
    else if (route === "asma") { v.innerHTML = await viewAsma(); }
    else if (route === "tasbih") { v.innerHTML = viewTasbih(); bindTasbih(v); }
    else if (route === "ayah") { v.innerHTML = await viewAyah(arg); }
    else { v.innerHTML = viewHome(); }
  } catch (e) { v.innerHTML = `<p>${esc(t().empty)}</p>`; }
  if (DATA) {
    const shown = DATA.hadith.filter((x) => !x.id.startsWith("ev_"));
    $("dk-note").textContent = t().note(DATA.built_at.slice(0, 10), shown.filter((x) => (x.shown || []).length).length, shown.length);
  }
}

async function load() {
  try { DATA = await (await fetch(`/api/adhkar?lang=${lang}`)).json(); CATS = Object.fromEntries((DATA.categories || []).map((c) => [c.key, c])); } catch (e) { DATA = null; }
  try { const d = await (await fetch("/api/mushaf")).json(); SURAHS = d.surahs; DATA_MUSHAF_TOTAL = d.total; } catch (e) { /* the tile shows 0% */ }
  render();
}
$("lang").value = lang;
$("lang").addEventListener("change", (e) => { lang = e.target.value; try { localStorage.setItem("tathabbut-lang", lang); } catch (x) { /* ignore */ } ASMA = null; load(); });
window.addEventListener("hashchange", () => { render(); window.scrollTo({ top: 0 }); });
load();
