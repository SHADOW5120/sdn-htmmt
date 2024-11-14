import requests
import networkx as nx
import time

# Lấy thông tin topology từ Floodlight và xây dựng đồ thị NetworkX, bao gồm cả host và switch
def get_topology():
    url_links = "http://127.0.0.1:8080/wm/topology/links/json"
    url_hosts = "http://127.0.0.1:8080/wm/device/"
    
    # Tạo đồ thị NetworkX
    graph = nx.Graph()

    # Thêm các liên kết giữa các switch
    response_links = requests.get(url_links)
    links = response_links.json()
    for link in links:
        src = link['src-switch']
        dst = link['dst-switch']
        src_port = link['src-port']
        dst_port = link['dst-port']
        weight = 1  # Trọng số mặc định cho liên kết giữa switch

        # Thêm cạnh giữa các switch trong đồ thị
        graph.add_edge(src, dst, src_port=src_port, dst_port=dst_port, weight=weight)

    # Thêm host vào đồ thị và kết nối với switch tương ứng
    response_hosts = requests.get(url_hosts)
    hosts = response_hosts.json()
    for host in hosts:
        if len(host['attachmentPoint']) > 0:
            host_id = host['mac'][0]
            attached_switch = host['attachmentPoint'][0]['switchDPID']
            attached_port = host['attachmentPoint'][0]['port']
            
            # Thêm host vào đồ thị và kết nối với switch qua cổng tương ứng
            graph.add_edge(host_id, attached_switch, src_port=None, dst_port=attached_port, weight=1)
    
    return graph

# Lấy thống kê cổng của một switch
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

    # Tính toán tải cho mỗi đường đi để chọn đường ít tải nhất
    for path in paths:
        path_load = 0

        for i in range(len(path) - 1):
            src = path[i]
            dst = path[i + 1]
            src_port = graph[src][dst]['src_port']
            
            # Nếu src_port không tồn tại (host kết nối), bỏ qua bước tính toán tải
            if src_port is None:
                continue
            
            stats = get_link_statistics(src, src_port)
            
            if stats and len(stats) > 0:
                path_load += stats[0]['bits-per-second-tx'] + stats[0]['bits-per-second-rx']
        
        if path_load < min_load:
            min_load = path_load
            min_load_path = path

    # Đặt flow rule trên mỗi switch của đường đi có tải thấp nhất
    if min_load_path:
        for i in range(len(min_load_path) - 1):
            src_switch = min_load_path[i]
            dst_switch = min_load_path[i + 1]
            in_port = graph[dst_switch][src_switch]['dst_port']
            out_port = graph[src_switch][dst_switch]['src_port']
            push_flow_rule(src_switch, in_port, out_port, src_ip, dst_ip)

# Hàm chính để khởi động load balancer
def main():
    graph = get_topology()
    src_host, dst_host = "10:00:00:00:00:01", "10:00:00:00:00:04"  # MAC của h1 và h4
    src_ip, dst_ip = "10.0.0.1", "10.0.0.4"

    while True:
        apply_load_balancing(graph, src_host, dst_host, src_ip, dst_ip)
        time.sleep(60)  # Cập nhật mỗi 60 giây

if __name__ == "__main__":
    main()
