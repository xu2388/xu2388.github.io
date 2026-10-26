/* 科研与学习档案 · 交互（零依赖，渐进增强）
   - 明暗主题切换（顶栏圆钮）
   - 移动端导航
   - 文章页右侧目录（滚动高亮）
   - 阅读进度 / 回到顶部
   - 标题搜索
   - 公式渲染（KaTeX，按需）
   刻意不做：粒子背景、滚动入场、卡片悬停位移——这些只增加噪音。 */
(function () {
  "use strict";
  var root = document.documentElement;
  root.className += " js";
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  var ICON_MOON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8Z"/></svg>';
  var ICON_SUN = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round"><circle cx="12" cy="12" r="4"/><path d="M12 2v2M12 20v2M2 12h2M20 12h2M4.9 4.9l1.4 1.4M17.7 17.7l1.4 1.4M19.1 4.9l-1.4 1.4M6.3 17.7l-1.4 1.4"/></svg>';

  function currentTheme() {
    return root.getAttribute("data-theme") || "light";
  }

  /* ---------- 主题切换 ---------- */
  function initThemeToggle() {
    var bar = document.querySelector(".topbar-inner");
    if (!bar || document.querySelector(".theme-btn")) return;
    var btn = document.createElement("button");
    btn.className = "theme-btn";
    btn.type = "button";
    btn.setAttribute("aria-label", "切换明暗主题");
    function paint() {
      var dark = currentTheme() === "dark";
      btn.innerHTML = dark ? ICON_SUN : ICON_MOON;
      btn.title = dark ? "切换到浅色" : "切换到深色";
    }
    btn.addEventListener("click", function () {
      var next = currentTheme() === "dark" ? "light" : "dark";
      root.setAttribute("data-theme", next);
      try { localStorage.setItem("theme", next); } catch (e) { }
      paint();
    });
    paint();
    bar.appendChild(btn);
  }

  /* ---------- 移动端导航 ---------- */
  function initMobileNav() {
    var btn = document.querySelector(".nav-btn");
    if (!btn) return;
    function close() {
      document.body.classList.remove("nav-open");
      btn.setAttribute("aria-expanded", "false");
    }
    btn.addEventListener("click", function (e) {
      e.stopPropagation();
      var open = document.body.classList.toggle("nav-open");
      btn.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("click", function (e) {
      if (!document.body.classList.contains("nav-open")) return;
      if (e.target.closest(".topbar")) return;
      close();
    });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });
    window.addEventListener("resize", function () { if (window.innerWidth > 720) close(); });
  }

  /* ---------- 阅读进度（仅文章页） ---------- */
  function initProgress() {
    if (!document.querySelector(".article")) return;
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
      if ((document.documentElement.scrollTop || document.body.scrollTop) > 700) btn.classList.add("show");
      else btn.classList.remove("show");
    }, { passive: true });
  }

  /* ---------- 右侧目录 ---------- */
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
        var top = h.getBoundingClientRect().top + window.pageYOffset - 24;
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
      var pos = window.pageYOffset + 110, current = links[0];
      for (var i = 0; i < heads.length; i++) {
        if (heads[i].getBoundingClientRect().top + window.pageYOffset <= pos) current = links[i];
      }
      links.forEach(function (l) { l.classList.remove("active"); });
      if (current) current.classList.add("active");
    }
    window.addEventListener("scroll", spy, { passive: true });
    spy();
  }

  /* ---------- 标题搜索 ---------- */
  function navPrefix() {
    var a = document.querySelector(".brand");
    if (!a) return "";
    return (a.getAttribute("href") || "index.html").replace(/index\.html.*$/, "");
  }
  function initSearchPage() {
    var input = document.getElementById("search-q");
    if (!input) return;
    var data = window.SEARCH_INDEX || [];
    var list = document.getElementById("search-results");
    var cnt = document.getElementById("search-count");
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
        if (cnt) cnt.textContent = "";
        return;
      }
      var hits = data.filter(function (it) {
        return String(it.t || "").toLowerCase().indexOf(q) >= 0;
      });
      hits.sort(function (a, b) {
        var ai = a.t.toLowerCase().indexOf(q), bi = b.t.toLowerCase().indexOf(q);
        if (ai !== bi) return ai - bi;
        return String(b.d || "").localeCompare(String(a.d || ""));
      });
      if (cnt) cnt.textContent = hits.length ? hits.length + " 条" : "无结果";
      if (!hits.length) {
        list.innerHTML = '<li class="search-empty">没有标题包含「' + esc(raw.trim()) +
          '」的内容。换个关键词，或到 <a href="research.html">研究</a>、<a href="notes.html">笔记</a> 里逐层浏览。</li>';
        return;
      }
      list.innerHTML = hits.map(function (it) {
        return '<li><a href="' + it.u + '">' + mark(it.t, q) + "</a>" +
          '<span class="sr-meta"><span>' + esc(it.s) + "</span><span>" + esc(it.g || "") + "</span>" +
          '<span class="sr-date">' + esc(it.d || "") + "</span></span></li>";
      }).join("");
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
      }, 80);
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
      location.href = navPrefix() + "archive.html";
    });
  }

  /* ---------- 公式渲染（KaTeX，按需） ---------- */
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
    initMobileNav();
    initProgress();
    initBackTop();
    initTOC();
    initMath();
    initSearchPage();
    initSlashSearch();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
