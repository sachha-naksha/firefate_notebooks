# FIREFate notebooks

All code notebooks for reproducibility, for
[**FIREFate**](https://github.com/sachha-naksha/FIREFate) — Functional and Interpretable
Regulatory Encoding of cellular Fate.

This repository is consumed as a git submodule at `docs/notebooks` in the main
repository, and rendered into the documentation at
[firefate.readthedocs.io](https://firefate.readthedocs.io/). Keeping the notebooks
here keeps ~26 MB of stored cell outputs out of the source tree while still letting the
docs render them.

## Layout

Notebooks are grouped by the FIREFate module they exercise, mirroring `src/firefate/`:

| directory | module | what it covers |
|---|---|---|
| `temporal/` | `firefate.temporal` | trajectory inference, dynamic GRNs, episodic GRNs and their enrichment (capabilities 3, 4, dynamic 5) |
| `state_specific/` | `firefate.state_specific` | preprocessing, state-specific GRN inference, latent-factor enrichment, in-silico perturbation (capabilities 1, 2, static 5, 6) |
| `cross_prediction/` | `firefate.cross_prediction` | fate-bias stratification by transferring programs across datasets (capability 7) — empty until that module is ported |

Within `temporal/`, `trajectory/` comes first (STREAM/Palantir/MultiVelo pseudotime),
then `dynamic_grn/` (dictys inputs and window networks), then `analysis/` (everything
built on top of the reconstructed networks).

## Running them

These are **research records, not tutorials.** They were run on a SLURM cluster against
data that is not distributed with either repository, and their paths reflect that. To
re-run one you need:

1. The `fftemporal` environment, which pins `dictys` 1.1.0 and the rest of the
   runtime stack it needs — `pytorch` 2.3.1 (CUDA 11.8), `gimmemotifs`, `genomepy`,
   `homer`, `macs2`, `samtools`, `bedtools`:
   ```bash
   conda env create -f environment.yml
   conda activate fftemporal
   ```
2. `firefate` on top of it, editable from your own clone. It is deliberately **not**
   in `environment.yml`: the package is under active development, so the environment
   tracks whatever you have checked out rather than a pinned snapshot. `--no-deps`
   keeps pip from re-resolving packages conda already placed:
   ```bash
   git clone https://github.com/sachha-naksha/FIREFate
   pip install -e FIREFate --no-deps
   ```
3. Dataset paths pointed at your own copies. Every path lives in
   `temporal/datasets.yaml` — edit that file, not the notebooks. Each temporal
   notebook already opens with the loader cell that reads it:
   ```python
   from firefate.io import DatasetPaths
   config = DatasetPaths.from_yaml("../datasets.yaml")
   ```
   `temporal/SETUP.md` explains which roots are live on this cluster and which are
   dead PSC paths you have to repoint first.
4. For the trajectory notebooks only, `stream` / `palantir` / `scvelo` / `multivelo`.
   These are **not** in `environment.yml` and should not be added to it: `dictys`
   holds `anndata` at 0.6.22.post1, which is far older than those packages (and than
   current `scanpy`, also absent here) expect. Build a separate environment for the
   trajectory step and carry its output forward as files.

### Regenerating environment.yml

`environment.yml` is an export of the working `fftemporal` environment with the
`firefate` line stripped, since that entry refers to a local editable install and
resolves for nobody else:

```bash
conda env export -n fftemporal --no-builds \
  | sed -e '/^      - firefate==/d' -e '/^prefix: /d' > environment.yml
```

It pins exact versions and is linux-64 only — the `homer` / `macs2` / `samtools`
dependencies have no macOS or Windows builds.

`NOTEBOOK_MIGRATION.md` records the import changes made when the FIREFate package was
restructured around its three modules, with the old and new cell for each notebook.

## Page titles

Sphinx needs one top-level heading per notebook to give the page a title and a sidebar
link. `add_titles.py` prepends a `# Title` cell to any notebook missing one — run
`python add_titles.py` for a dry run, `--apply` to write. It is idempotent, so run it
again after adding a notebook.

## Migration tools

`temporal/apply_paths.py` is the one-shot tool that rewrote the hardcoded dataset paths
in the temporal notebooks into `config.NAME` lookups against `temporal/datasets.yaml`.
It is idempotent and dry-run by default (`--apply` to write), so re-running it after
adding a notebook picks up only the new literals. It never touches cell outputs,
`%%bash` cells, or scratch paths (`/dev/shm`, `.cache`). **Close the notebooks in
Jupyter before running it with `--apply`** — an open kernel will overwrite the change
on its next autosave.

`temporal/apply_imports.py` is its counterpart for imports: it applied
`NOTEBOOK_MIGRATION.md` to the temporal notebooks, moving them off the pre-split
modules (`utils_custom`, `pseudotime_curves`, `firefate.core.*`, …) and onto
`firefate.temporal` / `state_specific` / `io` / `backends.dictys`. Same contract —
idempotent, dry-run by default, matches on cell content rather than index, and leaves
outputs untouched. Its docstring records the three places it deliberately departs from
the doc.

## Contributing

Commit notebooks **with their outputs** — the documentation renders stored outputs and
never executes anything (`nb_execution_mode = "off"`), so a stripped notebook shows up
as an empty page. Keep the folder a notebook lives in matched to the module it exercises.

## License

MIT, same as the main repository.
