# Upstream AlphaGeometry README (archived)

This is an abridged archival reference to the inherited AlphaGeometry README, retained for provenance and orientation. It is not a verbatim copy and is not the current project guide. The original README remains available in the repository's earlier Git history.

---

# Solving Olympiad Geometry without Human Demonstrations

This repository contains the code necessary to reproduce DDAR and AlphaGeometry, the two geometry theorem provers introduced in the [Nature 2024 paper](https://www.nature.com/articles/s41586-023-06747-5).

*“Solving Olympiad Geometry without Human Demonstrations.”*

**Update (Jan 2026):** AlphaGeometry2 is [published](https://jmlr.org/papers/v26/25-1654.html), its code for DDAR is released at [alphageometry2](https://github.com/google-deepmind/alphageometry2).

## Dependencies

The original implementation uses Python 3.10.9 and dependencies pinned in `requirements.txt`. It depends on `meliad`, which is not registered with pip. The DDAR solver can run without `meliad` and `sentencepiece`.

## Installation and model assets

The original instructions create a virtual environment, install the pinned requirements, download the geometry checkpoint and vocabulary using `download.sh`, and clone [Meliad](https://github.com/google-research/meliad) separately.

## Solvers

The repository contains two geometry solvers: DDAR and AlphaGeometry. DDAR uses the symbolic definitions and deduction rules in `defs.txt` and `rules.txt`. AlphaGeometry combines DDAR with a language model that proposes auxiliary geometric constructions.

The original README reports these geometry results:

| Mode | `imo_ag_30.txt` | `jgex_ag_231.txt` |
|---|---:|---:|
| DDAR | 14 | 198 |
| AlphaGeometry | 25 | 228 |

These are upstream geometry results, not AlphaAlgebra results.

## Source code

The original code includes geometry-specific modules such as `geometry.py`, `graph.py`, `problem.py`, `dd.py`, `ar.py`, `ddar.py`, `alphageometry.py`, and language-model/search modules. Its definitions, rules, and datasets describe geometry problems and constructions.

## Citation

```bibtex
@Article{AlphaGeometryTrinh2024,
  author  = {Trinh, Trieu and Wu, Yuhuai and Le, Quoc and He, He and Luong, Thang},
  journal = {Nature},
  title   = {Solving Olympiad Geometry without Human Demonstrations},
  year    = {2024},
  doi     = {10.1038/s41586-023-06747-5}
}
```

## Acknowledgements and disclaimer

The original research was a collaboration between the Google Brain team (now Google DeepMind) and the Computer Science Department of New York University. The original README acknowledges the researchers, collaborators, and referees involved in the work.

This is not an officially supported Google product. The original research code is provided “as-is”; Google does not promise to maintain or otherwise support it.

## License

Copyright 2023 DeepMind Technologies Limited. The original software is licensed under Apache License 2.0. Other materials are licensed under Creative Commons Attribution 4.0. Consult the original LICENSE files and notices for the terms applicable to each component.
