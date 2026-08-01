# -*- coding: utf-8 -*-
"""
N47Lab — Test "rumore di fondo strutturato vs casuale"
Analisi su dati esistenti (zero QPU time):
  A) Test B saturazione: MI(N) bootstrap da counts -> converge a costante (matrice)
     o decade come 1/sqrt(N) -> 0 (rumore casuale)?
  B) Autocorrelazione seriale della sequenza MI(phi_echo, 49 circuiti):
     fondo coerente => AC != 0; rumore i.i.d. => AC ~ 0
  C) Test di struttura sulla distribuzione dei MI dei controlli (N2N3_sweep_noH)
Output: JSON in data/
"""
import json, math, random
from collections import Counter

BASE = r"C:\Users\Utente\Downloads\Esperimento\MatterMemory\pasm-experiments"
random.seed(47)

def mi_from_counts(counts, ntot=None):
    if ntot is None:
        ntot = sum(counts.values())
    p = {k: v / ntot for k, v in counts.items()}
    px = {}
    py = {}
    for k, v in p.items():
        b = f"{int(k):02d}"
        px[b[0]] = px.get(b[0], 0.0) + v
        py[b[1]] = py.get(b[1], 0.0) + v
    mi = 0.0
    for k, v in p.items():
        b = f"{int(k):02d}"
        if v > 0:
            mi += v * math.log2(v / (px[b[0]] * py[b[1]]))
    return mi

def bootstrap_mi(counts, N, reps=40):
    items = []
    for k, v in counts.items():
        items.extend([k] * v)
    vals = []
    for _ in range(reps):
        samp = [items[random.randrange(len(items))] for _ in range(N)]
        c = Counter(samp)
        vals.append(mi_from_counts(c))
    return sum(vals) / len(vals), (sum(x * x for x in vals) / len(vals) - (sum(vals) / len(vals)) ** 2) ** 0.5

def serial_ac(seq, lag):
    n = len(seq)
    if n <= lag:
        return None
    m = sum(seq) / n
    num = sum((seq[i] - m) * (seq[i + lag] - m) for i in range(n - lag))
    den = sum((x - m) ** 2 for x in seq)
    return num / den if den > 0 else 0.0

results = {}

# ---------- A) Test B saturazione MI(N) ----------
r7 = json.load(open(BASE + r"\data\n47lab_7x7_results.json", encoding="utf-8"))
mon = json.load(open(BASE + r"\data\n47lab_monitor_results.json", encoding="utf-8"))

targets = {}
for c in r7["phi_echo"]["results"]:
    if "counts" in c:
        targets[f"phi_echo_idx{c['index']:02d}"] = c["counts"]
for name in ("N2_pi_H", "N2_0_H"):
    for c in mon.get(name, {}).get("results", []):
        if "counts" in c:
            targets[f"{name}_c{c['circuit']}"] = c["counts"]

saturation = {}
Nvals = [512, 1024, 2048, 4096, 8192]
for name in ["phi_echo_idx00", "phi_echo_idx08", "phi_echo_idx12", "N2_pi_H_c0", "N2_0_H_c0"]:
    if name not in targets:
        continue
    curve = {}
    for N in Nvals:
        if N <= sum(targets[name].values()):
            m, s = bootstrap_mi(targets[name], N)
            curve[str(N)] = {"MI": m, "std": s}
    mi_full = mi_from_counts(targets[name])
    curve["full"] = {"MI": mi_full}
    # fit lineare MI vs 1/sqrt(N): pendenza (rumore) e intercetta (deterministico)
    pts = [(1.0 / math.sqrt(int(k)), v["MI"]) for k, v in curve.items() if k != "full"]
    mx = sum(x for x, _ in pts) / len(pts)
    my = sum(y for _, y in pts) / len(pts)
    num = sum((x - mx) * (y - my) for x, y in pts)
    den = sum((x - mx) ** 2 for x, _ in pts)
    slope = num / den if den else 0.0
    inter = my - slope * mx
    saturation[name] = {"curve": curve, "fit_1sqrtN": {"slope": slope, "intercept": inter}}
results["A_saturazione"] = saturation

# ---------- B) Autocorrelazione seriale sequenza MI phi_echo ----------
seq = [c["MI"] for c in r7["phi_echo"]["results"] if "MI" in c]
ac = {str(lag): serial_ac(seq, lag) for lag in range(1, 9)}
# z-score approssimato: AC ~ N(0, 1/n)
n = len(seq)
ac_z = {str(lag): (v * math.sqrt(n)) for lag, v in ac.items() if v is not None}
results["B_autocorr_MI_seq"] = {"n_circuiti": n, "AC": ac, "z_AC": ac_z}

# ---------- C) Struttura della distribuzione dei controlli ----------
ctrl = [c["MI"] for c in mon["N2N3_sweep_noH"]["results"]]
m = sum(ctrl) / len(ctrl)
var = sum((x - m) ** 2 for x in ctrl) / (len(ctrl) - 1)
std = math.sqrt(var)
# kurtosis campionaria (eccesso) e skewness
n = len(ctrl)
s2 = sum((x - m) ** 2 for x in ctrl) / n
s3 = sum((x - m) ** 3 for x in ctrl) / n
s4 = sum((x - m) ** 4 for x in ctrl) / n
skew = s3 / s2 ** 1.5 if s2 > 0 else 0.0
kurt = s4 / s2 ** 2 - 3.0 if s2 > 0 else 0.0
# test chi2 su 4 bin contro uniforme? meglio: frazione |MI| > 2 sigma (attesa 5% sotto gaussiana)
over2s = sum(1 for x in ctrl if abs(x - m) > 2 * std) / len(ctrl)
results["C_struttura_controlli"] = {
    "n": len(ctrl), "media": m, "std": std,
    "skew": skew, "kurtosi_eccesso": kurt,
    "frazione_oltre_2sigma": over2s, "attesa_gaussiana": 0.0455,
}

json.dump(results, open(BASE + r"\data\n47lab_rumore_fondo_test.json", "w", encoding="utf-8"), indent=2, ensure_ascii=False)

print("=== A) SATURAZIONE MI(N) ===")
for name, d in saturation.items():
    c = d["curve"]
    print(f"{name}: MI_full={c['full']['MI']:.4f}  slope(1/sqrtN)={d['fit_1sqrtN']['slope']:.4f}  intercept={d['fit_1sqrtN']['intercept']:.4f}")
print("\n=== B) AUTOCORRELAZIONE SEQUENZA MI (phi_echo, %d circ) ===" % n)
for lag in range(1, 9):
    print(f"lag {lag}: AC={ac[str(lag)]:.4f}  z={ac_z[str(lag)]:.2f}")
print("\n=== C) DISTRIBUZIONE CONTROLLI N2N3_sweep_noH ===")
print(json.dumps(results["C_struttura_controlli"], indent=2, ensure_ascii=False))
