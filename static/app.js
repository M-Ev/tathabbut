"use strict";

const T = {
  ar: {
    title: "تثبّت", tagline: "مدقق ذكي للاستشهادات الشرعية",
    intro: "الصق منشورًا أو درسًا أو إجابة روبوت محادثة. يستخرج تثبّت كل آية وحديث، ويتتبع كل واحد إلى مصدره العربي، وينقل أحكام علماء الحديث المعتمدين كما هي، ويقول بوضوح إن لم يجد ويحيل إلى المختص.",
    inputLabel: "النص المراد فحصه", placeholder: "الصق النص هنا…", tryLabel: "جرّب مثالًا:",
    sampleAr: "منشور عربي", sampleEn: "English post", deep: "تحليل أعمق بالنموذج اللغوي علّام (أبطأ)",
    check: "تحقّق", checking: "جارٍ التحقق من المصادر…", checkingDeep: "جارٍ التحقق… النموذج اللغوي يعمل على معالج مجاني وقد يستغرق دقيقة أو أكثر.",
    none: "لم نجد في النص آيات أو أحاديث مستشهدًا بها.", failed: "تعذّر الفحص الآن. حاول مرة أخرى.",
    howTitle: "كيف يعمل تثبّت؟",
    how1: "يستخرج الآيات والأحاديث من النص بقواعد ثابتة، ويمكن أن يستعين بنموذج علّام. وكل ما يقترحه النموذج يجب أن يوجد حرفيًا في نصك وإلا يُحذف.",
    how2: "يطابق الآيات مع نص مصحف مجمع الملك فهد، ويبيّن الكلمات المخالفة والعزو الخطأ. نص القرآن لا يُولَّد أبدًا.",
    how3: "يبحث عن الأحاديث في الموسوعة الحديثية للدرر السنية، ويعرض أحكام أئمة الحديث ثم أحكام المحققين المعاصرين كما هي، مع اسم قائل كل حكم، دون ترجيح آلي.",
    how4: "إن لم يجد حكمًا لأحد علماء الحديث المعتمدين قال ذلك صراحة وأحال إلى المختص.",
    privacy: "الخصوصية: لا نحفظ نصك. لا يُرسل إلى الدرر إلا لفظ الحديث المستخرج.",
    disclosure: "تثبّت أداة آلية مدعومة بالذكاء الاصطناعي، وليست عالمًا ولا مفتيًا. أحكام الأحاديث منقولة من مصادرها، والفتوى لأهلها.",
    apiLink: "واجهة برمجية (API) لفحص إجابات روبوتات المحادثة",
    footer: "فريق قيد الأوابد · تحدي الذكاء الاصطناعي في خدمة المحتوى الإسلامي",
    sumTotal: "استشهادات", sumTraced: "وُجدت في مصادرها", sumAttention: "تحتاج انتباهًا", sumReferred: "أُحيلت إلى مختص",
    quran: "آية", hadith: "حديث", quoted: "كما ورد في النص",
    st: {
      verified: "مطابق للمصحف", differs: "يخالف لفظ المصحف", not_in_mushaf: "ليس في المصحف",
      graded: "وُجد في كتب الحديث", found_similar: "وُجد بلفظ مقارب", not_found: "لم نجد له حكمًا معتمدًا",
      needs_model: "يحتاج النموذج اللغوي", source_error: "المصدر غير متاح الآن", source_offline: "البحث في الحديث متوقف",
      error: "خطأ",
    },
    mushafText: "النص في المصحف", translationEn: "الترجمة (صحيح إنترناشونال)", diffTitle: "الفروق: الأحمر كما ورد في النص، والأخضر كما في المصحف",
    surah: "سورة", ayah: "آية", occurrences: (n) => `تتكرر هذه العبارة في ${n} مواضع من المصحف، وهذا أولها.`,
    wrongRef: (given, s, a) => `العزو المكتوب ${given} لا يطابق موضع النص، وموضعه الصحيح: سورة ${s} آية ${a}.`,
    rightRef: (given) => `العزو المكتوب ${given} صحيح.`,
    notes: {
      hadith_is_quran: "هذا النص آية قرآنية، وقد نُسب في النص إلى النبي ﷺ.",
      quran_claim_found_in_hadith: "نُسب هذا النص إلى القرآن، وليس آية. وجدناه في كتب الحديث:",
      match_by_model: "المطابقة بين الترجمة والأصل العربي اقترحها النموذج اللغوي علّام، فراجع النص العربي بنفسك.",
      wording_differs: "اللفظ المنقول يختلف عن ألفاظ الروايات التي وجدناها، فانقل اللفظ كما في المصدر.",
    },
    fabricated: (names) => `حكم عليه بالوضع أو البطلان أو بأنه لا أصل له: ${names}. لا يُذكر إلا مع بيان حكمه.`,
    ijtihad: "إذا اختلفت الأحكام فكلها اجتهاد يُعرض كما هو، ولا يرجّح تثبّت بينها.",
    narrator: (n) => `أُخفي ${n} من أقوال علماء الجرح في الرواة لأنها حكم على راوٍ لا على الحديث.`,
    rawi: "الراوي", source: "المصدر", number: "الرقم", sourceText: "النص في المصدر", openDorar: "فتح في الدرر السنية", searchDorar: "البحث في الدرر السنية",
    matchedArabic: "الأصل العربي الذي طابقه النموذج", similarity: "قرب اللفظ",
    leveld: (b) => `يبدو أن النص يتضمن سؤالًا عن حالة شخصية. تثبّت لا يفتي، ويُرجى الرجوع إلى ${b}.`,
    foundBy: { rules: "", model: "اكتشفه النموذج اللغوي" },
    unknownScholarNote: "يعرض تثبّت أحكام علماء الحديث المعتمدين فقط.",
  },
  en: {
    title: "Tathabbut", tagline: "Verify before you share: a citation checker for Islamic content",
    intro: "Paste a post, a lecture or a chatbot answer. Tathabbut extracts every Quran verse and hadith, traces each one to its Arabic source, quotes the approved hadith scholars' gradings verbatim, and says plainly when nothing is found and refers you to a specialist.",
    inputLabel: "Text to check", placeholder: "Paste your text here…", tryLabel: "Try an example:",
    sampleAr: "Arabic post", sampleEn: "English post", deep: "Deeper analysis with the ALLaM language model (slower)",
    check: "Check", checking: "Checking the sources…", checkingDeep: "Checking… the language model runs on a free CPU and may take a minute or more.",
    none: "No Quran verses or hadith citations were found in the text.", failed: "The check failed. Please try again.",
    howTitle: "How does it work?",
    how1: "Citations are extracted with fixed rules, optionally helped by the ALLaM model. Anything the model suggests must appear verbatim in your text or it is dropped.",
    how2: "Verses are matched against the King Fahd Complex Mushaf text, showing wrong words and wrong references. Quran text is never generated.",
    how3: "Hadith are searched in the Dorar hadith encyclopedia. Gradings by the classical imams of hadith, then by modern hadith editors, are shown verbatim with who said each one, with no automated preference.",
    how4: "If none of the approved hadith scholars graded a text, the tool says so and refers you to a specialist.",
    privacy: "Privacy: your text is not stored. Only the extracted hadith wording is sent to Dorar.",
    disclosure: "Tathabbut is an AI-assisted tool, not a scholar or a mufti. Gradings are quoted from their sources; rulings belong to qualified scholars.",
    apiLink: "API for checking chatbot answers",
    footer: "Team Qayd al-Awabid · AI Challenge in Serving Islamic Content",
    sumTotal: "citations", sumTraced: "traced to source", sumAttention: "need attention", sumReferred: "referred to a specialist",
    quran: "Quran", hadith: "Hadith", quoted: "As quoted",
    st: {
      verified: "Matches the Mushaf", differs: "Differs from the Mushaf", not_in_mushaf: "Not in the Mushaf",
      graded: "Found in hadith sources", found_similar: "Similar wording found", not_found: "No approved grading found",
      needs_model: "Needs the language model", source_error: "Source unavailable", source_offline: "Hadith search is off",
      error: "Error",
    },
    mushafText: "Mushaf text", translationEn: "Translation (Saheeh International)", diffTitle: "Differences: red as quoted, green as in the Mushaf",
    surah: "Surah", ayah: "Ayah", occurrences: (n) => `This phrase occurs in ${n} places in the Mushaf; this is the first.`,
    wrongRef: (given, s, a) => `The reference ${given} is wrong. The text is in surah ${s}, ayah ${a}.`,
    rightRef: (given) => `The reference ${given} is correct.`,
    notes: {
      hadith_is_quran: "This text is a Quran verse, but it was attributed to the Prophet ﷺ.",
      quran_claim_found_in_hadith: "This text was attributed to the Quran but it is not a verse. It was found in hadith sources:",
      match_by_model: "The match between the translation and the Arabic source was suggested by the ALLaM model. Please check the Arabic text yourself.",
      wording_differs: "The quoted wording differs from the narrations found. Quote the wording as it is in the source.",
    },
    fabricated: (names) => `Graded as fabricated, false or baseless by: ${names}. It should only be mentioned together with its grading.`,
    ijtihad: "Where gradings differ, all are scholarly ijtihad shown as they are; Tathabbut does not prefer one over another.",
    narrator: (n) => `${n} statement(s) about narrators were hidden: they judge a narrator, not this hadith.`,
    rawi: "Narrator", source: "Source", number: "No.", sourceText: "Text in the source", openDorar: "Open on Dorar", searchDorar: "Search on Dorar",
    matchedArabic: "Arabic source matched by the model", similarity: "Wording closeness",
    leveld: (b) => `The text seems to include a personal fatwa question. Tathabbut does not issue fatwas; please ask ${b}.`,
    foundBy: { rules: "", model: "found by the language model" },
    unknownScholarNote: "Only gradings by the approved hadith scholars are shown.",
  },
};

const SAMPLES = {
  ar: "أيها الإخوة، يقول الله تعالى: ﴿يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا جَاءَكُمْ فَاسِقٌ بِنَبَإٍ فَتَبَيَّنُوا﴾ (البقرة: 6).\nوقال رسول الله ﷺ: «إنما الأعمال بالنيات».\nوفي الحديث: «اطلبوا العلم ولو في الصين».\nومن يتق الله يجعل له مخرجا ويرزقه من حيث لا يحتسب، فلا تيأسوا.\nوقال تعالى: «النظافة من الإيمان».",
  en: "The Prophet (ﷺ) said: \"Actions are judged by intentions.\"\nAllah says in the Quran: \"Indeed, with hardship comes ease\" (94:5).\nThe Prophet (pbuh) said: \"Seek knowledge even if you have to go to China.\"",
};

let lang = "ar";
let lastResult = null;
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const t = () => T[lang];

function applyLang() {
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = t()[el.dataset.i18n]; });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => { el.placeholder = t()[el.dataset.i18nPh]; });
  $("lang").textContent = lang === "ar" ? "English" : "العربية";
  document.title = lang === "ar" ? "تثبّت · مدقق الاستشهادات الشرعية" : "Tathabbut · Islamic citation checker";
  if (lastResult) render(lastResult);
}

function badgeClass(status) {
  if (["verified", "graded"].includes(status)) return "ok";
  if (["differs", "found_similar", "needs_model"].includes(status)) return "warn";
  if (["not_in_mushaf", "not_found", "error", "source_error"].includes(status)) return "bad";
  return "info";
}

function renderDiff(diff) {
  return diff.map((d) => {
    if (d.op === "equal") return esc(d.mushaf || d.quoted);
    let out = "";
    if (d.quoted) out += `<del>${esc(d.quoted)}</del> `;
    if (d.mushaf) out += `<ins>${esc(d.mushaf)}</ins>`;
    return out;
  }).join(" ");
}

function renderQuran(q, c) {
  if (!q || q.surah == null) return "";
  const name = lang === "ar" ? q.surah_name_ar : q.surah_name_en;
  let h = `<div class="sub">${esc(t().mushafText)} · ${esc(t().surah)} ${esc(name)} (${esc(q.ref)})</div>`;
  h += `<div class="mushaf">${esc(q.mushaf_text)}</div>`;
  if (lang === "en" || c.lang === "en") h += `<div class="sub">${esc(t().translationEn)}</div><div class="translation">${esc(q.translation_en)}</div>`;
  const changed = (q.diff || []).filter((d) => d.op !== "equal");
  if (changed.length) h += `<div class="sub">${esc(t().diffTitle)}</div><div class="diff mushaf">${renderDiff(q.diff)}</div>`;
  if (q.occurrences > 1) h += `<p class="muted">${esc(t().occurrences(q.occurrences))}</p>`;
  if (q.reference_given) {
    h += q.reference_ok === false
      ? `<div class="notice bad">${esc(t().wrongRef(q.reference_given, name, q.ayah_from))}</div>`
      : `<div class="notice ok">${esc(t().rightRef(q.reference_given))}</div>`;
  }
  h += `<div class="links"><a href="${esc(q.url)}" target="_blank" rel="noopener">quranenc.com · ${esc(q.ref)}</a></div>`;
  return h;
}

function renderHadith(hd) {
  if (!hd) return "";
  let h = "";
  if (hd.fabricated_by && hd.fabricated_by.length) h += `<div class="notice bad">${esc(t().fabricated(hd.fabricated_by.join("، ")))}</div>`;
  const groups = hd.groups || [];
  const grades = new Set(groups.flatMap((g) => g.items.map((i) => i.grade.replace(/[\[\]]/g, "").trim())));
  if (grades.size > 1) h += `<div class="notice info">${esc(t().ijtihad)}</div>`;
  for (const g of groups) {
    h += `<div class="group-title">${esc(lang === "ar" ? g.label_ar : g.label_en)}</div>`;
    for (const i of g.items) {
      h += `<div class="grade">
        <div class="grade-top"><span class="who">${esc(lang === "ar" ? i.scholar_ar : i.scholar_en)}</span>
        <span class="verdict">${esc(i.grade)}</span></div>
        <div class="meta">${esc(t().source)}: ${esc(i.book)} · ${esc(t().number)}: ${esc(i.number)}${i.rawi ? ` · ${esc(t().rawi)}: ${esc(i.rawi)}` : ""} · ${esc(t().similarity)}: ${Math.round(i.similarity)}%</div>
        <details><summary>${esc(t().sourceText)}</summary><div class="htext">${esc(i.text)}</div></details>
        ${i.url ? `<div class="links"><a href="${esc(i.url)}" target="_blank" rel="noopener">${esc(t().openDorar)}</a></div>` : ""}
      </div>`;
    }
  }
  if (hd.hidden_narrator_statements) h += `<p class="muted">${esc(t().narrator(hd.hidden_narrator_statements))}</p>`;
  if (groups.length) h += `<p class="muted">${esc(t().unknownScholarNote)}</p>`;
  if (hd.search_url) h += `<div class="links"><a href="${esc(hd.search_url)}" target="_blank" rel="noopener">${esc(t().searchDorar)}</a></div>`;
  return h;
}

function renderCitation(c) {
  const kind = c.type === "quran" ? t().quran : t().hadith;
  let h = `<article class="cite"><div class="cite-head"><span class="kind">${c.id}. ${esc(kind)}${c.found_by === "model" ? ` · <span class="muted">${esc(t().foundBy.model)}</span>` : ""}</span>
    <span class="badge ${badgeClass(c.status)}">${esc(t().st[c.status] || c.status)}</span></div><div class="cite-body">`;
  h += `<div class="sub">${esc(t().quoted)}</div><blockquote class="quote" dir="${c.lang === "ar" ? "rtl" : "ltr"}">${esc(c.quote)}</blockquote>`;
  for (const n of c.notes || []) {
    if (t().notes[n]) h += `<div class="notice ${n === "wording_differs" || n === "match_by_model" ? "warn" : "info"}">${esc(t().notes[n])}</div>`;
  }
  if (c.matched_arabic) h += `<div class="sub">${esc(t().matchedArabic)}</div><div class="htext">${esc(c.matched_arabic)}</div>`;
  if (c.quran && (c.type === "quran" || (c.notes || []).includes("hadith_is_quran"))) h += renderQuran(c.quran, c);
  if (c.hadith) h += renderHadith(c.hadith);
  if (c.referral) h += `<div class="notice warn">${esc(c.referral[lang])}</div>`;
  h += `</div></article>`;
  return h;
}

function render(r) {
  const s = r.summary;
  const box = $("summary");
  box.hidden = !s.total;
  box.innerHTML = [
    [s.total, t().sumTotal], [s.traced, t().sumTraced], [s.attention, t().sumAttention], [s.referred, t().sumReferred],
  ].map(([n, l]) => `<div class="stat"><b>${n}</b><span>${esc(l)}</span></div>`).join("");
  const ld = $("leveld");
  ld.hidden = !r.level_d;
  if (r.level_d) {
    const b = r.level_d.body;
    ld.innerHTML = `${esc(t().leveld(lang === "ar" ? b.ar : b.en))} <a href="${esc(b.url)}" target="_blank" rel="noopener">${esc(b.url)}</a>`;
  }
  $("results").innerHTML = r.citations.length ? r.citations.map(renderCitation).join("") : `<div class="notice info">${esc(t().none)}</div>`;
}

async function check() {
  const text = $("text").value.trim();
  if (text.length < 3) return;
  const deep = $("deep").checked;
  $("go").disabled = true;
  $("status").innerHTML = `<span class="spinner"></span>${esc(deep ? t().checkingDeep : t().checking)}`;
  try {
    const res = await fetch("/api/check", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, deep }) });
    if (!res.ok) throw new Error(res.status);
    lastResult = await res.json();
    $("status").textContent = "";
    render(lastResult);
    $("summary").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (e) {
    $("status").textContent = t().failed;
  } finally {
    $("go").disabled = false;
  }
}

$("go").addEventListener("click", check);
$("text").addEventListener("input", () => { $("counter").textContent = `${$("text").value.length} / 8000`; });
$("text").addEventListener("keydown", (e) => { if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) check(); });
document.querySelectorAll("[data-sample]").forEach((b) => b.addEventListener("click", () => {
  $("text").value = SAMPLES[b.dataset.sample];
  $("text").dispatchEvent(new Event("input"));
}));
$("lang").addEventListener("click", () => {
  lang = lang === "ar" ? "en" : "ar";
  try { localStorage.setItem("tathabbut-lang", lang); } catch (e) { /* storage may be blocked */ }
  applyLang();
});
try { const saved = localStorage.getItem("tathabbut-lang"); if (saved === "en" || saved === "ar") lang = saved; } catch (e) { /* ignore */ }
applyLang();
