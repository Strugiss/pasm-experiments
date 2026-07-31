"""
N47Lab — Quantum Discord from QST data (MLE-corrected)
"""
import sys, math, json
sys.stdout.reconfigure(encoding='utf-8')
from qiskit_ibm_runtime import QiskitRuntimeService
import numpy as np

API2 = 'LmFkNotDbS5kNFuRwjnUDAN5RRuq2VwTz9l9aMtUr0YB'

def entropy(mat):
    ev = np.linalg.eigvalsh(mat)
    ev = ev[ev > 1e-12]
    return -np.sum(ev * np.log2(ev))

def pauli_op(p):
    sx = np.array([[0,1],[1,0]], dtype=complex)
    sy = np.array([[0,-1j],[1j,0]], dtype=complex)
    sz = np.array([[1,0],[0,-1]], dtype=complex)
    id2 = np.eye(2, dtype=complex)
    return {'I': id2, 'X': sx, 'Y': sy, 'Z': sz}[p]

def mle_projection(rho):
    """Spectral MLE: project onto positive semidefinite cone + renormalize."""
    evals, evecs = np.linalg.eigh(rho)
    evals_pos = np.maximum(evals, 0)
    rho_pos = evecs @ np.diag(evals_pos) @ evecs.conj().T
    rho_pos /= np.trace(rho_pos).real
    return rho_pos, evals

s2 = QiskitRuntimeService(channel='ibm_cloud', token=API2)
j = s2.job('d9l6q2jhdfks73ckir1g')
r = j.result()

bases = [('Z','Z'),('Z','X'),('Z','Y'),('X','Z'),('X','X'),('X','Y'),('Y','Z'),('Y','X'),('Y','Y')]

corr = np.zeros((4, 4))
paulis = ['I', 'X', 'Y', 'Z']
corr[0][0] = 1.0

for idx, (b1, b2) in enumerate(bases):
    counts = r[idx].data.c.get_counts()
    n = sum(counts.values())
    p00 = counts.get('00',0)/n; p01 = counts.get('01',0)/n
    p10 = counts.get('10',0)/n; p11 = counts.get('11',0)/n

    ev_bb = p00 + p11 - p01 - p10
    ev_Ib = (p00+p10) - (p01+p11)
    ev_bI = (p00+p01) - (p10+p11)

    i1 = paulis.index(b1); i2 = paulis.index(b2)
    corr[i1][i2] = ev_bb
    corr[0][i2] = ev_Ib
    corr[i1][0] = ev_bI

rho_raw = np.zeros((4,4), dtype=complex)
for i in range(4):
    for j in range(4):
        rho_raw += corr[i][j] * np.kron(pauli_op(paulis[i]), pauli_op(paulis[j]))
rho_raw /= 4.0
rho_raw = (rho_raw + rho_raw.conj().T) / 2

rho_mle, evals_pre = mle_projection(rho_raw)
n_neg = np.sum(evals_pre < -1e-12)

print("=== RICOSTRUZIONE QST (MLE) ===")
print("Job ID: d9l6q2jhdfks73ckir1g")
print()
print("Matrice densita RAW (pre-MLE):")
for i in range(4):
    row = ''
    for j in range(4):
        row += '%+.4f%+.4fj ' % (rho_raw[i,j].real, rho_raw[i,j].imag)
    print("  " + row)
print("Autovalori RAW: %s" % evals_pre)
print("Autovalori negativi: %d" % n_neg)

print()
print("Matrice densita MLE (positiva):")
for i in range(4):
    row = ''
    for j in range(4):
        row += '%+.4f%+.4fj ' % (rho_mle[i,j].real, rho_mle[i,j].imag)
    print("  " + row)

evals_pos = np.linalg.eigvalsh(rho_mle)
purity = np.trace(rho_mle @ rho_mle).real
S_AB = entropy(rho_mle)

rho_A = np.array([[rho_mle[0,0]+rho_mle[1,1], rho_mle[0,2]+rho_mle[1,3]],
                  [rho_mle[2,0]+rho_mle[3,1], rho_mle[2,2]+rho_mle[3,3]]], dtype=complex)
rho_B = np.array([[rho_mle[0,0]+rho_mle[2,2], rho_mle[0,1]+rho_mle[2,3]],
                  [rho_mle[1,0]+rho_mle[3,2], rho_mle[1,1]+rho_mle[3,3]]], dtype=complex)

S_A = entropy(rho_A)
S_B = entropy(rho_B)
MI_vn = S_A + S_B - S_AB

print()
print("Purity: %.6f" % purity)
print("Autovalori MLE: %s" % evals_pos)
print("S(AB): %.6f" % S_AB)
print("S(A): %.6f, S(B): %.6f" % (S_A, S_B))
print("MI(von Neumann): %.6f" % MI_vn)

print()
print("Calcolo discord (961 angoli su sfera di Bloch)...")
discords = {}
for target in ['A', 'B']:
    nq = 0 if target == 'A' else 1
    S_other = S_B if nq == 0 else S_A
    max_J = -1e10
    best_theta = best_phi = None
    for theta in np.linspace(0, np.pi, 31):
        for phi in np.linspace(0, 2*np.pi, 31):
            ct = math.cos(theta/2)
            st = math.sin(theta/2)
            psi = np.array([ct, st * complex(math.cos(phi), math.sin(phi))])
            Pi0 = np.outer(psi, psi.conj())
            Pi1 = np.eye(2) - Pi0
            if nq == 0:
                Pi0_full = np.kron(Pi0, np.eye(2))
                Pi1_full = np.kron(Pi1, np.eye(2))
            else:
                Pi0_full = np.kron(np.eye(2), Pi0)
                Pi1_full = np.kron(np.eye(2), Pi1)
            p0 = max(np.trace(Pi0_full @ rho_mle @ Pi0_full).real, 0)
            p1 = max(np.trace(Pi1_full @ rho_mle @ Pi1_full).real, 0)
            if p0 < 1e-10 or p1 < 1e-10:
                continue
            rho0 = (Pi0_full @ rho_mle @ Pi0_full) / p0
            rho1 = (Pi1_full @ rho_mle @ Pi1_full) / p1
            if nq == 0:
                rho_cond0 = np.array([[rho0[0,0]+rho0[2,2], rho0[0,1]+rho0[2,3]],
                                     [rho0[1,0]+rho0[3,2], rho0[1,1]+rho0[3,3]]], dtype=complex)
                rho_cond1 = np.array([[rho1[0,0]+rho1[2,2], rho1[0,1]+rho1[2,3]],
                                     [rho1[1,0]+rho1[3,2], rho1[1,1]+rho1[3,3]]], dtype=complex)
            else:
                rho_cond0 = np.array([[rho0[0,0]+rho0[1,1], rho0[0,2]+rho0[1,3]],
                                     [rho0[2,0]+rho0[3,1], rho0[2,2]+rho0[3,3]]], dtype=complex)
                rho_cond1 = np.array([[rho1[0,0]+rho1[1,1], rho1[0,2]+rho1[1,3]],
                                     [rho1[2,0]+rho1[3,1], rho1[2,2]+rho1[3,3]]], dtype=complex)
            tr0 = np.trace(rho_cond0).real
            tr1 = np.trace(rho_cond1).real
            if tr0 < 1e-10 or tr1 < 1e-10:
                continue
            rho_cond0 /= tr0
            rho_cond1 /= tr1
            J = S_other - (p0 * entropy(rho_cond0) + p1 * entropy(rho_cond1))
            if J > max_J:
                max_J = J
                best_theta = theta
                best_phi = phi
    discords[target] = MI_vn - max_J

print("Discord D(A|B) = %.6f (best theta=%.3f, phi=%.3f)" % (discords['A'], best_theta, best_phi))
print("Discord D(B|A) = %.6f" % discords['B'])
discord = min(discords['A'], discords['B'])
print("Discord minimo = %.6f" % discord)

if discord > 0.01:
    print()
    print("*** DISCORD QUANTISTICO RILEVATO: %.4f ***" % discord)
    print("La correlazione PASM contiene componente quantistica non-classica.")
    print("Dimostra che l'imprint non e' solo correlazione classica,")
    print("ma ha natura genuinamente quantistica (coerenza di fase condivisa).")
else:
    print()
    print("Discord trascurabile (<0.01). Correlazione classica.")

result = {
    "job_id": "d9l6q2jhdfks73ckir1g",
    "purity": float(purity),
    "S_AB": float(S_AB), "S_A": float(S_A), "S_B": float(S_B),
    "MI_vn": float(MI_vn),
    "discord_A": float(discords['A']),
    "discord_B": float(discords['B']),
    "discord_min": float(discord),
    "n_negative_eigenvalues_raw": int(n_neg),
    "eigenvalues_mle": [float(v) for v in evals_pos]
}
with open('n47lab_discord_result.json', 'w') as f:
    json.dump(result, f, indent=2)
print()
print("Risultato salvato in n47lab_discord_result.json")
