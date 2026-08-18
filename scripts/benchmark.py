import time
import requests
import json

API_URL = "http://localhost:8000"

def run_performance_benchmark():
    print("=" * 60)
    print(" SmartCache Performance Evaluation Benchmark")
    print("=" * 60)
    
    try:
        res = requests.post(f"{API_URL}/benchmark/run", params={"iterations": 100})
        if res.status_code == 200:
            data = res.json()
            print("\n[+] Benchmark Results:")
            print(f"    - Cold Disk Read Latency : {data['without_smartcache']['average_disk_read_time_ms']} ms")
            print(f"    - Warm RAM Read Latency  : {data['with_smartcache']['average_ram_read_time_ms']} ms")
            print(f"    - Latency Reduction      : {data['results']['latency_reduction_ms']} ms")
            print(f"    - Speedup Percentage     : {data['results']['speedup_percentage']}%")
            print(f"    - Cache Hit Ratio        : {data['results']['hit_ratio_percentage']}%")
            print(f"    - Memory Savings         : {data['results']['memory_savings_mb']} MB")
            print("=" * 60)
        else:
            print(f"[!] Benchmark request failed: {res.status_code} - {res.text}")
    except Exception as e:
        print(f"[!] Error connecting to SmartCache API at {API_URL}: {e}")

if __name__ == "__main__":
    run_performance_benchmark()
