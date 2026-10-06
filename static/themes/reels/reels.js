/* VehicleRent · Showroom Reels theme: hero car reel, fleet chips shuffle, wedding photo reel, mobile sheet.
   Markup is server-rendered; vehicle data for the hero comes from data-* attributes on the thumbnails.
   Runs on DOMContentLoaded (after motion.js has booted), works without GSAP and animates when it is there. */
document.addEventListener("DOMContentLoaded", () => {
  const $ = id => document.getElementById(id);
  const G = window.gsap, ST = window.ScrollTrigger, M = window.Motion;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const anim = !!(G && ST && M && !reduce);
  const esc = s => String(s).replace(/[&<>"]/g, c => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c]));
  const tones = el => { const cs = getComputedStyle(el); return [cs.getPropertyValue("--c0").trim(), cs.getPropertyValue("--c1").trim()]; };

  /* ---------- mobile sheet ---------- */
  const sheet = $("sheet"), btn = $("menuBtn"), close = $("sheetClose");
  if (sheet && btn && close) {
    const open = on => {
      sheet.classList.toggle("open", on); btn.setAttribute("aria-expanded", on);
      document.documentElement.style.overflow = on ? "hidden" : "";
      if (on) {
        close.focus();
        if (anim) {
          G.fromTo(sheet, { clipPath: "inset(0 0 100% 0 round 0 0 40px 40px)" }, { clipPath: "inset(0 0 0% 0 round 0 0 0px 0px)", duration: .6, ease: "expo.out" });
          G.fromTo(sheet.querySelectorAll("nav a > span, nav a small"), { yPercent: 120 }, { yPercent: 0, duration: .7, ease: "back.out(1.4)", stagger: .045, delay: .1 });
        }
      } else btn.focus();
    };
    btn.addEventListener("click", () => open(true));
    close.addEventListener("click", () => open(false));
    sheet.querySelectorAll("a").forEach(a => a.addEventListener("click", () => open(false)));
    addEventListener("keydown", e => { if (e.key === "Escape" && sheet.classList.contains("open")) open(false); });
  }

  /* ---------- hero reel through the featured fleet ---------- */
  const thumbWrap = $("thumbs"), stack = $("heroStack"), tileEl = $("heroTile"), reelEl = $("heroReel"), reelLine = $("reelLine");
  const copy = document.querySelector(".hero-copy");
  /* long car names: shrink the reel line so it never overflows the column */
  const fit = () => {
    if (!reelLine || !reelEl || !copy) return;
    reelLine.style.fontSize = "";
    const span = reelEl.lastElementChild; if (!span) return;
    const w = span.scrollWidth, room = copy.clientWidth;
    if (w > room) reelLine.style.fontSize = Math.max(.42, room / w * .98) + "em";
  };
  fit(); addEventListener("resize", fit);
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(fit);

  if (thumbWrap && stack && tileEl && reelEl) {
    const thumbs = [...thumbWrap.children];
    const HERO = thumbs.map(t => ({ ...t.dataset, tone: tones(t) }));
    const DWELL = 3400;
    thumbWrap.style.setProperty("--dwell", DWELL / 1000 + "s");
    let cur = 0, timer = null, running = false, hovering = false;
    const media = c => c.img ? `<img src="${esc(c.img)}" alt="${esc(c.full)}">` : `<span class="ph-empty"><span class="material-symbols-outlined">${esc(c.icon)}</span></span>`;
    const node = c => { const d = document.createElement("div"); d.innerHTML = media(c); return d.firstElementChild; };
    function setPrice(c, prev) {
      const wrap = $("heroPriceWrap"); if (!wrap) return;
      if (!c.price) { wrap.textContent = "Price on request"; return; }
      if (!$("heroPrice")) wrap.innerHTML = `from <b>₹<span id="heroPrice"></span></b> a <span id="heroLabel"></span>`;
      $("heroLabel").textContent = c.label;
      if (anim && prev && prev.price) M.slotTo($("heroPrice"), c.price, { from: prev.price, dur: .9, stagger: .05 });
      else $("heroPrice").textContent = c.price;
    }
    function show(n) {
      if (n === cur) return;
      const c = HERO[n], prev = HERO[cur]; cur = n;
      thumbs.forEach((t, k) => t.setAttribute("aria-pressed", k === n));
      const cat = $("heroCat"); cat.textContent = c.cat; cat.hidden = !c.cat;
      $("heroName").innerHTML = `<b>${esc(c.full)}</b>`;
      $("heroIdx").textContent = `${String(n + 1).padStart(2, "0")} / ${String(HERO.length).padStart(2, "0")}`;
      $("heroMeta").textContent = c.meta;
      setPrice(c, prev);
      if (anim) {
        M.roll(reelEl, c.name); fit();
        G.to(tileEl, { "--c0": c.tone[0], "--c1": c.tone[1], duration: .9, ease: "power2.out" });
        const old = [...stack.children], im = node(c);
        stack.appendChild(im);
        old.forEach(o => { G.killTweensOf(o); G.to(o, { yPercent: -125, rotation: -12, scale: .82, duration: .55, ease: "power3.in", onComplete: () => o.remove() }); });
        G.fromTo(im, { yPercent: 125, rotation: 14, scale: .9 }, { yPercent: 0, rotation: 0, scale: 1, duration: 1.05, ease: "back.out(1.5)", delay: .12 });
        G.fromTo(tileEl, { rotation: 0 }, { keyframes: [{ rotation: -2.5, duration: .22, ease: "power2.out" }, { rotation: 0, duration: .8, ease: "elastic.out(1, .45)" }] });
      } else {
        reelEl.innerHTML = `<span>${esc(c.name)}</span>`; fit();
        tileEl.style.setProperty("--c0", c.tone[0]); tileEl.style.setProperty("--c1", c.tone[1]);
        stack.innerHTML = media(c);
      }
      restartBar();
    }
    function restartBar() { thumbWrap.classList.remove("run"); void thumbWrap.offsetWidth; if (running) thumbWrap.classList.add("run"); }
    function schedule() { clearTimeout(timer); if (running && !hovering) timer = setTimeout(() => { show((cur + 1) % HERO.length); schedule(); }, DWELL); }
    function start() { if (!anim || running) return; running = true; restartBar(); schedule(); }
    function stop() { running = false; clearTimeout(timer); thumbWrap.classList.remove("run"); }
    thumbs.forEach((t, k) => t.addEventListener("click", () => { show(k); schedule(); }));
    const stage = $("stage");
    stage.addEventListener("pointerenter", () => { hovering = true; clearTimeout(timer); thumbWrap.classList.add("paused"); });
    stage.addEventListener("pointerleave", () => { hovering = false; thumbWrap.classList.remove("paused"); restartBar(); schedule(); });
    if (anim) {
      setTimeout(start, 2200);
      ST.create({ trigger: "#hero", start: "top top", end: "bottom top", onLeave: stop, onEnterBack: start });
      document.addEventListener("visibilitychange", () => { if (document.hidden) stop(); else if (scrollY < innerHeight) start(); });
    }
  }
  if (anim && document.querySelector(".hero-tile")) {
    /* the stage drifts and the copy lifts as the hero scrolls away */
    G.to(".hero-tile", { yPercent: 10, ease: "none", scrollTrigger: { trigger: "#hero", start: "top top", end: "bottom top", scrub: true } });
    G.to(".hero-copy", { yPercent: -12, opacity: .3, ease: "none", scrollTrigger: { trigger: "#hero", start: "center top+=35%", end: "bottom top", scrub: true } });
  }

  /* ---------- fleet: chips (built from the categories on the cards) filter with a card shuffle ---------- */
  const grid = $("cards"), chipWrap = $("fleetChips");
  if (grid) {
    const cards = [...grid.children];
    const cats = [];
    cards.forEach(c => { const k = c.dataset.cat; let e = cats.find(x => x.k === k); if (!e) cats.push(e = { k, n: 0, tone: c.dataset.tone }); e.n++; });
    if (chipWrap && cats.length > 1) {
      const pad = n => String(n).padStart(2, "0");
      chipWrap.innerHTML = `<button type="button" class="chip" data-f="all" aria-pressed="true"><span class="dot t-night"></span>All<sup>${pad(cards.length)}</sup></button>` +
        cats.map(c => `<button type="button" class="chip" data-f="${esc(c.k)}" aria-pressed="false"><span class="dot t-${esc(c.tone)}"></span>${esc(c.k)}<sup>${pad(c.n)}</sup></button>`).join("");
    }
    const chips = chipWrap ? [...chipWrap.children] : [];
    let busy = false;
    function filter(f) {
      chips.forEach(c => c.setAttribute("aria-pressed", c.dataset.f === f));
      const want = c => f === "all" || c.dataset.cat === f;
      if (!anim) { cards.forEach(c => c.hidden = !want(c)); return; }
      if (busy) G.killTweensOf(cards);
      busy = true;
      const leaving = cards.filter(c => !c.hidden && !want(c));
      const first = new Map(cards.map(c => [c, c.hidden ? null : c.getBoundingClientRect()]));
      const reflow = () => {
        cards.forEach(c => { c.hidden = !want(c); G.set(c, { clearProps: "transform,opacity" }); });
        cards.filter(c => !c.hidden).forEach((c, i) => {
          const a = first.get(c), b = c.getBoundingClientRect();
          if (!a) G.fromTo(c, { opacity: 0, y: 80, rotation: i % 2 ? 5 : -5, scale: .9 }, { opacity: 1, y: 0, rotation: 0, scale: 1, duration: .85, delay: .05 + i * .06, ease: "back.out(1.4)", clearProps: "transform,opacity" });
          else G.fromTo(c, { x: a.left - b.left, y: a.top - b.top, rotation: (a.left - b.left) / 60 }, { x: 0, y: 0, rotation: 0, duration: .85, delay: i * .03, ease: "expo.out", clearProps: "transform" });
        });
        ST.refresh(); busy = false;
      };
      if (leaving.length) G.to(leaving, { scale: .8, opacity: 0, rotation: i => i % 2 ? 6 : -6, duration: .28, ease: "power2.in", stagger: .03, onComplete: reflow });
      else reflow();
    }
    chips.forEach(c => c.addEventListener("click", () => filter(c.dataset.f)));

    if (anim) {
      /* cards dealt from a deck sitting at the centre of the grid; prices spin as they land */
      G.set(cards, { opacity: 0 });
      ST.create({ trigger: grid, start: "clamp(top 80%)", once: true, onEnter: () => {
        const g = grid.getBoundingClientRect(), cx = g.left + g.width / 2;
        cards.forEach((c, i) => {
          const r = c.getBoundingClientRect();
          G.fromTo(c, { opacity: 0, x: cx - (r.left + r.width / 2), y: 160, rotation: (i % 2 ? 1 : -1) * (8 + i * 2), scale: .8 },
            { opacity: 1, x: 0, y: 0, rotation: 0, scale: 1, duration: 1.1, delay: i * .1, ease: "back.out(1.2)", clearProps: "transform,opacity",
              onStart: () => { const p = c.querySelector(".pr"); if (p) M.slotTo(p, p.dataset.v || p.textContent.trim(), { from: "0", delay: .3 }); } });
        });
      } });
    }
  }

  if (!anim) return;

  /* wedding: scrubbing through the photo reel, one slot at a time */
  if ($("wreel")) {
    const wcaps = [...$("wcaps").children];
    const wtl = G.timeline({ defaults: { ease: "back.inOut(1.6)" } })
      .to({}, { duration: .4 })
      .to("#wreel", { yPercent: -33.3334, duration: 1 })
      .to({}, { duration: .5 })
      .to("#wreel", { yPercent: -66.6667, duration: 1 })
      .to({}, { duration: .4 });
    ST.create({ trigger: "#wedding", start: "top 65%", end: "bottom 35%", scrub: .8, animation: wtl,
      onUpdate: s => { const k = s.progress < .37 ? 0 : s.progress < .7 ? 1 : 2; wcaps.forEach((w, j) => w.classList.toggle("on", j === k)); } });
    G.from("#wedTile", { y: 80, rotation: -4, opacity: 0, duration: 1.2, ease: "back.out(1.3)", scrollTrigger: { trigger: "#wedding", start: "clamp(top 80%)", once: true } });
  }

  /* testimonial tile rises; CTA band rises; city rows slide in */
  if (document.querySelector(".quote")) G.from(".quote", { scale: .92, y: 60, borderRadius: "120px", duration: 1.2, ease: "expo.out", scrollTrigger: { trigger: ".quote", start: "clamp(top 85%)", once: true } });
  if (document.querySelector(".band")) G.from(".band", { y: 80, rotation: 1.5, duration: 1.1, ease: "expo.out", scrollTrigger: { trigger: ".band", start: "clamp(top 88%)", once: true } });
  if (document.querySelector(".city-rows")) G.from(".city-rows .m-marquee", { xPercent: i => i ? 30 : -30, opacity: 0, duration: 1.4, ease: "expo.out", stagger: .1, scrollTrigger: { trigger: ".city-rows", start: "clamp(top 90%)", once: true } });
});
