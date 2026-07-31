"""
N47Lab — Zero-Noise Extrapolation (ZNE) per PASM
Estrapola MI a rumore zero via gate folding (1x, 3x, 5x)
Se MI -> 0 a rumore zero: effetto è artefatto. Se MI > 0: reale.
"""
import sys, time; sys.stdout.reconfigure(encoding='utf-8')
import numpy as np; from numpy import pi, log2
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

API3 = 'MiPxZZAuroZIHuc_YEvPPrdoG9r7DalscGWqhL5NMcj0'
BACKEND = 'ibm_kingston'
SHOTS = 8192

def H(ps):
    ps = [x for x in ps if x>0]
    return -sum(x*log2(x) for x in ps)

def calc_mi_2q(counts):
    t = sum(counts.values()) or 1
    p00 = counts.get('00',0)/t; p01 = counts.get('01',0)/t
    p10 = counts.get('10',0)/t; p11 = counts.get('11',0)/t
    p0 = p00 + p01; p1 = p10 + p11
    q0 = p00 + p10; q1 = p01 + p11
    return H([p0, p1]) + H([q0, q1]) - H([p00, p01, p10, p11])

def pasm_circuit(phi, noise_factors=1):
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.h(1)
    for _ in range(noise_factors):
        qc.cp(phi/noise_factors, 0, 1)  # fold: CP diviso in N parti
    qc.h(0); qc.h(1)
    qc.measure(0, 0); qc.measure(1, 1)
    return qc

S = QiskitRuntimeService(channel='ibm_cloud', token=API3, instance='auto')
backend = S.backend(BACKEND)
pm = generate_preset_pass_manager(optimization_level=1, backend=backend)

phis = [pi/2, pi]
noise_levels = [1, 3, 5]  # gate folding factors
circuits = []
for nf in noise_levels:
    for phi in phis:
        c = pasm_circuit(phi, noise_factors=nf)
        c.name = f"pasm_zne_nf{nf}_phi{phi:.2f}"
        circuits.append(c)

circuits_t = pm.run(circuits)
print(f"Circuiti ZNE: {len(circuits_t)}")

job = SamplerV2(mode=backend).run(circuits_t, shots=SHOTS)
print(f"Job inviato! ID: {job.job_id()}")
for _ in range(120):
    s = job.status()
    if s == 'DONE': break
    print(f"  {s}"); time.sleep(10)

if job.status() == 'DONE':
    r = job.result()
    print("\n=== ZNE PASM ===")
    print(f"{'phi':>6} {'noise_factor':>13} {'MI':>10}")
    idx = 0
    for nf in noise_levels:
        for phi in phis:
            c = r[idx].data.c.get_counts()
            mi = calc_mi_2q(c)
            print(f"{phi:6.2f} {nf:13d} {mi:10.6f}")
            idx += 1
    # Stima MI a noise=0 via regressione lineare
    print("\n=== Estrapolazione noise=0 ===")
    for phi in phis:
        xs = []; ys = []
        for i, nf in enumerate(noise_levels):
            c = r[noise_levels.index(nf)*2 + phis.index(phi)].data.c.get_counts()
            ys.append(calc_mi_2q(c))
            xs.append(nf)
        if len(xs) >= 2:
            coeffs = np.polyfit(xs, ys, 1)
            mi_zero = coeffs[1]
            print(f"phi={phi:.2f}: MI(noise=0) ≈ {mi_zero:.6f}  (fit lineare {coeffs[0]:.6f}*nf + {coeffs[1]:.6f})")
else:
    print(f"Job fallito: {job.status()}")
