// Drawn figures for the pillars page: a faceless figure in profile for each position of the prayer, and a front
// diagram for wudu with the part being washed lit. Plain SVG, no images, no faces. The player moves the figure from
// one position to the next (a short animation, like a video of the step), and stops if the reader prefers less motion.
const FIG = (() => {
  const NS = "http://www.w3.org/2000/svg";
  // Joints in a 240×240 box, the figure facing right (toward the qibla); the page mirrors it for right-to-left.
  const P = {
    stand: { head: [120, 38], neck: [120, 64], hip: [120, 128], knee: [121, 172], ankle: [120, 213], toe: [134, 218],
      elbow: [123, 96], wrist: [125, 127], elbow2: [119, 96], wrist2: [118, 127] },
    takbir: { head: [120, 38], neck: [120, 64], hip: [120, 128], knee: [121, 172], ankle: [120, 213], toe: [134, 218],
      elbow: [134, 78], wrist: [130, 46], elbow2: [130, 80], wrist2: [126, 48] },
    qiyam: { head: [120, 38], neck: [120, 64], hip: [120, 128], knee: [121, 172], ankle: [120, 213], toe: [134, 218],
      elbow: [128, 106], wrist: [136, 86], elbow2: [125, 108], wrist2: [133, 88] },
    ruku: { head: [184, 126], neck: [166, 124], hip: [110, 126], knee: [114, 172], ankle: [112, 213], toe: [126, 218],
      elbow: [140, 150], wrist: [121, 170], elbow2: [137, 150], wrist2: [118, 171] },
    sujud: { head: [168, 205], neck: [150, 188], hip: [94, 172], knee: [108, 216], ankle: [70, 204], toe: [77, 219],
      elbow: [140, 194], wrist: [160, 218], elbow2: [136, 195], wrist2: [156, 218] },
    jalsa: { head: [104, 110], neck: [101, 132], hip: [92, 196], knee: [142, 213], ankle: [84, 214], toe: [64, 218],
      elbow: [112, 170], wrist: [138, 198], elbow2: [109, 171], wrist2: [135, 199] },
  };
  P.itidal = P.qiyam;
  P.tashahhud = { ...P.jalsa, wrist: [140, 194] };
  P.salamR = { ...P.jalsa, head: [98, 110], turn: 1 };
  P.salamL = { ...P.jalsa, head: [110, 110], turn: -1 };
  const JOINTS = Object.keys(P.stand);

  const lerp = (a, b, t) => [a[0] + (b[0] - a[0]) * t, a[1] + (b[1] - a[1]) * t];
  const ease = (t) => (t < 0.5 ? 2 * t * t : 1 - Math.pow(-2 * t + 2, 2) / 2);
  const mix = (a, b, t) => { const o = {}; for (const k of JOINTS) o[k] = lerp(a[k], b[k], t); o.turn = t < 0.5 ? a.turn : b.turn; return o; };
  const pts = (...xs) => xs.map((p) => p.map((n) => n.toFixed(1)).join(",")).join(" ");

  function body(p) {
    const far = `<g class="fig-far"><polyline points="${pts(p.hip, p.knee, p.ankle, p.toe)}"/><polyline points="${pts(p.neck, p.elbow2, p.wrist2)}"/></g>`;
    const near = `<g class="fig-near"><polyline points="${pts(p.hip, p.knee, p.ankle, p.toe)}"/><polyline points="${pts(p.neck, p.hip)}" class="fig-torso"/>
      <polyline points="${pts(p.neck, p.elbow, p.wrist)}"/><circle class="fig-hand" cx="${p.wrist[0].toFixed(1)}" cy="${p.wrist[1].toFixed(1)}" r="7"/></g>`;
    const head = `<circle class="fig-head" cx="${p.head[0].toFixed(1)}" cy="${p.head[1].toFixed(1)}" r="16"/>`;
    const turn = p.turn ? `<path class="fig-turn" d="M ${p.head[0] - 22} ${p.head[1] - 26} q 22 -14 44 0" marker-end="url(#fig-arrow)" transform="${p.turn < 0 ? `scale(-1,1) translate(${-2 * p.head[0]},0)` : ""}"/>` : "";
    return far + near + head + turn;
  }

  function stage(kind) {
    const svg = document.createElementNS(NS, "svg");
    svg.setAttribute("viewBox", "0 0 240 240");
    svg.setAttribute("overflow", "visible");
    svg.setAttribute("class", `fig fig-${kind}`);
    svg.setAttribute("aria-hidden", "true");
    return svg;
  }

  const defs = `<defs><marker id="fig-arrow" viewBox="0 0 10 10" refX="6" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
    <path d="M0 0 L10 5 L0 10 z" class="fig-arrowhead"/></marker></defs>`;
  const mat = `<ellipse class="fig-shadow" cx="120" cy="224" rx="92" ry="9"/><rect class="fig-mat" x="40" y="219" width="170" height="7" rx="3"/>`;

  function prayer(pose, rtl) {
    const svg = stage("prayer");
    svg.innerHTML = defs + mat + `<g class="fig-body" ${rtl ? 'transform="translate(240,0) scale(-1,1)"' : ""}>${body(P[pose])}</g>`;
    return svg;
  }

  // Wudu: a front diagram; `part` names what is washed (or wiped), lit in the accent colour, with falling drops.
  const PARTS = {
    hands: `<circle cx="62" cy="152" r="11"/><circle cx="178" cy="152" r="11"/>`,
    mouth: `<ellipse cx="120" cy="60" rx="13" ry="8"/>`,
    face: `<ellipse cx="120" cy="50" rx="19" ry="23"/>`,
    arms: `<path class="ln" d="M74 118 L64 140 L62 154"/><path class="ln" d="M166 118 L176 140 L178 154"/>`,
    head: `<path d="M97 40 Q120 12 143 40 Q120 30 97 40 Z"/><ellipse cx="95" cy="52" rx="5" ry="8"/><ellipse cx="145" cy="52" rx="5" ry="8"/>`,
    feet: `<path d="M94 200 h18 v22 h-22 q-3 0 -1 -5 z"/><path d="M146 200 h-18 v22 h22 q3 0 1 -5 z"/>`,
    none: "",
  };
  const DROPS = {
    hands: [[62, 122], [178, 122]], mouth: [[120, 28]], face: [[104, 10], [136, 10]], arms: [[60, 100], [180, 100]],
    head: [], feet: [[102, 180], [138, 180]], none: [],
  };
  function wudu(part) {
    const svg = stage("wudu");
    const drops = (DROPS[part] || []).map(([x, y], i) =>
      `<path class="drop" style="animation-delay:${i * 0.35}s" d="M${x} ${y} q -5 8 0 12 q 5 -4 0 -12 z"/>`).join("");
    const wipe = part === "head" ? `<path class="wipe" d="M98 28 Q120 2 142 28" />` : "";
    svg.innerHTML = `<g class="fig-front">
        <path class="fb-limb" d="M100 168 L104 220"/><path class="fb-limb" d="M140 168 L136 220"/>
        <path class="fb-limb" d="M88 92 L64 140 L62 150"/><path class="fb-limb" d="M152 92 L176 140 L178 150"/>
        <path class="fb-neck" d="M120 70 L120 84"/>
        <path class="fb-torso" d="M86 84 Q120 76 154 84 L150 172 Q120 180 90 172 Z"/>
        <circle class="fb-head" cx="120" cy="48" r="24"/>
      </g><g class="lit">${PARTS[part] || ""}</g>${wipe}${drops}`;
    return svg;
  }

  // The player: one large figure moving through the steps, a caption, and play / back / next.
  function player(host, steps, opts) {
    const reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    let i = 0, timer = null, anim = null, playing = false;
    host.innerHTML = `<div class="player-stage"></div>
      <div class="player-cap"><span class="player-n"></span><b class="player-t"></b><span class="player-say" lang="ar" dir="rtl"></span></div>
      <div class="player-ctl">
        <button type="button" class="pbtn prev" aria-label="${opts.labels.prev}">‹</button>
        <button type="button" class="pbtn play">${opts.labels.play}</button>
        <button type="button" class="pbtn next" aria-label="${opts.labels.next}">›</button>
        <div class="player-dots" role="tablist"></div>
      </div>`;
    const st = host.querySelector(".player-stage");
    const dots = host.querySelector(".player-dots");
    dots.innerHTML = steps.map((s, k) => `<button type="button" role="tab" class="dot" aria-label="${k + 1}"></button>`).join("");
    const draw = (k, from) => {
      const s = steps[k];
      if (opts.kind === "wudu") {
        st.replaceChildren(wudu(s.part));
      } else {
        const svg = prayer(s.pose, opts.rtl);
        st.replaceChildren(svg);
        const a = from ? P[from] : null, b = P[s.pose];
        if (a && a !== b && !reduce) {
          const g = svg.querySelector(".fig-body");
          const t0 = performance.now(), dur = 900;
          cancelAnimationFrame(anim);
          const tick = (now) => {
            const t = Math.min(1, (now - t0) / dur);
            g.innerHTML = body(mix(a, b, ease(t)));
            if (t < 1) anim = requestAnimationFrame(tick);
          };
          anim = requestAnimationFrame(tick);
        }
      }
      host.querySelector(".player-n").textContent = opts.num(k + 1) + " / " + opts.num(steps.length);
      host.querySelector(".player-t").textContent = s.title;
      host.querySelector(".player-say").textContent = s.say || "";
      dots.querySelectorAll(".dot").forEach((d, n) => d.setAttribute("aria-selected", String(n === k)));
      if (opts.onStep) opts.onStep(k);
    };
    const go = (k) => { const from = steps[i].pose; i = (k + steps.length) % steps.length; draw(i, from); };
    const stop = () => { playing = false; clearInterval(timer); host.querySelector(".play").textContent = opts.labels.play; };
    const play = () => {
      playing = true; host.querySelector(".play").textContent = opts.labels.pause;
      timer = setInterval(() => { if (i === steps.length - 1) stop(); else go(i + 1); }, opts.hold || 3200);
    };
    host.querySelector(".prev").onclick = () => { stop(); go(i - 1); };
    host.querySelector(".next").onclick = () => { stop(); go(i + 1); };
    host.querySelector(".play").onclick = () => { if (playing) stop(); else { if (i === steps.length - 1) go(0); play(); } };
    dots.querySelectorAll(".dot").forEach((d, n) => (d.onclick = () => { stop(); go(n); }));
    draw(0);
    return { show: (k) => { stop(); go(k); } };
  }

  return { prayer, wudu, player };
})();
