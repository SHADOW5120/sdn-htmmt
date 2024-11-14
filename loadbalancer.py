import requests
import networkx as nx
import time

# Lấy thông tin topology từ Floodlight và xây dựng đồ thị NetworkX
def get_topology():
    url = "http://127.0.0.1:8080/wm/topology/links/json"
    response = requests.get(url)
    data = response.json()
    graph = nx.Graph()

    for link in data:
        src = link['src-switch']
        dst = link['dst-switch']
        port = link['src-port']
        weight = 1  # Mặc định, bạn có thể điều chỉnh trọng số dựa trên băng thông
        graph.add_edge(src, dst, port=port, weight=weight)
    
    return graph

# Lấy thống kê của các cổng switch
def get_link_statistics(switch_id, port):
    url = f"http://127.0.0.1:8080/wm/statistics/port/{switch_id}/{port}/json"
    response = requests.get(url)
    data = response.json()
    return data

# Tìm các đường ngắn nhất giữa hai host trong đồ thị NetworkX
def find_shortest_paths(graph, src, dst):
    paths = list(nx.all_shortest_paths(graph, source=src, target=dst, weight='weight'))
    return paths

# Đẩy flow rule lên switch qua REST API
def push_flow_rule(switch_id, in_port, out_port, src_ip, dst_ip):
    url = "http://127.0.0.1:8080/wm/staticflowentrypusher/json"
    flow = {
        "switch": switch_id,
        "name": f"flow-{src_ip}-{dst_ip}",
        "priority": 32768,
        "in_port": in_port,
        "eth_type": "0x0800",
        "ipv4_src": src_ip,
        "ipv4_dst": dst_ip,
        "actions": f"output={out_port}"
    }
    response = requests.post(url, json=flow)
    return response.status_code

# Chọn đường có tải thấp nhất và cài đặt flow rule cho các switch trên đường đi
def apply_load_balancing(graph, src_host, dst_host, src_ip, dst_ip):
    paths = find_shortest_paths(graph, src_host, dst_host)
    min_load_path = None
    min_load = float('inf')

    for path in paths:
        path_load = 0

        for i in range(len(path) - 1):
            src = path[i]
            dst = path[i+1]
            port = graph[src][dst]['port']
            stats = get_link_statistics(src, port)
            
            if stats and len(stats) > 0:
                path_load += stats[0]['bits-per-second-tx'] + stats[0]['bits-per-second-rx']
        
        if path_load < min_load:
            min_load = path_load
            min_load_path = path

    # Đặt flow rule trên mỗi switch của đường đi có tải thấp nhất
    if min_load_path:
        for i in range(len(min_load_path) - 1):
            src_switch = min_load_path[i]
            dst_switch = min_load_path[i+1]
            in_port = graph[min_load_path[i+1]][min_load_path[i]]['port']
            out_port = graph[min_load_path[i]][min_load_path[i+1]]['port']
            push_flow_rule(src_switch, in_port, out_port, src_ip, dst_ip)

# Hàm chính để khởi động load balancer
def main():
    graph = get_topology()
    src_host, dst_host = "h1", "h4"
    src_ip, dst_ip = "10.0.0.1", "10.0.0.4"

    while True:
        apply_load_balancing(graph, src_host, dst_host, src_ip, dst_ip)
        time.sleep(60)  # Cập nhật mỗi 60 giây

if __name__ == "__main__":
    main()
