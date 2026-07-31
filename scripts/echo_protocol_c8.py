"""
N47Lab — Echo Protocol C8 su ibm_marrakesh (REVISIONATO da 50 agenti)
Confronta echo (CPhase + delay + anti-CPhase) vs baseline (solo delay)
Scan tau: 0 -> 300 us (T2 ~150us, oltre e' solo rumore)
"""
import numpy as np
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

import config
API_TOKEN = config.API_TOKEN
CRN = config.CRN
PHI = np.pi / 2
SHOTS = 8192
TAUS_US = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300]

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
print("N47Lab - Echo Protocol C8 (REVISIONATO)")
print("Scan tau: 0-300 us, 11 valori + controllo baseline")
print("="*60)

# Circuito echo: |+>|+> -> CPhase(phi) -> delay(tau) -> CPhase(-phi) -> H
qc_list = []
for tau_us in TAUS_US:
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.h(1)
    qc.cp(PHI, 0, 1)
    qc.barrier()
    qc.delay(tau_us, 0, unit='us')
    qc.delay(tau_us, 1, unit='us')
    qc.barrier()
    qc.cp(-PHI, 0, 1)
    qc.h(0); qc.h(1)
    qc.measure(0, 0); qc.measure(1, 1)
    qc.name = f"echo_tau_{tau_us}us"
    qc_list.append(qc)

# Circuito controllo (baseline): |+> -> delay(tau) -> H (nessun CPhase)
# Isola decadimento T1/T2 senza imprint
for tau_us in TAUS_US:
    qc = QuantumCircuit(2, 2)
    qc.h(0); qc.h(1)
    qc.barrier()
    qc.delay(tau_us, 0, unit='us')
    qc.delay(tau_us, 1, unit='us')
    qc.barrier()
    qc.h(0); qc.h(1)
    qc.measure(0, 0); qc.measure(1, 1)
    qc.name = f"ctrl_tau_{tau_us}us"
    qc_list.append(qc)

service = QiskitRuntimeService(channel='ibm_cloud', token=API_TOKEN, instance=CRN)
backend = service.backend("ibm_marrakesh")
print(f"Backend: {backend.name}")

# optimization_level=1 per preservare i delay (opt=3 potrebbe ottimizzarli via)
pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
qc_t_list = [pm.run(qc) for qc in qc_list]

for i in range(0, len(qc_t_list), 2):
    print(f"tau={TAUS_US[i//2]:>3}us  echo_depth={qc_t_list[i].depth():>4}  ctrl_depth={qc_t_list[i+1].depth():>4}")

sampler = SamplerV2(mode=backend)
job = sampler.run(qc_t_list, shots=SHOTS)
print(f"Job inviato! ID: {job.job_id()}")
print(f"Circuiti: {len(qc_t_list)} (11 echo + 11 controllo)")

with open("echo_job_id.txt", "w") as f:
    f.write(job.job_id())

print("Per recuperare: python recupera_echo.py")
