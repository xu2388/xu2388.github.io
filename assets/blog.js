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

  /* ---------- 明暗主题（初始化脚本已在 <head> 提前执行，这里只负责切换按钮） ---------- */
  function currentTheme() {
    return root.getAttribute("data-theme") || "light";
  }
  function initThemeToggle() {
    var header = document.querySelector(".site-header");
    var nav = document.querySelector(".site-nav");
    if (!header || !nav || document.querySelector(".theme-toggle")) return;
    var btn = document.createElement("button");
    btn.className = "theme-toggle";
    btn.type = "button";
    btn.setAttribute("aria-label", "切换明暗主题");
    function paint() {
      btn.innerHTML = '<span class="ic">' + (currentTheme() === "dark" ? "☀️" : "🌙") + "</span><span>" +
        (currentTheme() === "dark" ? "浅色模式" : "深色模式") + "</span>";
    }
    btn.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) { }
      paint();
    });
    paint();
    nav.insertAdjacentElement("afterend", btn);
  }

  /* ---------- 侧栏搜索框 ----------
     由 JS 注入而不是写死在每页 HTML 里：相对路径从导航第一个链接反推，
     这样根目录页（index.html）和 articles/notes/ 下的深层页都不用各写一份。 */
  function navPrefix() {
    var a = document.querySelector(".site-nav a");
    if (!a) return "";
    return (a.getAttribute("href") || "index.html").replace(/index\.html.*$/, "");
  }
  function initSideSearch() {
    var nav = document.querySelector(".site-nav");
    if (!nav || document.querySelector(".side-search")) return;
    var prefix = navPrefix();
    var wrap = document.createElement("div");
    wrap.className = "side-search";
    wrap.innerHTML =
      '<form role="search" action="' + prefix + 'search.html">' +
      '<input type="search" name="q" placeholder="搜索标题…" aria-label="搜索文章标题" autocomplete="off" />' +
      '<button type="submit" aria-label="搜索">⌕</button></form>';
    nav.parentNode.insertBefore(wrap, nav);
  }

  /* ---------- 搜索页：标题即时筛选 ---------- */
  function initSearchPage() {
    var input = document.getElementById("search-q");
    if (!input) return;
    var data = window.SEARCH_INDEX || [];
    var list = document.getElementById("search-results");
    var cnt = document.getElementById("search-count");
    var hint = document.getElementById("search-hint");
    var total = document.getElementById("search-total");
    var def = document.getElementById("search-default");
    if (total) total.textContent = data.length;

    function esc(s) {
      return String(s).replace(/[&<>"]/g, function (c) {
        return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;" }[c];
      });
    }
    function mark(text, q) {
      var i = text.toLowerCase().indexOf(q);
      if (i < 0) return esc(text);
      return esc(text.slice(0, i)) + "<mark>" + esc(text.slice(i, i + q.length)) + "</mark>" + esc(text.slice(i + q.length));
    }

    function render(raw) {
      var q = (raw || "").trim().toLowerCase();
      if (def) def.hidden = !!q;
      if (!q) {
        list.innerHTML = "";
        cnt.textContent = "";
        if (hint) hint.hidden = false;
        return;
      }
      if (hint) hint.hidden = true;
      var hits = data.filter(function (it) {
        return String(it.t || "").toLowerCase().indexOf(q) >= 0;
      });
      hits.sort(function (a, b) {
        var ai = a.t.toLowerCase().indexOf(q), bi = b.t.toLowerCase().indexOf(q);
        if (ai !== bi) return ai - bi;
        return String(b.d || "").localeCompare(String(a.d || ""));
      });
      cnt.textContent = hits.length ? hits.length + " 条" : "无结果";
      if (!hits.length) {
        list.innerHTML = '<li class="search-empty">没有标题包含「' + esc(raw.trim()) + '」的内容。换个关键词试试，或到 <a href="study.html">学习</a> / <a href="research.html">科研</a> 里逐层浏览。</li>';
        return;
      }
      list.innerHTML = hits.map(function (it) {
        return '<li><a href="' + it.u + '">' + mark(it.t, q) + "</a>" +
          '<span class="sr-meta"><i class="badge ' + badgeClass(it.s) + '">' + esc(it.s) + "</i>" +
          "<span>" + esc(it.g || "") + "</span>" +
          '<span class="sr-date">' + esc(it.d || "") + "</span></span></li>";
      }).join("");
    }
    function badgeClass(s) {
      return { "科研": "b-research", "学习": "b-study", "随笔": "b-essay", "资料库": "b-archive" }[s] || "b-study";
    }

    var q0 = "";
    try { q0 = new URLSearchParams(location.search).get("q") || ""; } catch (e) { }
    if (q0) input.value = q0;
    render(q0);

    var timer;
    input.addEventListener("input", function () {
      clearTimeout(timer);
      timer = setTimeout(function () {
        render(input.value);
        try {
          var u = new URL(location.href);
          if (input.value.trim()) u.searchParams.set("q", input.value.trim());
          else u.searchParams.delete("q");
          history.replaceState(null, "", u);
        } catch (e) { }
      }, 90);
    });
    input.focus();
    input.setSelectionRange(input.value.length, input.value.length);
  }

  /* ---------- 全局「/」跳到搜索 ---------- */
  function initSlashSearch() {
    if (document.getElementById("search-q")) return;
    document.addEventListener("keydown", function (e) {
      if (e.key !== "/" || e.metaKey || e.ctrlKey || e.altKey) return;
      var t = e.target;
      if (t && (t.tagName === "INPUT" || t.tagName === "TEXTAREA" || t.isContentEditable)) return;
      e.preventDefault();
      location.href = navPrefix() + "search.html";
    });
  }

  /* ---------- 侧边栏画布粒子（配色随主题） ---------- */
  function initCanvas() {
    var header = document.querySelector(".site-header");
    if (!header || reduce) return;
    var canvas = document.createElement("canvas");
    canvas.className = "side-canvas";
    header.insertBefore(canvas, header.firstChild);
    var ctx = canvas.getContext("2d");
    var W = 0, H = 0, pts = [], dpr = Math.min(window.devicePixelRatio || 1, 2);

    function palette() {
      var dark = currentTheme() === "dark";
      return {
        dot: dark ? "rgba(45,212,191,0.38)" : "rgba(13,148,136,0.30)",
        line: dark ? "rgba(45,212,191,0.10)" : "rgba(13,148,136,0.09)"
      };
    }
    function resize() {
      W = header.clientWidth; H = header.clientHeight;
      canvas.width = W * dpr; canvas.height = H * dpr;
      canvas.style.width = W + "px"; canvas.style.height = H + "px";
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    }
    function seed() {
      var n = Math.max(14, Math.round(W * H / 20000));
      pts = [];
      for (var i = 0; i < n; i++) {
        pts.push({
          x: Math.random() * W, y: Math.random() * H,
          vx: (Math.random() - 0.5) * 0.22,
          vy: (Math.random() - 0.5) * 0.22,
          r: Math.random() * 1.4 + 0.6
        });
      }
    }
    function tick() {
      var c = palette();
      ctx.clearRect(0, 0, W, H);
      var i, j, p, q, d;
      for (i = 0; i < pts.length; i++) {
        p = pts[i];
        p.x += p.vx; p.y += p.vy;
        if (p.x < 0 || p.x > W) p.vx *= -1;
        if (p.y < 0 || p.y > H) p.vy *= -1;
        ctx.beginPath();
        ctx.arc(p.x, p.y, p.r, 0, Math.PI * 2);
        ctx.fillStyle = c.dot;
        ctx.fill();
      }
      for (i = 0; i < pts.length; i++) {
        for (j = i + 1; j < pts.length; j++) {
          p = pts[i]; q = pts[j];
          d = (p.x - q.x) * (p.x - q.x) + (p.y - q.y) * (p.y - q.y);
          if (d < 110 * 110) {
            ctx.beginPath();
            ctx.moveTo(p.x, p.y); ctx.lineTo(q.x, q.y);
            ctx.strokeStyle = c.line.replace("0.10", (0.10 * (1 - Math.sqrt(d) / 110)).toFixed(3));
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
    var targets = document.querySelectorAll(".article-list li, .spot-card, .card, .block, .stat");
    targets.forEach(function (el) { el.classList.add("reveal"); });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); }
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.05 });
    targets.forEach(function (el) { io.observe(el); });
    // 兜底：2.5 秒后仍未触发的元素直接显示，避免任何情况下内容被永久隐藏
    setTimeout(function () {
      targets.forEach(function (el) {
        if (!el.classList.contains("in")) { el.classList.add("in"); io.unobserve(el); }
      });
    }, 2500);
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

  /* ---------- 公式渲染（KaTeX，按需加载） ----------
     文章里的 $...$ / $$...$$ 是 LaTeX。只在页面确实出现 $ 时才去 CDN 取 KaTeX，
     取不到就原样保留，不影响阅读。 */
  function initMath() {
    var art = document.querySelector(".article");
    if (!art || art.textContent.indexOf("$") === -1) return;
    var V = "0.16.9", CDN = "https://cdn.jsdelivr.net/npm/katex@" + V + "/dist/";
    var link = document.createElement("link");
    link.rel = "stylesheet"; link.href = CDN + "katex.min.css";
    document.head.appendChild(link);
    function load(src, cb) {
      var s = document.createElement("script");
      s.src = src; s.onload = cb; s.onerror = function () { };
      document.head.appendChild(s);
    }
    load(CDN + "katex.min.js", function () {
      load(CDN + "contrib/auto-render.min.js", function () {
        if (typeof renderMathInElement !== "function") return;
        renderMathInElement(art, {
          delimiters: [
            { left: "$$", right: "$$", display: true },
            { left: "$", right: "$", display: false }
          ],
          throwOnError: false,
          ignoredTags: ["script", "noscript", "style", "textarea", "pre", "code"]
        });
      });
    });
  }

  function boot() {
    initThemeToggle();
    initSideSearch();
    initCanvas();
    initMobileNav();
    initProgress();
    initBackTop();
    initTOC();
    /* 入场动画已关闭：列表项先 opacity:0 再等 IntersectionObserver，
       在慢网络或某些渲染环境下会出现「内容短暂不可见」，对纯文字归档得不偿失。 */
    initNavSpy();
    initMath();
    initSearchPage();
    initSlashSearch();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
