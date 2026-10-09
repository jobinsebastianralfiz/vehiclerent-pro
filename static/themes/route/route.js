/* Kerala Route · inner pages. The drawn road (same engine as the home page), plus the page props:
   tickets flip like boarding passes, stamps thump down, polaroids fan out, the departures board flaps.
   Everything renders complete without GSAP or with reduced motion; motion only adds on top. */
(() => {
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ═══════ the road: built from .road-gap[data-stop] markers inside #journey ═══════ */
  const J = document.getElementById("journey");
  let Road = null;
  if (J && J.querySelector(".road-svg")) Road = (() => {
    const svg = J.querySelector(".road-svg");
    const q = s => svg.querySelector(s);
    const plan = q(".rd-plan"), shoulder = q(".rd-shoulder"), asphalt = q(".rd-asphalt"), center = q(".rd-center"), maskPath = q(".rd-maskpath"), mask = q("mask");
    const car = J.querySelector(".road-car"), pinsHost = J.querySelector(".road-pins");
    const stops = [...J.querySelectorAll("[data-stop]")];
    let L = 0, ys = [], N = 0, top = 0, pinLen = [], cur = 0, animated = false;
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
      maskPath.style.strokeDashoffset = L - l;
      if (l <= 1) car.classList.remove("on");
      else {
        const p = asphalt.getPointAtLength(l), a2 = asphalt.getPointAtLength(Math.min(L, l + 3)), b = asphalt.getPointAtLength(Math.max(0, l - 3));
        car.style.transform = `translate(${p.x}px, ${p.y}px) rotate(${Math.atan2(a2.y - b.y, a2.x - b.x) * 180 / Math.PI}deg)`;
        car.classList.add("on");
      }
      pins.forEach((p, i) => p.classList.toggle("on", l >= pinLen[i] - 2));
    }
    function build() {
      const W = J.clientWidth, H = J.offsetHeight;
      const lg = W >= 1024, md = W >= 768;
      const xa = lg ? 52 : md ? 34 : 20, xb = lg ? W - 52 : md ? W - 34 : 34, r = lg ? 82 : md ? 64 : 44;
      const sw = lg ? 16 : md ? 13 : 9;
      top = J.getBoundingClientRect().top + scrollY;
      svg.setAttribute("width", W); svg.setAttribute("height", H); svg.setAttribute("viewBox", `0 0 ${W} ${H}`);
      ["x", "y"].forEach(k => mask.setAttribute(k, 0)); mask.setAttribute("width", W); mask.setAttribute("height", H);
      let side = 0; const X = () => (side ? xb : xa);
      let d = `M ${xa} 0`;
      const pts = [];
      stops.forEach(s => {
        const b = s.getBoundingClientRect(), y = b.top + scrollY - top + b.height / 2;
        if (s.hasAttribute("data-stop-end")) {
          const x0 = X(), xm = W / 2;
          d += ` L ${x0} ${y - r} C ${x0} ${y} ${x0} ${y} ${xm} ${y}`;
          pts.push([xm, y]); return;
        }
        const x0 = X(); side ^= 1; const x1 = X();
        d += ` L ${x0} ${y - r} C ${x0} ${y} ${x1} ${y} ${x1} ${y + r}`;
        pts.push([(x0 + x1) / 2, y]);
      });
      [plan, shoulder, asphalt, center, maskPath].forEach(p => p.setAttribute("d", d));
      shoulder.setAttribute("stroke-width", sw + 8); asphalt.setAttribute("stroke-width", sw); maskPath.setAttribute("stroke-width", sw + 14);
      L = asphalt.getTotalLength();
      N = Math.max(2, Math.ceil(L / 8)); ys = new Float32Array(N + 1);
      for (let i = 0; i <= N; i++) ys[i] = asphalt.getPointAtLength(i * L / N).y;
      pts.forEach(([x, y], i) => { pins[i].style.left = x + "px"; pins[i].style.top = y + "px"; });
      pinLen = pts.map(([, y]) => lenAtY(y));
      if (animated) { maskPath.style.strokeDasharray = `${L} ${L + 40}`; render(Math.min(cur, L)); }
      else { maskPath.style.strokeDasharray = "none"; pins.forEach(p => p.classList.add("on")); }
    }
    const target = () => lenAtY(scrollY + innerHeight * .58 - top);
    return { build, render, target, setAnimated(v) { animated = v; } };
  })();

  if (Road) {
    Road.build();
    addEventListener("load", () => Road.build());
    let t; addEventListener("resize", () => { clearTimeout(t); t = setTimeout(() => Road.build(), 150); });
  }

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
      const go = G.quickTo(proxy, "l", { duration: .6, ease: "power3", onUpdate: () => Road.render(proxy.l) });
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
