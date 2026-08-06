# PASM Experiments — Classical Prethermal DTC on IBM Heron (N47Lab / MatterMemory)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21830091.svg)](https://doi.org/10.5281/zenodo.21830091)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21830071.svg)](https://doi.org/10.5281/zenodo.21830071)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21830095.svg)](https://doi.org/10.5281/zenodo.21830095)

Experimental evidence for a **classical prethermal discrete time crystal (DTC)** realized via
**Phase-Anchored State Multiplexing (PASM)** on IBM Quantum processors.

## Abstract

14 independent QPU experiments on two IBM Heron r2 processors
(`ibm_marrakesh`, `ibm_kingston`) demonstrate a **classical prethermal discrete time crystal (DTC)**
via the **Phase-Anchored State Multiplexing (PASM)** protocol:

- **Subharmonic response**: φ-scan peak MI = **0.785 at φ = π** (period-doubling)
- **Classical correlations**: Discord < 0.01 (QST), zero entanglement
- **Distance independence**: MI distance-independent (Z = 34σ)
- **3-qubit resonance**: MI peak at 3 qubits (0.159 ± 0.008)
- **PASM-H enhancement**: MI = 0.722 ± 0.005 at φ = π/2 (phase-to-population conversion)
- **Witness null**: MI = 0.00013 ± 0.0001 (below Miller–Madow floor)
- **Noise resilience**: 25% degradation under amplitude damping
- **Reproducibility**: 10 replicas, Z = 39.6σ (Kingston), combined Z > 50σ (Fisher)

## Repository structure

```
pasm-experiments/
├── scripts/     # QPU submission, monitoring, and analysis code
├── data/        # Raw results, job IDs, per-experiment outputs
├── analysis/    # LaTeX paper source (n47lab_paper.tex), arXiv submission
│                #   package (arxiv_submission/), analysis reports
├── figures/     # Figures used in the paper
└── README.md
```

## Hardware & environment

- IBM Quantum Open Plan (free tier), `SamplerV2(mode=backend)` — no Session/Batch
- `optimization_level=1` always (preserves barriers/delays)
- Qiskit 2.5.1, qiskit-ibm-runtime 0.48.0
- Backends: `ibm_marrakesh`, `ibm_kingston` (Heron r2, 156q), `ibm_fez`

## Key experiments (scripts → data)

| Experiment | Script | Result |
|---|---|---|
| PASM shared MI | `pasm_marrakesh.py` | MI = 0.0628 ± 0.005 (13σ) |
| φ-scan fine structure | `phi_scan.py` | peak MI = 0.785 at φ = π |
| SWAP test | `esperimento_swap.py` | ΔF = +0.393 (34.2σ) |
| PASM distance | `n47lab_submit_7x7.py` | MI = 0.0600, distance-independent (34σ) |
| PASM 3-qubit | `n47lab_submit_7x7.py` | MI = 0.369 (8-outcome) |
| Replica 10× | `n47lab_relancio_esperimenti.py` | MI = 0.0465 ± 0.0037 (39.6σ) |
| QST/DISCORD | `n47lab_discord_analysis.py` | MI = 0.728, discord < 0.01 (classical) |
| PASM-H φ-scan | `n47lab_phi_scan_approfondito.py` | **MI = 0.722 at φ = π/2** |
| WITNESS control | `n47lab_submit_7x7.py` | MI = 0.00013 (null) |

## Upcoming experiments (window 26/08/2026)

- `n47lab_pasm_zne.py` — zero-noise extrapolation (gate folding 1×/3×/5×)
- `n47lab_pasm_symmetric.py` — symmetric qubit map, shared vs separate
- `n47lab_chsh_pasm.py` — CHSH Bell test on PASM preparation
- `n47lab_twirled_pasm.py` — Pauli twirling on CP gate
- `n47lab_readout_cal.py` — 4×4 readout assignment calibration

## Submission

Preprint package for arXiv is available in `analysis/arxiv_submission/`
(LaTeX source + 4 figures + submission checklist). Target journals:
`quant-ph` (primary), `hep-th`, `astro-ph.CO`. Target journals: **PRL / Nature Physics / Science Advances**.

## Author

**N47Lab** — Independent researcher without academic degrees.

This work was conceived, designed, executed, and analyzed by the author, using large language models (LLMs) as **cognitive prostheses** — tools that translate hypotheses into code, formalism, analysis pipelines, and prose.

The author is part of a **growing community of independent researchers who use LLMs as cognitive prostheses** (see: *The Agentic Researcher* [arXiv:2603.15914], *Research Factory* [GitHub: mindheadllc/research-factory], *JZ Institute of Science*, *OpenPhysica*, *Independent Research.ai*; surveys indicate >80% of researchers now use LLMs in their workflow [arXiv:2411.05025]).

All scientific decisions — experimental design, parameter selection, interpretation pivots, control choices, conclusion framing — were made by the human researcher. The LLMs used (Claude, GPT-4) served as force multipliers for translation; every scientific decision was made by the human researcher.

## Citation

```bibtex
@unpublished{tulli2026pasm,
  author  = {Alessandro Tulli},
  title   = {Observation of a Classical Prethermal Discrete Time Crystal on a Superconducting Quantum Processor},
  note    = {Preprint in preparation},
  year    = {2026}
}
```

## License

All data and code released under CC BY 4.0. Raw QPU data retain IBM Quantum Open Plan terms of use.

## Acknowledgments

The author acknowledges the broader community of independent researchers using LLMs as cognitive prostheses, including the developers of *The Agentic Researcher* (ZIB-IOL, arXiv:2603.15914), *Research Factory* (GitHub: mindheadllc/research-factory), *JZ Institute of Science* (AI-augmented theoretical physics), *OpenPhysica* (openphysica.org), and the *Independent Research.ai* community. The survey by [arXiv:2411.05025] documenting >80% LLM adoption among researchers provided context for this work's methodology. IBM Quantum Network is acknowledged for open-plan access to Heron r2 processors.