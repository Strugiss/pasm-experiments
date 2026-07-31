"""
N47Lab — Esperimento PASM correttivo con H gate prima della misura
"""
import sys, time
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from numpy import pi, cos, log2
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

API2 = 'LmFkNotDbS5kNFuRwjnUDAN5RRuq2VwTz9l9aMtUr0YB'
BACKEND = 'ibm_kingston'
SHOTS = 8192

S = QiskitRuntimeService(channel='ibm_cloud', token=API2)
backend = S.backend(BACKEND)

def entropy_bin(x):
    x = np.clip(x, 1e-15, 1-1e-15)
    return -x*log2(x) - (1-x)*log2(1-x)

def make_circuit(N, phi, with_h=True):
    qc = QuantumCircuit(N, N)
    for i in range(N):
        qc.h(i)
    qc.barrier()
    for i in range(N):
        for j in range(i+1, N):
            qc.cx(i, j)
            qc.rz(phi, j)
            qc.cx(i, j)
    qc.barrier()
    if with_h:
        for i in range(N):
            qc.h(i)  # Converts phase info to population
    qc.measure(range(N), range(N))
    qc.name = f"PASM_N{N}_phi{phi:.1f}_H{int(with_h)}"
    return qc

# Full phi-scan for N=2, with and without H gate
phis = [0.0, pi/2, pi, 3*pi/2]
circuits = []
for phi in phis:
    circuits.append(make_circuit(2, phi, with_h=True))
    circuits.append(make_circuit(2, phi, with_h=False))
# Add N=3 with H
for phi in phis:
    circuits.append(make_circuit(3, phi, with_h=True))

pm = generate_preset_pass_manager(optimization_level=1, backend=backend)
circuits_t = pm.run(circuits)
print(f"Circuiti: {len(circuits_t)}")

job = SamplerV2(mode=backend).run(circuits_t, shots=SHOTS)
job_id = job.job_id()
print(f"Job inviato! ID: {job_id}")

for _ in range(120):
    s = job.status()
    if s == 'DONE':
        break
    print(f"  Stato: {s}")
    time.sleep(10)

if job.status() == 'DONE':
    r = job.result()
    print("\n=== RISULTATI ===")
    print(f"{'N':>2} {'phi':>6} {'H':>2} {'c_zz':>8} {'MI':>8}")
    print("-"*30)
    idx = 0
    for phi in phis:
        # N=2 with H
        c = r[idx].data.c.get_counts()
        t = sum(c.values())
        p00, p01, p10, p11 = c.get('00',0)/t, c.get('01',0)/t, c.get('10',0)/t, c.get('11',0)/t
        p_tot = p00 + p01 + p10 + p11
        p0 = p00 + p01; p1 = p10 + p11
        q0 = p00 + p10; q1 = p01 + p11
        def H(ps):
            ps = [x for x in ps if x>0]
            return -sum(x*log2(x) for x in ps)
        MI = H([p0, p1]) + H([q0, q1]) - H([p00, p01, p10, p11])
        print(f"{2:2d} {phi:6.2f}  Y {c_zz:8.4f} {MI:8.4f}")

        # N=2 without H
        c = r[idx].data.c.get_counts()
        t = sum(c.values())
        p00, p01, p10, p11 = c.get('00',0)/t, c.get('01',0)/t, c.get('10',0)/t, c.get('11',0)/t
        c_zz = p00 - p01 - p10 + p11
        p0 = p00 + p01; p1 = p10 + p11
        q0 = p00 + p10; q1 = p01 + p11
        MI = H([p0, p1]) + H([q0, q1]) - H([p00, p01, p10, p11])
        print(f"{2:2d} {phi:6.2f}  N {c_zz:8.4f} {MI:8.4f}")
        idx += 1

    for phi in phis:
        c = r[idx].data.c.get_counts()
        t = sum(c.values())
        p00 = (c.get('000',0)+c.get('001',0))/t
        p01 = (c.get('010',0)+c.get('011',0))/t
        p10 = (c.get('100',0)+c.get('101',0))/t
        p11 = (c.get('110',0)+c.get('111',0))/t
        c_zz = p00 - p01 - p10 + p11
        p0 = p00 + p01; p1 = p10 + p11
        q0 = p00 + p10; q1 = p01 + p11
        MI = H([p0, p1]) + H([q0, q1]) - H([p00, p01, p10, p11])
        print(f"{3:2d} {phi:6.2f}  Y {c_zz:8.4f} {MI:8.4f}")
        idx += 1

    print(f"\nJob {job_id} completato con successo!")
else:
    print(f"Job non completato: {job.status()}")
    print(f"ID: {job_id}")
    print(f"Recupera con: python -c 'from qiskit_ibm_runtime import QiskitRuntimeService; S = QiskitRuntimeService(channel=\"ibm_cloud\", token=\"API2\"); j = S.job(\"{job_id}\"); print(j.status())'")
