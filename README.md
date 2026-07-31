# PASM Experiments — Sub-Planckian Phase Memory (N47Lab / MatterMemory)

Experimental evidence for a **sub-Planckian phase memory** accessed via
**Phase-Anchored State Multiplexing (PASM)** on IBM Quantum processors.

## Abstract

14 independent QPU experiments on two IBM Heron r2 processors
(`ibm_marrakesh`, `ibm_kingston`) demonstrate a shared phase memory producing
anomalous mutual information (MI) between identically-prepared qubit arrays:

- MI up to **0.722** at φ = π/2 (PASM-H variant), 99.9% reproducibility
- Combined Z-score **> 50σ** (Fisher, 7 independent experiments)
- **Distance-independent** memory (Z = 34σ)
- **Classical** nature of the imprint (quantum discord < 0.01 in QST)
- Null controls: entanglement witness MI = 0.00013, separate preparation MI < 0.001

## Repository structure

```
pasm-experiments/
├── scripts/     # QPU submission, monitoring, and analysis code
├── data/        # Raw results, job IDs, per-experiment outputs
├── analysis/    # LaTeX paper source (n47lab_paper.tex) and compiled PDF
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
| PASM 3-qubit | `n47lab_submit_7x7.py` | MI = 0.369 |
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

## Citation

```bibtex
@unpublished{tulli2026pasm,
  author  = {Alessandro Tulli},
  title   = {Experimental Evidence for a Sub-Planckian Phase Memory
             Accessible via Quantum Phase-Anchored State Multiplexing},
  note    = {Preprint in preparation},
  year    = {2026}
}
```

## License

All data and code released under CC BY 4.0. Raw QPU data retain IBM Quantum
Open Plan terms of use.
