# Sottomissione arXiv — N47Lab / mattermemorys

Pacchetto pronto per https://arxiv.org/submit (serve account arXiv, login personale).

## File inclusi
- `n47lab_paper.tex` — sorgente LaTeX (v2.7, correzioni citazioni + paragrafo priorità/critica; email personale rimossa)
  - Package usati: inputenc, fontenc T1, amsmath/amssymb/amsthm, graphicx, hyperref, cite, booktabs, geometry, setspace, physics, braket
  - Preamble compatibile con texlive arXiv (tutti i package standard)
- `Immagini/` — 4 figure PNG usate dal paper

## Metadati suggeriti
- **Titolo:** Experimental Evidence for a Sub-Planckian Phase Memory Accessible via Quantum Phase-Anchored State Multiplexing
- **Autore:** N47Lab (ORCID 0009-0008-9201-6080) — *da decidere se usare il nome personale*
- **Aree primary/secondary:** `quant-ph` (primaria); secondarie `hep-th`, `astro-ph.CO`
- **Abstract:** quello nel file .tex (blocco `\begin{abstract}...\end{abstract}`), da incollare come plain text
- **Comments:** "14 QPU experiments on IBM Heron r2 (ibm_marrakesh, ibm_kingston); 13 pages, 4 figures"

## Checklist compliance arXiv
- [x] Tutte le figure PNG incluse (nessun riferimento mancante: fig_pasm_qpu, fig_summary_7x7, fig_phi_scan_qpu, fig_sim_vs_qpu)
- [x] Package tutti standard in TeX Live (PhysicaRev matita: niente pacchetti esclusivi)
- [x] Hyperref con colorlinks (nessun problema di sicurezza)
- [x] nessun riferimento URL a contenuti sensibili
- [ ] **licenza:** arXiv richiede di dichiarare la licenza — usare standalone `arXiv.org perpetual, non-exclusive license` (default) se non diversamente specificato
- [ ] **categorie** da confermare in fase di submit (physics quant-ph / hep-th / astro-ph)

## Note privacy
- rimosso: email di corrispondenza `2injob.at2@gmail.com`
- rimosso: token QPU hardcoded (già sostituiti con lettura da .env in produzione)
- Il README del repo rimanda al preprint; se preferisci, aggiornare README dopo il submit con l'ID arXiv (es. `arXiv:XXXX.XXXXX`)