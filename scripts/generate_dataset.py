import os
import random
import time
import requests

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
API_URL = "http://localhost:8000"

def create_sample_files():
    os.makedirs(DATA_DIR, exist_ok=True)
    print(f"[*] Creating sample dataset in: {DATA_DIR}")

    files = [
        ("report_q1.pdf.txt", "PDF Document Header\n" + "Quarterly Financial Analysis Data Row...\n" * 2000),
        ("report_q2.pdf.txt", "PDF Document Header\n" + "Q2 Revenue and Expenditure Summary...\n" * 2000),
        ("user_profile.json", "{\n  \"users\": [\n" + "    {\"id\": 1, \"name\": \"Alice\", \"role\": \"admin\"},\n" * 500 + "  ]\n}"),
        ("dataset_matrix.csv", "id,feature_1,feature_2,label\n" + "1,0.85,0.42,1\n2,0.12,0.99,0\n" * 2500),
        ("image_asset.bin.txt", "BINARY_HEADER_554219\n" + "01010101010101010101010101010101\n" * 3000),
        ("config_settings.yaml", "system:\n  cache_size: 100MB\n  preloader: active\n" + "  module: enabled\n" * 1000)
    ]

    filepaths = []
    for fname, content in files:
        fpath = os.path.abspath(os.path.join(DATA_DIR, fname))
        with open(fpath, "w", encoding="utf-8") as f:
            f.write(content)
        filepaths.append(fpath)
        print(f"    [+] Created: {fname} ({os.path.getsize(fpath) / 1024:.2f} KB)")

    return filepaths

def simulate_markov_sequence(filepaths):
    print("\n[*] Simulating Markov access pattern (Sequential flow A -> B -> C)...")
    # Define strong sequential pattern: report_q1 -> report_q2 -> user_profile -> dataset_matrix
    if len(filepaths) < 4:
        return

    sequence = [
        filepaths[0], filepaths[1], filepaths[2], filepaths[3],
        filepaths[0], filepaths[1], filepaths[2], filepaths[3],
        filepaths[0], filepaths[1], filepaths[2], filepaths[3],
        filepaths[0], filepaths[1], filepaths[2], filepaths[3],
        filepaths[0], filepaths[1], filepaths[2], filepaths[3]
    ]

    for fpath in sequence:
        try:
            res = requests.get(f"{API_URL}/file", params={"path": fpath})
            status = res.headers.get("X-SmartCache-Status", "N/A")
            lat = res.headers.get("X-SmartCache-Latency-MS", "0")
            print(f"    -> Accessing {os.path.basename(fpath)} | Status: {status} | Latency: {lat} ms")
            time.sleep(0.2)
        except Exception as e:
            print(f"    [!] Error requesting API: {e}. Is server running at {API_URL}?")
            break

if __name__ == "__main__":
    paths = create_sample_files()
    simulate_markov_sequence(paths)
    print("\n[+] Dataset generation & Markov sequence simulation complete.")
