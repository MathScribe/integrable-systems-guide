const assert = require("node:assert/strict");
const { filterEntries, paginate, fold } = require("../docs/javascripts/radar.js");
const all = { q: "", period: "all", topic: "", from: "", to: "" };
const rows = [
  { date: "2026-09-26", week: "2026-W39", tags: ["inverse scattering"], search: fold("Schrödinger inverse scattering Lin") },
  { date: "2026-08-28", week: "2026-W35", tags: ["Painlevé"], search: fold("Painlevé geometry") },
  { date: "2026-08-27", week: "2026-W35", tags: ["inverse scattering"], search: fold("Old scattering") },
  { date: "2026-09-27", week: "2026-W39", tags: [], search: fold("Future event") },
];
assert.equal(filterEntries(rows, all).length, 4);
assert.equal(filterEntries(rows, { ...all, q: "schrodinger lin" }).length, 1);
assert.equal(filterEntries(rows, { ...all, topic: "inverse scattering" }).length, 2);
assert.equal(filterEntries(rows, { ...all, period: "30" }, "2026-09-26").length, 2);
assert.equal(filterEntries(rows, { ...all, period: "week:2026-W35" }).length, 2);
assert.equal(filterEntries(rows, { ...all, period: "custom", from: "2026-08-28", to: "2026-08-28" }).length, 1);
assert.equal(filterEntries(rows, { ...all, period: "custom", from: "2026-09-26", to: "2026-08-28" }).length, 0);
assert.equal(filterEntries(rows, { ...all, topic: "Painlevé", q: "scattering" }).length, 0);
const many = Array.from({ length: 41 }, (_, id) => ({ id }));
assert.equal(paginate(many, 1).entries.length, 20);
assert.equal(paginate(many, 2).entries[0].id, 20);
assert.equal(paginate(many, 999).entries[0].id, 40);
assert.equal(paginate(many, -1).page, 1);
assert.equal(paginate([], 2).pages, 0);
console.log("radar search, date ranges, combined filters, and pagination checks passed");
