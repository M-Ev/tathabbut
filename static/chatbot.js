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
    // A question about a ruling: the two scholars' published fatwas, verbatim with their source; never written by the tool.
    const ld = res.level_d;
    if (ld) {
      const sc = ((ld.fatwas || {}).scholars || []);
      const items = sc.flatMap((x) => (x.fatwas || []).map((f) => ({ who: x.ar, ...f })));
      const fa = ld.answer;
      let h = `<div class="bot-fatwas">` + (fa ? `<section class="fatwa-answer${fa.same_question ? "" : " near"}"><h3 class="fatwas-h">${fa.same_question ? "الجواب من فتاواهم" : "أقرب ما في فتاواهم (في مسألة قريبة من السؤال)"}</h3>
        <blockquote>«${esc(fa.quote)}»</blockquote>
        <p class="fine">${esc(fa.scholar_ar)} · <a href="${esc(fa.url)}" target="_blank" rel="noopener">${esc(fa.title)}</a>${fa.source ? " · " + esc(fa.source) : ""}</p>
        ${fa.same_question ? "" : `<p class="line warn">لم نجد في فتاواهما المنشورة جوابًا عن السؤال نفسه؛ هذه أقرب فتوى إليه، ومسألتها قد تختلف عنه في قيد أو تفصيل. اقرأها كاملة، واسأل أهل العلم أو جهة الإفتاء.</p>`}
        <p class="fine">الجملة منقولة بنصها من الفتوى: اختارها النموذج اللغوي، وتحقّق النظام أنها فيها حرفًا بحرف، ولم يكتب منها شيئًا. اقرأ الفتوى كاملة قبل العمل بها.</p></section>` : "") + `<p class="line warn">${esc(ld.form === "general" ? "في النص سؤال عن حكم شرعي، وتثبّت لا يفتي. هذه فتاوى العالمين الجليلين في مسائل قريبة، بنصها من موقعيهما الرسميين. اختيرت بتقارب الألفاظ لا بالمعنى، فاقرأ الفتوى كاملة وتأكد أنها في مسألتك نفسها:" : "في النص سؤال فتوى شخصية، وتثبّت لا يفتي. هذه فتاوى العالمين الجليلين في مسائل قريبة، بنصها من موقعيهما الرسميين. اختيرت بتقارب الألفاظ لا بالمعنى، فاقرأ الفتوى كاملة وتأكد أنها في مسألتك نفسها:")}</p>`;
      h += items.length ? `<ul class="bot-fatwa-list">` + items.map((f) => `<li><p class="fatwa-title"><a href="${esc(f.url)}" target="_blank" rel="noopener">${esc(f.title)}</a></p>
          <p class="fine">${esc(f.who)}${f.source ? " · " + esc(f.source) : ""}</p>
          ${f.answer ? `<details class="fatwa-full"><summary>عرض الفتوى كاملة</summary><p class="fatwa-text">${esc(f.answer)}</p></details>` : f.opening ? `<p class="fatwa-part">${esc(f.opening)}</p>` : ""}</li>`).join("") + `</ul>`
        : `<p class="fine">لم نجد في فتاواهما المنشورة ما يقارب ألفاظ السؤال.</p>`;
      h += `<p class="fine">ثم: <a href="${esc(ld.body.url)}" target="_blank" rel="noopener">${esc(ld.body.ar)}</a></p></div>`;
      $("seen").innerHTML += h;
    } else if (!res.citations.length) {
      $("seen").innerHTML += `<p class="fine">لم نجد في الإجابة آية ولا حديثًا مستشهدًا به، ولا سؤال فتوى.</p>`;
    }
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
