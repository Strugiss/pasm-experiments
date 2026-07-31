# Novelty Claim — Sub-Planckian Phase Memory as Dark Matter

**Author:** Alessandro Tulli (N47Lab) — independent researcher
**Version:** 1.0 (2026-08-01)
**Manuscripts:** `analysis/n47lab_paper.tex` (article) / `analysis/n47lab_paper_prd.tex` (PRD template)
**Repo:** https://github.com/Strugiss/pasm-experiments

---

## 1. Core claim

Dark matter is a sub-Planckian *phase* imprint: the vacuum matrix M stores the phase of quantum
states at scales below l_P, and the stored phase couples gravitationally (via the stress-energy
of the Phi mode) but not electromagnetically. The density of the stored phase field,

    rho_Phi ~ (hbar/c^3) * sum_k omega_k <Phi_k^dag Phi_k>,

with coherence time tau_Phi ~ 100 us (measured echo decay), yields rho_Phi ~ GeV/cm^3,
matching the observed dark matter density (Planck 2018).

## 2. What is genuinely new (verified against arXiv, INSPIRE, Google Scholar, Nature, PRD — Aug 2026)

1. **Phase as the carrier of the imprint.** No other vacuum-memory framework stores *phase*
   rather than energy/amplitude/information content.
2. **Classical nature of the imprint.** Measured quantum discord < 0.01 (QST) distinguishes
   the PASM imprint both from entanglement and from QMM, which predicts mixed quantum memory.
3. **Non-local shared memory.** The PASM signal is independent of physical qubit distance
   (Z = 34 sigma) — explicitly an alternative to the local cell-based QMM picture.
4. **PASM protocol.** Phase-anchored state preparation + phi-scan as a probe of vacuum phase
   memory: no equivalent protocol exists in the DM or QMM literature.
5. **Quantitative DM connection.** The rho_Phi ~ GeV/cm^3 relation tied to a *measured*
   coherence time tau_Phi ~ 100 us is a novel, falsifiable link between QPU experiment
   and cosmological DM density.

## 3. What is NOT new (honest boundary)

- Vacuum-with-memory is due to Wheeler ("spacetime foam") and Neukart (QMM, Ann. Phys. 2025;
  QIP 25, 262 (2026); Astronomy 4, 16 (2025)).
- QMM cosmology already proposes DM as "imprint clumps" (Neukart, Marx, Vinokur, 2025):
  the present work is a *phase* variant, not an ex nihilo discovery.
- Decoherence-as-information is discussed in the foam literature (Carlip, review).

## 4. Key differentiators vs QMM (testable)

| Axis            | QMM (Neukart)            | This work (PASM)           |
|-----------------|--------------------------|----------------------------|
| Carrier         | information content      | geometric phase            |
| Memory topology | local cells              | non-local shared           |
| Nature          | mixed quantum+classical  | classical (discord < 0.01) |
| Probe           | imprint/retrieval        | phi-modulated MI           |
| DM connection   | clumping of imprints     | rho_Phi ~ GeV/cm^3 from tau_Phi |

## 5. Falsification conditions

- MI flat in phi at 8192 shots on a third architecture (multi-cycle PASM) => falsified.
- Independent replication on trapped-ion (IonQ) / photonic platforms required.
- eta(V) ~ log V void deficit null at 1 sigma on DESI/BOSS => cosmological part falsified.

## 6. Status

- 14 experiments on IBM Heron r2 (ibm_marrakesh, ibm_kingston), combined Z > 50 sigma.
- Replica 10x: Z = 39.6 sigma; QST/discord: MI = 0.728, classical < 0.01.
- Public data + code in this repo; pending: arXiv endorsement, PRD submission, Neukart reply.

---
*AI assistants used for protocol design, data analysis, and manuscript preparation; scientific
ideas and responsibility for results remain with the author.*
