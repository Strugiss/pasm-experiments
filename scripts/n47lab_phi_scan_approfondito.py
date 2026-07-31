import json, time, os, gc, itertools
import numpy as np

os.environ['OMP_NUM_THREADS'] = '24'
os.environ['MKL_NUM_THREADS'] = '24'
os.environ['OPENBLAS_NUM_THREADS'] = '24'

from qiskit import QuantumCircuit
from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeSherbrooke

N_THREADS = 24
SHOTS = 8192
N_REPLICAS = 100
PHI_VALUES = [0, np.pi/8, np.pi/4, 3*np.pi/8, np.pi/2, 5*np.pi/8, 3*np.pi/4, 7*np.pi/8, np.pi]
PHI_FINE = np.linspace(0.5, 1.0, 11) * np.pi
OUTPUT = os.path.join(r'C:\Users\Utente\AppData\Local\Temp\opencode', 'n47lab_phi_scan_approfondito.json')

def build_pasm_standard(N, phi):
    qc = QuantumCircuit(N)
    qc.h(range(N))
    for i in range(N):
        for j in range(i+1, N):
            qc.cp(phi, i, j)
    qc.barrier()
    qc.h(range(N))
    qc.measure_all()
    return qc

def build_pasm_hgate(N, phi):
    """H-gate variant: apply H extra dopo CP"""
    qc = QuantumCircuit(N)
    qc.h(range(N))
    for i in range(N):
        for j in range(i+1, N):
            qc.cp(phi, i, j)
    qc.barrier()
    qc.h(range(N))
    qc.h(range(N))
    qc.measure_all()
    return qc

def build_pasm_separate(N, phi):
    qc = QuantumCircuit(N)
    qc.h(range(N))
    for i in range(N):
        qc.p(phi / N, i)
    qc.barrier()
    qc.h(range(N))
    qc.measure_all()
    return qc

def compute_mi(counts, N):
    outcomes = np.array(list(counts.keys()) if counts else [], dtype=int)
    probs = np.array(list(counts.values()) if counts else [], dtype=float)
    if len(probs) == 0:
        return {'MI': 0.0}
    probs = probs / probs.sum()
    eps = 1e-15
    p_joint = np.zeros((2, 2))
    for obs, prob in zip(outcomes, probs):
        b0 = (obs >> 0) & 1
        b1 = (obs >> 1) & 1
        p_joint[b0, b1] += prob
    p0 = p_joint.sum(axis=1)
    p1 = p_joint.sum(axis=0)
    mi = 0.0
    for b0 in (0, 1):
        for b1 in (0, 1):
            denom = p0[b0] * p1[b1] + eps
            if p_joint[b0, b1] > eps:
                mi += p_joint[b0, b1] * np.log2(p_joint[b0, b1] / denom)
    c_zz = p_joint[0, 0] + p_joint[1, 1] - p_joint[0, 1] - p_joint[1, 0]
    return {'MI': float(mi), 'p00': float(p_joint[0,0]), 'p11': float(p_joint[1,1]),
            'c_zz': float(c_zz)}

def run_experiment(simulator, label, configs, pm=None):
    results = {}
    total = len(configs)
    t0 = time.time()
    for idx, (circ_fn, N, phi, dd, rep) in enumerate(configs):
        qc = circ_fn(N, phi)
        if pm is not None:
            qc = pm.run(qc)
        job = simulator.run(qc, shots=SHOTS)
        counts = job.result().get_counts()
        res = compute_mi(counts, N)
        key = f"N{N}_phi{phi:.6f}_{circ_fn.__name__}_rep{rep}"
        results[key] = res
        elapsed = time.time() - t0
        rate = (idx + 1) / elapsed if elapsed > 0 else 0
        if (idx+1) % 50 == 0 or idx+1 == total:
            print(f"[{label}] {idx+1}/{total} | {rate:.1f} circ/s | ultimo MI={res['MI']:.6f}")
    return results

def summarize(results, label):
    grouped = {}
    for key, val in results.items():
        parts = key.split('_rep')[0]
        phi_val = float(key.split('_phi')[1].split('_')[0])
        circ = key.split('_')[-2] if '_pasm_' in key else key.split('_')[2]
        # better grouping
        gkey = key.rsplit('_rep', 1)[0]
        if gkey not in grouped:
            grouped[gkey] = {'MI': [], 'c_zz': []}
        grouped[gkey]['MI'].append(val['MI'])
        grouped[gkey]['c_zz'].append(val['c_zz'])
    summary = {}
    for gkey, vals in grouped.items():
        mi_arr = np.array(vals['MI'])
        summary[gkey] = {
            'MI_mean': float(np.mean(mi_arr)),
            'MI_std': float(np.std(mi_arr, ddof=1)) if len(mi_arr) > 1 else 0.0,
            'c_zz_mean': float(np.mean(vals['c_zz'])),
            'c_zz_std': float(np.std(vals['c_zz'], ddof=1)) if len(vals['c_zz']) > 1 else 0.0,
            'n_replicas': len(mi_arr)
        }
    return summary

def main():
    print("="*60)
    print("N47Lab -- phi-scan Approfondito (100 repliche)")
    print(f"Processori: {N_THREADS}, Shots: {SHOTS}, Repliche: {N_REPLICAS}")
    print("="*60)

    fake_backend = FakeSherbrooke()
    pm_noisy = generate_preset_pass_manager(optimization_level=1, backend=fake_backend)
    sim_ideal = AerSimulator(method='automatic', max_parallel_threads=N_THREADS)
    sim_noisy = AerSimulator.from_backend(fake_backend, method='automatic', max_parallel_threads=N_THREADS)

    # --- TESTS ---
    # 1) PASM standard N=2, phi-scan, 100 repliche (IDEALE + RUMOROSO)
    # 2) PASM H-gate N=2, phi-scan, 100 repliche (IDEALE)
    # 3) PASM standard phi-scan FINE 0.5pi->1.0pi, 100 repliche (IDEALE)
    # 4) PASM N=3, phi-scan, 50 repliche (IDEALE)
    # 5) PASM "QPU-like" -- SWAP test simulation at phi=pi

    configs_standard = []
    for phi in PHI_VALUES:
        for rep in range(N_REPLICAS):
            configs_standard.append((build_pasm_standard, 2, phi, False, rep))

    configs_hgate = []
    for phi in PHI_VALUES:
        for rep in range(N_REPLICAS):
            configs_hgate.append((build_pasm_hgate, 2, phi, False, rep))

    configs_fine = []
    for phi in PHI_FINE:
        for rep in range(N_REPLICAS):
            configs_fine.append((build_pasm_standard, 2, phi, False, rep))

    configs_n3 = []
    for phi in PHI_VALUES:
        for rep in range(50):
            configs_n3.append((build_pasm_standard, 3, phi, False, rep))

    all_data = {}
    timings = {}

    print("\n[Batch 1] PASM standard N=2 -- 100 rep x 9 phi")
    t1 = time.time()
    r1 = run_experiment(sim_ideal, "IDEALE-STD", configs_standard)
    all_data['ideale_standard_100rep'] = r1
    timings['ideale_standard_100rep'] = time.time() - t1
    print(f"  Tempo: {timings['ideale_standard_100rep']:.1f}s")
    gc.collect()

    print("\n[Batch 2] PASM H-gate N=2 -- 100 rep x 9 phi")
    t2 = time.time()
    r2 = run_experiment(sim_ideal, "IDEALE-HGATE", configs_hgate)
    all_data['ideale_hgate_100rep'] = r2
    timings['ideale_hgate_100rep'] = time.time() - t2
    print(f"  Tempo: {timings['ideale_hgate_100rep']:.1f}s")
    gc.collect()

    print("\n[Batch 3] PASM standard phi-scan FINE (0.5pi->1.0pi) -- 100 rep x 11 phi")
    t3 = time.time()
    r3 = run_experiment(sim_ideal, "IDEALE-FINE", configs_fine)
    all_data['ideale_fine_100rep'] = r3
    timings['ideale_fine_100rep'] = time.time() - t3
    print(f"  Tempo: {timings['ideale_fine_100rep']:.1f}s")
    gc.collect()

    print("\n[Batch 4] PASM N=3 phi-scan -- 50 rep x 9 phi")
    t4 = time.time()
    r4 = run_experiment(sim_ideal, "IDEALE-N3", configs_n3)
    all_data['ideale_n3_50rep'] = r4
    timings['ideale_n3_50rep'] = time.time() - t4
    print(f"  Tempo: {timings['ideale_n3_50rep']:.1f}s")
    gc.collect()

    print("\n[Batch 5] RUMOROSO Standard N=2 -- 100 rep x 9 phi")
    t5 = time.time()
    r5 = run_experiment(sim_noisy, "RUMOROSO-STD", configs_standard, pm=pm_noisy)
    all_data['rumoroso_standard_100rep'] = r5
    timings['rumoroso_standard_100rep'] = time.time() - t5
    print(f"  Tempo: {timings['rumoroso_standard_100rep']:.1f}s")
    gc.collect()

    print("\n[Batch 6] RUMOROSO H-gate N=2 -- 100 rep x 9 phi")
    t6 = time.time()
    r6 = run_experiment(sim_noisy, "RUMOROSO-HGATE", configs_hgate, pm=pm_noisy)
    all_data['rumoroso_hgate_100rep'] = r6
    timings['rumoroso_hgate_100rep'] = time.time() - t6
    print(f"  Tempo: {timings['rumoroso_hgate_100rep']:.1f}s")
    gc.collect()

    # Summarize
    summaries = {}
    for batch_label, batch_data in all_data.items():
        summaries[batch_label] = summarize(batch_data, batch_label)

    # Build clean output
    output = {
        'metadata': {
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'n_replicas': N_REPLICAS,
            'shots': SHOTS,
        },
        'timings': timings,
        'summaries': summaries,
        'theory': {}
    }

    # Add theoretical predictions for PASM standard N=2
    for phi in PHI_VALUES:
        c = np.cos(phi)
        p00 = (10 + 6*c) / 16
        p01 = (2 - 2*c) / 16
        p10, p11 = p01, p01
        p0 = p00 + p01
        p1 = p10 + p11
        q0 = p00 + p10
        q1 = p01 + p11
        eps = 1e-15
        mi = 0.0
        for prob, px, py in [(p00, p0, q0), (p01, p0, q1), (p10, p1, q0), (p11, p1, q1)]:
            if prob > eps:
                mi += prob * np.log2(prob / (px*py + eps) + eps)
        output['theory'][f'N2_phi{phi:.6f}'] = float(mi)

    for phi in PHI_FINE:
        c = np.cos(phi)
        p00 = (10 + 6*c) / 16
        p01 = (2 - 2*c) / 16
        p10, p11 = p01, p01
        p0 = p00 + p01
        p1 = p10 + p11
        q0 = p00 + p10
        q1 = p01 + p11
        eps = 1e-15
        mi = 0.0
        for prob, px, py in [(p00, p0, q0), (p01, p0, q1), (p10, p1, q0), (p11, p1, q1)]:
            if prob > eps:
                mi += prob * np.log2(prob / (px*py + eps) + eps)
        output['theory'][f'N2_phi{phi:.6f}_fine'] = float(mi)

    with open(OUTPUT, 'w') as f:
        json.dump(output, f, indent=2, cls=CustomEncoder)
    print(f"\nRisultati salvati in {OUTPUT}")

    # Print key comparisons
    print("\n=== RIEPILOGO ===")
    for batch, summ in summaries.items():
        print(f"\n[{batch}]")
        for key in sorted(summ.keys()):
            v = summ[key]
            print(f"  {key}: MI={v['MI_mean']:.6f} +- {v['MI_std']:.6f}")
        print()

    # Compare QPU phi-scan values vs theory
    print("=== CONFRONTO QPU phi-scan ===")
    qpu_data = {0.0: 0.0000, 0.5: 0.0653, 0.75: 0.3921, 1.0: 0.7852}
    for phi_ratio, mi_qpu in qpu_data.items():
        phi = phi_ratio * np.pi
        key_th = f'N2_phi{phi:.6f}'
        if key_th in output['theory']:
            mi_th = output['theory'][key_th]
        else:
            mi_th = 0
        for batch, summ in summaries.items():
            for sk, sv in summ.items():
                if f'{phi:.6f}' in sk and 'build_pasm_standard' in sk and 'n2' not in batch.lower():
                    pass
        print(f"  phi/pi={phi_ratio:.2f}: QPU={mi_qpu:.4f}, Teorico PASM={mi_th:.6f}, Ratio={mi_qpu/mi_th if mi_th > 1e-6 else 'inf'}")

    total = sum(timings.values())
    print(f"\nTempo totale: {total:.1f}s ({total/60:.1f} min)")

class CustomEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.floating):
            return float(obj)
        if isinstance(obj, np.integer):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return super().default(obj)

if __name__ == '__main__':
    main()
