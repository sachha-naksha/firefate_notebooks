# Setup for the temporal notebooks

Two things have to be true before any notebook in `trajectory/`, `dynamic_grn/` or
`analysis/` runs: `firefate` must be importable in the kernel, and `datasets.yaml` must
point at your copies of the data. Nothing here is notebook-specific — do it once per
machine.

## 1. Install the FIREFate backend (editable)

The notebooks import `firefate` as an ordinary package; there is no `sys.path`
bootstrap any more. Install the main repository in editable mode **into the same
environment whose kernel the notebooks use** (`dictys` on our cluster):

```bash
source /sw/rh9.4/python/miniforge3/etc/profile.d/conda.sh
conda activate dictys

git clone https://github.com/sachha-naksha/FIREFate      # or use your existing clone
cd FIREFate
pip install -e .
```

`-e` means edits under `src/firefate/` are picked up on the next kernel restart — no
reinstall. Verify from the same environment:

```bash
python -c "import firefate, firefate.io; print(firefate.__file__)"
```

The path printed must be your clone's `src/firefate/__init__.py`, not a copy under
`site-packages/`. If it is not, you installed into a different environment.

If you would rather not leave the notebook, `%pip install -e /path/to/FIREFate` in the
first cell installs into the running kernel's environment; restart the kernel after.

### Optional extras

`pyproject.toml` declares only the numeric/plotting core as required. Add what a given
notebook needs:

```bash
pip install -e ".[scanpy]"      # scanpy
pip install -e ".[dev]"         # pytest
pip install -e ".[docs]"        # sphinx + myst-nb, only for building the docs
```

**Not** declared anywhere, and **not** installed by the line above: `dictys` (every
`dynamic_grn/` and most `analysis/` notebooks), and `stream` / `palantir` / `scvelo` /
`multivelo` / `cellrank` / `velocyto` (the `trajectory/` notebooks). Those have
conflicting pins, which is why they live in separate conda environments here rather
than in `dependencies`. Match the environment to the notebook directory.

## 2. Point `datasets.yaml` at your data

Every dataset location for these notebooks lives in `temporal/datasets.yaml`. Edit that
file — never the notebooks, and never `src/firefate/`, which is why the paths were
moved out of the package in the first place.

### The three sections

```yaml
roots:                                  # reusable prefixes; may reference each other
  bcell: /work/nvme/bhdw/asachan/data_files/firefate/bcell
  inputs: "{bcell}/outs/intermediate_tmp_files"

scalars:                                # one path per name
  OUTPUT_FOLDER: "{figures}"
  CELL_LABELS: "{bcell}/data/clusters.csv"

groups:                                 # one path per episode
  PB:
    template: "{enrichment}/enrichment_ep{i}_pb.csv"
    n_episodes: 4
```

* `{name}` is substituted from `roots`. Roots may refer to other roots — they are
  expanded repeatedly until stable, so ordering does not matter.
* `{i}` in a group `template` is the episode number.
* A group needs **either** `n_episodes: 4` (meaning 1…4) **or** an explicit
  `episodes: [1, 2, 5]` when the numbering has gaps. Giving neither raises `KeyError`.
* Quote any value containing `{`, otherwise YAML reads it as a flow mapping.

### Loading it

`from_yaml` resolves relative paths against the kernel's working directory, which in
Jupyter is the notebook's own directory. The notebooks sit one level below the config,
so:

```python
from firefate.io import DatasetPaths

config = DatasetPaths.from_yaml("../datasets.yaml")   # from analysis/, dynamic_grn/, trajectory/
config.OUTPUT_FOLDER          # scalar -> str
config.PB["ep1"]              # group  -> path for episode 1
config.load_enrichment("PB")  # the group's CSVs, in episode order, p_value < 0.05
```

Keep the variable named `config`: the notebooks were written against an older
`Config()` class with the same attribute names, so every downstream
`config.OUTPUT_FOLDER` / `config.PB['ep1']` keeps working unchanged. Unknown names
raise `AttributeError` listing the scalars and groups that *are* defined, so a typo
fails at the top of the notebook rather than three cells in.

### Check it before running anything

```python
from pathlib import Path

for name, path in config.scalars.items():
    print(f"{'ok     ' if Path(path).exists() else 'MISSING'}  {name}  {path}")

for name, episodes in config.groups.items():
    present = sum(Path(p).exists() for p in episodes.values())
    print(f"{name}: {present}/{len(episodes)} episode files present")
```

`load_enrichment` returns an empty frame for a missing episode by default so partial
runs still line up positionally; pass `missing_ok=False` if you would rather it raise.

### Keeping your paths out of git

The committed `datasets.yaml` records the paths these notebooks were run against, and
the `tcell` root is a PSC `/ocean/...` path that no longer resolves on this cluster.
Rather than committing a rewrite of it, copy it:

```bash
cp datasets.yaml datasets.local.yaml     # edit this one
echo "datasets.local.yaml" >> ../.gitignore
```

and load `"../datasets.local.yaml"`. Only commit a change to `datasets.yaml` itself
when the canonical location of a dataset actually moves.

## 3. Known gap — the notebooks are not fully migrated yet

The committed notebooks still open with `config = Config()` and stale imports
(`firefate.core.pseudotime_curves`, `firefate.enrichment`, `firefate.utils.plots`) from
the layout that preceded the `temporal` / `state_specific` / `cross_prediction` split.
Steps 1 and 2 are what make the replacement cells work, but they do not rewrite the
cells for you. `../NOTEBOOK_MIGRATION.md` gives the OLD → NEW block for each notebook;
in short, `from firefate.temporal import *` now covers the classes and their figures,
and `Config()` becomes `DatasetPaths.from_yaml(...)`. Paste the new cell, restart the
kernel, re-run.
