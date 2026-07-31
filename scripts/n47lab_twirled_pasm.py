"""
N47Lab — PASM con Pauli Twirling sulle CP gates
Trasforma errori coerenti in incoerenti.
Se MI persiste dopo twirling: non è errore coerente di gate.
Se MI scompare: era artefatto da errori coerenti.
"""
import sys, time; sys.stdout.reconfigure(encoding='utf-8')
import numpy as np; from numpy import pi, log2, random
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

API3 = 'MiPxZZAuroZIHuc_YEvPPrdoG9r7DalscGWqhL5NMcj0'
BACKEND = 'ibm_kingston'
SHOTS = 8192
N_TWIRL = 10  # circuiti twirlati

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

def pauli_twirled_pasm():
    """Crea PASM con Pauli twirl random sul CP gate"""
    pauli_map = {'I': (0, QuantumCircuit(1)), 'X': (1, QuantumCircuit(1)), 
                 'Y': (2, QuantumCircuit(1)), 'Z': (3, QuantumCircuit(1))}
    pauli_gates = {
        'X': lambda qc, q: qc.x(q),
        'Y': lambda qc, q: qc.y(q),
        'Z': lambda qc, q: qc.z(q),
    }
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.h(1)

    qc.barrier()
    # Pauli twirl prima del CP: scegli P1, P2 random
    p1 = random.choice(['I', 'X', 'Y', 'Z'])
    p2 = random.choice(['I', 'X', 'Y', 'Z'])
    if p1 != 'I': pauli_gates[p1](qc, 0)
    if p2 != 'I': pauli_gates[p2](qc, 1)

    qc.cp(pi/2, 0, 1)  # CP gate da twirlare

    # Pauli twirl dopo: P1*P2 aggiustato per CP commutation
    if p1 != 'I': pauli_gates[p1](qc, 0)
    if p2 != 'I': pauli_gates[p2](qc, 1)
    qc.barrier()

    qc.h(0); qc.h(1)
    qc.measure(0, 0); qc.measure(1, 1)
    return qc

S = QiskitRuntimeService(channel='ibm_cloud', token=API3, instance='auto')
backend = S.backend(BACKEND)
pm = generate_preset_pass_manager(optimization_level=1, backend=backend)

circuits = []
for i in range(N_TWIRL):
    c = pauli_twirled_pasm()
    c.name = f"pasm_twirled_{i}"
    circuits.append(c)
# Controllo: PASM standard senza twirl
qc_ref = QuantumCircuit(2, 2); qc_ref.h(0); qc_ref.h(1)
qc_ref.barrier(); qc_ref.cp(pi/2, 0, 1); qc_ref.barrier()
qc_ref.h(0); qc_ref.h(1); qc_ref.measure(0, 0); qc_ref.measure(1, 1)
qc_ref.name = "pasm_ref"
circuits.append(qc_ref)

circuits_t = pm.run(circuits)
print(f"Circuiti: {N_TWIRL} twirlati + 1 reference = {len(circuits_t)}")

job = SamplerV2(mode=backend).run(circuits_t, shots=SHOTS)
print(f"Job inviato! ID: {job.job_id()}")
for _ in range(120):
    s = job.status()
    if s == 'DONE': break
    print(f"  {s}"); time.sleep(10)

if job.status() == 'DONE':
    r = job.result()
    mis = []
    for i in range(N_TWIRL):
        c = r[i].data.c.get_counts()
        mis.append(calc_mi_2q(c))
    mi_ref = calc_mi_2q(r[N_TWIRL].data.c.get_counts())
    mi_mean = np.mean(mis); mi_std = np.std(mis, ddof=1)

    print("\n=== PAULI TWIRLED PASM ===")
    print(f"MI reference (no twirl): {mi_ref:.6f}")
    print(f"MI twirl medio: {mi_mean:.6f} ± {mi_std:.6f} su {N_TWIRL} circuiti")
    print(f"Delta: {mi_mean - mi_ref:.6f}")
    if mi_ref > mi_mean + 3*mi_std:
        print("\nCONCLUSIONE: MI si riduce con twirling -> errore coerente presente")
    elif abs(mi_ref - mi_mean) < mi_std:
        print("\nCONCLUSIONE: MI invariata -> non è errore coerente di gate")
    else:
        print("\nCONCLUSIONE: Risultato ambiguo, servono più statistiche")
else:
    print(f"Job fallito: {job.status()}")
