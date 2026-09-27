const assert = require("node:assert/strict");
const { filterEntries, paginate, fold, defaultDateRange } = require("../docs/javascripts/radar.js");
const all = { q: "", period: "all", topic: "", from: "", to: "" };
const rows = [
  { date: "2026-09-26", directions: ["spectral", "waves"], search: fold("Schrödinger inverse scattering Lin") },
  { date: "2026-08-28", directions: ["structures"], search: fold("Painlevé geometry") },
  { date: "2026-08-27", directions: ["spectral"], search: fold("Old scattering") },
  { date: "2026-09-27", directions: ["waves"], search: fold("Future event") },
];
assert.equal(filterEntries(rows, all).length, 4);
assert.equal(filterEntries(rows, { ...all, q: "schrodinger lin" }).length, 1);
assert.equal(filterEntries(rows, { ...all, topic: "spectral" }).length, 2);
assert.equal(filterEntries(rows, { ...all, topic: "waves" }).length, 2);
assert.equal(filterEntries(rows, { ...all, period: "30" }, "2026-09-26").length, 2);
assert.equal(filterEntries(rows, { ...all, period: "custom", from: "2026-08-28", to: "2026-08-28" }).length, 1);
assert.equal(filterEntries(rows, { ...all, period: "custom", from: "2026-09-26", to: "2026-08-28" }).length, 0);
assert.equal(filterEntries(rows, { ...all, topic: "structures", q: "scattering" }).length, 0);
assert.equal(filterEntries(rows, { ...all, topic: "spectral", period: "custom", from: "2026-09-01", to: "2026-09-26" }).length, 1);
assert.deepEqual(defaultDateRange("", "", "2026-06-15", "2026-09-27"), { from: "2026-06-15", to: "2026-09-27" });
assert.deepEqual(defaultDateRange("2026-01-01", "2026-02-01", "2026-06-15", "2026-09-27"), { from: "2026-01-01", to: "2026-02-01" });
assert.deepEqual(defaultDateRange("2026-08-01", "", "2026-06-15", "2026-09-28"), { from: "2026-08-01", to: "2026-09-28" });
const many = Array.from({ length: 41 }, (_, id) => ({ id }));
assert.equal(paginate(many, 1).entries.length, 20);
assert.equal(paginate(many, 2).entries[0].id, 20);
assert.equal(paginate(many, 999).entries[0].id, 40);
assert.equal(paginate(many, -1).page, 1);
assert.equal(paginate([], 2).pages, 0);
console.log("radar search, date ranges, combined filters, and pagination checks passed");
