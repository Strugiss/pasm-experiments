# pasm-experiments — Dati e analisi degli esperimenti PASM/DTC su IBM Quantum

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.21830151.svg)](https://doi.org/10.5281/zenodo.21830151)
[![Licenza: MIT](https://img.shields.io/badge/Licenza-MIT-yellow.svg)](LICENSE)
[![Versione](https://img.shields.io/badge/versione-v1.0.1-informational)](https://github.com/Strugiss/pasm-experiments/releases/tag/v1.0.1)

## Abstract

Questo repository contiene i **dati grezzi**, gli **script di analisi** e il **sorgente LaTeX** degli esperimenti che hanno osservato un **cristallo temporale discreto (DTC) classico pre-termale** tramite il protocollo **PASM (Phase-Anchored State Multiplexing)** su processori IBM Quantum Heron. I **14 esperimenti QPU** indipendenti su `ibm_marrakesh` e `ibm_kingston` mostrano una memoria di fase condivisa con **significatività combinata Z > 50σ** (replica 10×: Z = 39.6σ; test distanza: Z = 34σ) e mutua informazione condivisa **0.063 ± 0.005** (marrakesh) / **0.047 ± 0.004** (kingston). Il manoscritto è in revisione presso **Physical Review Letters** (preprint: DOI [10.5281/zenodo.21938548](https://doi.org/10.5281/zenodo.21938548)).

![Mutua informazione per esperimento PASM/DTC](https://n47lab.altervista.org/research/immagini/pasm_mi_esperimenti.png)

*Mutua informazione (MI) per esperimento. Fonte: manoscritto PRL es2026aug09_746 e report di laboratorio.*

## Method and Results

**Metodo.** PASM usa ancore di fase per collegare esecuzioni separate di circuiti quantistici e misurare le correlazioni residue tra qubit (mutua informazione condivisa). Hardware: IBM Quantum Heron r2, `SamplerV2(mode=backend)` senza Session/Batch, `optimization_level=1` sempre (preserva barriere e delay), 8192–65536 shots per circuito. Ogni esperimento è corredato di veti di controllo (baseline, duplicati, split-half, guardie) e job ID tracciabili.

Risultati chiave (tutti dai dati reali pubblicati):

| Esperimento | Valore |
|---|---|
| Esperimenti QPU completati | 14 |
| Significatività combinata (memoria condivisa) | Z > 50σ |
| MI condivisa — ibm_marrakesh | 0.063 ± 0.005 |
| MI condivisa — ibm_kingston | 0.047 ± 0.004 |
| Replica 10× | Z = 39.6σ |
| PASM Distanza | Z = 34σ, MI indipendente dalla distanza |
| φ-scan | MI modulata da φ, picco a π |
| WITNESS (controllo) | MI = 0.00013 (zero) |
| QST / DISCORD | MI = 0.728, classico (< 0.01) |
| Scaling | MI picco a 3 qubit = 0.159 |

Le correlazioni sono **classiche**: il controllo WITNESS dà W = 6.1e-17 (nessun entanglement), e la QST stima discord < 0.01.

## Dataset Overview

I dati degli esiti QPU sono file JSON; nel repository sono raccolti in `data/` (l'archivio completo con job ID e output per esperimento è anche su Zenodo, DOI [10.5281/zenodo.21830151](https://doi.org/10.5281/zenodo.21830151)). Struttura e campi principali:

| File / gruppo | Campi principali | Contenuto |
|---|---|---|
| `pasm_dtc_experiments_metadata.json` | `generated`, `experiments`, `backends`, `qubit_triplets`, `distance_pairs` | Metadati di 9 campagne (`pasm_base`, `phi_scan`, `echo_hahn`, `delay_sweep`, `frequency_sweep`, `fft_subharmonic_discovery`, `fft_subharmonic_precision`, `m3_3q_readout`, `vz_tomography`) con backend, shots, qubit, valori di φ, ripetizioni |
| `scissione_qpu_report_*.json` | `mode`, `job_id`, `nrep`, `S3_net`, `S3_se`, `M4_net`, `lambda2`, `lambda1_ratio`, `soglie`, `sv`, `chirp`, `esito`, `veti` | Report del test di scissione (una sola memoria o più componenti): autovalori, soglie null, esito e veti |
| `witness_report_sim_*.json` | `W`, `XX`, `YY`, `ZZ`, `entanglement_detected`, `verdict` | Controllo WITNESS: W = 6.1e-17 → nessun entanglement |
| `piano_E3_qpu_report_*.json` | `R1`, `R4`, `dK`, `KSCAN`, `WITNESS`, `ANNICH`, `BASELINE`, `veti` | Test di annichilazione (Piano E3) con soglie e veti per backend |
| `orme_qpu_report_*.json`, `linearita_qpu_report_*.json` | metriche per cella, `z`, `p`, verdetti | Controlli di robustezza: orme (eco − DUP) e linearità |
| `scissione_calibra_aer_*.json` | `lambda2` p99/media, `lambda1_ratio` p99, seed, repliche | Calibrazione del null su AER/simulatore per backend |

## Data Processing Notes

- **Flusso:** submit del circuito → fetch dell'esito (`mode: fetch`) → analisi. Gli script di submit/analisi principali sono in `scripts/` (es. submit PASM, phi-scan, analisi discord, relancio repliche); il sorgente del paper è in `analysis/`.
- **Metriche:** mutua informazione condivisa per coppia/tripletta di qubit, con barre di errore; FFT per la subarmonica a f = 0.5 (period-doubling); autovalori (λ2, λ1-ratio) per il test di scissione; operatore W per l'entanglement; Z combinato con Fisher.
- **Veti:** ogni run passa da controlli su baseline, duplicati (DUP), split-half e guardie; un run che fallisce un veto è dichiarato invalido, non interpretato.
- **Nota FFT:** la subarmonica è a f = 0.5 (indice n/2), con SNR robusto senza bias.

## Riproducibilità

```bash
pip install qiskit qiskit-ibm-runtime
# 1) submit su IBM Quantum Open Plan (SamplerV2(mode=backend) diretto, niente Session/Batch)
python scripts/pasm_marrakesh.py
# 2) analisi degli esiti (MI, FFT subarmonica, veti)
python scripts/n47lab_discord_analysis.py
```

Requisiti: Qiskit 2.5.x + qiskit-ibm-runtime 0.4x; backend `ibm_marrakesh`, `ibm_kingston` (Heron r2, 156 qubit) o `ibm_fez`. I token IBM non sono inclusi nel repository.

## Come citare

Il file [`CITATION.cff`](CITATION.cff) è pronto per GitHub ("Cite this repository"). Testo:

```bibtex
@dataset{tulli2026pasmdatasets,
  author = {Tulli, Alessandro},
  title  = {pasm-experiments: PASM/DTC experimental data on IBM Quantum},
  year   = {2026},
  doi    = {10.5281/zenodo.21830151},
  url    = {https://github.com/Strugiss/pasm-experiments}
}
```

## Link

- Sito N47Lab: <https://n47lab.altervista.org/>
- Ricerca (dati, grafici, tabelle): <https://n47lab.altervista.org/research/>
- Preprint PRL: <https://doi.org/10.5281/zenodo.21938548>
- Repository della ricerca: <https://github.com/Strugiss/N47Lab-QuantumResearch>
- Traiettoria di ricerca (research-timeline): <https://doi.org/10.5281/zenodo.21855315>
- Dossier anomalia π-echo: <https://doi.org/10.5281/zenodo.21893791>

## Licenza

I **dati** di questo repository e il deposito Zenodo [10.5281/zenodo.21830151](https://doi.org/10.5281/zenodo.21830151) sono rilasciati sotto **CC BY 4.0**; il **codice** degli script è rilasciato sotto **MIT** (vedi [`LICENSE`](LICENSE)). I dati QPU grezzi restano soggetti ai termini dell'IBM Quantum Open Plan.

**Avviso di stato:** i risultati non sono peer-reviewed; il manoscritto è in revisione presso Physical Review Letters.
