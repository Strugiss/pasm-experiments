"""
N47Lab — Relancio 3 esperimenti cancellati su ibm_kingston (API2)
QST/DISCORD + PASM_SCALE (4 circ, 6q) + WITNESS (10 circ)
"""
import sys, math, json, time
sys.stdout.reconfigure(encoding='utf-8')
from qiskit import QuantumCircuit
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager

API2 = "LmFkNotDbS5kNFuRwjnUDAN5RRuq2VwTz9l9aMtUr0YB"
BACKEND = "ibm_kingston"

def pasm_nqubit_circuit(n, phi_denom=4, shared=True):
    qc = QuantumCircuit(n, n)
    for i in range(n):
        qc.h(i)
    if shared:
        for i in range(n):
            for j in range(i+1, n):
                qc.cp(2*math.pi/phi_denom, i, j)
    else:
        for i in range(n):
            qc.p(2*math.pi/(phi_denom*2), i)
    for i in range(n):
        qc.h(i)
    qc.measure(range(n), range(n))
    return qc

def witness_circuits():
    """Entanglement witness + fidelity."""
    circs = []
    for phi_step in range(10):
        phi = phi_step * 2*math.pi / 10
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cp(phi, 0, 1)
        qc.h(1)
        qc.measure(0, 0)
        qc.measure(1, 1)
        circs.append(qc)
    return circs

def qst_discord_circuits():
    """9 basi di misura per tomografia."""
    circs = []
    bases = [('z','z'),('z','x'),('z','y'),('x','z'),('x','x'),('x','y'),('y','z'),('y','x'),('y','y')]
    for b1, b2 in bases:
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.cp(math.pi/2, 0, 1)
        if b1 == 'x': qc.h(0)
        elif b1 == 'y': qc.sdg(0); qc.h(0)
        if b2 == 'x': qc.h(1)
        elif b2 == 'y': qc.sdg(1); qc.h(1)
        qc.measure(0, 0)
        qc.measure(1, 1)
        circs.append(qc)
    return circs

# ─── BUILD ───
print("Costruzione circuiti...")

# Exp A: QST/DISCORD (9 circuiti)
circs_a = qst_discord_circuits()
labels_a = ['QST_'+str(i) for i in range(9)]
print("  QST/DISCORD: 9 circuiti, 2 qubit")

# Exp B: PASM_SCALE (4 circuiti: 4q,5q,6q shared + baseline)
circs_b = [
    pasm_nqubit_circuit(4, shared=True),
    pasm_nqubit_circuit(4, shared=False),
    pasm_nqubit_circuit(6, shared=True),
    pasm_nqubit_circuit(6, shared=False),
]
labels_b = ['PASM_4q_S','PASM_4q_P','PASM_6q_S','PASM_6q_P']
print("  PASM_SCALE: 4 circuiti (4q,6q)")

# Exp C: WITNESS (10 circuiti, 2 qubit)
circs_c = witness_circuits()
labels_c = ['WITNESS_'+str(i) for i in range(10)]
print("  WITNESS: 10 circuiti, 2 qubit")

all_circuits = circs_a + circs_b + circs_c
all_labels = labels_a + labels_b + labels_c

# ─── TRANSPILE + SUBMIT ───
print("Connessione a", BACKEND)
service = QiskitRuntimeService(channel='ibm_cloud', token=API2)
backend = service.backend(BACKEND)

pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
circs_transpiled = pm.run(all_circuits)
print("Circuiti transpilati:", len(circs_transpiled))

sampler = SamplerV2(mode=backend)
job = sampler.run(circs_transpiled, shots=8192)
job_id = job.job_id  # This will correctly get the string now with Qiskit 2.x
print("JOB INVIATO:", job_id)
print("Status:", job.status())

# Salva
info = {
    "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
    "job_id": job_id,
    "backend": BACKEND,
    "account": "API2",
    "esperimenti": ["QST_DISCORD (9 circ)", "PASM_SCALE (4 circ)", "WITNESS (10 circ)"],
    "n_circuiti": len(all_circuits),
    "shots": 8192,
    "status": str(job.status())
}
with open("n47lab_relancio_job.json", "w") as f:
    json.dump(info, f, indent=2)
print("Info salvate in n47lab_relancio_job.json")
