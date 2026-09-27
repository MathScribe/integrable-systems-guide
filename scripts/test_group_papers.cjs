const assert = require("node:assert/strict");
const { belongsToAuthor, mergeWorks, filterWorks, normalizeWork } = require("../docs/javascripts/group-papers.js");
const name = "Liming Ling";
const orcid = "0000-0002-3051-4366";
const paper = {
  DOI: "10.0000/EXAMPLE",
  title: ["Inverse scattering for a nonlinear Schrödinger equation"],
  author: [{ given: "Liming", family: "Ling" }],
  "container-title": ["Example Journal"],
  published: { "date-parts": [[2026, 9, 22]] },
  "published-print": { "date-parts": [[2027, 1]] },
};
assert(belongsToAuthor(paper, name, orcid));
assert(!belongsToAuthor({ ...paper, title: ["Serotonin and NMDA receptors in respiratory long-term facilitation"] }, name, orcid));
assert(!belongsToAuthor({ ...paper, author: [{ given: "Liming", family: "Lin" }] }, name, orcid));
assert(!belongsToAuthor({ ...paper, author: [{ given: "Liming", family: "Ling", ORCID: "https://orcid.org/0000-0000-0000-0000" }] }, name, orcid));
assert(belongsToAuthor({ ...paper, title: ["A new research direction"], author: [{ given: "L.", family: "Ling", ORCID: `https://orcid.org/${orcid}` }] }, name, orcid));
const merged = mergeWorks([[paper], [{ ...paper, DOI: paper.DOI.toLowerCase() }]], name, orcid);
assert.equal(merged.length, 1);
assert.equal(merged[0].year, "2027"); // Citation year, not an invented first-online date.
assert.equal(filterWorks(merged, "scattering", "2027").length, 1);
assert.equal(filterWorks(merged, "scattering", "2026").length, 0);
assert.equal(filterWorks(merged, "example journal", "").length, 1);
assert.equal(normalizeWork({ title: ["<i>N</i>-solitons"], author: [] }).title, "N-solitons");
assert.equal(normalizeWork({}).year, "");
assert.equal(normalizeWork({ "container-title": ["Chaos, Solitons &amp; Fractals"] }).journal, "Chaos, Solitons & Fractals");
console.log("group publication identity, deduplication, and filtering checks passed");
