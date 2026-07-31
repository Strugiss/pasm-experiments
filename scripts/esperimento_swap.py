"""
N47Lab - SWAP test: due campi con memoria condivisa sono piu' simili?
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error

SHOTS = 32768
sim = AerSimulator()

noise = NoiseModel()
noise.add_all_qubit_quantum_error(depolarizing_error(0.005, 1), ['h'])
noise.add_all_qubit_quantum_error(depolarizing_error(0.01, 2), ['cx', 'cp'])
noise.add_all_qubit_quantum_error(depolarizing_error(0.02, 1), ['measure'])

print("="*60)
print("SWAP TEST: MEMORIA CONDIVISA vs SEPARATA")
print("="*60)

for phi in [0.25, 0.5, 1.0, np.pi/2, np.pi]:
    for desc, nm in [("ideale", None), ("rumore", noise)]:
        qc = QuantumCircuit(5, 1)
        qc.h(0); qc.h(2)
        qc.h(1)
        qc.cp(phi, 0, 1)
        qc.barrier()
        qc.cp(phi, 2, 1)
        qc.barrier()
        qc.h(3)
        qc.cswap(3, 0, 2)
        qc.h(3)
        qc.measure(3, 0)
        try:
            cnt = sim.run(qc, shots=SHOTS, noise_model=nm).result().get_counts()
            p0 = cnt.get('0', 0) / SHOTS
            fid = 2*p0 - 1
            marker = "*" if abs(fid) > 0.01 else ""
            print(f"  phi={phi:.3f} {desc:8s}: P(0)={p0:.4f} F={fid:.4f} {marker}")
        except Exception as e:
            print(f"  phi={phi:.3f} {desc:8s}: ERR: {e}")
