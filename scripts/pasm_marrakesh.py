"""
N47Lab — PASM su ibm_marrakesh (REVISIONATO)
optimization_level=1, readout_mitigation, Session
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, Session, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

import config
API_TOKEN = config.API_TOKEN
CRN = config.CRN
PHI = np.pi / 2
SHOTS = 8192

def calc_mi(cnt, nq, qi, qj):
    shots = sum(cnt.values()) or 1
    pk = {k: v/shots for k,v in cnt.items()}
    p00 = sum(v for k,v in pk.items() if k[nq-1-qi]=='0' and k[nq-1-qj]=='0')
    p01 = sum(v for k,v in pk.items() if k[nq-1-qi]=='0' and k[nq-1-qj]=='1')
    p10 = sum(v for k,v in pk.items() if k[nq-1-qi]=='1' and k[nq-1-qj]=='0')
    p11 = sum(v for k,v in pk.items() if k[nq-1-qi]=='1' and k[nq-1-qj]=='1')
    def H(ps):
        ps = [x for x in ps if x>0]
        return -sum(x*np.log2(x) for x in ps)
    return H([p00+p01, p10+p11]) + H([p00+p10, p01+p11]) - H([p00,p01,p10,p11])

print("="*60)
print("N47Lab - PASM su ibm_marrakesh (REVISIONATO)")
print("="*60)

qc_s = QuantumCircuit(3, 2)
qc_s.h(0); qc_s.h(2); qc_s.h(1)
qc_s.cp(PHI, 0, 1); qc_s.barrier()
qc_s.cp(PHI, 2, 1); qc_s.barrier()
qc_s.h(0); qc_s.h(2)
qc_s.measure(0, 0); qc_s.measure(2, 1)
qc_s.name = "pasm_shared"

qc_p = QuantumCircuit(4, 2)
qc_p.h(0); qc_p.h(2); qc_p.h(1); qc_p.h(3)
qc_p.cp(PHI, 0, 1); qc_p.barrier()
qc_p.cp(PHI, 2, 3); qc_p.barrier()
qc_p.h(0); qc_p.h(2)
qc_p.measure(0, 0); qc_p.measure(2, 1)
qc_p.name = "pasm_separate"

service = QiskitRuntimeService(channel='ibm_cloud', token=API_TOKEN, instance=CRN)
backend = service.backend("ibm_marrakesh")
print(f"Backend: {backend.name}")

pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
qc_s_t = pm.run(qc_s)
qc_p_t = pm.run(qc_p)

print(f"Shared depth={qc_s_t.depth()} gates={qc_s_t.count_ops()}")
print(f"Separate depth={qc_p_t.depth()} gates={qc_p_t.count_ops()}")

sampler = SamplerV2(mode=backend)
job = sampler.run([qc_s_t, qc_p_t], shots=SHOTS)
print(f"Job inviato! ID: {job.job_id()}")

with open("pasm_job_id.txt", "w") as f:
    f.write(job.job_id())

print("Per recuperare: python recupera_pasm.py")
