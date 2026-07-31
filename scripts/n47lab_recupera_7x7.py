"""
N47Lab — Recupero e analisi 7 nuovi esperimenti della rete 7x7
"""
import sys, json, time, numpy as np
sys.stdout.reconfigure(encoding='utf-8')
from qiskit_ibm_runtime import QiskitRuntimeService
import config

with open("n47lab_7x7_job_ids.json", encoding="utf-8") as f:
    JOBS = json.load(f)["jobs"]

def mi_from_counts(counts):
    total = sum(counts.values()) or 1
    px = np.zeros(4)
    for k,v in counts.items():
        try: px[int(k,2)] = v/total
        except: pass
    px = np.clip(px, 1e-12, 1)
    pA = np.array([px[0]+px[1], px[2]+px[3]])
    pB = np.array([px[0]+px[2], px[1]+px[3]])
    pA, pB = np.clip(pA,1e-12,1), np.clip(pB,1e-12,1)
    mi = sum(px[i]*(np.log2(px[i])-np.log2(pA[i//2]*pB[i%2])) for i in range(4))
    return max(0, mi)

if __name__ == "__main__":
    print("="*70)
    print("N47Lab - Recupero 7 esperimenti 7x7")
    print("="*70)
    
    service = QiskitRuntimeService(channel='ibm_cloud', token=config.API_TOKEN, instance=config.CRN)
    all_results = {}
    
    for exp_name, info in JOBS.items():
        jid = info["job_id"]
        print(f"\n[{exp_name}] {info['description']}")
        print(f"  Job: {jid}")
        
        try:
            job = service.job(jid)
            status = job.status()
            status_str = status.name if hasattr(status, 'name') else str(status)
            print(f"  Stato: {status_str}")
            
            if status_str in ("DONE", "JobStatus.DONE"):
                result = job.result()
                results = []
                idx = 0
                for pub_result in result:
                    if hasattr(pub_result, 'data'):
                        data = pub_result.data
                        if hasattr(data, 'meas'):
                            counts = data.meas.get_counts()
                        elif hasattr(data, 'c'):
                            counts = data.c.get_counts()
                        else:
                            # fallback: cerca il primo array-like
                            for attr_name in dir(data):
                                if not attr_name.startswith('_'):
                                    try:
                                        arr = getattr(data, attr_name)
                                        if hasattr(arr, 'get_counts'):
                                            counts = arr.get_counts()
                                            break
                                    except: pass
                            else:
                                counts = {}
                    else:
                        counts = pub_result.get_counts() if hasattr(pub_result, 'get_counts') else {}
                    
                    mi = mi_from_counts(counts)
                    results.append({"index": idx, "counts": counts, "MI": round(mi,6)})
                    idx += 1
                
                all_results[exp_name] = {"status": "DONE", "results": results}
                print(f"  Risultati: {len(results)} circuiti recuperati")
                
                for r in results[:5]:
                    print(f"    idx={r['index']} MI={r['MI']:.6f}")
                if len(results) > 5:
                    print(f"    ... e altri {len(results)-5}")
            else:
                all_results[exp_name] = {"status": status_str}
                print(f"  Ancora in coda/esecuzione")
        except Exception as e:
            print(f"  ERRORE: {e}")
            all_results[exp_name] = {"status": "ERROR", "error": str(e)}
    
    with open("n47lab_7x7_results.json", "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*70}")
    done = sum(1 for v in all_results.values() if v.get("status") == "DONE")
    print(f"Completati: {done}/{len(all_results)}")
    print(f"Risultati salvati in: n47lab_7x7_results.json")
