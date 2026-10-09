/* VehicleRent · Showroom Reels theme, inner pages: vehicle photo reel, wedding tier tiles → fleet chips, legal table of contents.
   Loaded after reels.js (which handles the mobile sheet, fleet card deal/shuffle and the wedding photo reel).
   Works without GSAP and animates when it is there. */
document.addEventListener("DOMContentLoaded", () => {
  const $ = id => document.getElementById(id);
  const G = window.gsap;
  const reduce = matchMedia("(prefers-reduced-motion: reduce)").matches;
  const anim = !!(G && !reduce);

  /* ---------- vehicle detail: thumbnails swap the photo in the tile like a card deck ---------- */
  const stack = $("vdStack"), thumbWrap = $("vdThumbs");
  if (stack && thumbWrap) {
    const thumbs = [...thumbWrap.querySelectorAll(".th")];
    const tile = stack.closest(".ct"), idx = $("vdIdx");
    const alt = (stack.querySelector("img") || {}).alt || "";
    let cur = 0;
    const show = (n, dir) => {
      if (n === cur) return;
      dir = dir || (n > cur ? 1 : -1); cur = n;
      thumbs.forEach((t, k) => t.setAttribute("aria-pressed", k === n));
      if (idx) idx.textContent = `${String(n + 1).padStart(2, "0")} / ${String(thumbs.length).padStart(2, "0")}`;
      const im = new Image(); im.src = thumbs[n].dataset.img; im.alt = alt;
      const old = [...stack.children];
      stack.appendChild(im);
      if (anim) {
        old.forEach(o => { G.killTweensOf(o); G.to(o, { xPercent: -110 * dir, rotation: -10 * dir, scale: .85, opacity: 0, duration: .5, ease: "power3.in", onComplete: () => o.remove() }); });
        G.fromTo(im, { xPercent: 110 * dir, rotation: 12 * dir, scale: .9 }, { xPercent: 0, rotation: 0, scale: 1, duration: .95, ease: "back.out(1.4)", delay: .08 });
        if (tile) G.fromTo(tile, { rotation: 0 }, { keyframes: [{ rotation: -1.6 * dir, duration: .2, ease: "power2.out" }, { rotation: 0, duration: .8, ease: "elastic.out(1, .45)" }] });
      } else old.forEach(o => o.remove());
    };
    thumbs.forEach((t, k) => t.addEventListener("click", () => show(k)));
    thumbWrap.addEventListener("keydown", e => {
      if (e.key !== "ArrowRight" && e.key !== "ArrowLeft") return;
      e.preventDefault();
      const n = (cur + (e.key === "ArrowRight" ? 1 : -1) + thumbs.length) % thumbs.length;
      show(n, e.key === "ArrowRight" ? 1 : -1); thumbs[n].focus();
    });
    /* swipe on the photo itself (touch) */
    let x0 = null;
    stack.addEventListener("pointerdown", e => { x0 = e.clientX; });
    stack.addEventListener("pointerup", e => {
      if (x0 == null) return;
      const dx = e.clientX - x0; x0 = null;
      if (Math.abs(dx) < 40) return;
      const d = dx < 0 ? 1 : -1;
      show((cur + d + thumbs.length) % thumbs.length, d);
    });
  }

  /* ---------- wedding: tier tiles filter the fleet below through its chips ---------- */
  document.querySelectorAll("[data-tier]").forEach(a => a.addEventListener("click", () => {
    const chip = document.querySelector(`#fleetChips [data-f="${a.dataset.tier}"]`);
    if (chip) setTimeout(() => chip.click(), reduce ? 0 : 450);
  }));

  /* ---------- legal: table of contents built from the section headings ---------- */
  const body = $("legalBody"), toc = $("legalToc");
  if (body && toc) {
    const secs = [...body.querySelectorAll(":scope > section:not(.legal-ask)")];
    const links = secs.map((s, i) => {
      const h = s.querySelector("h2"); if (!h) return null;
      s.id = s.id || "s" + (i + 1);
      const li = document.createElement("li"), a = document.createElement("a");
      a.href = "#" + s.id; a.textContent = h.textContent.trim();
      li.appendChild(a); toc.appendChild(li);
      return a;
    });
    if ("IntersectionObserver" in window) {
      const io = new IntersectionObserver(es => es.forEach(e => {
        if (!e.isIntersecting) return;
        const k = secs.indexOf(e.target);
        links.forEach((a, j) => a && a.setAttribute("aria-current", j === k ? "true" : "false"));
      }), { rootMargin: "-30% 0px -60% 0px" });
      secs.forEach(s => io.observe(s));
    }
  }
});
