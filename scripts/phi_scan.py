"""
N47Lab — phi-scan completo 0->pi su ibm_marrakesh (REVISIONATO)
optimization_level=1, readout_mitigation, Session
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, Session, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

import config
API_TOKEN = config.API_TOKEN
CRN = config.CRN
SHOTS = 8192
NPHI = 16
PHIS = [i * np.pi / NPHI for i in range(NPHI + 1)]

print("="*60)
print("N47Lab - phi-scan 0->pi (REVISIONATO)")
print(f"{NPHI+1} valori di phi, {SHOTS} shots cad.")
print("="*60)

qc_list = []
for phi in PHIS:
    qc = QuantumCircuit(3, 2)
    qc.h(0); qc.h(2); qc.h(1)
    qc.cp(phi, 0, 1)
    qc.barrier()
    qc.cp(phi, 2, 1)
    qc.barrier()
    qc.h(0); qc.h(2)
    qc.measure(0, 0); qc.measure(2, 1)
    qc.name = f"pasm_phi_{phi:.4f}"
    qc_list.append(qc)

service = QiskitRuntimeService(channel='ibm_cloud', token=API_TOKEN, instance=CRN)
backend = service.backend("ibm_marrakesh")
print(f"Backend: {backend.name}")

pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
qc_t_list = [pm.run(qc) for qc in qc_list]

for i, qc_t in enumerate(qc_t_list[:3]):
    print(f"phi={PHIS[i]:.4f} depth={qc_t.depth()} gates={qc_t.count_ops()}")
print(f"... e altri {len(qc_t_list)-3} circuiti")

sampler = SamplerV2(mode=backend)
job = sampler.run(qc_t_list, shots=SHOTS)
print(f"Job inviato! ID: {job.job_id()}")

with open("phi_job_id.txt", "w") as f:
    f.write(job.job_id())

print("Per recuperare: python recupera_phi.py")
