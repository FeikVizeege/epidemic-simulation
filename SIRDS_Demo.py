import random
import networkx as nx
from collections import Counter

# Khởi tạo đồ thị tiếp xúc vô hướng
# Đối số n là tổng số nodes, tượng trưng cho một đối tượng, giả sử ta sẽ thống nhất là một cá thể
# Đối số p là xác suất tạo ra cạnh, tượng trưng cho mức độ tiếp xúc xã hội
TOTAL_NODES = 200
P_EDGE_CONNECTED = 0.1
graph_g = nx.erdos_renyi_graph(n=TOTAL_NODES, p=P_EDGE_CONNECTED)
"""
Mô Hình SIRDS: SUSCEPTIBLE - INFECTED - RECOVERED - DECEASED - SUSCEPTIBLE

Sự chuyển giao trạng thái hợp lệ:
    S -> I
    I -> R
    I -> D
    R -> S
"""

# Trạng thái của mỗi đỉnh
SUSCEPTIBLE = "S"
INFECTED    = "I"
RECOVERED   = "R"
DECEASED    = "D"

# Tham số mô hình
P_INFECT    = 0.25   # Xác suất lây nhiễm
P_RECOVER   = 0.1    # Xác suất hồi phục
P_REINFECT  = 0.05   # Xác suất tái bệnh
P_DECEASED  = 0.02   # Xác suất tử vong
T_STEP = 30          # Số bước thời gian

# Khởi tạo trạng thái
state = {v: SUSCEPTIBLE for v in graph_g.nodes()}

# Giả sử mô phỏng: Patient zero (người nhiễm đầu tiên) chỉ có một người
# Tại t = 0, Patient zero đã tiếp xúc và có thể đã lây nhiễm cho người khác
initial_infected = random.choice(list(graph_g.nodes()))
state[initial_infected] = INFECTED

def simulate(graph_g, state, t_step):
    history = []

    for t in range(t_step):
        new_state = state.copy()

        for v in graph_g.nodes():
            # Trạng thái hấp thụ
            if state[v] == DECEASED:
                continue

            # S -> I, Lây nhiễm
            if state[v] == SUSCEPTIBLE:
                infected_neighbors = [u for u in graph_g.neighbors(v) if state[u] == INFECTED]

                if infected_neighbors:
                    prob_no_infect = 1.0
                    for _ in infected_neighbors:
                        prob_no_infect *= (1 - P_INFECT)
                    
                    prob_infect = 1 - prob_no_infect
                    if random.random() < prob_infect:
                        new_state[v] = INFECTED

            # I -> R hoặc D, Phục hồi hoặc tử vong
            elif state[v] == INFECTED:
                random_temp = random.random()

                # Diễn giải:
                # Trong trường hợp này, người đang bệnh có 3 khả năng:
                # 1. Vẫn đang INFECTED, 2. RECOVERED, 3. DECEASED
                # Chia ra 3 ngưỡng khác nhau, 
                # 0                    P_DECEASED                        P_RECOVER                                1
                # | ======= DECEASED ====== | ========= RECOVERED ==========  | ========== STAY INFECTED ======== |
                #
                # Từ đó ta phải P_DECEASED + P_RECOVER

                if random_temp < P_DECEASED:
                    new_state[v] = DECEASED
                elif random_temp < P_DECEASED + P_RECOVER:
                    new_state[v] = RECOVERED
                # Còn lại vẫn là I

            # R -> S, Tái nhiễm
            elif state[v] == RECOVERED:
                if random.random() < P_REINFECT:
                    new_state[v] = SUSCEPTIBLE
        
        state = new_state
        counts = Counter(state.values())
        history.append(counts)

        print(
            f"t = {t:5d} | "
            f"S = {counts.get(SUSCEPTIBLE, 0):5d}; "
            f"I = {counts.get(INFECTED, 0):5d}; "
            f"R = {counts.get(RECOVERED, 0):5d}; "
            f"D = {counts.get(DECEASED, 0):5d} "
        )

    return history

# Mô phỏng
history = simulate(graph_g, state, T_STEP)