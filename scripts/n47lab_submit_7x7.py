"""
N47Lab — Submission: 7 nuovi esperimenti della rete 7x7
Tutti su ibm_marrakesh, open plan (no Session), SamplerV2(mode=backend)
"""
import sys, json, time, os
sys.stdout.reconfigure(encoding='utf-8')
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
import config

SHOTS = 8192
BACKEND_NAME = "ibm_marrakesh"
PHIS = [0, 0.1963, 0.3927, 0.5890, 0.7854, 0.9817, 1.1781, 1.3744, 1.5708, 1.7671, 1.9635, 2.1598, 2.3562, 2.5525, 2.7489, 2.9452, 3.1416]

EXPERIMENTS = {}

# 1. PHI_ECHO — phi-scan con echo pulse
def build_phi_echo():
    qcs = []
    for phi in np.linspace(0, np.pi, 17):
        for typ in ['echo','noecho']:
            qc = QuantumCircuit(2)
            qc.h(0); qc.h(1)
            qc.cp(phi, 0, 1)
            qc.barrier()
            if typ == 'echo':
                qc.barrier()
                qc.x(0); qc.x(1)
                qc.barrier()
            qc.barrier()
            qc.h(0); qc.h(1)
            qc.measure_all()
            qc.metadata = {'phi': round(float(phi),4), 'type': typ, 'exp': 'phi_echo'}
            qcs.append(qc)
    return qcs, "phi_echo", "phi-scan con echo (34 circuiti, 2 qubit)"

# 2. PASM_DIST — distanza fisica
def build_pasm_dist():
    qcs = []
    phi = np.pi/2
    for d, (qa, qb) in enumerate([(0,1),(0,2),(1,3)]):
        qc = QuantumCircuit(5, 2)
        qc.h(qa); qc.h(qb)
        qc.cp(phi, qa, qb)
        qc.barrier()
        qc.h(qa); qc.h(qb)
        qc.measure(qa,0); qc.measure(qb,1)
        qc.metadata = {'distance': d, 'exp': 'pasm_dist'}
        qcs.append(qc)
    return qcs, "pasm_dist", "PASM distanza fisica (3 circuiti, 5 qubit)"

# 3. PASM_3Q
def build_pasm_3q():
    qcs = []
    phi = np.pi/2
    for cond in ['shared','separate']:
        qc = QuantumCircuit(3)
        if cond == 'shared':
            qc.h(0); qc.h(1); qc.h(2)
            qc.cp(phi,0,1); qc.cp(phi,0,2); qc.cp(phi,1,2)
        else:
            qc.h(0); qc.h(1)
        qc.barrier()
        qc.h(0); qc.h(1); qc.h(2)
        qc.measure_all()
        qc.metadata = {'cond': cond, 'exp': 'pasm_3q'}
        qcs.append(qc)
    return qcs, "pasm_3q", "PASM 3 qubit (2 circuiti, 3 qubit)"

# 4. PASM_NOISE
def build_pasm_noise():
    qcs = []
    phi = np.pi/2
    for theta in [0, 0.1, 0.5, 1.0]:
        qc = QuantumCircuit(2)
        qc.h(0); qc.h(1)
        qc.cp(phi,0,1)
        qc.barrier()
        qc.rx(theta,0)
        qc.barrier()
        qc.h(0); qc.h(1)
        qc.measure_all()
        qc.metadata = {'theta': theta, 'exp': 'pasm_noise'}
        qcs.append(qc)
    return qcs, "pasm_noise", "PASM noise scan (4 circuiti, 2 qubit)"

# 5. PASM_PLUS
def build_pasm_plus():
    qcs = []
    for phi in PHIS[::2]:
        qc = QuantumCircuit(2)
        qc.h(0); qc.h(1)
        qc.cp(phi,0,1)
        qc.barrier()
        qc.h(0); qc.h(1)
        qc.measure_all()
        qc.metadata = {'phi': round(float(phi),4), 'cond': 'plus', 'exp': 'pasm_plus'}
        qcs.append(qc)
    return qcs, "pasm_plus", "PASM |++> init (9 circuiti, 2 qubit)"

# 6. PASM_SCALE
def build_pasm_scale():
    qcs = []
    phi = np.pi/2
    for n in [2,3,4,5]:
        qc = QuantumCircuit(6, 2)
        for j in range(n):
            qc.h(j)
        for j in range(n-1):
            qc.cp(phi, j, j+1)
        qc.barrier()
        qc.h(0); qc.h(1)
        qc.measure(0,0); qc.measure(1,1)
        qc.metadata = {'n_qubit': n, 'exp': 'pasm_scale'}
        qcs.append(qc)
    return qcs, "pasm_scale", "PASM N-qubit scaling (4 circuiti, fino a 6 qubit)"

# 7. WITNESS
def build_witness():
    qcs = []
    for cond in ['shared','separate']:
        for phi in PHIS[::4]:
            qc = QuantumCircuit(2)
            if cond == 'shared':
                qc.h(0); qc.h(1)
            else:
                qc.h(0)
            qc.cp(phi,0,1)
            qc.barrier()
            qc.h(0); qc.h(1)
            qc.measure_all()
            qc.metadata = {'cond': cond, 'phi': round(float(phi),4), 'exp': 'witness'}
            qcs.append(qc)
    return qcs, "witness", "Entanglement witness (10 circuiti, 2 qubit)"

BUILDERS = [build_phi_echo, build_pasm_dist, build_pasm_3q, build_pasm_noise, build_pasm_plus, build_pasm_scale, build_witness]

if __name__ == "__main__":
    print("="*70)
    print("N47Lab — Submission 7 nuovi esperimenti (rete 7x7)")
    print("="*70)
    
    service = QiskitRuntimeService(channel='ibm_cloud', token=config.API_TOKEN, instance=config.CRN)
    backend = service.backend(BACKEND_NAME)
    print(f"Backend: {backend.name}")
    
    all_jobs = {}
    total_circuits = 0
    
    for builder in BUILDERS:
        qcs, exp_name, description = builder()
        total_circuits += len(qcs)
        print(f"\n[{exp_name}] {description}")
        
        qc_t = transpile(qcs, backend, optimization_level=1)
        
        sampler = SamplerV2(mode=backend)
        job = sampler.run(qc_t, shots=SHOTS)
        
        jid = job.job_id()
        all_jobs[exp_name] = {
            "job_id": jid,
            "description": description,
            "n_circuits": len(qcs),
            "status": "submitted",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
        }
        print(f"  Job inviato! ID: {jid}")
        time.sleep(1)  # delay tra submission
    
    # Salva job IDs
    output = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "backend": BACKEND_NAME,
        "shots": SHOTS,
        "total_circuits": total_circuits,
        "jobs": all_jobs
    }
    with open("n47lab_7x7_job_ids.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    print(f"TOTALE: {len(all_jobs)} job, {total_circuits} circuiti inviati")
    print(f"Job IDs salvati in: n47lab_7x7_job_ids.json")
    print(f"{'='*70}")
