"""
N47Lab — PASM simmetrico: shared/separate usano STESSI qubit, STESSA profondità
Bug fix: rimuove bias strutturale dell'asimmetria circuitale 3q vs 4q
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

S = QiskitRuntimeService(channel='ibm_cloud', token=API3, instance='auto')
backend = S.backend(BACKEND)
pm = generate_preset_pass_manager(optimization_level=1, backend=backend)

# Circuito SHARED: 2 qubit, CP(phi) tra loro
qc_shared = QuantumCircuit(2, 2)
qc_shared.h(0); qc_shared.h(1)
qc_shared.barrier()
qc_shared.cp(pi/2, 0, 1)  # CPhase condiviso
qc_shared.barrier()
qc_shared.h(0); qc_shared.h(1)
qc_shared.measure(0, 0); qc_shared.measure(1, 1)
qc_shared.name = "pasm_shared_sym"

# Circuito SEPARATE (controllo): 2 qubit, CP(phi) omesso, rimpiazzato da P(phi/2) locale
qc_sep = QuantumCircuit(2, 2)
qc_sep.h(0); qc_sep.h(1)
qc_sep.barrier()
qc_sep.p(pi/4, 0); qc_sep.p(pi/4, 1)  # fase locale, NESSUNA interazione
qc_sep.barrier()
qc_sep.h(0); qc_sep.h(1)
qc_sep.measure(0, 0); qc_sep.measure(1, 1)
qc_sep.name = "pasm_separate_sym"

# Controllo vuoto: H + misura (nessuna fase)
qc_null = QuantumCircuit(2, 2)
qc_null.h(0); qc_null.h(1)
qc_null.barrier()
qc_null.h(0); qc_null.h(1)
qc_null.measure(0, 0); qc_null.measure(1, 1)
qc_null.name = "pasm_null_sym"

circuits_t = pm.run([qc_shared, qc_sep, qc_null])
print(f"Circuiti: {len(circuits_t)} (shared, separate, null)")
print(f"Profondità: shared={circuits_t[0].depth()}, separate={circuits_t[1].depth()}, null={circuits_t[2].depth()}")

job = SamplerV2(mode=backend).run(circuits_t, shots=SHOTS)
print(f"Job inviato! ID: {job.job_id()}")
for _ in range(120):
    s = job.status()
    if s == 'DONE': break
    print(f"  {s}"); time.sleep(10)

if job.status() == 'DONE':
    r = job.result()
    print("\n=== PASM SIMMETRICO ===")
    for i, name in enumerate(['shared', 'separate', 'null']):
        c = r[i].data.c.get_counts()
        mi = calc_mi_2q(c)
        print(f"{name:>10}: MI = {mi:.6f}  counts = {dict(sorted(c.items()))}")
else:
    print(f"Job fallito: {job.status()}")
