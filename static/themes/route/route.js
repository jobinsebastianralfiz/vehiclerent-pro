/* Kerala Route · every page. The drawn road down the page, the header road a car drives along, plus the page props:
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
  function rider(host, path, keepVisible) {
    const car = host.querySelector(".road-car"), puffHost = host.querySelector(".road-puffs");
    const puffs = Array.from({ length: 7 }, () => { const s = document.createElement("span"); s.className = "road-puff"; puffHost.appendChild(s); return s; });
    let last = null, idle = 0, sc = 1;
    const settle = () => puffs.forEach(p => { p.style.opacity = 0; });
    return {
      scale(v) { sc = v; },
      place(l, L) {
        if (l <= 1 && !keepVisible) { car.classList.remove("on"); settle(); last = l; return; }
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

  /* ═══════ header roads: the car drives from the start pin to the destination once the strip is in view ═══════ */
  document.querySelectorAll("[data-drive]").forEach(host => {
    const R = layers(host.querySelector(".road-svg")), ride = rider(host, R.asphalt, true);
    const [pinA, pinB] = host.querySelectorAll(".r-drive-pin");
    let L = 0, stopAt = 0, t = 0;
    function render(v) {
      t = v;
      const l = v * stopAt, reveal = v >= 1 ? L : Math.min(L, l + 26);
      R.maskPath.style.strokeDashoffset = L - reveal;
      ride.place(l, L);
      host.classList.toggle("arrived", v >= 1);
    }
    function build() {
      const W = host.clientWidth, H = host.offsetHeight;
      const lg = W >= 1024, md = W >= 640, pad = lg ? 10 : 8, sw = lg ? 18 : md ? 14 : 10;
      const sx = x => (pad + x / 1000 * (W - 2 * pad)).toFixed(1), y = v => (v / 72 * H).toFixed(1);
      const d = `M ${sx(0)} ${y(44)} C ${sx(160)} ${y(44)}, ${sx(220)} ${y(20)}, ${sx(380)} ${y(26)} S ${sx(640)} ${y(54)}, ${sx(800)} ${y(40)} S ${sx(940)} ${y(26)}, ${sx(1000)} ${y(32)}`;
      L = shape(R, d, W, H, sw);
      R.maskPath.style.strokeDasharray = `${L} ${L + 40}`;
      const sc = carScale(W) * .9;
      ride.scale(sc);
      stopAt = L - 44 * sc;
      [[pinA, 0], [pinB, L]].forEach(([el, l]) => { const p = R.asphalt.getPointAtLength(l); el.style.left = p.x + "px"; el.style.top = p.y + "px"; });
      render(t);
    }
    build();
    let rt; addEventListener("resize", () => { clearTimeout(rt); rt = setTimeout(build, 150); });
    if (reduce || !("IntersectionObserver" in window)) { render(1); return; }
    const ease = x => (x < .5 ? 4 * x * x * x : 1 - Math.pow(-2 * x + 2, 3) / 2);
    const io = new IntersectionObserver(es => {
      if (!es[0].isIntersecting) return;
      io.disconnect();
      const t0 = performance.now() + 450, dur = 3200;
      const tick = now => { const k = Math.max(0, Math.min(1, (now - t0) / dur)); render(ease(k)); if (k < 1) requestAnimationFrame(tick); };
      requestAnimationFrame(tick);
    }, { threshold: .4 });
    io.observe(host);
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
