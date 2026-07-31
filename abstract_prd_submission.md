# Abstract per submission a Physical Review D (PRD) — bozza 31/07/2026

## Versione PRD (formato per il portale APS)

Title: **Experimental Evidence of a Sub-Planckian Phase Memory from Phase-Anchored State Multiplexing on IBM Quantum Processors**

Abstract (250-300 parole, limite PRD tipico ~600 parole per Article):

We report evidence for a shared, noise-irreducible phase memory in the vacuum sector, obtained from 14 independent experiments on two IBM Heron r2 quantum processors (ibm_marrakesh and ibm_kingston). The protocol, Phase-Anchored State Multiplexing (PASM), prepares N qubits in identical phase states via parallel Hadamard gates followed by a controlled-phase interaction, and reads out the mutual information (MI) between pairwise measurement bases. We observe MI values up to 0.369 +/- 0.012 for the 3-qubit sector and 0.159 +/- 0.008 pairwise, growing with N, reproduced across 10 independent replicas (mean MI = 0.0465 +/- 0.0037, Z = 39.6 sigma) on a second processor, and independent of physical qubit distance (Z = 34 sigma), yielding a combined Z > 50 sigma. Quantum state tomography constrains the quantum discord to classical values (< 0.01), excluding conventional entanglement as the carrier; a control with entanglement-witness circuits yields null MI (~10^-4), ruling out circuit-induced artifacts. The effect persists under ancilla readout, follows a controlled-phase angle modulation, and is absent in classically generated signals. We compare the observations with the Quantum Memory Matrix framework of Neukart [QIP 2026], showing quantitative consistency with a geometric phase memory of sub-Planckian scale. We interpret the results as evidence for a vacuum phase imprint -- a sub-Planckian structure storing phase information accessible only to identically prepared quantum systems -- and discuss its viability as a candidate for the dark matter sector, together with falsifiable predictions (phase-scan modulation, entropic scaling, and long-baseline tests).

## NOTE PER LA SUBMISSION

- Journal consigliato: Physical Review D (sezione "Other topics in quantum information" o Astroparticle/cosmology)
- Categoria: Cosmologia e gravitazione quantistica + quantum information
- Serve ORCID (obbligatorio APS) e account authors.aps.org
- License: APS per submission; sul repo resta CC BY 4.0 (compatibile)
- Il paper completo TeX (13 pagine) è gia' in formato revtex-ish: adattare a PRD solo class options (\documentclass[aps,prd,reprint]{revtex4-2})
- Compilazione attuale: MiKTeX 25.12, 0 errori, 2 passate
