"""
N47Lab — CHSH Bell test con preparazione PASM
Verifica se la correlazione PASM viola la disuguaglianza CHSH.
Se S > 2: correlazione non-locale quantistica. Se S <= 2: classica.
"""
import sys, time; sys.stdout.reconfigure(encoding='utf-8')
import numpy as np; from numpy import pi, cos, sin, sqrt
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

API3 = 'MiPxZZAuroZIHuc_YEvPPrdoG9r7DalscGWqhL5NMcj0'
BACKEND = 'ibm_kingston'
SHOTS = 8192

def chsh_circuit(theta_a, theta_b):
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.h(1)
    qc.cp(pi/2, 0, 1)  # PASM phase imprint
    qc.rz(theta_a, 0); qc.rz(theta_b, 1)  # rotazioni misura CHSH
    qc.h(0); qc.h(1)
    qc.measure(0, 0); qc.measure(1, 1)
    return qc

S = QiskitRuntimeService(channel='ibm_cloud', token=API3, instance='auto')
backend = S.backend(BACKEND)
pm = generate_preset_pass_manager(optimization_level=1, backend=backend)

# CHSH angles: (a,b), (a,b'), (a',b), (a',b')
a, ap = 0.0, pi/4
b, bp = pi/8, 3*pi/8

circuits = []
for theta_a, theta_b in [(a,b), (a,bp), (ap,b), (ap,bp)]:
    c = chsh_circuit(theta_a, theta_b)
    c.name = f"chsh_a{theta_a:.2f}_b{theta_b:.2f}"
    circuits.append(c)

circuits_t = pm.run(circuits)
print(f"Circuiti CHSH: {len(circuits_t)}")

job = SamplerV2(mode=backend).run(circuits_t, shots=SHOTS)
print(f"Job inviato! ID: {job.job_id()}")
for _ in range(120):
    s = job.status()
    if s == 'DONE': break
    print(f"  {s}"); time.sleep(10)

if job.status() == 'DONE':
    r = job.result()
    print("\n=== CHSH PASM ===")
    E = []
    for i, (ta, tb) in enumerate([(a,b), (a,bp), (ap,b), (ap,bp)]):
        c = r[i].data.c.get_counts()
        t = sum(c.values()) or 1
        p00 = c.get('00',0)/t; p11 = c.get('11',0)/t
        p01 = c.get('01',0)/t; p10 = c.get('10',0)/t
        corr = p00 + p11 - p01 - p10  # E = <ZZ>
        E.append(corr)
        print(f"  a={ta:.2f} b={tb:.2f}: E={corr:.6f}")

    S = abs(E[0] - E[1] + E[2] + E[3])
    print(f"\n  CHSH S = {S:.6f}")
    print(f"  Violazione: {'SI (non-locale)' if S > 2 else 'NO (classica)'}")
    if S > 2:
        print(f"  Significatività: {S - 2:.6f} sopra limite classico")
else:
    print(f"Job fallito: {job.status()}")

print("\nInterpretazione:")
print("  S > 2: la correlazione PASM è quantistica non-locale (rivoluzione!)")
print("  S <= 2: la correlazione è classica (coerente con QST Discord < 0.01)")
