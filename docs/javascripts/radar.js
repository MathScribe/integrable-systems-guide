(() => {
  const ROLE_LABELS = new Set([
    "近期进展",
    "近期漏读",
    "正式版本",
    "课题组相关",
    "方法基础",
    "综述地图",
    "核心旧文",
    "相邻方向",
    "自动整理",
  ]);

  function isRadarPage() {
    const heading = document.querySelector("article.md-content__inner > h1");
    const title = heading ? heading.textContent.trim() : "";
    return title === "可积系统研究雷达" || title.startsWith("研究雷达归档");
  }

  function directParagraphs(nodes) {
    return nodes.filter((node) => node.tagName === "P");
  }

  function paragraphLabel(paragraph) {
    const strong = paragraph.querySelector(":scope > strong:first-child");
    return strong ? strong.textContent.trim().replace(/[。．:]$/, "") : "";
  }

  function cleanTags(paragraph) {
    if (!paragraph) return null;
    [...paragraph.querySelectorAll("code")].forEach((code) => {
      if (ROLE_LABELS.has(code.textContent.trim())) code.remove();
    });
    if (!paragraph.textContent.trim()) paragraph.remove();
    return paragraph;
  }

  function strippedClone(paragraph) {
    const clone = paragraph.cloneNode(true);
    const strong = clone.querySelector(":scope > strong:first-child");
    if (strong) strong.remove();
    return clone.innerHTML.trim();
  }

  function makeDetailSection(title, paragraph) {
    const section = document.createElement("section");
    const heading = document.createElement("h4");
    heading.textContent = title;
    section.appendChild(heading);

    const body = document.createElement("p");
    body.innerHTML = strippedClone(paragraph);
    section.appendChild(body);
    return section;
  }

  function enhanceEntry(heading) {
    if (heading.dataset.radarEnhanced === "true") return;

    const nodes = [];
    let cursor = heading.nextElementSibling;
    while (cursor && !["H2", "H3", "HR"].includes(cursor.tagName)) {
      const next = cursor.nextElementSibling;
      nodes.push(cursor);
      cursor = next;
    }
    if (!nodes.length) return;

    const paragraphs = directParagraphs(nodes);
    if (!paragraphs.length) return;

    const detailParagraphs = paragraphs.filter((paragraph) => {
      const label = paragraphLabel(paragraph);
      return ["做了什么", "为什么值得读", "研究问题与主要结果", "可积结构与方法", "创新"].includes(label);
    });

    const card = document.createElement("article");
    card.className = "radar-paper-card";
    heading.parentNode.insertBefore(card, heading);
    card.appendChild(heading);
    heading.dataset.radarEnhanced = "true";

    const nonDetailParagraphs = paragraphs.filter((paragraph) => !detailParagraphs.includes(paragraph));
    const meta = nonDetailParagraphs.shift();
    if (meta) {
      meta.classList.add("radar-paper-meta");
      card.appendChild(meta);
    }

    const tagParagraph = cleanTags(nonDetailParagraphs.find((paragraph) => paragraph.querySelector("code")));
    if (tagParagraph && tagParagraph.isConnected) {
      tagParagraph.classList.add("radar-paper-tags");
      card.appendChild(tagParagraph);
    }

    const overviewSource = detailParagraphs[0] || nonDetailParagraphs.find((paragraph) => paragraph !== tagParagraph);
    if (overviewSource) {
      const overview = document.createElement("p");
      overview.className = "radar-paper-overview";
      overview.innerHTML = strippedClone(overviewSource);
      card.appendChild(overview);
    }

    if (detailParagraphs.length) {
      const details = document.createElement("details");
      details.className = "radar-paper-details";
      const summary = document.createElement("summary");
      summary.textContent = "展开研究内容与创新";
      details.appendChild(summary);

      const grid = document.createElement("div");
      grid.className = "radar-paper-detail-grid";

      const mapped = new Map(detailParagraphs.map((paragraph) => [paragraphLabel(paragraph), paragraph]));
      const main = mapped.get("研究问题与主要结果") || mapped.get("做了什么");
      const structure = mapped.get("可积结构与方法");
      const innovation = mapped.get("创新") || mapped.get("为什么值得读");

      if (main) grid.appendChild(makeDetailSection("研究问题与主要结果", main));
      if (structure) grid.appendChild(makeDetailSection("可积结构与方法", structure));
      if (innovation) grid.appendChild(makeDetailSection("创新", innovation));

      details.appendChild(grid);
      card.appendChild(details);
    }

    nodes.forEach((node) => {
      if (node.isConnected && node !== meta && node !== tagParagraph) node.remove();
    });
  }

  function enhanceRadar() {
    if (!isRadarPage()) return;
    const root = document.querySelector("article.md-content__inner");
    if (!root) return;
    [...root.querySelectorAll(":scope > h3")].forEach(enhanceEntry);
  }

  document.addEventListener("DOMContentLoaded", enhanceRadar);
  if (typeof document$ !== "undefined") document$.subscribe(enhanceRadar);
})();
