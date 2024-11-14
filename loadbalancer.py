import requests
import time

FLOODLIGHT_URL = "http://127.0.0.1:8080"

def get_switch_stats():
    response = requests.get(f"{FLOODLIGHT_URL}/wm/statistics/bandwidth/all/json")
    return response.json()

def find_best_path(paths):
    best_path = None
    min_load = float('inf')

    for path in paths:
        load = sum(link['tx'] for link in path)  # Sum TX for simplicity
        if load < min_load:
            min_load = load
            best_path = path
    return best_path

def push_flow_rules(best_path):
    for link in best_path:
        # Construct flow rule for each link
        flow = {
            "switch": link['switch'],
            "name": f"flow_{link['src']}_{link['dst']}",
            "priority": "32768",
            "in_port": link['in_port'],
            "eth_type": "0x0800",
            "ipv4_src": "10.0.0.1",
            "ipv4_dst": "10.0.0.4",
            "actions": f"output={link['out_port']}"
        }
        requests.post(f"{FLOODLIGHT_URL}/wm/staticflowpusher/json", json=flow)

while True:
    paths = get_paths()  # Obtain paths via Dijkstra algorithm
    best_path = find_best_path(paths)
    push_flow_rules(best_path)
    time.sleep(60)  # Re-run every minute
