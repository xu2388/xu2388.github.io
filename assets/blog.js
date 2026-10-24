/* 科研博客 · 交互增强（零依赖，渐进增强）
   - 侧边栏画布粒子动效
   - 移动端抽屉导航
   - 文章页悬浮目录（滚动高亮）
   - 回到顶部 / 阅读进度条
   - 滚动入场动画 / 导航高亮 */
(function () {
  "use strict";
  var root = document.documentElement;
  root.className += " js";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ---------- 侧边栏画布粒子 ---------- */
  function initCanvas() {
    var header = document.querySelector(".site-header");
    if (!header || reduce) return;
    var canvas = document.createElement("canvas");
    canvas.className = "side-canvas";
    header.insertBefore(canvas, header.firstChild);
    var ctx = canvas.getContext("2d");
    var W = 0, H = 0, pts = [], dpr = Math.min(window.devicePixelRatio || 1, 2);

    function resize() {
      W = header.clientWidth; H = header.clientHeight;
      canvas.width = W * dpr; canvas.height = H * dpr;
      canvas.style.width = W + "px"; canvas.style.height = H + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function seed() {
      var n = Math.max(18, Math.round(W * H / 16000));
      pts = [];
      for (var i = 0; i < n; i++) {
        pts.push({
          x: Math.random() * W, y: Math.random() * H,
          vx: (Math.random() - 0.5) * 0.28,
          vy: (Math.random() - 0.5) * 0.28,
          r: Math.random() * 1.6 + 0.6
        });
      }
    }
    function tick() {
      ctx.clearRect(0, 0, W, H);
      var i, j, p, q, d;
      for (i = 0; i < pts.length; i++) {
        p = pts[i];
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > W) p.vx *= -1;
        if (p.y < 0 || p.y > H) p.vy *= -1;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = "rgba(110,231,210,0.5)";
        ctx.fill();
      }
      for (i = 0; i < pts.length; i++) {
        for (j = i + 1; j < pts.length; j++) {
          p = pts[i]; q = pts[j];
          d = (p.x - q.x) * (p.x - q.x) + (p.y - q.y) * (p.y - q.y);
          if (d < 120 * 120) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y);
            ctx.strokeStyle = "rgba(110,231,210," + (0.14 * (1 - Math.sqrt(d) / 120)).toFixed(3) + ")";
            ctx.lineWidth = 1;
            ctx.stroke();
          }
        }
      }
      requestAnimationFrame(tick);
    }
    resize(); seed(); tick();
    var rt;
    window.addEventListener("resize", function () {
      clearTimeout(rt);
      rt = setTimeout(function () { var ox = W; resize(); if (W !== ox) seed(); }, 150);
    });
  }

  /* ---------- 移动端抽屉 ---------- */
  function initMobileNav() {
    var titleEl = document.querySelector(".site-title");
    var title = titleEl ? titleEl.textContent.replace(/\s+/g, " ").trim() : "目录";
    var bar = document.createElement("div");
    bar.className = "mobile-topbar";
    bar.innerHTML =
      '<button class="nav-toggle" aria-label="打开目录"><span style="font-size:18px;line-height:1">☰</span> 目录</button>' +
      '<span class="mt-title"></span>';
    bar.querySelector(".mt-title").textContent = title;
    document.body.insertBefore(bar, document.body.firstChild);

    var bd = document.createElement("div");
    bd.className = "nav-backdrop";
    document.body.appendChild(bd);

    function close() { document.body.classList.remove("nav-open"); }
    bar.querySelector(".nav-toggle").addEventListener("click", function () {
      document.body.classList.toggle("nav-open");
    });
    bd.addEventListener("click", close);
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
    document.querySelectorAll(".site-nav a").forEach(function (a) {
      a.addEventListener("click", close);
    });
  }

  /* ---------- 阅读进度 ---------- */
  function initProgress() {
    var wrap = document.createElement("div");
    wrap.className = "read-progress";
    wrap.innerHTML = '<div class="bar"></div>';
    document.body.appendChild(wrap);
    var bar = wrap.querySelector(".bar");
    function upd() {
      var h = document.documentElement;
      var max = h.scrollHeight - window.innerHeight;
      var p = max > 0 ? (h.scrollTop || document.body.scrollTop) / max : 0;
      bar.style.width = (p * 100).toFixed(2) + "%";
    }
    window.addEventListener("scroll", upd, { passive: true });
    window.addEventListener("resize", upd);
    upd();
  }

  /* ---------- 回到顶部 ---------- */
  function initBackTop() {
    var btn = document.createElement("button");
    btn.className = "back-top";
    btn.innerHTML = "↑";
    btn.setAttribute("aria-label", "回到顶部");
    document.body.appendChild(btn);
    btn.addEventListener("click", function () {
      window.scrollTo({ top: 0, behavior: reduce ? "auto" : "smooth" });
    });
    window.addEventListener("scroll", function () {
      if ((document.documentElement.scrollTop || document.body.scrollTop) > 360) btn.classList.add("show");
      else btn.classList.remove("show");
    }, { passive: true });
  }

  /* ---------- 悬浮目录 + 滚动高亮 ---------- */
  function slug(s) {
    return "h-" + s.trim().toLowerCase().replace(/[^\w\u4e00-\u9fa5]+/g, "-").replace(/^-+|-+$/g, "");
  }
  function initTOC() {
    var art = document.querySelector(".article");
    if (!art) return;
    var heads = art.querySelectorAll("h2, h3");
    if (heads.length < 2) return;
    var aside = document.createElement("aside");
    aside.className = "toc";
    var ul = document.createElement("ul");
    heads.forEach(function (h) {
      if (!h.id) h.id = slug(h.textContent);
      var li = document.createElement("li");
      if (h.tagName === "H3") li.className = "toc-h3";
      var a = document.createElement("a");
      a.href = "#" + h.id;
      a.textContent = h.textContent;
      a.addEventListener("click", function (e) {
        e.preventDefault();
        var top = h.getBoundingClientRect().top + window.pageYOffset - 20;
        window.scrollTo({ top: top, behavior: reduce ? "auto" : "smooth" });
        history.replaceState(null, "", "#" + h.id);
      });
      li.appendChild(a); ul.appendChild(li);
    });
    var t = document.createElement("div");
    t.className = "toc-title"; t.textContent = "目录";
    aside.appendChild(t); aside.appendChild(ul);
    document.body.appendChild(aside);

    var links = Array.prototype.slice.call(aside.querySelectorAll("a"));
    function spy() {
      var pos = window.pageYOffset + 90, current = links[0];
      for (var i = 0; i < heads.length; i++) {
        if (heads[i].getBoundingClientRect().top + window.pageYOffset <= pos) current = links[i];
      }
      links.forEach(function (l) { l.classList.remove("active"); });
      if (current) current.classList.add("active");
    }
    window.addEventListener("scroll", spy, { passive: true });
    spy();
  }

  /* ---------- 滚动入场 ---------- */
  function initReveal() {
    if (reduce || !("IntersectionObserver" in window)) return;
    var targets = document.querySelectorAll(".article-list li, .card, .block, .stat");
    targets.forEach(function (el) { el.classList.add("reveal"); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    targets.forEach(function (el) { io.observe(el); });
  }

  /* ---------- 导航高亮（首页锚点） ---------- */
  function initNavSpy() {
    var links = Array.prototype.slice.call(document.querySelectorAll(".site-nav a[href*='#']"));
    if (!links.length) return;
    var map = links.map(function (a) {
      var id = a.getAttribute("href").split("#")[1];
      return { a: a, el: id ? document.getElementById(id) : null };
    }).filter(function (m) { return m.el; });
    if (!map.length) return;
    function spy() {
      var pos = window.pageYOffset + 120, cur = null;
      map.forEach(function (m) {
        var top = m.el.getBoundingClientRect().top + window.pageYOffset;
        if (top <= pos) cur = m;
      });
      links.forEach(function (a) { a.classList.remove("active"); });
      if (cur) cur.a.classList.add("active");
    }
    window.addEventListener("scroll", spy, { passive: true });
    spy();
  }

  function boot() {
    initCanvas();
    initMobileNav();
    initProgress();
    initBackTop();
    initTOC();
    initReveal();
    initNavSpy();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
