#!/usr/bin/env python3
"""Prepend a level-1 markdown title cell to each notebook.

Why this exists
---------------
Sphinx builds a page's title from its single top-level heading. Most of these
notebooks either open on a code cell, start at ``##``/``###``, or carry several
``#`` headings, so the rendered page has no document title. When that happens
Sphinx ignores the explicit title given in the ``toctree`` and falls back to the
first section heading -- and for a notebook with no markdown at all it emits
``toctree contains reference to document ... that doesn't have a title: no link
will be generated``, leaving the page unreachable from the sidebar.

One ``# Title`` cell at the top of each notebook fixes all of that.

Usage
-----
Dry run (default) prints what would change::

    python add_titles.py

Write the cells::

    python add_titles.py --apply

Safe to re-run: a notebook whose first cell is already a level-1 markdown
heading is left untouched. Only ``cells[0]`` is inserted -- no existing cell,
output, or metadata is modified.

Close these notebooks in Jupyter before running with ``--apply``; an open kernel
will otherwise overwrite the change when it next autosaves.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

#: Page title for each notebook, matching the toctree entries in the index files.
TITLES = {
    "state_specific/01_sc_preproc.ipynb": "Single-cell preprocessing",
    "state_specific/02_grn_inference.ipynb": "State-specific GRN inference",
    "state_specific/02_1_predisposed_plotting.ipynb": "Predisposed-population figures",
    "state_specific/03_1_cicero.ipynb": "Cicero co-accessibility",
    "state_specific/03_lf_enrich.ipynb": "Latent-factor enrichment",
    "state_specific/04_plotting.ipynb": "Result figures",
    "state_specific/perturbation/PS_Bcell_dynamic.ipynb": "Perturbation score — B cell",
    "state_specific/perturbation/PS_Tonsil_dynamic.ipynb": "Perturbation score — tonsil",
    "temporal/trajectory/traj_stream_male_donor.ipynb": "STREAM trajectory — male donor",
    "temporal/trajectory/traj_stream_female_donor.ipynb": "STREAM trajectory — female donor",
    "temporal/trajectory/imputation_male_donor.ipynb": "Expression imputation — male donor",
    "temporal/trajectory/imputation_female_donor.ipynb": "Expression imputation — female donor",
    "temporal/trajectory/b_cell_velocity.ipynb": "B-cell RNA velocity (MultiVelo)",
    "temporal/trajectory/t_cell_trajectory.ipynb": "T-cell trajectory",
    "temporal/trajectory/t_cell_imputation.ipynb": "T-cell expression imputation",
    "temporal/dynamic_grn/data_prep_and_checks.ipynb": "Preparing and checking dictys inputs",
    "temporal/dynamic_grn/dynamic_grn_b_cell.ipynb": "B-cell dynamic GRN reconstruction",
    "temporal/dynamic_grn/t_cell_dictys_data.ipynb": "T-cell dictys inputs",
    "temporal/analysis/LF_global_dynamics.ipynb": "Global regulation of a latent factor",
    "temporal/analysis/LF_local_dynamics.ipynb": "Episodic regulation of a latent factor",
    "temporal/analysis/episodic_enrichment.ipynb": "Episodic TF enrichment",
    "temporal/analysis/phase_clustered_links.ipynb": "Clustering links into regulatory phases",
    "temporal/analysis/chromatin_dynamics.ipynb": "TF binding dynamics from chromatin",
    "temporal/analysis/dynamic_validation.ipynb": "Validation — enriched vs random TF force",
    "temporal/analysis/t_cell_analysis.ipynb": "T-cell episodic analysis",
}

ROOT = Path(__file__).resolve().parent


def has_title_cell(nb: dict) -> bool:
    """True when ``cells[0]`` is already a level-1 markdown heading."""
    cells = nb.get("cells") or []
    if not cells or cells[0].get("cell_type") != "markdown":
        return False
    first = "".join(cells[0].get("source", [])).lstrip()
    return bool(re.match(r"^#\s+\S", first))


def title_cell(title: str) -> dict:
    return {"cell_type": "markdown", "metadata": {}, "source": [f"# {title}"]}


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "--apply", action="store_true", help="Write the changes. Default is a dry run."
    )
    args = parser.parse_args(argv)

    changed = skipped = missing = 0
    for rel, title in TITLES.items():
        path = ROOT / rel
        if not path.is_file():
            print(f"  MISSING  {rel}")
            missing += 1
            continue

        nb = json.loads(path.read_text())
        if has_title_cell(nb):
            skipped += 1
            continue

        changed += 1
        if not args.apply:
            print(f"  would add  # {title:45} -> {rel}")
            continue

        nb.setdefault("cells", []).insert(0, title_cell(title))
        # nbformat writes a trailing newline; match it so diffs stay minimal.
        path.write_text(json.dumps(nb, indent=1, ensure_ascii=False) + "\n")
        print(f"  added  # {title:45} -> {rel}")

    verb = "added" if args.apply else "to add"
    print(f"\n{changed} {verb}, {skipped} already titled, {missing} missing")
    if changed and not args.apply:
        print("Re-run with --apply to write them.")
    return 1 if missing else 0


if __name__ == "__main__":
    sys.exit(main())
