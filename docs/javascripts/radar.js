(() => {
  const PAGE_SIZE = 20;
  const fold = (text) => String(text || "").normalize("NFKD").replace(/\p{Diacritic}/gu, "").toLocaleLowerCase();
  const isoDate = (date) => `${date.getFullYear()}-${String(date.getMonth() + 1).padStart(2, "0")}-${String(date.getDate()).padStart(2, "0")}`;
  const cleanDate = (value) => /^\d{4}-\d{2}-\d{2}$/.test(value || "") ? value : "";

  function defaultDateRange(from, to, earliest, today = isoDate(new Date())) {
    return { from: cleanDate(from) || earliest, to: cleanDate(to) || today };
  }

  function filterEntries(entries, filters, today = isoDate(new Date())) {
    const words = fold(filters.q).trim().split(/\s+/).filter(Boolean);
    let from = filters.period === "custom" ? filters.from : "";
    let to = filters.period === "custom" ? filters.to : "";
    if (["30", "90"].includes(filters.period)) {
      const start = new Date(`${today}T12:00:00`);
      start.setDate(start.getDate() - Number(filters.period) + 1);
      from = isoDate(start);
      to = today;
    }
    if (from && to && from > to) return [];
    return entries.filter((entry) => (
      (!from || entry.date >= from) && (!to || entry.date <= to)
      && (!filters.topic || entry.directions.includes(filters.topic))
      && words.every((word) => entry.search.includes(word))
    ));
  }

  function paginate(entries, requestedPage, size = PAGE_SIZE) {
    const pages = Math.ceil(entries.length / size);
    const page = Math.min(Math.max(1, Number(requestedPage) || 1), Math.max(1, pages));
    const start = (page - 1) * size;
    return { page, pages, start, entries: entries.slice(start, start + size) };
  }

  if (typeof module !== "undefined" && module.exports) module.exports = { filterEntries, paginate, fold, defaultDateRange };
  if (typeof document === "undefined") return;
  let teardown = () => {};

  function setup(root) {
    const navigation = root.querySelector(":scope > .radar-browse-controls");
    if (!navigation || navigation.dataset.radarReady) return;
    teardown();
    navigation.dataset.radarReady = "true";
    root.classList.add("radar-home", "radar-compact");
    const skipLink = document.querySelector("a.md-skip");
    if (skipLink) skipLink.href = "#research-radar";
    const cards = [...root.querySelectorAll(":scope > article.radar-paper-card")];
    const entries = cards.map((card) => ({
      card, anchor: card.dataset.radarAnchor, date: card.dataset.radarDate || card.dataset.radarAddedOn,
      directions: JSON.parse(card.dataset.radarDirections || "[]"),
      search: fold(`${card.textContent} ${card.dataset.radarSearch || ""}`),
    }));
    const input = navigation.querySelector("#radar-paper-search");
    const period = navigation.querySelector("#radar-time-filter");
    const topic = navigation.querySelector("#radar-topic-filter");
    const from = navigation.querySelector("#radar-date-from");
    const to = navigation.querySelector("#radar-date-to");
    const customDates = navigation.querySelector(".radar-custom-dates");
    const count = navigation.querySelector(".radar-search-count");
    const reset = navigation.querySelector('[data-radar-action="reset"]');
    const empty = root.querySelector(".radar-empty-state");
    const pagination = root.querySelector(".radar-pagination");
    const previous = pagination.querySelector('[data-radar-action="previous"]');
    const next = pagination.querySelector('[data-radar-action="next"]');
    const pageLabel = pagination.querySelector("[data-radar-page]");
    const pageInfo = pagination.querySelector("[data-radar-page-info]");
    const pageSelect = pagination.querySelector("#radar-page-number");
    const earliestDate = navigation.dataset.earliestDate;
    function initializeDates() {
      const range = defaultDateRange(from.value, to.value, earliestDate);
      from.value = range.from;
      to.value = range.to;
    }
    let page = 1;
    let totalPages = 0;
    let ready = false;
    let searchTimer;

    function filters() {
      return { q: input.value, period: period.value, topic: topic.value, from: from.value, to: to.value };
    }

    function readURL() {
      const params = new URLSearchParams(location.search);
      input.value = (params.get("q") || "").slice(0, 300);
      const range = params.get("period") || "all";
      period.value = [...period.options].some((option) => option.value === range) ? range : "all";
      const tag = params.get("topic") || "";
      topic.value = [...topic.options].some((option) => option.value === tag) ? tag : "";
      // Old method-tag links now open a keyword search rather than silently losing their scope.
      if (tag && !topic.value) input.value = `${input.value} ${tag}`.trim().slice(0, 300);
      from.value = cleanDate(params.get("from"));
      to.value = cleanDate(params.get("to"));
      initializeDates();
      const requested = Number(params.get("page"));
      page = Number.isSafeInteger(requested) && requested > 0 ? requested : 1;
    }

    function writeURL(replace = false, preserveHash = false) {
      const url = new URL(location.href);
      const values = { ...filters(), page: page > 1 ? String(page) : "" };
      if (values.period === "all") values.period = "";
      if (values.period !== "custom") { values.from = ""; values.to = ""; }
      Object.entries(values).forEach(([key, value]) => {
        if (value.trim()) url.searchParams.set(key, value.trim());
        else url.searchParams.delete(key);
      });
      if (!preserveHash) url.hash = "";
      if (url.href !== location.href) history[replace ? "replaceState" : "pushState"](null, "", url);
    }

    const storageKey = () => `radar-view-v1:${location.pathname}${location.search}`;
    function saveView() {
      if (!ready) return;
      try {
        sessionStorage.setItem(storageKey(), JSON.stringify({
          scroll: window.scrollY,
          open: entries.filter((entry) => entry.card.querySelector("details")?.open).map((entry) => entry.anchor),
        }));
      } catch (_) { /* Browser storage is optional. */ }
    }

    function restoreView(restoreScroll) {
      try {
        const saved = JSON.parse(sessionStorage.getItem(storageKey()));
        if (!saved) return;
        entries.forEach((entry) => {
          const details = entry.card.querySelector("details");
          if (details) details.open = saved.open?.includes(entry.anchor) || false;
        });
        if (restoreScroll && Number.isFinite(saved.scroll)) requestAnimationFrame(() => window.scrollTo(0, saved.scroll));
      } catch (_) { /* Invalid or unavailable storage does not block browsing. */ }
    }

    function render() {
      const current = filters();
      const filtered = filterEntries(entries, current);
      const result = paginate(filtered, page);
      page = result.page;
      totalPages = result.pages;
      const visible = new Set(result.entries.map((entry) => entry.anchor));
      cards.forEach((card) => {
        card.hidden = !visible.has(card.dataset.radarAnchor);
        const heading = card.previousElementSibling;
        if (heading?.matches(".radar-search-heading")) heading.hidden = card.hidden;
      });
      customDates.hidden = current.period !== "custom";
      count.textContent = `${filtered.length} 篇论文`;
      empty.hidden = filtered.length !== 0;
      const invalidRange = current.period === "custom" && current.from && current.to && current.from > current.to;
      empty.textContent = invalidRange ? "起始日期不能晚于结束日期，请调整日期范围。"
        : current.period !== "all" && !current.q && !current.topic ? "该时间范围暂无收录。可调整日期或查看全部已收录论文。"
        : "没有找到匹配论文。试试其他关键词，或清除筛选。";
      pageLabel.textContent = `/ ${totalPages} 页`;
      pageInfo.textContent = filtered.length ? `显示 ${result.start + 1}–${result.start + result.entries.length} / ${filtered.length} 篇` : "没有匹配论文";
      previous.disabled = page <= 1;
      next.disabled = page >= totalPages;
      if (pageSelect.dataset.pageCount !== String(totalPages)) {
        pageSelect.replaceChildren(...Array.from({ length: Math.max(1, totalPages) }, (_, index) => {
          const option = document.createElement("option");
          option.value = option.textContent = String(totalPages ? index + 1 : 0);
          return option;
        }));
        pageSelect.dataset.pageCount = String(totalPages);
      }
      pageSelect.value = String(filtered.length ? page : 0);
      pageSelect.disabled = totalPages <= 1;
      reset.hidden = !current.q && current.period === "all" && !current.topic;
    }

    function changeFilters(replace = false) {
      saveView();
      page = 1;
      render();
      writeURL(replace);
      saveView();
    }

    function revealHashTarget() {
      let anchor;
      try { anchor = decodeURIComponent(location.hash.slice(1)); } catch (_) { return false; }
      const target = entries.find((entry) => entry.anchor === anchor);
      if (!target) return false;
      let filtered = filterEntries(entries, filters());
      if (!filtered.includes(target)) {
        input.value = ""; topic.value = ""; period.value = "all"; from.value = ""; to.value = "";
        filtered = entries;
      }
      page = Math.floor(filtered.indexOf(target) / PAGE_SIZE) + 1;
      render();
      const details = target.card.querySelector("details");
      if (details) details.open = true;
      writeURL(true, true);
      requestAnimationFrame(() => target.card.scrollIntoView({ block: "start" }));
      return true;
    }

    input.addEventListener("input", () => {
      clearTimeout(searchTimer);
      searchTimer = setTimeout(() => changeFilters(true), 180);
    });
    period.addEventListener("change", () => { if (period.value === "custom") initializeDates(); changeFilters(); });
    [topic, from, to].forEach((control) => control.addEventListener("change", () => changeFilters()));
    reset.addEventListener("click", () => {
      input.value = ""; period.value = "all"; topic.value = ""; from.value = ""; to.value = "";
      changeFilters();
    });
    function goToPage(requestedPage) {
      saveView();
      page = requestedPage;
      render();
      writeURL();
      navigation.scrollIntoView({ block: "start" });
      saveView();
    }
    previous.addEventListener("click", () => goToPage(page - 1));
    next.addEventListener("click", () => goToPage(page + 1));
    pageSelect.addEventListener("change", () => goToPage(Number(pageSelect.value)));
    cards.forEach((card) => card.querySelector("details")?.addEventListener("toggle", saveView));
    const onPopState = () => { readURL(); render(); if (!revealHashTarget()) restoreView(true); };
    const onHashChange = () => revealHashTarget();
    const onPageHide = () => saveView();
    window.addEventListener("popstate", onPopState);
    window.addEventListener("hashchange", onHashChange);
    window.addEventListener("pagehide", onPageHide);
    teardown = () => {
      clearTimeout(searchTimer);
      window.removeEventListener("popstate", onPopState);
      window.removeEventListener("hashchange", onHashChange);
      window.removeEventListener("pagehide", onPageHide);
    };
    readURL();
    render();
    if (!revealHashTarget()) { writeURL(true, true); restoreView(true); }
    ready = true;
  }

  const enhance = () => {
    const root = document.querySelector("article.md-content__inner");
    if (root?.querySelector(".radar-browse-controls")) setup(root);
    else teardown();
  };
  document.addEventListener("DOMContentLoaded", enhance);
  if (typeof document$ !== "undefined") document$.subscribe(enhance);
})();
