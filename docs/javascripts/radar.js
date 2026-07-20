(() => {
  function enableWeekFilter(root) {
    const navigation = root.querySelector(":scope > .radar-week-navigation");
    if (!navigation || navigation.dataset.radarReady === "true") return;

    const weekOptions = [...navigation.querySelectorAll("[data-radar-week-option]")].map((option) => ({
      id: option.dataset.radarWeekOption,
      label: option.dataset.label,
      count: Number(option.dataset.count),
    }));
    const cards = [...root.querySelectorAll(":scope > article.radar-paper-card[data-radar-week]")];
    const monthMarkers = [...root.querySelectorAll(":scope > .radar-month-label[data-radar-month-group]")];
    const screeningNotes = [...root.querySelectorAll(":scope > .radar-week-overview[data-radar-screening-week]")];
    const current = navigation.querySelector(".radar-week-current");
    const older = navigation.querySelector('[data-radar-action="older"]');
    const newer = navigation.querySelector('[data-radar-action="newer"]');
    const showAll = navigation.querySelector('[data-radar-action="all"]');
    const searchInput = navigation.querySelector("#radar-paper-search");
    const searchCount = navigation.querySelector(".radar-search-count");
    if (!weekOptions.length || !current || !older || !newer || !showAll || !searchInput || !searchCount) return;

    let currentIndex = 0;
    let showingAll = false;
    const toc = document.querySelector(".md-sidebar--secondary .md-nav--secondary");

    function rebuildToc(selected) {
      if (!toc) return;
      const title = toc.querySelector(":scope > .md-nav__title");
      const list = toc.querySelector(":scope > .md-nav__list");
      if (!list) return;
      if (title) title.textContent = selected === "all" ? "论文目录" : "本期论文";
      list.replaceChildren();

      function makeLink(item) {
        const li = document.createElement("li");
        li.className = "md-nav__item";
        const link = document.createElement("a");
        link.className = "md-nav__link";
        link.href = item.href;
        const span = document.createElement("span");
        span.className = "md-ellipsis";
        span.textContent = item.label;
        link.appendChild(span);
        li.appendChild(link);
        return li;
      }

      if (selected === "all") {
        monthMarkers.filter((marker) => !marker.hidden).forEach((marker) => {
          const monthItem = makeLink({ href: `#${marker.id}`, label: marker.textContent.trim() });
          const nested = document.createElement("nav");
          nested.className = "md-nav";
          const nestedList = document.createElement("ul");
          nestedList.className = "md-nav__list";
          cards
            .filter((card) => !card.hidden && card.dataset.radarMonth === marker.dataset.radarMonthGroup)
            .forEach((card) => {
              nestedList.appendChild(makeLink({
                href: `#${card.id}`,
                label: card.querySelector("h3")?.textContent.trim() || card.id,
              }));
            });
          nested.appendChild(nestedList);
          monthItem.appendChild(nested);
          list.appendChild(monthItem);
        });
      } else {
        cards
          .filter((card) => !card.hidden && card.dataset.radarWeek === selected)
          .forEach((card) => {
            list.appendChild(makeLink({
              href: `#${card.id}`,
              label: card.querySelector("h3")?.textContent.trim() || card.id,
            }));
          });
      }
    }

    function applySearch() {
      const selected = weekOptions[currentIndex];
      const query = searchInput.value.trim().toLocaleLowerCase();
      let visibleCount = 0;

      cards.forEach((card) => {
        const inScope = showingAll || card.dataset.radarWeek === selected.id;
        const matches = !query || card.textContent.toLocaleLowerCase().includes(query);
        card.hidden = !(inScope && matches);
        if (!card.hidden) visibleCount += 1;
      });

      monthMarkers.forEach((marker) => {
        marker.hidden = !showingAll || !cards.some((card) => (
          !card.hidden && card.dataset.radarMonth === marker.dataset.radarMonthGroup
        ));
      });
      screeningNotes.forEach((note) => {
        note.hidden = showingAll || note.dataset.radarScreeningWeek !== selected.id;
      });

      searchCount.textContent = query ? `找到 ${visibleCount} 篇` : "";
      rebuildToc(showingAll ? "all" : selected.id);
    }

    function showWeek(index) {
      currentIndex = Math.max(0, Math.min(index, weekOptions.length - 1));
      showingAll = false;
      const selected = weekOptions[currentIndex];
      root.classList.remove("radar-all-mode");
      current.textContent = `${selected.label} · ${selected.count} 篇`;
      older.disabled = currentIndex >= weekOptions.length - 1;
      newer.disabled = currentIndex <= 0;
      older.hidden = false;
      newer.hidden = false;
      showAll.textContent = "查看全部";
      applySearch();
    }

    function showAllPapers() {
      showingAll = true;
      root.classList.add("radar-all-mode");
      current.textContent = `全部论文 · ${navigation.dataset.totalCount} 篇`;
      older.hidden = true;
      newer.hidden = true;
      showAll.textContent = "返回最新一周";
      applySearch();
    }

    older.addEventListener("click", () => showWeek(currentIndex + 1));
    newer.addEventListener("click", () => showWeek(currentIndex - 1));
    showAll.addEventListener("click", () => {
      if (showingAll) showWeek(0);
      else showAllPapers();
    });
    searchInput.addEventListener("input", applySearch);

    const defaultWeek = navigation.dataset.defaultWeek;
    const defaultIndex = weekOptions.findIndex((option) => option.id === defaultWeek);
    showWeek(defaultIndex >= 0 ? defaultIndex : 0);
    navigation.dataset.radarReady = "true";
  }

  function enhanceRadar() {
    const root = document.querySelector("article.md-content__inner");
    if (!root) return;
    enableWeekFilter(root);
  }

  document.addEventListener("DOMContentLoaded", enhanceRadar);
  if (typeof document$ !== "undefined") document$.subscribe(enhanceRadar);
})();
