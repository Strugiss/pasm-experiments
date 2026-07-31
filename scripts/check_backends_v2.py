"""
N47Lab — Check backends e stato coda (API3, instance auto)
"""
import sys; sys.stdout.reconfigure(encoding='utf-8')
from qiskit_ibm_runtime import QiskitRuntimeService

API3 = 'MiPxZZAuroZIHuc_YEvPPrdoG9r7DalscGWqhL5NMcj0'

S = QiskitRuntimeService(channel='ibm_cloud', token=API3, instance='auto')
print("=== BACKENDS DISPONIBILI ===")
for b in S.backends():
    try:
        st = b.status()
        n_pending = getattr(st, 'pending_jobs', '?')
        print(f"  {b.name:<20} queue={n_pending:<5} operational={getattr(st, 'operational', '?')}")
    except Exception as e:
        print(f"  {b.name:<20} ERRORE: {e}")
