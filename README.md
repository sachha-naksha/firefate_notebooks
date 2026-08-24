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

1. `firefate` installed from the main repository:
   ```bash
   git clone https://github.com/sachha-naksha/FIREFate
   cd FIREFate && pip install -e .
   ```
2. Dataset paths pointed at your own copies. Every path lives in
   `temporal/datasets.yaml` — edit that file, not the notebooks:
   ```python
   from firefate.io import DatasetPaths
   config = DatasetPaths.from_yaml("datasets.yaml")
   ```
3. `dictys` (and, for the trajectory notebooks, `stream` / `palantir` / `scvelo` /
   `multivelo`), which are not declared dependencies of `firefate`.

`NOTEBOOK_MIGRATION.md` records the import changes made when the FIREFate package was
restructured around its three modules, with the old and new cell for each notebook.

## Page titles

Sphinx needs one top-level heading per notebook to give the page a title and a sidebar
link. `add_titles.py` prepends a `# Title` cell to any notebook missing one — run
`python add_titles.py` for a dry run, `--apply` to write. It is idempotent, so run it
again after adding a notebook.

## Contributing

Commit notebooks **with their outputs** — the documentation renders stored outputs and
never executes anything (`nb_execution_mode = "off"`), so a stripped notebook shows up
as an empty page. Keep the folder a notebook lives in matched to the module it exercises.

## License

MIT, same as the main repository.
