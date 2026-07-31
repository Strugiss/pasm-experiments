"""
N47Lab — Monitor automatico 7 esperimenti 7x7
Controlla ogni 60s, recupera risultati appena DONE
"""
import sys, time, json, numpy as np
sys.stdout.reconfigure(encoding='utf-8')
import config
from qiskit_ibm_runtime import QiskitRuntimeService

JOBS = {
    'PHI_ECHO': 'd9l5p4bhdfks73ckhlog',
    'PASM_DIST': 'd9l5p4rjf64c739j30n0',
    'PASM_3Q': 'd9l5p5abr2fc73e8884g',
    'PASM_NOISE': 'd9l5p63jf64c739j30og',
    'PASM_PLUS': 'd9l5p6rhdfks73ckhls0',
    'PASM_SCALE': 'd9l5p7abr2fc73e8887g',
    'WITNESS': 'd9l5p7qbr2fc73e88890',
}

def mi_from_counts(counts):
    total = sum(counts.values()) or 1
    px = np.zeros(4)
    for k,v in counts.items():
        try: px[int(k,2)] = v/total
        except: pass
    px = np.clip(px, 1e-12, 1)
    pA = np.clip(np.array([px[0]+px[1], px[2]+px[3]]), 1e-12, 1)
    pB = np.clip(np.array([px[0]+px[2], px[1]+px[3]]), 1e-12, 1)
    mi = sum(px[i]*(np.log2(px[i])-np.log2(pA[i//2]*pB[i%2])) for i in range(4))
    return max(0, mi)

if __name__ == "__main__":
    service = QiskitRuntimeService(channel='ibm_cloud', token=config.API_TOKEN, instance=config.CRN)
    completed = {n: False for n in JOBS}
    results = {}
    first_run = True
    
    while not all(completed.values()):
        if not first_run:
            time.sleep(60)
        first_run = False
        
        for name, jid in JOBS.items():
            if completed[name]:
                continue
            try:
                job = service.job(jid)
                st = job.status()
                st_str = st if isinstance(st, str) else st.name
                
                if st_str == 'DONE':
                    cl = job.result().get_counts()
                    if isinstance(cl, dict):
                        cl = [cl]
                    mis = [mi_from_counts(c) for c in cl]
                    
                    results[name] = {
                        'status': 'DONE',
                        'n_circuits': len(cl),
                        'MI_values': [round(m,6) for m in mis],
                        'MI_mean': round(float(np.mean(mis)),6),
                        'MI_max': round(float(max(mis)),6),
                    }
                    completed[name] = True
                    print(f"[{time.strftime('%H:%M:%S')}] {name}: DONE! {len(cl)} circ, MI_mean={results[name]['MI_mean']:.6f}")
                
                elif st_str == 'RUNNING':
                    print(f"[{time.strftime('%H:%M:%S')}] {name}: RUNNING...")
                else:
                    print(f"[{time.strftime('%H:%M:%S')}] {name}: {st_str}")
            except Exception as e:
                print(f"[{time.strftime('%H:%M:%S')}] {name}: ERRORE {e}")
        
        print(f"  -> {sum(completed.values())}/{len(completed)} completati")
    
    print("\n" + "="*60)
    print("TUTTI I 7 ESPERIMENTI COMPLETATI!")
    print("="*60)
    
    with open("n47lab_7x7_results_auto.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    for name, r in results.items():
        print(f"\n{name}: MI_mean={r['MI_mean']:.6f}, MI_max={r['MI_max']:.6f}")
    
    print(f"\nRisultati salvati in: n47lab_7x7_results_auto.json")
