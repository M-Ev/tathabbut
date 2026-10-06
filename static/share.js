// Share a verse or a hadith as an image and as text. The card is drawn in the browser (canvas) from the source
// fields only, as the copy button is: the Mushaf's text for a verse, the narration's text and the scholars' gradings
// verbatim for a hadith. A hadith the sources do not support is shared only as a correction, with its gradings and
// a red mark. Every card carries a link that checks the text on the site. Nothing is uploaded: the image is made here.
const TathShare = (() => {
  const SITE = "https://3rb-tathabbut.hf.space";
  const C = { navy: "#12183F", ink: "#12183F", ink2: "#3D4370", ink3: "#5F6489", canvas: "#F7F9FB", line: "#D8E1EA",
    turq: "#2EF2C2", ok: "#0B7A5E", okTint: "#E3F7F0", bad: "#A8231A", badTint: "#FCE8E6", warn: "#8F5200", warnTint: "#FFF1DA" };
  const W = 1080, H = 1350, PAD = 80;
  let logo = null;

  function loadLogo() {
    if (logo) return Promise.resolve(logo);
    return new Promise((res) => { const i = new Image(); i.onload = () => { logo = i; res(i); }; i.onerror = () => res(null); i.src = "/static/brand/challenge-logo.png"; });
  }

  function wrap(ctx, text, width) {
    const words = text.split(/\s+/), lines = [];
    let cur = "";
    for (const w of words) {
      const next = cur ? cur + " " + w : w;
      if (ctx.measureText(next).width > width && cur) { lines.push(cur); cur = w; } else cur = next;
    }
    if (cur) lines.push(cur);
    return lines;
  }

  async function draw(card) {
    const cv = document.createElement("canvas");
    cv.width = W; cv.height = H;
    const ctx = cv.getContext("2d");
    const ui = '"Readex Pro", system-ui, sans-serif', qf = '"Amiri Quran", "Amiri", serif';
    try { await Promise.all([document.fonts.load(`500 40px ${ui}`, "تثبت"), document.fonts.load(`48px ${qf}`, "بسم")]); } catch (e) { /* system fonts */ }
    await loadLogo();
    ctx.direction = "rtl";
    // background and band
    ctx.fillStyle = C.canvas; ctx.fillRect(0, 0, W, H);
    ctx.fillStyle = C.navy; ctx.fillRect(0, 0, W, 190);
    ctx.fillStyle = C.turq; ctx.fillRect(W - PAD - 120, 150, 120, 6);
    ctx.fillStyle = "#FFFFFF"; ctx.textAlign = "right"; ctx.font = `700 64px ${ui}`;
    ctx.fillText("تثبّت", W - PAD, 118);
    ctx.font = `400 24px ${ui}`; ctx.fillStyle = "#C9D3EA";
    ctx.fillText("مدقق الاستشهادات الشرعية", W - PAD - 200, 112);
    if (logo) ctx.drawImage(logo, PAD, 50, 173, 90);
    // badge
    const tone = { ok: [C.ok, C.okTint], bad: [C.bad, C.badTint], warn: [C.warn, C.warnTint] }[card.tone || "ok"];
    ctx.font = `600 30px ${ui}`;
    const bw = ctx.measureText(card.badge).width + 56;
    ctx.fillStyle = tone[1]; roundRect(ctx, W - PAD - bw, 240, bw, 60, 30); ctx.fill();
    ctx.fillStyle = tone[0]; ctx.textAlign = "center"; ctx.fillText(card.badge, W - PAD - bw / 2, 281);
    // the text: largest size that fits, then the block (text and source lines) centred between badge and footer
    const quran = card.kind === "quran";
    const areaTop = 340, areaBottom = H - 170;
    ctx.font = `400 28px ${ui}`;
    const src = card.lines.slice(0, 4).flatMap((x) => wrap(ctx, x, W - 2 * PAD).slice(0, 2));
    const srcH = src.length ? 40 + src.length * 42 : 0;
    let size = quran ? 60 : 50, lines, lh;
    for (; size >= 26; size -= 2) {
      ctx.font = quran ? `${size}px ${qf}` : `500 ${size}px ${ui}`;
      lines = wrap(ctx, card.text, W - 2 * PAD - 30);
      lh = size * (quran ? 1.95 : 1.7);
      if (lines.length * lh + srcH <= areaBottom - areaTop) break;
    }
    if (lines.length * lh + srcH > areaBottom - areaTop) { // still too long: cut, and say so
      const keep = Math.max(1, Math.floor((areaBottom - areaTop - srcH) / lh));
      lines = lines.slice(0, keep); lines[keep - 1] += " …";
    }
    const blockH = lines.length * lh + srcH;
    const top = Math.max(areaTop, areaTop + (areaBottom - areaTop - blockH) / 2);
    ctx.fillStyle = tone[0]; ctx.fillRect(W - PAD + 10, top + lh * 0.15, 6, lines.length * lh - lh * 0.2);
    ctx.fillStyle = C.ink; ctx.textAlign = "right";
    lines.forEach((l, i) => ctx.fillText(l, W - PAD - 20, top + (i + 0.8) * lh));
    let y = top + lines.length * lh + 40 + 28;
    ctx.font = `400 28px ${ui}`; ctx.fillStyle = C.ink2;
    for (const l of src) { ctx.fillText(l, W - PAD - 20, y); y += 42; }
    // footer
    ctx.fillStyle = C.line; ctx.fillRect(PAD, H - 140, W - 2 * PAD, 2);
    ctx.font = `500 28px ${ui}`; ctx.fillStyle = C.ink; ctx.textAlign = "right";
    ctx.fillText("تحقّق منه تثبّت · افحص أي نص بنفسك", W - PAD, H - 88);
    ctx.font = `400 26px ${ui}`; ctx.fillStyle = C.ink3; ctx.textAlign = "left"; ctx.direction = "ltr";
    ctx.fillText(SITE.replace("https://", ""), PAD, H - 88);
    ctx.font = `400 20px ${ui}`; ctx.direction = "rtl"; ctx.textAlign = "right";
    ctx.fillText("تحدي الذكاء الاصطناعي في خدمة المحتوى الإسلامي · أداة آلية، ليست مفتيًا", W - PAD, H - 48);
    return cv;
  }

  function roundRect(ctx, x, y, w, h, r) {
    ctx.beginPath(); ctx.moveTo(x + r, y); ctx.arcTo(x + w, y, x + w, y + h, r); ctx.arcTo(x + w, y + h, x, y + h, r);
    ctx.arcTo(x, y + h, x, y, r); ctx.arcTo(x, y, x + w, y, r); ctx.closePath();
  }

  const L = {
    ar: { title: "مشاركة", share: "مشاركة الصورة", download: "تنزيل الصورة", copy: "نسخ النص", copied: "نُسخ", whatsapp: "واتساب", close: "إغلاق", making: "جارٍ تجهيز الصورة…" },
    en: { title: "Share", share: "Share image", download: "Download image", copy: "Copy text", copied: "Copied", whatsapp: "WhatsApp", close: "Close", making: "Preparing the image…" },
  };

  async function open(card, lang) {
    const t = L[lang === "ar" || lang === "ur" ? "ar" : "en"];
    const link = `${SITE}/?q=${encodeURIComponent(card.check || card.text)}`;
    const text = `${card.shareText}\n\n${t === L.ar ? "تحقّق منه تثبّت" : "Checked by Tathabbut"}: ${link}`;
    let dlg = document.getElementById("share-dlg");
    if (!dlg) { dlg = document.createElement("dialog"); dlg.id = "share-dlg"; dlg.className = "share-dlg"; document.body.appendChild(dlg); }
    dlg.innerHTML = `<form method="dialog" class="share-box"><div class="share-head"><b>${t.title}</b><button class="share-x" aria-label="${t.close}">×</button></div>
      <div class="share-prev"><p class="fine">${t.making}</p></div>
      <div class="share-btns"><button type="button" class="primary share-go" hidden>${t.share}</button>
        <a class="pbtn share-dl" download="tathabbut.png" hidden>${t.download}</a>
        <button type="button" class="pbtn share-copy">${t.copy}</button>
        <a class="pbtn" target="_blank" rel="noopener" href="https://wa.me/?text=${encodeURIComponent(text)}">${t.whatsapp}</a></div></form>`;
    dlg.showModal ? dlg.showModal() : dlg.setAttribute("open", "");
    dlg.querySelector(".share-copy").onclick = async (e) => {
      try { await navigator.clipboard.writeText(text); } catch (x) { const ta = document.createElement("textarea"); ta.value = text; document.body.appendChild(ta); ta.select(); try { document.execCommand("copy"); } catch (y) { /* nothing more */ } ta.remove(); }
      e.target.textContent = t.copied;
    };
    const cv = await draw(card);
    const url = cv.toDataURL("image/png");
    const prev = dlg.querySelector(".share-prev");
    prev.innerHTML = `<img src="${url}" alt="" width="540" height="675">`;
    const dl = dlg.querySelector(".share-dl"); dl.href = url; dl.hidden = false;
    const blob = await new Promise((r) => cv.toBlob(r, "image/png"));
    const file = blob ? new File([blob], "tathabbut.png", { type: "image/png" }) : null;
    if (file && navigator.canShare && navigator.canShare({ files: [file] })) {
      const go = dlg.querySelector(".share-go"); go.hidden = false;
      go.onclick = () => navigator.share({ files: [file], text }).catch(() => { /* cancelled */ });
    }
  }

  return { open, draw };
})();
