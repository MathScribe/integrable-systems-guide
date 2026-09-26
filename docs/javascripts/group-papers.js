(() => {
  const PAGE_SIZE = 5;
  const CACHE_AGE = 15 * 60 * 1000;
  const TOPICS = /integrab|soliton|schr[oö]|darboux|riemann|rogue|breather|korteweg|painlev|hirota|fokas|lenells|sasa.satsuma|kaup|newell|landau.lifshitz|short.pulse|boussinesq|sine.gordon|maxwell.bloch|akns|nonlinear wave|dispersive/i;
  const normalizeName = (value) => String(value || "").toLowerCase().replace(/[^a-z]/g, "");
  const orcidId = (value) => String(value || "").replace(/^https?:\/\/orcid.org\//, "").replace(/\/$/, "");
  function plain(value) {
    const entities = { amp: "&", quot: '"', apos: "'", lt: "<", gt: ">", nbsp: " ", ndash: "–", mdash: "—" };
    return String(value || "").replace(/<[^>]*>/g, "").replace(/&(#x[\da-f]+|#\d+|[a-z]+);/gi, (original, entity) => {
      if (!entity.startsWith("#")) return entities[entity.toLowerCase()] || original;
      const code = entity[1].toLowerCase() === "x" ? parseInt(entity.slice(2), 16) : Number(entity.slice(1));
      return code >= 0 && code <= 0x10ffff ? String.fromCodePoint(code) : original;
    }).replace(/\s+/g, " ").trim();
  }

  function belongsToAuthor(work, name, orcid) {
    const authors = work.author || [];
    if (authors.some((author) => orcidId(author.ORCID) === orcid)) return true;
    // Name searches are fuzzy and include medical papers by a namesake.
    // Only expand beyond the ORCID set for an exact name and a relevant title.
    const exactName = authors.some((author) => (
      normalizeName(`${author.given || ""} ${author.family || ""}`) === normalizeName(name)
      && (!author.ORCID || orcidId(author.ORCID) === orcid)
    ));
    return exactName && TOPICS.test(plain((work.title || [])[0]));
  }

  function normalizeWork(work) {
    const parts = (work["published-print"] || work.published || work["published-online"] || {})["date-parts"]?.[0] || [];
    return {
      doi: String(work.DOI || "").toLowerCase(),
      title: plain(work.title?.[0]),
      authors: (work.author || []).map((a) => plain(a.name || `${a.given || ""} ${a.family || ""}`)),
      journal: plain(work["container-title"]?.[0]),
      year: parts[0] ? String(parts[0]) : "",
      date: parts.map((part) => String(part).padStart(2, "0")).join("-"),
      volume: plain(work.volume),
      locator: plain(work["article-number"] || work.page),
    };
  }

  function mergeWorks(batches, name, orcid) {
    const papers = new Map();
    batches.flat().forEach((work) => {
      if (!work.DOI || !belongsToAuthor(work, name, orcid)) return;
      const paper = normalizeWork(work);
      if (paper.title) papers.set(paper.doi, paper);
    });
    return [...papers.values()].sort((a, b) => b.date.localeCompare(a.date) || a.title.localeCompare(b.title));
  }

  function filterWorks(papers, query, year) {
    const words = query.trim().toLocaleLowerCase().split(/\s+/).filter(Boolean);
    return papers.filter((paper) => (!year || paper.year === year) && words.every((word) => (
      [paper.title, paper.journal, ...paper.authors].join(" ").toLocaleLowerCase().includes(word)
    )));
  }

  if (typeof module !== "undefined" && module.exports) {
    module.exports = { belongsToAuthor, normalizeWork, mergeWorks, filterWorks };
  }
  if (typeof document === "undefined") return;

  async function requestWorks(params) {
    const url = new URL("https://api.crossref.org/works");
    Object.entries({
      select: "DOI,title,author,container-title,published,published-print,published-online,volume,page,article-number",
      ...params,
    }).forEach(([key, value]) => url.searchParams.set(key, value));
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), 18000);
    try {
      const response = await fetch(url, { signal: controller.signal, credentials: "omit" });
      if (!response.ok) throw new Error(`Crossref ${response.status}`);
      const body = await response.json();
      if (!Array.isArray(body.message?.items)) throw new Error("Invalid Crossref response");
      return body.message.items;
    } finally {
      window.clearTimeout(timer);
    }
  }

  function setup(root) {
    if (root.dataset.ready) return;
    root.dataset.ready = "true";
    const name = root.dataset.author;
    const orcid = root.dataset.orcid;
    const input = root.querySelector("[data-paper-query]");
    const year = root.querySelector("[data-paper-year]");
    const status = root.querySelector("[data-paper-status]");
    const results = root.querySelector("[data-paper-results]");
    const previous = root.querySelector("[data-paper-prev]");
    const next = root.querySelector("[data-paper-next]");
    const pageLabel = root.querySelector("[data-paper-page]");
    const retry = root.querySelector("[data-paper-retry]");
    const cacheKey = `group-papers-v2:${orcid}`;
    let papers = [];
    let page = 0;
    let partial = false;

    function element(tag, className, text) {
      const node = document.createElement(tag);
      if (className) node.className = className;
      if (text) node.textContent = text;
      return node;
    }

    function render() {
      const filtered = filterWorks(papers, input.value, year.value);
      const pages = Math.ceil(filtered.length / PAGE_SIZE);
      page = Math.min(page, Math.max(0, pages - 1));
      status.textContent = `${filtered.length} 篇匹配论文${partial ? " · 部分结果暂未加载" : ""}`;
      results.replaceChildren();
      filtered.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE).forEach((paper) => {
        const article = element("article", "group-paper");
        const date = element("span", "group-paper-year", paper.year || "—");
        const body = element("div", "group-paper-body");
        const title = element("h3", "group-paper-title");
        const link = element("a", "", paper.title);
        link.href = `https://doi.org/${paper.doi}`;
        link.target = "_blank";
        link.rel = "noopener noreferrer";
        title.append(link);
        body.append(title, element("p", "group-paper-authors", paper.authors.join(", ")));
        body.append(element("p", "group-paper-journal", [paper.journal, paper.volume, paper.locator].filter(Boolean).join(" · ")));
        article.append(date, body);
        results.append(article);
      });
      if (!filtered.length) results.append(element("p", "group-papers-empty", "没有找到匹配论文，试试其他关键词或年份。"));
      pageLabel.textContent = pages ? `${page + 1} / ${pages}` : "0 / 0";
      previous.disabled = page === 0;
      next.disabled = page + 1 >= pages;
      retry.hidden = !partial;
    }

    function populateYears() {
      const selected = year.value;
      year.replaceChildren(new Option("全部年份", ""));
      [...new Set(papers.map((paper) => paper.year).filter(Boolean))].sort().reverse().forEach((value) => year.add(new Option(value, value)));
      if ([...year.options].some((option) => option.value === selected)) year.value = selected;
    }

    async function load(force = false) {
      status.textContent = "正在查询论文…";
      results.setAttribute("aria-busy", "true");
      input.disabled = true;
      year.disabled = true;
      retry.hidden = true;
      previous.disabled = true;
      next.disabled = true;
      try {
        let cached;
        if (!force) {
          try { cached = JSON.parse(sessionStorage.getItem(cacheKey)); } catch (_) { /* storage is optional */ }
        }
        if (cached && Date.now() - cached.time < CACHE_AGE && Array.isArray(cached.papers)) {
          papers = cached.papers;
          partial = false;
        } else {
          const responses = await Promise.allSettled([
            requestWorks({ filter: `orcid:https://orcid.org/${orcid},type:journal-article`, rows: "200" }),
            requestWorks({ "query.author": name, filter: "type:journal-article", rows: "200" }),
          ]);
          const successful = responses.filter((response) => response.status === "fulfilled");
          if (!successful.length) throw new Error("Sources unavailable");
          partial = successful.length !== responses.length;
          papers = mergeWorks(successful.map((response) => response.value), name, orcid);
          if (!partial) {
            try { sessionStorage.setItem(cacheKey, JSON.stringify({ time: Date.now(), papers })); } catch (_) { /* storage is optional */ }
          }
        }
        populateYears();
        page = 0;
        render();
      } catch (_) {
        papers = [];
        status.textContent = "暂时无法连接论文来源";
        results.replaceChildren(element("p", "group-papers-empty", "请稍后重试，或使用下方的 Crossref 链接查询。"));
        pageLabel.textContent = "";
        retry.hidden = false;
      } finally {
        results.setAttribute("aria-busy", "false");
        input.disabled = !papers.length;
        year.disabled = !papers.length;
      }
    }

    input.addEventListener("input", () => { page = 0; render(); });
    year.addEventListener("change", () => { page = 0; render(); });
    previous.addEventListener("click", () => { page -= 1; render(); });
    next.addEventListener("click", () => { page += 1; render(); });
    retry.addEventListener("click", () => load(true));
    load();
  }

  const enhance = () => document.querySelectorAll("[data-group-papers]").forEach(setup);
  document.addEventListener("DOMContentLoaded", enhance);
  if (typeof document$ !== "undefined") document$.subscribe(enhance);
})();
