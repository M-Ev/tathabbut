// Plan item 25: the chatbot answer as written, beside what its user sees under the default policy.
const $ = (id) => document.getElementById(id);
const esc = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const SAMPLES = {
  bad: "سؤالك عن فضل العلم مهم. قال الله تعالى: ﴿قل هل يستوي الذين يعلمون والذين لا يعلمون﴾ (الزمر: 9). وقال رسول الله ﷺ: «اطلبوا العلم ولو في الصين» رواه البخاري.",
  good: "من أعظم ما يُستشهد به في الإخلاص قول النبي ﷺ: «إنما الأعمال بالنيات» متفق عليه. وقال تعالى: ﴿وَمَآ أُمِرُوٓاْ إِلَّا لِيَعۡبُدُواْ ٱللَّهَ مُخۡلِصِينَ لَهُ ٱلدِّينَ﴾ (البينة: 5).",
  fatwa: "أنا مسافر للدراسة، هل يجوز لي الجمع بين الصلاتين في السفر؟ نعم يجوز لك ذلك.",
};
const ACTION = { pass: ["تُعرض كما هي", "ok"], annotate: ["تُعرض مع ملاحظة", "warn"], block: ["تُوقف", "bad"] };
const TIER = { documented: "مطابق للمصحف", supported: "تؤيده المصادر", not_supported: "لا تؤيده المصادر المعتمدة", verify: "يحتاج مزيدًا من التحقق", refer: "يُحال إلى مختص" };
const RULE = { fatwa_question: "في الإجابة سؤال فتوى شخصية: تُعرض معها فتاوى الشيخين المنشورة وجهة الإفتاء الرسمية.", not_fully_checked: "لم يُفحص كل ما في الإجابة، فلا تمر دون ملاحظة." };

function marked(text, cits, cls) {
  // Mark each citation at its span, never changing a character of the answer.
  let h = "", at = 0;
  for (const c of [...cits].sort((a, b) => a.span[0] - b.span[0])) {
    const [s, e] = c.span;
    if (s < at) continue;
    h += esc(text.slice(at, s)) + `<mark class="cite ${cls(c)}" data-n="${c.id}">${esc(text.slice(s, e))}</mark>`;
    at = e;
  }
  return h + esc(text.slice(at));
}
const clsOf = (c) => ({ documented: "ok", supported: "ok", verify: "warn", refer: "warn", not_supported: "bad" }[c.tier] || "");

async function go() {
  const text = $("answer").value.trim();
  if (text.length < 3) return;
  $("go").disabled = true;
  $("status").textContent = "جارٍ الفحص…";
  try {
    const r = await fetch("/api/check", { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ text }) });
    if (!r.ok) throw new Error(r.status);
    const res = await r.json();
    const d = res.decision;
    $("status").textContent = "";
    $("out").hidden = false;
    $("orig").innerHTML = esc(text);
    const [label, cls] = ACTION[d.action];
    $("action").className = `tier ${cls}`;
    $("action").textContent = label;
    if (d.action === "block") {
      $("seen").innerHTML = `<p class="line bad">لم تُعرض هذه الإجابة لأن فيها استشهادًا لم يثبت في المصادر المعتمدة.</p>`;
    } else {
      $("seen").innerHTML = marked(text, res.citations, clsOf);
    }
    const byId = Object.fromEntries(res.citations.map((c) => [c.id, c]));
    $("notes").innerHTML = d.reasons.map((x) => {
      if (x.citation == null) return `<li>${esc(RULE[x.rule] || x.rule)}</li>`;
      const c = byId[x.citation];
      return `<li>«${esc(c.quote)}» · ${esc(TIER[c.tier] || c.tier)}${x.action === "block" ? " · سبب الإيقاف" : ""}</li>`;
    }).join("") + res.citations.filter((c) => !d.reasons.some((x) => x.citation === c.id))
      .map((c) => `<li>«${esc(c.quote)}» · ${esc(TIER[c.tier] || c.tier)}</li>`).join("");
    $("disc").textContent = `${res.disclaimer.ar} السياسة: ${d.policy.name} (${d.policy.version}).`;
    $("out").scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (e) {
    $("status").textContent = "تعذّر الفحص الآن. لا تُعرض الإجابة على أنها مفحوصة.";
  } finally {
    $("go").disabled = false;
  }
}
$("go").addEventListener("click", go);
document.querySelectorAll("[data-sample]").forEach((b) => b.addEventListener("click", () => { $("answer").value = SAMPLES[b.dataset.sample]; $("answer").focus(); }));
