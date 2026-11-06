/* Progressive enhancement: descriptions and source links work without JS. */
(() => {
  "use strict";
  function init() {
    const root = document.querySelector("[data-problems]");
    if (!root || root.dataset.ready) return;
    root.dataset.ready = "true";
    const cards = [...root.querySelectorAll(".problem-card")];
    const query = root.querySelector("[data-problem-query]");
    const reset = root.querySelector("[data-problem-reset]");
    const searchText = new Map(cards.map(card => [card,
      card.querySelector("textarea").value.normalize("NFKC").toLowerCase()]));
    function filter() {
      const terms = query.value.normalize("NFKC").trim().toLowerCase().split(/\s+/).filter(Boolean);
      let count = 0;
      cards.forEach(card => {
        const match = terms.every(term => searchText.get(card).includes(term));
        card.hidden = !match;
        if (match) count += 1;
      });
      root.querySelector("[data-problem-count]").textContent = `显示 ${count} / ${cards.length} 个问题`;
      root.querySelector("[data-problem-empty]").hidden = count !== 0;
      reset.hidden = !terms.length;
    }
    function clear() { query.value = ""; filter(); }
    query.addEventListener("input", filter);
    reset.addEventListener("click", () => { clear(); query.focus(); });
    root.querySelector("[data-problem-clear]").addEventListener("click", () => { clear(); query.focus(); });
    function revealHash() {
      const card = cards.find(item => `#${item.id}` === location.hash);
      if (!card) return;
      clear();
      card.querySelector(".problem-body").open = true;
      requestAnimationFrame(() => card.scrollIntoView({ block: "start" }));
    }
    window.addEventListener("hashchange", revealHash);
    cards.forEach(card => card.querySelector("h2 a").addEventListener("click", () => {
      clear();
      card.querySelector(".problem-body").open = true;
    }));
    root.querySelector(".problems-controls").hidden = false;
    root.querySelectorAll("[data-copy-target]").forEach(button => {
      button.hidden = false;
      button.addEventListener("click", async () => {
        const text = document.getElementById(button.dataset.copyTarget);
        const status = button.parentElement.querySelector("[role=status]");
        button.disabled = true;
        let copied = false;
        try {
          if (navigator.clipboard && window.isSecureContext) {
            await navigator.clipboard.writeText(text.value);
            copied = true;
          }
        } catch (_) { /* Fall back to a selectable text field. */ }
        if (!copied) {
          text.hidden = false;
          text.focus();
          text.select();
          try { copied = document.execCommand("copy"); } catch (_) { /* Manual copy remains available. */ }
        }
        button.disabled = false;
        if (copied) {
          text.hidden = true;
          status.textContent = "已复制（含公式与来源）";
          button.focus();
        } else {
          status.textContent = "自动复制未成功；下方文字已选中，请按 Ctrl/Cmd+C 复制。";
        }
      });
    });
    filter();
    revealHash();
  }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", init);
  else init();
  if (typeof document$ !== "undefined") document$.subscribe(init);
})();
