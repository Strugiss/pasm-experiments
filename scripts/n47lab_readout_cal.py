"""
N47Lab — Readout Error Calibration per PASM
Calcola matrice di assegnazione 4x4 per coppia di qubit
Usata per REM (Readout Error Mitigation) su tutti gli esperimenti
"""
import sys, time; sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

API3 = 'MiPxZZAuroZIHuc_YEvPPrdoG9r7DalscGWqhL5NMcj0'
BACKEND = 'ibm_kingston'
SHOTS = 8192

S = QiskitRuntimeService(channel='ibm_cloud', token=API3, instance='auto')
backend = S.backend(BACKEND)
pm = generate_preset_pass_manager(optimization_level=1, backend=backend)

# Calibrazione: prepara |00>, |01>, |10>, |11> e misura
cal_states = [(0, '00'), (1, '01'), (2, '10'), (3, '11')]
circuits = []
for state_id, label in cal_states:
    qc = QuantumCircuit(2, 2)
    if state_id & 1:  # qubit 0 in |1>
        qc.x(0)
    if state_id & 2:  # qubit 1 in |1>
        qc.x(1)
    qc.measure(0, 0); qc.measure(1, 1)
    qc.name = f"cal_{label}"
    circuits.append(qc)

circuits_t = pm.run(circuits)
print(f"Circuiti calibrazione: {len(circuits_t)}")

job = SamplerV2(mode=backend).run(circuits_t, shots=SHOTS)
print(f"Job inviato! ID: {job.job_id()}")
for _ in range(120):
    s = job.status()
    if s == 'DONE': break
    print(f"  {s}"); time.sleep(10)

if job.status() == 'DONE':
    r = job.result()
    print("\n=== MATRICE DI ASSEGNAZIONE READOUT ===")
    outcomes = ['00','01','10','11']
    M = np.zeros((4,4))
    for prep_idx, (_, prep_label) in enumerate(cal_states):
        c = r[prep_idx].data.c.get_counts()
        t = sum(c.values()) or 1
        for meas_idx, meas_label in enumerate(outcomes):
            M[prep_idx, meas_idx] = c.get(meas_label, 0)/t
        print(f"Preparato |{prep_label}> -> misurato: ", end="")
        print(" ".join(f"{M[prep_idx,j]:.4f}" for j in range(4)))

    print(f"\nReadout fidelity media: {np.mean([M[i,i] for i in range(4)]):.4f}")
    print(f"Readout error medio: {1 - np.mean([M[i,i] for i in range(4)]):.4f}")

    # Salva matrice per uso successivo
    np.save("readout_matrix_kingston.npy", M)
    print("\nMatrice salvata in readout_matrix_kingston.npy")
    print("Usare: M = np.load('readout_matrix_kingston.npy') per REM")
else:
    print(f"Job fallito: {job.status()}")
