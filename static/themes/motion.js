/* VehicleRent · motion layer (GSAP 3 + ScrollTrigger), ported from the AGC "Reels" helpers.
   Works off data attributes so any public template can opt in, plus a few safe automatic
   hooks (section headings, kickers, vehicle cards, big images) so every page gets motion.

   data-intro="N"            hero element, plays in order N on load (data-intro-kind="split|media|fade")
   data-split[="chars"]      heading rolls up word by word (or letter by letter) when scrolled to
   data-deal                 children are dealt in like cards
   data-tilt                 3D tilt + glare toward the cursor
   data-slot                 numbers spin like a slot machine when scrolled to ("120+", "15")
   data-cycle="a|b|c"        word reel that rolls through the words
   data-magnetic             button leans toward the cursor
   data-marquee              infinite marquee (CSS), contents duplicated here
   data-hscroll              section pinned while its .m-htrack scrolls sideways (desktop)
   data-scrub-text           words light up as you scroll through
   data-parallax="80"        drifts +/- N px across the viewport
   data-reveal               fades up when scrolled to
*/
(() => {
  const html = document.documentElement;
  const G = window.gsap, ST = window.ScrollTrigger;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const fine = matchMedia("(pointer: fine)").matches;
  const $$ = (s, r = document) => [...r.querySelectorAll(s)];
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));

  /* marquees duplicate their track so the loop is seamless; needed even without GSAP */
  function marquees() {
    $$("[data-marquee]").forEach(m => {
      const t = m.querySelector(".m-marquee-track");
      if (!t || m._dup) return; m._dup = 1;
      const c = t.cloneNode(true); c.setAttribute("aria-hidden", "true");
      $$("a, button", c).forEach(a => a.tabIndex = -1);
      m.appendChild(c);
    });
  }

  const ready = () => { window.__motionReady = 1; };
  if (!G || !ST || reduce) {
    html.classList.remove("motion"); ready();
    const boot0 = () => marquees();
    if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot0); else boot0();
    return;
  }
  G.registerPlugin(ST);
  G.defaults({ ease: "expo.out", duration: 1 });

  /* ---------- text splitting ---------- */
  function split(el, mode = "words") {
    if (el._split) return el._split;
    const out = [];
    const mk = (cls, txt) => { const s = document.createElement("span"); s.className = cls; if (txt != null) s.textContent = txt; return s; };
    const walk = node => [...node.childNodes].forEach(n => {
      if (n.nodeType === 3) {
        const frag = document.createDocumentFragment();
        n.textContent.split(/(\s+)/).forEach(p => {
          if (!p) return;
          if (/^\s+$/.test(p)) { frag.appendChild(document.createTextNode(" ")); return; }
          const line = mk("m-line");
          if (mode === "chars") { [...p].forEach(ch => { const w = mk("m-word", ch); line.appendChild(w); out.push(w); }); }
          else { const w = mk("m-word", p); line.appendChild(w); out.push(w); }
          frag.appendChild(line);
        });
        n.replaceWith(frag);
      } else if (n.nodeType === 1 && !n.matches("br, svg, img, .slot, .m-reel, .material-symbols-outlined, [data-slot], [data-cycle]")) walk(n);
    });
    walk(el);
    el._split = out;
    return out;
  }
  const rollUp = (words, o = {}) => G.from(words, { yPercent: 115, rotation: o.rot ?? 5, transformOrigin: "0% 100%", duration: o.dur || 1.15, stagger: o.stagger ?? .055, delay: o.delay || 0, ease: "expo.out", scrollTrigger: o.st });

  /* ---------- slot-machine digits (from AGC Reels) ---------- */
  const DIG = "012345678901234567890123456789";
  function slotSet(el, str) {
    str = String(str); el.classList.add("slot"); el.dataset.v = str;
    el.innerHTML = `<span class="sr-only">${esc(str)}</span>` + [...str].map(ch => /\d/.test(ch)
      ? `<span class="sc" aria-hidden="true"><span class="ss">${[...DIG].map(d => `<span>${d}</span>`).join("")}</span></span>`
      : `<span class="sx" aria-hidden="true">${esc(ch)}</span>`).join("");
    const ds = str.replace(/\D/g, "");
    $$(".ss", el).forEach((s, i) => G.set(s, { yPercent: -(20 + +ds[i]) / 30 * 100 }));
  }
  function slotTo(el, str, o = {}) {
    str = String(str);
    const prev = o.from != null ? String(o.from) : (el.dataset.v || "");
    slotSet(el, str);
    const ds = str.replace(/\D/g, ""), ps = prev.replace(/\D/g, "").padStart(ds.length, "0").slice(-ds.length);
    $$(".ss", el).forEach((s, i) => G.fromTo(s, { yPercent: -(+ps[i]) / 30 * 100 },
      { yPercent: -(20 + +ds[i]) / 30 * 100, duration: (o.dur || 1.2) + i * .2, delay: (o.delay || 0) + i * .06, ease: "back.out(1.15)" }));
  }

  /* ---------- word reel ---------- */
  function roll(el, text) {
    const cur = el.lastElementChild;
    if (cur && cur.textContent === text) return;
    [...el.children].slice(0, -1).forEach(x => { G.killTweensOf(x); x.remove(); });
    const n = document.createElement("span"); n.textContent = text; el.appendChild(n);
    if (cur) { G.killTweensOf(cur); G.to(cur, { yPercent: -115, duration: .4, ease: "power3.in", onComplete: () => cur.remove() }); }
    G.fromTo(n, { yPercent: 115 }, { yPercent: 0, duration: .75, ease: "back.out(1.7)", delay: .14 });
  }
  function cycles() {
    $$("[data-cycle]").forEach(el => {
      const words = el.dataset.cycle.split("|").map(s => s.trim()).filter(Boolean);
      if (words.length < 2) return;
      el.classList.add("m-reel");
      el.innerHTML = `<span>${esc(words[0])}</span>`;
      el.setAttribute("aria-label", words.join(", "));
      let i = 0;
      const every = +(el.dataset.every || 2.4);
      const step = () => { i = (i + 1) % words.length; roll(el, words[i]); G.delayedCall(every, step); };
      G.delayedCall(every + (+(el.dataset.wait || 0)), step);
    });
  }

  /* ---------- hero intro ---------- */
  function intro() {
    const els = $$("[data-intro]").sort((a, b) => (+a.dataset.intro || 0) - (+b.dataset.intro || 0));
    if (!els.length) return;
    const tl = G.timeline({ delay: .1 });
    els.forEach(el => {
      const kind = el.dataset.introKind || "fade";
      const at = (+el.dataset.intro || 0) * .12;
      tl.set(el, { opacity: 1 }, at);
      if (kind === "split") tl.from(split(el), { yPercent: 118, rotation: 6, transformOrigin: "0% 100%", duration: 1.3, stagger: .07 }, at);
      else if (kind === "media") {
        tl.fromTo(el, { clipPath: "inset(18% 14% 18% 14% round 48px)" }, { clipPath: "inset(0% 0% 0% 0% round 24px)", duration: 1.6, ease: "expo.inOut" }, at);
        const img = el.querySelector("img, .m-runway");
        if (img) tl.from(img, { scale: 1.35, duration: 2.2, ease: "expo.out" }, at);
      } else if (kind === "pop") tl.fromTo(el, { scale: .6, y: 30, opacity: 0 }, { scale: 1, y: 0, opacity: 1, duration: 1, ease: "back.out(1.8)" }, at);
      else tl.fromTo(el, { y: 36, opacity: 0 }, { y: 0, opacity: 1, duration: 1.1 }, at);
    });
    $$("[data-intro] [data-slot]").forEach((s, i) => tl.add(() => slotTo(s, s.dataset.slotValue || s.textContent.trim(), { from: "0", delay: i * .12 }), .7));
  }

  /* ---------- headings, kickers, copy ---------- */
  function headings() {
    const hs = new Set($$("[data-split]"));
    $$("main h1, main h2").forEach(h => { if (!h.closest("[data-intro], [data-no-split]") && !h.hasAttribute("data-intro")) hs.add(h); });
    hs.forEach(h => {
      if (h.closest("[data-intro]")) return;
      const words = split(h, h.dataset.split === "chars" ? "chars" : "words");
      if (!words.length) return;
      rollUp(words, { stagger: h.dataset.split === "chars" ? .025 : .055, st: { trigger: h, start: "top 88%", once: true } });
    });
    $$("main .label-tiny").forEach(k => {
      const nx = k.nextElementSibling;
      if (!nx || !nx.matches("h1, h2") || k.closest("[data-intro]")) return;
      G.from(k, { opacity: 0, letterSpacing: ".6em", duration: 1.4, scrollTrigger: { trigger: k, start: "top 90%", once: true } });
    });
    $$("main h1 + p, main h2 + p, [data-reveal]").forEach(p => {
      if (p.closest("[data-intro]")) return;
      G.from(p, { y: 30, opacity: 0, duration: 1.1, delay: .15, scrollTrigger: { trigger: p, start: "top 92%", once: true } });
    });
  }

  /* ---------- cards dealt from a deck ---------- */
  function deal() {
    const groups = new Map();
    $$("[data-deal]").forEach(g => groups.set(g, [...g.children]));
    $$(".vehicle-card").forEach(c => { const g = c.parentElement.closest("[data-deal]") ? null : c.parentElement; if (g) { if (!groups.has(g)) groups.set(g, []); groups.get(g).push(c); } });
    groups.forEach(items => {
      if (!items.length) return;
      items.forEach(c => { c._tr = c.style.transition; c.style.transition = "none"; });
      G.set(items, { opacity: 0, y: 90, rotation: (i) => (i % 2 ? 3 : -3), scale: .92, transformOrigin: "50% 100%" });
      ST.batch(items, {
        start: "top 92%", once: true,
        onEnter: batch => G.to(batch, { opacity: 1, y: 0, rotation: 0, scale: 1, duration: 1.1, ease: "back.out(1.3)", stagger: .09, overwrite: true,
          onComplete() { batch.forEach(c => { G.set(c, { clearProps: "transform,opacity" }); c.style.transition = c._tr || ""; }); } })
      });
    });
  }

  /* ---------- tilt + glare ---------- */
  function tilt() {
    if (!fine) return;
    $$("[data-tilt], .vehicle-card").forEach(el => {
      if (el._tilt) return; el._tilt = 1;
      el.classList.add("m-glare");
      const q = p => G.quickTo(el, p, { duration: .7, ease: "power3" });
      const rx = q("rotationX"), ry = q("rotationY");
      let r = null, active = false;
      el.addEventListener("pointerenter", () => { r = el.getBoundingClientRect(); active = true; el.style.transition = "box-shadow .4s"; G.set(el, { transformPerspective: 1000 }); });
      el.addEventListener("pointermove", e => {
        if (!active) return;
        if (!r) r = el.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - .5, y = (e.clientY - r.top) / r.height - .5;
        const k = +(el.dataset.tilt || 1);
        ry(x * 10 * k); rx(-y * 8 * k);
        el.style.setProperty("--gx", (x + .5) * 100 + "%"); el.style.setProperty("--gy", (y + .5) * 100 + "%");
      });
      el.addEventListener("pointerleave", () => { r = null; active = false; rx(0); ry(0); });
    });
  }

  /* ---------- magnetic buttons ---------- */
  function magnetic() {
    const btns = new Set($$("[data-magnetic]"));
    $$("main a.rounded-full.bg-primary-container, main a.rounded-full.bg-primary, main button.rounded-full.bg-primary-container").forEach(b => btns.add(b));
    btns.forEach(b => {
      b.classList.add("m-shine");
      if (!fine) return;
      const x = G.quickTo(b, "x", { duration: .6, ease: "power3" }), y = G.quickTo(b, "y", { duration: .6, ease: "power3" });
      b.addEventListener("pointermove", e => { const r = b.getBoundingClientRect(); x((e.clientX - r.left - r.width / 2) * .25); y((e.clientY - r.top - r.height / 2) * .35); });
      b.addEventListener("pointerleave", () => { x(0); y(0); });
    });
  }

  /* ---------- slots on scroll ---------- */
  function slots() {
    $$("[data-slot]").forEach(s => {
      if (s.closest("[data-intro]")) return;
      const v = s.dataset.slotValue || s.textContent.trim();
      ST.create({ trigger: s, start: "top 90%", once: true, onEnter: () => slotTo(s, v, { from: "0" }) });
    });
  }

  /* ---------- images: parallax zoom inside their frame ---------- */
  function images() {
    $$("main img").forEach(img => {
      if (img.closest(".vehicle-card, [data-intro], [data-no-parallax], [data-hscroll], .m-runway, nav, footer")) return;
      const box = img.parentElement;
      if (!box || getComputedStyle(box).overflow !== "hidden") return;
      const r = box.getBoundingClientRect();
      if (r.height < 300 || r.width < innerWidth * .3) return;
      G.fromTo(img, { scale: 1.18, yPercent: -5 }, { scale: 1.02, yPercent: 5, ease: "none", scrollTrigger: { trigger: box, start: "top bottom", end: "bottom top", scrub: true } });
      G.fromTo(box, { clipPath: "inset(10% 6% 10% 6% round 48px)" }, { clipPath: "inset(0% 0% 0% 0% round 0px)", ease: "expo.out", duration: 1.6, scrollTrigger: { trigger: box, start: "top 85%", once: true }, clearProps: "clipPath" });
    });
    $$("[data-parallax]").forEach(el => {
      const d = +el.dataset.parallax || 60;
      G.fromTo(el, { y: -d }, { y: d, ease: "none", scrollTrigger: { trigger: el, start: "top bottom", end: "bottom top", scrub: true } });
    });
  }

  /* ---------- pinned sideways track ---------- */
  function hscroll() {
    const mm = G.matchMedia();
    $$("[data-hscroll]").forEach(sec => {
      const track = sec.querySelector(".m-htrack"); if (!track) return;
      const count = sec.querySelector("[data-hscroll-count]");
      const items = [...track.children];
      mm.add("(min-width: 1024px)", () => {
        track.style.overflow = "visible";
        const dist = () => Math.max(0, track.scrollWidth - track.clientWidth);
        let last = -1;
        const tw = G.to(track, { x: () => -dist(), ease: "none", scrollTrigger: {
          trigger: sec, start: "top top", end: () => "+=" + dist(), pin: true, scrub: .8, invalidateOnRefresh: true, anticipatePin: 1,
          onUpdate(self) {
            if (!count) return;
            const i = Math.min(items.length - 1, Math.round(self.progress * (items.length - 1)));
            if (i !== last) { slotTo(count, String(i + 1).padStart(2, "0"), { from: String(last + 1 < 1 ? 1 : last + 1).padStart(2, "0"), dur: .6 }); last = i; }
          } } });
        items.forEach(it => {
          const im = it.querySelector("img");
          if (im) G.fromTo(im, { xPercent: -10, scale: 1.15 }, { xPercent: 10, scale: 1.15, ease: "none", scrollTrigger: { trigger: it, containerAnimation: tw, start: "left right", end: "right left", scrub: true } });
        });
        return () => { track.style.overflow = ""; };
      });
    });
  }

  /* ---------- scrubbed words ---------- */
  function scrubText() {
    $$("[data-scrub-text]").forEach(el => {
      const words = split(el);
      words.forEach(w => w.classList.add("m-scrub-word"));
      G.to(words, { opacity: 1, stagger: .1, ease: "none", scrollTrigger: { trigger: el, start: "top 82%", end: "bottom 50%", scrub: true } });
    });
  }

  /* ---------- chrome: progress bar, nav, mobile menu ---------- */
  function chrome() {
    const bar = document.createElement("div"); bar.className = "m-progress"; bar.setAttribute("aria-hidden", "true");
    document.body.appendChild(bar);
    ST.create({ start: 0, end: "max", onUpdate: s => { bar.style.transform = `scaleX(${s.progress})`; } });
    const nav = document.querySelector("nav.m-nav");
    if (nav) {
      const f = () => nav.classList.toggle("is-solid", scrollY > 20); f();
      addEventListener("scroll", f, { passive: true });
      G.from(nav, { yPercent: -100, duration: 1, ease: "expo.out", delay: .05 });
    }
    addEventListener("toggle-mobile-menu", () => requestAnimationFrame(() => requestAnimationFrame(() => {
      const m = document.getElementById("mobile-menu");
      if (!m || getComputedStyle(m).display === "none") return;
      G.fromTo(m, { clipPath: "inset(0 0 100% 0)" }, { clipPath: "inset(0 0 0% 0)", duration: .6, ease: "expo.out" });
      G.fromTo(m.querySelectorAll("a"), { y: 24, opacity: 0 }, { y: 0, opacity: 1, duration: .6, stagger: .035, ease: "back.out(1.6)", delay: .08 });
    })));
  }

  const boot = () => {
    marquees(); chrome(); intro(); cycles(); headings(); deal(); tilt(); magnetic(); slots(); images(); hscroll(); scrubText();
    ready();
    addEventListener("load", () => ST.refresh());
    document.dispatchEvent(new CustomEvent("motion:ready", { detail: { G, ST, split, slotTo, roll, rollUp } }));
  };
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot); else boot();
  document.addEventListener("visibilitychange", () => { if (document.hidden) G.globalTimeline.pause(); else G.globalTimeline.resume(); });
  window.Motion = { split, slotTo, roll, rollUp };
})();
