# Report di analisi — post-delibera 220 agenti (2026-08-03)

Analisi offline eseguite dopo la delibera N47Lab (verdetto: tesi CONDIZIONATO,
solidita' pacchetto QPU 58/100). Dettagli completi in
`n47lab_delibera_220_report.json` (temp opencode).

## Contenuto

| File | Raccomandazione | Esito chiave |
|------|-----------------|--------------|
| `n47lab_scaletta_reanalisi.json` | R2 — scaletta MI 1q-6q | Nessun modello passa (estensivo chi2_red=51.1, pairwise 182.9, saturazione 32.8, quadratico 27.2). Plateau 4-6q autocoerente a 0.1244; 2q a -17σ dal plateau; picco 3q a +4.3σ (outlier reale). |
| `n47lab_mm_bootstrap_report.json` | R4 — Miller-Madow per punto | Bootstrap 2000 iter sui counts QPU. Segnali PASM a 100-600x il floor MM. I3 3q = 0.36929 riprodotta (paper 0.369±0.012). WITNESS 0.00013 in zona grigia (floor medio phi_echo 2.6e-4). |
| `n47lab_faseA_refit_report.json` | R5 — refit FASE A | Chiusura 3:-1:-1:-1 per singolo punto: chi2=373.8/51 dof (p=1.1e-50) → T19 ARTEFATTO confermato anche senza parametri condivisi. Jackknife: parametri stabili (Delta_d=0.118±0.007). Bilancio reale 4 validi : 1 artefatto : 2 parziali. |
| `n47lab_qst_bootstrap_report.json` | R7 — QST/DISCORD bootstrap | MI_vn = 0.7274±0.0109 (CI95 [0.708, 0.749]). Discord_min = 0.0070±0.0029 (CI95 [0.0027, 0.0137]) — la soglia 0.01 cade dentro l'intervallo: classificazione "classico" marginale. |

## Errata-corrige applicati ai dati

1. **`data/n47lab_7x7_results.json` — pasm_3q**: il campo `MI` del punto index 1
   (controllo) dichiarava 0.502444, valore ERRATO (bug di metrica, coincide con
   l'entropia marginale di 1 bit). Ricalcolato dai counts: I3 = 0.00007
   (controllo pulito). Aggiunti `MI_I3` (0.36929) e `MI_originale_dichiarata`
   per il punto index 0. I counts non sono stati modificati.
2. **Conteggio esperimenti**: il pasto della delibera cita 13 esperimenti QPU;
   il repo (paper, email Neukart) ne conta 14. Il repo e' la fonte autorevole:
   il numero ufficiale e' **14**.
3. **Omonimia PASM**: arXiv 2604.26635 usa la sigla PASM per Pinching
   Antenna-Aided Spatial Multiplexing (telecom 6G) — disambiguare nel paper.

## Limiti dichiarati delle analisi

- Punti scaletta (R2) da run diversi (backend/giorni non dichiarati nel file
  sorgente); sigma uniforme 0.004 assunto (0.008 per 3q).
- Autocorrelazione lag1-5 della sequenza MI del phi_echo (z fino a +5.18):
  i punti del phi-scan non sono indipendenti (drift condiviso o struttura liscia
  in phi) — da dichiarare nel paper.
- WITNESS 0.00013 sotto il floor medio reale dei punti phi_echo (2.6e-4 a k~4):
  il "controllo a zero" non e' risolto sotto il bias Miller-Madow.
