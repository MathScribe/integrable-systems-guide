#!/usr/bin/env python3
"""Validate staged or enabled compact-radar records in data/editions.yml."""

from __future__ import annotations

import importlib.util
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("render_radar", ROOT / "scripts" / "render_radar.py")
if SPEC is None or SPEC.loader is None:
    raise RuntimeError("cannot load scripts/render_radar.py")
render_radar = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(render_radar)

FORBIDDEN_PUBLIC_TERMS = (
    "新意",
    "创新后果",
    "核心前沿",
    "相邻前沿",
    "结构推进",
    "结构驱动创新",
    "自动整理",
    "谱控制",
)
FORBIDDEN_CONTENT_MARKERS = (
    "## ",
    "本轮值得关注的方向信号",
    "下一步",
    "reviewable PR",
    "自动合并",
)
PUBLIC_TEXT_FIELDS = ("summary", "main_result", "integrable_structure", "innovation")
CONTROLLED_STRUCTURE_TAGS = {
    "AKNS hierarchy",
    "2D Toda hierarchy",
    "Ablowitz--Ladik hierarchy",
    "Drinfeld--Sokolov hierarchy",
    "mKdV hierarchy",
    "Painlevé hierarchy",
    "Riemann--Hilbert problem",
    "nonlinear steepest descent",
    "inverse scattering",
    "Darboux transformation",
    "Bäcklund transformation",
    "Yang--Baxter equation",
    "Lax pair",
    "Hamiltonian structure",
    "Poisson structure",
    "Frobenius manifold",
    "finite-gap",
    "spectral curve",
    "Painlevé",
    "isomonodromy",
    "tau function",
    "integrable discretization",
    "recursion operator",
    "soliton gas",
    "soliton resolution",
    "generalized hydrodynamics",
    "loop equations",
    "integrable probability",
    "quantum integrability",
    "transfer matrix",
    "Bethe ansatz",
    "Chern--Simons theory",
    "inverse problem",
    "conservation laws",
    "symplectic geometry",
    "integrable geometry",
    "topological vector potential",
    "wave kinetics",
    "multiple orthogonal polynomials",
    "Laurent property",
    "Pfaffian",
    "bilinear method",
    "squared eigenfunctions",
    "Poisson--Lie geometry",
}


def main() -> None:
    data = yaml.safe_load((ROOT / "data" / "editions.yml").read_text(encoding="utf-8"))
    frontier = data.get("frontier") or data.get("frontier_staging")
    if frontier is None:
        print("no compact radar records staged")
        return

    papers = render_radar.paper_map()
    entries = render_radar.validate_frontier(frontier, papers)
    for entry in entries:
        for field in PUBLIC_TEXT_FIELDS:
            text = str(entry[field])
            for term in FORBIDDEN_PUBLIC_TERMS:
                if term in text:
                    raise ValueError(
                        f"{entry['paper_id']}.{field} contains deprecated public wording: {term}"
                    )
            for marker in FORBIDDEN_CONTENT_MARKERS:
                if marker in text:
                    raise ValueError(
                        f"{entry['paper_id']}.{field} contains report or workflow residue: {marker}"
                    )

        for tag in entry.get("structure_tags", []):
            if tag not in CONTROLLED_STRUCTURE_TAGS:
                raise ValueError(f"{entry['paper_id']} has uncontrolled structure tag: {tag}")

    dates = [entry["signal_date"] for entry in entries]
    print(
        f"validated {len(entries)} compact radar records "
        f"from {min(dates)} through {max(dates)}"
    )


if __name__ == "__main__":
    main()
