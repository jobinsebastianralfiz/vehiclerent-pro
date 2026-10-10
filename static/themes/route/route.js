/* Kerala Route · every page. The drawn road down the page, the Kerala scene an SUV drives through, plus the page props:
   tickets flip like boarding passes, stamps thump down, polaroids fan out, the departures board flaps.
   Everything renders complete without GSAP or with reduced motion; motion only adds on top. */
(() => {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ═══════ shared by both roads: the layered strokes, and a car (kicking up dust) that rides a path ═══════ */
  function layers(svg) {
    const q = s => svg.querySelector(s);
    return { svg, plan: q(".rd-plan"), shoulder: q(".rd-shoulder"), asphalt: q(".rd-asphalt"), edge: q(".rd-edge"), inner: q(".rd-inner"),
             center: q(".rd-center"), maskPath: q(".rd-maskpath"), mask: q("mask") };
  }
  function shape(R, d, W, H, sw) {
    R.svg.setAttribute("width", W); R.svg.setAttribute("height", H); R.svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
    [["x", -200], ["y", -200], ["width", W + 400], ["height", H + 400]].forEach(([k, v]) => R.mask.setAttribute(k, v));
    [R.plan, R.shoulder, R.asphalt, R.edge, R.inner, R.center, R.maskPath].forEach(p => p.setAttribute("d", d));
    R.shoulder.setAttribute("stroke-width", sw + 8); R.asphalt.setAttribute("stroke-width", sw);
    R.edge.setAttribute("stroke-width", sw - 3); R.inner.setAttribute("stroke-width", sw - 5);
    R.maskPath.setAttribute("stroke-width", sw + 14);
    return R.asphalt.getTotalLength();
  }
  /* the car is drawn at full size; carScale shrinks it to the road on smaller screens */
  const carScale = W => (W >= 1024 ? .9 : W >= 768 ? .72 : .52);
  function rider(host, path) {
    const car = host.querySelector(".road-car"), puffHost = host.querySelector(".road-puffs");
    const puffs = Array.from({ length: 7 }, () => { const s = document.createElement("span"); s.className = "road-puff"; puffHost.appendChild(s); return s; });
    let last = null, idle = 0, sc = 1;
    const settle = () => puffs.forEach(p => { p.style.opacity = 0; });
    return {
      scale(v) { sc = v; },
      place(l, L) {
        if (l <= 1) { car.classList.remove("on"); settle(); last = l; return; }
        l = Math.max(0, Math.min(L, l));
        const p = path.getPointAtLength(l), a = path.getPointAtLength(Math.min(L, l + 4)), b = path.getPointAtLength(Math.max(0, l - 4));
        car.style.transform = `translate(${p.x}px, ${p.y}px) rotate(${Math.atan2(a.y - b.y, a.x - b.x) * 180 / Math.PI}deg) scale(${sc})`;
        car.classList.add("on");
        /* dust only while moving: thicker the faster it goes, gone a moment after it stops */
        const speed = last == null ? 0 : Math.min(1, Math.abs(l - last) / 3);
        last = l;
        puffs.forEach((pf, k) => {
          const q = path.getPointAtLength(Math.max(0, l - (30 + k * 10) * sc)), s = (12 + k * 6) * sc;
          pf.style.width = pf.style.height = s + "px";
          pf.style.transform = `translate(${q.x - s / 2}px, ${q.y - s / 2}px)`;
          pf.style.opacity = (l > 30 * sc ? speed * .8 * (1 - k / 7) : 0).toFixed(3);
        });
        clearTimeout(idle); idle = setTimeout(settle, 160);
      },
    };
  }

  /* ═══════ the long road: built from .road-gap[data-stop] markers inside #journey, drawn by scroll ═══════ */
  const J = document.getElementById("journey");
  let Road = null;
  if (J && J.querySelector(".road-svg")) Road = (() => {
    const R = layers(J.querySelector(".road-svg")), ride = rider(J, R.asphalt), pinsHost = J.querySelector(".road-pins");
    const stops = [...J.querySelectorAll("[data-stop]")];
    let L = 0, ys = [], N = 0, top = 0, pinLen = [], cur = 0, animated = false;
    /* stops are numbered in page order, so hidden sections never leave a gap in the count */
    let n = 0;
    const pins = stops.map(s => {
      const end = s.hasAttribute("data-stop-end");
      const p = document.createElement("div");
      p.className = "road-pin" + (end ? " end" : "");
      const lbl = document.createElement("span");
      lbl.textContent = end ? s.dataset.stop : String(++n).padStart(2, "0") + " · " + s.dataset.stop;
      p.appendChild(lbl); pinsHost.appendChild(p);
      return p;
    });
    /* path y only ever increases, so binary-search the sampled table */
    function lenAtY(y) {
      if (!N) return 0;
      if (y <= ys[0]) return 0;
      if (y >= ys[N]) return L;
      let lo = 0, hi = N;
      while (hi - lo > 1) { const m = (lo + hi) >> 1; if (ys[m] < y) lo = m; else hi = m; }
      return (lo + (y - ys[lo]) / Math.max(.0001, ys[hi] - ys[lo])) * L / N;
    }
    function render(l) {
      cur = l;
      R.maskPath.style.strokeDashoffset = L - Math.min(L, l > 1 ? l + 24 : 0);
      ride.place(l, L);
      pins.forEach((p, i) => p.classList.toggle("on", l >= pinLen[i] - 2));
    }
    /* The road enters from off the left edge, then zig-zags: at each stop an S-bend carries it across the page
       (the stop's pin sits at the middle of the bend) and it runs straight down the far gutter to the next one. */
    function build() {
      const W = J.clientWidth, H = J.offsetHeight;
      const lg = W >= 1024, md = W >= 768;
      const xa = lg ? 52 : md ? 34 : 20, xb = lg ? W - 52 : md ? W - 34 : 34, R0 = lg ? 120 : md ? 90 : 54;
      const sw = lg ? 22 : md ? 17 : 11;
      top = J.getBoundingClientRect().top + scrollY;
      let side = 0; const X = () => (side ? xb : xa);
      let d = "";
      const pts = [];
      stops.forEach((s, i) => {
        const b = s.getBoundingClientRect(), y = b.top + scrollY - top + b.height / 2;
        /* keep each bend inside its gap so it never runs under the content around it */
        const r = Math.max(24, Math.min(R0, b.height / 2 - 6));
        if (s.hasAttribute("data-stop-end")) {
          const x0 = X(), xm = W / 2;
          d += ` L ${x0} ${y - r} C ${x0} ${y} ${x0} ${y} ${xm} ${y}`;
          pts.push([xm, y]); return;
        }
        const x0 = i ? X() : -60; side ^= 1; const x1 = X();
        d += `${i ? " L" : "M"} ${x0} ${y - r} C ${x0} ${y} ${x1} ${y} ${x1} ${y + r}`;
        pts.push([(x0 + x1) / 2, y]);
      });
      if (!d) return;
      L = shape(R, d, W, H, sw);
      ride.scale(carScale(W));
      N = Math.max(2, Math.ceil(L / 8)); ys = new Float32Array(N + 1);
      for (let i = 0; i <= N; i++) ys[i] = R.asphalt.getPointAtLength(i * L / N).y;
      pts.forEach(([x, y], i) => { pins[i].style.left = x + "px"; pins[i].style.top = y + "px"; });
      pinLen = pts.map(([, y]) => lenAtY(y));
      if (animated) { R.maskPath.style.strokeDasharray = `${L} ${L + 40}`; render(Math.min(cur, L)); }
      else { R.maskPath.style.strokeDasharray = "none"; pins.forEach(p => p.classList.add("on")); }
    }
    const target = () => lenAtY(scrollY + innerHeight * .58 - top);
    return { build, render, target, setAnimated(v) { animated = v; } };
  })();

  if (Road) {
    Road.build();
    addEventListener("load", () => Road.build());
    let t; addEventListener("resize", () => { clearTimeout(t); t = setTimeout(() => Road.build(), 150); });
  }

  /* ═══════ header scene: Kerala from the side (hills, backwater, palms), an SUV driving the road along the front ═══════ */
  const NS = "http://www.w3.org/2000/svg";
  const sv = (tag, attrs, parent) => { const el = document.createElementNS(NS, tag); for (const k in attrs) el.setAttribute(k, attrs[k]); if (parent) parent.appendChild(el); return el; };
  document.querySelectorAll("[data-scene]").forEach(host => {
    let stop = () => {};
    function build() {
      stop();
      host.textContent = "";
      const W = host.clientWidth, H = host.clientHeight;
      if (!W || !H) return;
      const svg = sv("svg", { width: W, height: H, viewBox: `0 0 ${W} ${H}`, "aria-hidden": "true" }, host);
      sv("defs", {}, svg).innerHTML = `
        <linearGradient id="scFar" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#b9d3c9"/><stop offset="1" stop-color="#dfe7dc"/></linearGradient>
        <linearGradient id="scMid" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#7fae9b"/><stop offset="1" stop-color="#b7cfbf"/></linearGradient>
        <linearGradient id="scWater" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#cfe3df"/><stop offset="1" stop-color="#e6efe9"/></linearGradient>
        <linearGradient id="scNear" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#e3cfa6"/><stop offset="1" stop-color="#f1e6cf"/></linearGradient>
        <radialGradient id="scSun"><stop offset="0" stop-color="#ffd58a"/><stop offset=".55" stop-color="#f6b45c" stop-opacity=".9"/><stop offset="1" stop-color="#f6b45c" stop-opacity="0"/></radialGradient>
        <linearGradient id="scBeam" x1="0" x2="1"><stop offset="0" stop-color="#fff1c8" stop-opacity=".7"/><stop offset="1" stop-color="#fff1c8" stop-opacity="0"/></linearGradient>`;
      const sm = W < 640;
      /* ground lines are sums of sines, measured from the bottom so the scene scales with its height */
      const wave = (base, parts) => x => H * base + parts.reduce((y, [a, f, p]) => y + a * H * Math.sin(x * f + p), 0);
      const far = wave(.40, [[.10, .0042, 1], [.05, .011, 2.2], [.02, .027, .3]]);
      const mid = wave(.56, [[.07, .0035, 4], [.035, .010, 1.1]]);
      const waterY = H * .68, near = wave(.80, [[.025, .005, 2.2], [.012, .013, .7]]);
      const fill = f => { let d = `M0 ${H}`; for (let x = 0; x <= W + 8; x += 8) d += `L${x} ${f(x).toFixed(1)}`; return d + `L${W} ${H}Z`; };
      const line = (f, o = 0) => { let d = ""; for (let x = -40; x <= W + 40; x += 8) d += (d ? "L" : "M") + `${x} ${(f(x) + o).toFixed(1)}`; return d; };
      sv("circle", { cx: W * .78, cy: far(W * .78) - H * .02, r: H * .2, fill: "url(#scSun)" }, svg);
      sv("path", { d: fill(far), fill: "url(#scFar)" }, svg);
      sv("path", { d: fill(mid), fill: "url(#scMid)" }, svg);
      sv("rect", { x: 0, y: waterY, width: W, height: H - waterY, fill: "url(#scWater)" }, svg);
      const shimmer = sv("g", { class: "sc-shimmer" }, svg);
      for (let i = 0; i < (sm ? 10 : 22); i++) {
        const x = (i * 137.5) % W, y = waterY + 4 + (i * 7) % (H * .1);
        sv("path", { d: `M${x.toFixed(0)} ${y.toFixed(1)}h${10 + (i % 4) * 6}`, stroke: "#fffaf0", "stroke-width": 1.4, "stroke-linecap": "round", opacity: .8 }, shimmer).style.animationDelay = (-i * .37).toFixed(2) + "s";
      }
      /* coconut palms leaning over the water; fronds sway */
      const palm = (x, y, h, lean, tone) => {
        const g = sv("g", { transform: `translate(${x.toFixed(1)} ${y.toFixed(1)})` }, svg);
        const tx = lean * h * .45;
        sv("path", { d: `M-2.4 0 C${-1.5 + tx * .2} ${-h * .4} ${tx * .7 - 1.6} ${-h * .8} ${tx - 1.2} ${-h} L${tx + 1.2} ${-h} C${tx * .7 + 1.6} ${-h * .8} ${1.5 + tx * .2} ${-h * .4} 2.4 0Z`, fill: tone }, g);
        const crown = sv("g", { class: "sc-crown", transform: `translate(${tx} ${-h})` }, g);
        crown.style.animationDelay = (-x % 5).toFixed(2) + "s";
        [[-160, 1], [-125, .9], [-80, .75], [-35, .95], [5, 1], [-200, .85], [35, .8]].forEach(([a, k]) => {
          const r = a * Math.PI / 180, L = h * .5 * k, ex = Math.cos(r) * L, ey = Math.sin(r) * L + L * .5, cx = Math.cos(r) * L * .55, cy = Math.sin(r) * L * .55 - L * .1;
          const nx = -Math.sin(r) * 3.6, ny = Math.cos(r) * 3.6;
          sv("path", { d: `M0 0 Q${cx + nx} ${cy + ny} ${ex} ${ey} Q${cx - nx} ${cy - ny} 0 0Z`, fill: tone }, crown);
        });
      };
      const ph = H * .34;
      [[.06, 1, -.25], [.09, .75, .3], [.31, .85, .2], [.55, .7, -.3], [.58, 1, .25], [.86, .9, -.2], [.92, .7, .35]].forEach(([fx, k, l], i) => {
        if (sm && i % 2) return;
        palm(W * fx, waterY + 2, ph * k, l, i % 3 ? "#2f6b5e" : "#134e4a");
      });
      sv("path", { d: fill(near), fill: "url(#scNear)" }, svg);
      /* the road along the near bank */
      const road = x => near(x) + H * .07, RW = sm ? 11 : 15;
      sv("path", { d: line(road), fill: "none", stroke: "#2c302a", "stroke-width": RW, "stroke-linecap": "round" }, svg);
      sv("path", { d: line(road, -RW / 2 + 1.5), fill: "none", stroke: "#fffaf0", "stroke-opacity": .5, "stroke-width": 1 }, svg);
      sv("path", { d: line(road), fill: "none", stroke: "#f2c14e", "stroke-width": 1.5, "stroke-dasharray": "12 14" }, svg);
      /* an SUV, side on and facing right; drawn in inches-ish units with the ground at y = 0, then scaled to the road */
      const car = sv("g", {}, svg), body = sv("g", {}, car), FW = 158, BW = 40, WR = 17;
      sv("path", { d: "M192 -46L360 -70L360 -16Z", fill: "url(#scBeam)" }, body);
      const dust = sv("g", { class: "sc-dust" }, body);
      for (let i = 0; i < 7; i++) sv("circle", { cx: 8 - i * 3, cy: -6 - (i % 3) * 4, r: 5 + (i % 3), fill: "#c9b993" }, dust).style.animationDelay = (-i * .13).toFixed(2) + "s";
      sv("path", { fill: "#d9692f", d: "M4 -16L3 -64C3 -70 6 -73 12 -73L112 -74C118 -74 121 -72 124 -68L138 -50L180 -46C186 -45 189 -42 190 -38L193 -26C194 -21 193 -17 189 -16L177 -16C176 -28 168 -38 158 -38C148 -38 140 -28 139 -16L59 -16C58 -28 50 -38 40 -38C30 -38 22 -28 21 -16Z" }, body);
      sv("path", { fill: "#b8521f", d: "M4 -30L190 -30L191 -24L4 -24Z", opacity: .55 }, body);
      sv("path", { fill: "#203330", d: "M16 -66L60 -66L60 -50L14 -50ZM66 -66L106 -66C110 -66 112 -65 114 -62L124 -50L66 -50Z" }, body);
      sv("path", { d: "M70 -64L82 -52M20 -64L30 -52", stroke: "#fff", "stroke-opacity": .35, "stroke-width": 2, "stroke-linecap": "round" }, body);
      sv("path", { d: "M63 -66L63 -20M128 -48L128 -22", stroke: "#b8521f", "stroke-width": 1.4 }, body);
      sv("rect", { x: 10, y: -78, width: 96, height: 4, rx: 2, fill: "#2c302a" }, body);
      sv("rect", { x: 84, y: -44, width: 10, height: 3, rx: 1.5, fill: "#7a3510" }, body);
      sv("rect", { x: 183, y: -42, width: 9, height: 6, rx: 2, fill: "#fff6cc" }, body);
      sv("rect", { x: 2, y: -60, width: 4, height: 14, rx: 2, fill: "#e5352b" }, body);
      const wheels = [BW, FW].map(cx => {
        const w = sv("g", {}, car);
        sv("circle", { cx, cy: -WR, r: WR, fill: "#1b1c17" }, w);
        sv("circle", { cx, cy: -WR, r: 9.5, fill: "#b9ab8c" }, w);
        const spokes = sv("g", {}, w);
        let d = ""; for (let k = 0; k < 5; k++) { const t = k * Math.PI * 2 / 5; d += `M${cx} ${-WR}L${(cx + 9 * Math.cos(t)).toFixed(1)} ${(-WR + 9 * Math.sin(t)).toFixed(1)}`; }
        sv("path", { d, stroke: "#4a4a3e", "stroke-width": 2.2, "stroke-linecap": "round" }, spokes);
        sv("circle", { cx, cy: -WR, r: 3, fill: "#4a4a3e" }, w);
        return { cx, spokes };
      });
      const K = H * (sm ? .0034 : .0036), SPAN = W + 400 * K + 200, SPEED = sm ? 70 : 105;
      const drive = t => {
        const dist = t * SPEED, x = -200 * K - 60 + (dist % SPAN), cx = x + 97 * K;
        const ang = Math.atan2(road(cx + 40) - road(cx - 40), 80) * 180 / Math.PI;
        car.setAttribute("transform", `translate(${x.toFixed(1)} ${(road(cx) + RW * .3).toFixed(1)}) rotate(${ang.toFixed(2)} ${97 * K} 0) scale(${K.toFixed(4)})`);
        body.setAttribute("transform", `translate(0 ${(Math.sin(t * 17) * .7 + Math.sin(t * 5.3) * .5).toFixed(2)})`);
        const spin = (dist / K / WR) * 180 / Math.PI;
        wheels.forEach(w => w.spokes.setAttribute("transform", `rotate(${(spin % 360).toFixed(1)} ${w.cx} ${-WR})`));
      };
      /* parked a little in from the left until it can drive; drives only while the scene is on screen */
      const T0 = (W * .28 + 200 * K + 60) / SPEED;
      drive(T0);
      if (reduce || !("IntersectionObserver" in window)) return;
      let raf = 0, t0 = null, clock = T0;
      const tick = now => { if (t0 === null) t0 = now - clock * 1000; clock = (now - t0) / 1000; drive(clock); raf = requestAnimationFrame(tick); };
      const io = new IntersectionObserver(([e]) => {
        if (e.isIntersecting && !raf) { t0 = null; raf = requestAnimationFrame(tick); }
        if (!e.isIntersecting && raf) { cancelAnimationFrame(raf); raf = 0; }
      });
      io.observe(host);
      stop = () => { io.disconnect(); cancelAnimationFrame(raf); };
    }
    build();
    let rt, lastW = host.clientWidth;
    addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(() => { if (host.clientWidth !== lastW) { lastW = host.clientWidth; build(); } }, 200); });
  });

  /* ═══════ departures board: pad rows to one width, then flap the letters in ═══════ */
  document.querySelectorAll("[data-board]").forEach(host => {
    const rows = [...host.querySelectorAll("[data-flap]")];
    if (!rows.length) return;
    const W = Math.min(16, Math.max(8, ...rows.map(r => r.dataset.flap.length)));
    rows.forEach(r => {
      const cells = [...r.querySelectorAll(".cell")];
      cells.slice(W).forEach(c => c.remove());
      for (let i = cells.length; i < W; i++) { const c = document.createElement("span"); c.className = "cell"; r.appendChild(c); }
    });
    if (reduce || !("IntersectionObserver" in window)) return;
    const A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ";
    rows.forEach(r => r.querySelectorAll(".cell").forEach(c => { c.textContent = ""; }));
    const run = (row, delay) => {
      const tgt = row.dataset.flap.padEnd(W, " ").slice(0, W), cells = [...row.querySelectorAll(".cell")];
      const start = performance.now() + delay;
      const tick = now => {
        let done = true;
        cells.forEach((c, i) => {
          const settle = start + 260 + i * 60;
          if (now < start) { done = false; return; }
          if (now >= settle) { c.textContent = tgt[i].trim(); return; }
          done = false;
          c.textContent = tgt[i] === " " ? "" : A[(Math.random() * 26) | 0];
        });
        if (!done) requestAnimationFrame(tick);
      };
      requestAnimationFrame(tick);
    };
    const io = new IntersectionObserver(es => es.forEach(e => {
      if (!e.isIntersecting) return;
      io.disconnect();
      rows.forEach((r, i) => run(r, i * 110));
    }), { threshold: .3 });
    io.observe(host);
  });

  /* ═══════ motion (GSAP present, motion allowed) ═══════ */
  document.addEventListener("motion:ready", ({ detail: { G, ST } }) => {
    if (Road) {
      Road.setAnimated(true);
      J.classList.add("road-live");
      const proxy = { l: 0 };
      const go = G.quickTo(proxy, "l", { duration: .9, ease: "power3", onUpdate: () => Road.render(proxy.l) });
      ST.addEventListener("refresh", () => { Road.build(); go(Road.target()); });
      ST.create({ trigger: J, start: "top bottom", end: "bottom top", onUpdate: () => go(Road.target()) });
      Road.build(); Road.render(0);
    }

    /* tickets flip over like boarding passes being handed out, a row at a time */
    G.utils.toArray("[data-tickets]").forEach(grid => {
      const tks = grid.querySelectorAll(".tk");
      if (!tks.length) return;
      if (matchMedia("(max-width: 767px)").matches) {
        /* one column: each ticket flips in as it arrives, gently, so none sits half-turned past the screen edge */
        tks.forEach(tk => G.from(tk, { rotationY: -12, y: 36, transformPerspective: 2400, transformOrigin: "0% 50%", opacity: 0, duration: .9, ease: "power3.out", clearProps: "transform",
          scrollTrigger: { trigger: tk, start: "top 92%", once: true } }));
        return;
      }
      G.from(tks, { rotationY: -28, rotation: -2, x: -36, y: 40, transformPerspective: 2400, transformOrigin: "0% 50%", opacity: 0, duration: 1.1, ease: "power3.out", clearProps: "transform", stagger: .1,
        scrollTrigger: { trigger: grid, start: "clamp(top 85%)", once: true } });
    });

    /* passport stamps thump down */
    G.utils.toArray("[data-stamps]").forEach(host => {
      G.from(host.querySelectorAll(".stamp"), { scale: 2.4, opacity: 0, rotation: -35, duration: .75, ease: "back.out(2.2)", stagger: .18,
        scrollTrigger: { trigger: host, start: "clamp(top 70%)", once: true } });
    });

    /* polaroids: dealt as a pile, fan out as they scroll in */
    G.utils.toArray(".pol-stack").forEach(st => {
      G.fromTo(st.querySelectorAll(".pol"), { xPercent: (i) => [40, 0, -40][i] || 0, rotation: (i) => [9, -2, -9][i] || 0, y: 40 },
        { xPercent: 0, rotation: 0, y: 0, ease: "none", scrollTrigger: { trigger: st, start: "top 90%", end: "center 55%", scrub: .6 } });
    });

    /* postcards drop onto the table */
    G.utils.toArray(".pc-in").forEach((el, i) => {
      G.fromTo(el, { opacity: 0, y: 60, rotation: (i % 2 ? 6 : -6) }, { opacity: 1, y: 0, rotation: 0, duration: 1.1, ease: "back.out(1.4)",
        scrollTrigger: { trigger: el, start: "clamp(top 88%)", once: true } });
    });
  });
})();
