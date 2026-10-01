"use strict";

const T = {
  ar: {
    title: "تثبّت", tagline: "مدقق الاستشهادات الشرعية", mottoRef: "الحجرات ٦",
    inputLabel: "النص المراد فحصه", intro: "الصق منشورًا أو درسًا أو إجابة روبوت محادثة، وسنتتبع كل آية وحديث فيه إلى مصدره.",
    placeholder: "الصق النص هنا", tryLabel: "أمثلة:", sampleAr: "منشور عربي", sampleEn: "English post",
    deep: "استعن بالنموذج اللغوي علّام لاكتشاف ما فات القواعد (أبطأ)", check: "تحقّق من الاستشهادات",
    checking: "نراجع المصادر…", checkingDeep: "نراجع المصادر… النموذج اللغوي يعمل على معالج مجاني وقد يستغرق دقيقة أو أكثر.",
    failed: "تعذّر الفحص الآن، حاول مرة أخرى.", reportTitle: "نتيجة الفحص",
    none: "لم نجد في النص آية أو حديثًا مستشهدًا به.",
    summary: (s, n) => `الاستشهادات: ${n(s.total)} · وُجد في مصدره: ${n(s.traced)} · يحتاج انتباهًا: ${n(s.attention)} · أُحيل إلى مختص: ${n(s.referred)}`,
    howTitle: "منهج الأداة",
    m1t: "القرآن", m1: "يُطابق النص مع مصحف مجمع الملك فهد، وتُبيَّن الكلمات المخالفة والعزو الخطأ. نص القرآن لا يُولَّد أبدًا.",
    m2t: "الحديث", m2: "يُبحث عنه في الموسوعة الحديثية للدرر السنية، وتُنقل أحكام أئمة الحديث ثم أحكام المحققين المعاصرين بنصها، مع اسم قائل كل حكم، دون ترجيح بينها.",
    m3t: "عند عدم الوجود", m3: "يقال ذلك صراحة ويُحال إلى المختص، وأسئلة الفتوى الشخصية تُحال إلى جهة الإفتاء.",
    m4t: "النموذج اللغوي", m4: "يستخرج ويطابق فقط، ولا يحكم ولا يفتي. وكل ما يقترحه يجب أن يوجد بنصه في كلامك وإلا يُحذف.",
    privacy: "لا نحفظ نصك، ولا يُرسل إلى الدرر إلا لفظ الحديث المستخرج.",
    disclosure: "تثبّت أداة آلية مدعومة بالذكاء الاصطناعي، وليست عالمًا ولا مفتيًا.",
    apiLink: "الواجهة البرمجية لفحص إجابات روبوتات المحادثة",
    footer: "فريق قيد الأوابد · تحدي الذكاء الاصطناعي في خدمة المحتوى الإسلامي",
    quran: "آية", hadith: "حديث", asQuoted: "ورد في النص", byModel: "اكتشفه النموذج اللغوي",
    v: {
      verified: "الآية منقولة بلفظ المصحف",
      verifiedBadRef: "الآية منقولة بلفظ المصحف، لكن عزوها خطأ",
      differs: (n) => n === 1 ? "في نقل الآية خطأ في موضع واحد" : n === 2 ? "في نقل الآية خطأ في موضعين" : `في نقل الآية خطأ في ${n} مواضع`,
      differsEn: "الترجمة قريبة من هذه الآية، وليست بلفظ الترجمة المعتمدة",
      not_in_mushaf: "هذا النص ليس آية من القرآن",
      graded: "وُجد في كتب الحديث، وهذه أحكام العلماء عليه",
      gradedFab: "وُجد في كتب الحديث، ومن العلماء من حكم عليه بالوضع أو البطلان",
      found_similar: "وُجدت روايات بلفظ مقارب، لا بلفظه",
      not_found: "لم نجد حكمًا لأحد علماء الحديث المعتمدين على هذا النص",
      needs_model: "النص مترجم، والبحث عن أصله العربي يحتاج إلى النموذج اللغوي",
      source_error: "تعذّر الوصول إلى الموسوعة الحديثية الآن",
      source_offline: "البحث في الحديث متوقف",
      error: "حدث خطأ أثناء الفحص",
    },
    surah: "سورة", ayahWord: "الآية", ayatWord: "الآيات",
    fixesHead: ["ورد في النص", "في المصحف"], missing: "(محذوف)", extra: "(زائد)",
    translationLbl: "ترجمة المعنى (صحيح إنترناشونال)",
    occurrences: (n) => `تتكرر هذه العبارة في ${n} مواضع من المصحف، وهذا أحدها.`,
    wrongRef: (given, where) => `العزو المكتوب ${given} خطأ، والصواب: ${where}.`,
    rightRef: (given) => `العزو المكتوب ${given} صحيح.`,
    notes: {
      hadith_is_quran: "هذا النص آية من القرآن، وقد نُسب في النص إلى النبي ﷺ.",
      quran_claim_found_in_hadith: "نُسب هذا النص إلى القرآن، ووجدناه في كتب الحديث:",
      match_by_model: "المطابقة بين الترجمة والأصل العربي اقترحها النموذج اللغوي، فراجع النص العربي بنفسك.",
      wording_differs: "انقل الحديث بلفظه كما في المصدر.",
    },
    fabBy: (names) => `حكم عليه بالوضع أو البطلان أو بأنه لا أصل له: ${names}. فلا يُذكر إلا مع بيان حكمه.`,
    ijtihad: "اختلفت الأحكام، وكلها اجتهاد يُعرض كما هو دون ترجيح.",
    gradeCols: ["العالِم", "الحكم بنصه", "المصدر"], died: (y) => `ت ${y}هـ`,
    sourceText: "نص الحديث في المصدر", rawi: "الراوي", openDorar: "في الدرر السنية",
    narrator: (n) => `أُخفي ${n} من أقوال علماء الجرح والتعديل لأنها حكم على راوٍ لا على الحديث.`,
    onlyApproved: "تُعرض أحكام علماء الحديث المعتمدين في الأداة فقط.", searchDorar: "ابحث بنفسك في الدرر السنية",
    matchedArabic: "الأصل العربي الذي طابقه النموذج",
    leveld: (b) => `يبدو أن في النص سؤالًا عن حالة شخصية. تثبّت لا يفتي، فيُرجى سؤال ${b}.`,
  },
  en: {
    title: "Tathabbut", tagline: "Islamic citation checker", mottoRef: "al-Hujurat 49:6 · “verify”",
    inputLabel: "Text to check", intro: "Paste a post, a lecture or a chatbot answer, and we will trace every Quran verse and hadith in it to its source.",
    placeholder: "Paste your text here", tryLabel: "Examples:", sampleAr: "Arabic post", sampleEn: "English post",
    deep: "Use the ALLaM language model to find what the rules missed (slower)", check: "Check citations",
    checking: "Checking the sources…", checkingDeep: "Checking the sources… the language model runs on a free CPU and may take a minute or more.",
    failed: "The check failed. Please try again.", reportTitle: "Result",
    none: "No Quran verse or hadith citation was found in the text.",
    summary: (s, n) => `Citations: ${n(s.total)} · traced to source: ${n(s.traced)} · need attention: ${n(s.attention)} · referred: ${n(s.referred)}`,
    howTitle: "Method",
    m1t: "Quran", m1: "Matched against the King Fahd Complex Mushaf; wrong words and wrong references are shown. Quran text is never generated.",
    m2t: "Hadith", m2: "Looked up in the Dorar hadith encyclopedia. Gradings by the classical imams of hadith, then by modern hadith editors, are quoted verbatim with who said each, with no preference between them.",
    m3t: "Not found", m3: "The tool says so plainly and refers you to a specialist; personal fatwa questions go to a fatwa authority.",
    m4t: "Language model", m4: "Only extracts and matches; it never grades or rules. Anything it suggests must appear verbatim in your text or it is dropped.",
    privacy: "Your text is not stored. Only the extracted hadith wording is sent to Dorar.",
    disclosure: "Tathabbut is an AI-assisted tool, not a scholar or a mufti.",
    apiLink: "API for checking chatbot answers",
    footer: "Team Qayd al-Awabid · AI Challenge in Serving Islamic Content",
    quran: "Quran", hadith: "Hadith", asQuoted: "As quoted", byModel: "found by the language model",
    v: {
      verified: "Quoted exactly as in the Mushaf",
      verifiedBadRef: "Quoted correctly, but the reference is wrong",
      differs: (n) => n === 1 ? "The verse is misquoted in one place" : `The verse is misquoted in ${n} places`,
      differsEn: "Close to this verse, but not the standard translation's wording",
      not_in_mushaf: "This text is not a verse of the Quran",
      graded: "Found in hadith sources, with these gradings",
      gradedFab: "Found in hadith sources; some scholars graded it fabricated or false",
      found_similar: "Narrations with similar, not identical, wording were found",
      not_found: "No grading by the approved hadith scholars was found",
      needs_model: "This is a translation; finding its Arabic source needs the language model",
      source_error: "The hadith encyclopedia could not be reached",
      source_offline: "Hadith lookup is off",
      error: "An error occurred",
    },
    surah: "Surah", ayahWord: "ayah", ayatWord: "ayat",
    fixesHead: ["As quoted", "In the Mushaf"], missing: "(missing)", extra: "(extra)",
    translationLbl: "Translation of the meaning (Saheeh International)",
    occurrences: (n) => `This phrase occurs in ${n} places in the Mushaf; this is one of them.`,
    wrongRef: (given, where) => `The reference ${given} is wrong; it should be ${where}.`,
    rightRef: (given) => `The reference ${given} is correct.`,
    notes: {
      hadith_is_quran: "This text is a Quran verse, but it was attributed to the Prophet ﷺ.",
      quran_claim_found_in_hadith: "This was attributed to the Quran; it was found in hadith sources:",
      match_by_model: "The language model matched the translation to the Arabic source. Please check the Arabic text yourself.",
      wording_differs: "Quote the hadith in the wording of its source.",
    },
    fabBy: (names) => `Graded fabricated, false or baseless by: ${names}. Mention it only together with its grading.`,
    ijtihad: "The gradings differ; all are scholarly ijtihad, shown as they are with no preference.",
    gradeCols: ["Scholar", "Grading (verbatim)", "Source"], died: (y) => `d. ${y} AH`,
    sourceText: "Hadith text in the source", rawi: "Narrator", openDorar: "on Dorar",
    narrator: (n) => `${n} statement(s) about narrators hidden: they judge a narrator, not this hadith.`,
    onlyApproved: "Only gradings by the tool's approved hadith scholars are shown.", searchDorar: "Search Dorar yourself",
    matchedArabic: "Arabic source matched by the model",
    leveld: (b) => `The text seems to include a personal fatwa question. Tathabbut does not issue fatwas; please ask ${b}.`,
  },
};

const SAMPLES = {
  ar: "أيها الإخوة، يقول الله تعالى: ﴿يَا أَيُّهَا الَّذِينَ آمَنُوا إِذَا جَاءَكُمْ فَاسِقٌ بِخَبَرٍ فَتَبَيَّنُوا﴾ (البقرة: 6).\nوقال رسول الله ﷺ: «إنما الأعمال بالنيات».\nوفي الحديث: «اطلبوا العلم ولو في الصين».\nومن يتق الله يجعل له مخرجا ويرزقه من حيث لا يحتسب، فلا تيأسوا.\nوقال تعالى: «النظافة من الإيمان».",
  en: "The Prophet (ﷺ) said: \"Actions are judged by intentions.\"\nAllah says in the Quran: \"Indeed, with hardship comes ease\" (94:6).\nThe Prophet (pbuh) said: \"Seek knowledge even if you have to go to China.\"",
};

let lang = "ar";
let lastResult = null;
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const t = () => T[lang];
const num = (n) => (lang === "ar" ? Number(n).toLocaleString("ar-EG") : String(n));
const arDigits = (n) => Number(n).toLocaleString("ar-EG", { useGrouping: false });

function applyLang() {
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === "ar" ? "rtl" : "ltr";
  document.querySelectorAll("[data-i18n]").forEach((el) => { el.textContent = t()[el.dataset.i18n]; });
  document.querySelectorAll("[data-i18n-ph]").forEach((el) => { el.placeholder = t()[el.dataset.i18nPh]; });
  $("lang").textContent = lang === "ar" ? "English" : "العربية";
  document.title = lang === "ar" ? "تثبّت · مدقق الاستشهادات الشرعية" : "Tathabbut · Islamic citation checker";
  if (lastResult) render(lastResult);
}

function place(q) {
  const name = lang === "ar" ? q.surah_name_ar : q.surah_name_en;
  const a = q.ayah_from === q.ayah_to ? num(q.ayah_from) : `${num(q.ayah_from)}–${num(q.ayah_to)}`;
  const word = q.ayah_from === q.ayah_to ? t().ayahWord : t().ayatWord;
  return `${t().surah} ${name}، ${word} ${a}`.replace("، ", lang === "ar" ? "، " : ", ");
}

function verdictFor(c) {
  const v = t().v;
  const q = c.quran || {};
  const hd = c.hadith || {};
  if (c.type === "quran") {
    if (c.status === "verified") return [q.reference_ok === false ? v.verifiedBadRef : v.verified, q.reference_ok === false ? "warn" : "ok"];
    if (c.status === "differs") {
      if (q.via !== "arabic") return [v.differsEn, "warn"];
      const n = (q.diff || []).filter((d) => d.op !== "equal").length || 1;
      return [v.differs(n), "bad"];
    }
    if (c.status === "not_in_mushaf") return [v.not_in_mushaf, "bad"];
  }
  if (c.status === "graded" && hd.fabricated_by && hd.fabricated_by.length) return [v.gradedFab, "bad"];
  const cls = { graded: "ok", found_similar: "warn", not_found: "bad", needs_model: "warn", source_error: "warn", error: "bad" }[c.status] || "";
  return [v[c.status] || c.status, cls];
}

function markWords(text, words) {
  let html = esc(text);
  for (const w of words) {
    const e = esc(w);
    if (e && html.includes(e)) html = html.replace(e, `<mark>${e}</mark>`);
  }
  return html;
}

function renderMushaf(q, c) {
  const changed = (q.diff || []).filter((d) => d.op !== "equal");
  const marked = changed.flatMap((d) => (d.mushaf ? d.mushaf.split(" ") : []));
  const ayat = (q.ayat && q.ayat.length ? q.ayat : [{ ayah: q.ayah_from, text: q.mushaf_text }])
    .map((a) => `${markWords(a.text, marked)}<span class="ayah-end">۝${arDigits(a.ayah)}</span>`).join(" ");
  let h = `<div class="mushaf"><div class="mushaf-inner">
    <div class="mushaf-head">${esc(place(q))}</div>
    <p class="ayat">${ayat}</p>`;
  if (lang === "en" || c.lang === "en") h += `<p class="translation"><span class="lbl">${esc(t().translationLbl)}</span>${esc(q.translation_en)}</p>`;
  h += `</div></div>`;
  if (changed.length) {
    h += `<table class="fixes"><thead><tr><th>${esc(t().fixesHead[0])}</th><th>${esc(t().fixesHead[1])}</th></tr></thead><tbody>`;
    for (const d of changed) {
      h += `<tr><td class="was">${esc(d.quoted || t().extra)}</td><td class="is">${esc(d.mushaf || t().missing)}</td></tr>`;
    }
    h += `</tbody></table>`;
  }
  if (q.reference_given) {
    h += q.reference_ok === false
      ? `<p class="line bad">${esc(t().wrongRef(q.reference_given, place(q)))}</p>`
      : `<p class="line ok">${esc(t().rightRef(q.reference_given))}</p>`;
  }
  if (q.occurrences > 1) h += `<p class="line note">${esc(t().occurrences(num(q.occurrences)))}</p>`;
  h += `<p class="after"><a href="${esc(q.url)}" target="_blank" rel="noopener">quranenc.com</a></p>`;
  return h;
}

function renderGradings(hd) {
  if (!hd) return "";
  let h = "";
  if (hd.fabricated_by && hd.fabricated_by.length) h += `<p class="line bad">${esc(t().fabBy(hd.fabricated_by.join("، ")))}</p>`;
  const groups = hd.groups || [];
  const distinct = new Set(groups.flatMap((g) => g.items.map((i) => i.grade.replace(/[\[\]]/g, "").trim())));
  if (distinct.size > 1) h += `<p class="line note">${esc(t().ijtihad)}</p>`;
  for (const g of groups) {
    h += `<table class="grades"><caption>${esc(lang === "ar" ? g.label_ar : g.label_en)}</caption>
      <thead><tr><th>${esc(t().gradeCols[0])}</th><th>${esc(t().gradeCols[1])}</th><th>${esc(t().gradeCols[2])}</th></tr></thead><tbody>`;
    for (const i of g.items) {
      h += `<tr>
        <td class="who">${esc(lang === "ar" ? i.scholar_ar : i.scholar_en)}<span class="died">${esc(t().died(num(i.died_ah)))}</span></td>
        <td><span class="g">${esc(i.grade)}</span>
          <details><summary>${esc(t().sourceText)}</summary><div class="htext">${esc(i.text)}${i.rawi ? `<div class="after">${esc(t().rawi)}: ${esc(i.rawi)}</div>` : ""}</div></details></td>
        <td class="src">${esc(i.book)}، ${esc(i.number)}${i.url ? `<br><a href="${esc(i.url)}" target="_blank" rel="noopener">${esc(t().openDorar)}</a>` : ""}</td>
      </tr>`;
    }
    h += `</tbody></table>`;
  }
  if (hd.hidden_narrator_statements) h += `<p class="after">${esc(t().narrator(num(hd.hidden_narrator_statements)))}</p>`;
  if (groups.length) h += `<p class="after">${esc(t().onlyApproved)}</p>`;
  if (hd.search_url) h += `<p class="after"><a href="${esc(hd.search_url)}" target="_blank" rel="noopener">${esc(t().searchDorar)}</a></p>`;
  return h;
}

function renderEntry(c) {
  const [verdict, cls] = verdictFor(c);
  const kind = c.type === "quran" ? t().quran : t().hadith;
  let h = `<li class="entry"><div class="entry-no">${num(c.id)}</div><div>
    <p class="entry-kind">${esc(kind)}${c.found_by === "model" ? ` · ${esc(t().byModel)}` : ""}</p>
    <p class="verdict ${cls}">${esc(verdict)}</p>
    <p class="as-quoted"><span class="lbl">${esc(t().asQuoted)}</span><q dir="${c.lang === "ar" ? "rtl" : "ltr"}">${esc(c.quote)}</q></p>`;
  for (const n of c.notes || []) if (t().notes[n]) h += `<p class="line ${n === "match_by_model" ? "warn" : "note"}">${esc(t().notes[n])}</p>`;
  if (c.matched_arabic) h += `<p class="as-quoted"><span class="lbl">${esc(t().matchedArabic)}</span>${esc(c.matched_arabic)}</p>`;
  if (c.quran && c.quran.surah != null && (c.type === "quran" || (c.notes || []).includes("hadith_is_quran"))) h += renderMushaf(c.quran, c);
  if (c.hadith) h += renderGradings(c.hadith);
  if (c.referral) h += `<p class="refer">${esc(c.referral[lang])}</p>`;
  return h + `</div></li>`;
}

function render(r) {
  $("report").hidden = false;
  $("summary").textContent = r.summary.total ? t().summary(r.summary, num) : t().none;
  const ld = $("leveld");
  ld.hidden = !r.level_d;
  if (r.level_d) {
    const b = r.level_d.body;
    ld.innerHTML = `${esc(t().leveld(lang === "ar" ? b.ar : b.en))} <a href="${esc(b.url)}" target="_blank" rel="noopener">${esc(b.url)}</a>`;
  }
  $("results").innerHTML = r.citations.map(renderEntry).join("");
}

async function check() {
  const text = $("text").value.trim();
  if (text.length < 3) return;
  const deep = $("deep").checked;
  $("go").disabled = true;
  $("status").textContent = deep ? t().checkingDeep : t().checking;
  try {
    const res = await fetch("/api/check", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text, deep }) });
    if (!res.ok) throw new Error(res.status);
    lastResult = await res.json();
    $("status").textContent = "";
    render(lastResult);
    $("report").scrollIntoView({ behavior: "smooth", block: "start" });
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
  $("text").focus();
}));
$("lang").addEventListener("click", () => {
  lang = lang === "ar" ? "en" : "ar";
  try { localStorage.setItem("tathabbut-lang", lang); } catch (e) { /* storage may be blocked */ }
  applyLang();
});
try { const saved = localStorage.getItem("tathabbut-lang"); if (saved === "en" || saved === "ar") lang = saved; } catch (e) { /* ignore */ }
applyLang();
