import SimClasses
import SimFunctions
import SimRNG
import os
import time
import sys

# ==========================================
# 設定區域
# ==========================================
VIS_DELAY = 0.2       # 動畫更新速度 (秒)
WARMUP_DURATION = 10000.0  # 暖身時間 (秒)，此期間不顯示動畫，全速運算
# ==========================================

# 啟用 Windows 的 ANSI 支援
os.system('')

RNGseed = SimRNG.InitializeRNSeed()

# 初始化必要的變數
Calendar = SimClasses.EventCalendar()
SimClasses.Clock = 0
traffic_state = 0

# 燈號週期設定
traffic_cycle = { 0 : 93., 1 : 20., 2 : 12., 3 : 14., 4 : 12. }

# 參數設定
car_arrival_parameters = {
    1: {'s': 3.0457*2, 'r': 43.2277, 'l': 40.3497},
    2: {'s': 3.0817*2, 'r': 35.6083, 'l': 259.7403},
    3: {'s': 129.8701, 'r': 55.0459, 'l': 181.8182},
    4: {'s': 363.6364, 'r': 53.4283, 'l': 72.6392}
}

t_car_warmup_parameters = {
    1 : {'s':(3.5, 0.99**2), 'r':(3.5, 0.99**2), 'l':(3.5, 0.99**2)},
    2 : {'s':(2.81, 0.91**2), 'r':(2.81, 0.91**2), 'l':(2.81, 0.91**2)},
    3 : {'s':(5.56, 2.12**2), 'r':(5.56, 2.12**2), 'l':(5.56, 2.12**2)},
    4 : {'s':(7, 1.13**2), 'r':(7, 1.13**2), 'l':(7, 1.13**2)}
}

t_passthrough_parameters = {
    1 : {'s':(2.34, 1.02**2), 'r':(2.34, 1.02**2), 'l':(2.34, 1.02**2)},
    2 : {'s':(2.24, 0.87**2), 'r':(2.24, 0.87**2), 'l':(2.24, 0.87**2)},
    3 : {'s':(3.4, 1.65**2), 'r':(3.4, 1.65**2), 'l':(3.4, 1.65**2)},
    4 : {'s':(3.58, 1.74**2), 'r':(3.58, 1.74**2), 'l':(3.58, 1.74**2)}
}

pedestrian_arrival_parameters = { 1: 22.1341, 2: 21.3529, 3: 14.1797, 4: 17.2857 }
pedestrian_passthrough_parameters = {
    1: (17.00, 7.82**2), 2: (17.00, 7.82**2), 3: (14.97, 10.77**2), 4: (14.97, 10.77**2)
}

# 隊列初始化
car_queue = {
    1: {'s': SimClasses.FIFOQueue(), 'r': SimClasses.FIFOQueue(), 'l': SimClasses.FIFOQueue()},
    2: {'s': SimClasses.FIFOQueue(), 'r': SimClasses.FIFOQueue(), 'l': SimClasses.FIFOQueue()},
    3: {'s': SimClasses.FIFOQueue(), 'r': SimClasses.FIFOQueue(), 'l': SimClasses.FIFOQueue()},
    4: {'s': SimClasses.FIFOQueue(), 'r': SimClasses.FIFOQueue(), 'l': SimClasses.FIFOQueue()}
}
pedestrian_queue= {
    1: SimClasses.FIFOQueue(), 2: SimClasses.FIFOQueue(), 3: SimClasses.FIFOQueue(), 4: SimClasses.FIFOQueue()
}

class car_entity(SimClasses.Entity):
    def __init__(self, road_index: int, direction: str):
        super().__init__()
        self.road_index = road_index
        self.direction = direction

class pedestrian_entity(SimClasses.Entity):
    def __init__(self, road_index: int):
        super().__init__()
        self.road_index = road_index

# 輔助計算函數
def get_car_inter_arrival_time(road_index: int, direction: str) -> float:
    return SimRNG.Expon(car_arrival_parameters[road_index][direction], 1)
def get_car_passthrough_time(road_index: int, direction: str, start_car: bool = False) -> float:
    if start_car: return max(SimRNG.Normal(t_car_warmup_parameters[road_index][direction][0], t_car_warmup_parameters[road_index][direction][1], 1), 0.)
    else: return max(SimRNG.Normal(t_passthrough_parameters[road_index][direction][0], t_passthrough_parameters[road_index][direction][1], 1), 0.)
def get_pedestrian_inter_arrival_time(road_index: int) -> float:
    return SimRNG.Expon(pedestrian_arrival_parameters[road_index], 1)
def get_pedestrian_passthrough_time(road_index: int) -> float:
    return SimRNG.Lognormal(pedestrian_passthrough_parameters[road_index][0], pedestrian_passthrough_parameters[road_index][1], 1)

# 事件處理函數
def car_passthrough(road_index: int, direction: str):
    if car_queue[road_index][direction].NumQueue() <= 0: return
    car_queue[road_index][direction].Remove()
    match traffic_state:
        case 0:
            if (road_index == 1 or road_index == 2) and direction == 's' and car_queue[road_index]['s'].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_{road_index}_s', get_car_passthrough_time(road_index, 's', False))
            if road_index == 1 and direction == 'r' and car_queue[road_index]['r'].NumQueue() > 0 and pedestrian_queue[4].NumQueue() <= 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_{road_index}_r', get_car_passthrough_time(road_index, 'r', False))
            if road_index == 2 and direction == 'r' and car_queue[road_index]['r'].NumQueue() > 0 and pedestrian_queue[3].NumQueue() <= 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_{road_index}_r', get_car_passthrough_time(road_index, 'r', False))
        case 1:
            if (road_index == 1 or road_index == 2) and direction == 'l' and car_queue[road_index]['l'].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_{road_index}_l', get_car_passthrough_time(road_index, 'l', False))
        case 2: pass
        case 3:
            if (road_index == 3 or road_index == 4) and direction == 's' and car_queue[road_index]['s'].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_{road_index}_s', get_car_passthrough_time(road_index, 's', False))
            if road_index == 3 and direction == 'r' and car_queue[road_index]['r'].NumQueue() > 0 and pedestrian_queue[1].NumQueue() <= 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_{road_index}_r', get_car_passthrough_time(road_index, 'r', False))
            if road_index == 4 and direction == 'r' and car_queue[road_index]['r'].NumQueue() > 0 and pedestrian_queue[2].NumQueue() <= 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_{road_index}_r', get_car_passthrough_time(road_index, 'r', False))
            if road_index == 3 and direction == 'l' and car_queue[road_index]['l'].NumQueue() > 0 and car_queue[4]['s'].NumQueue() <= 0 and pedestrian_queue[2].NumQueue() <= 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_{road_index}_l', get_car_passthrough_time(road_index, 'l', False))
            if road_index == 4 and direction == 'l' and car_queue[road_index]['l'].NumQueue() > 0 and car_queue[3]['s'].NumQueue() <= 0 and pedestrian_queue[1].NumQueue() <= 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_{road_index}_l', get_car_passthrough_time(road_index, 'l', False))
        case 4:
            if (road_index == 3 or road_index == 4) and (direction == 's' or direction == 'r') and car_queue[road_index][direction].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_{road_index}_{direction}', get_car_passthrough_time(road_index, direction, False))
            if road_index == 3 and direction == 'l' and car_queue[road_index]['l'].NumQueue() > 0 and car_queue[4]['s'].NumQueue() <= 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_{road_index}_l', get_car_passthrough_time(road_index, 'l', False))
            if road_index == 4 and direction == 'l' and car_queue[road_index]['l'].NumQueue() > 0 and car_queue[3]['s'].NumQueue() <= 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_{road_index}_l', get_car_passthrough_time(road_index, 'l', False))
        case _: pass

def car_arrival(road_index: int, direction: str):
    car = car_entity(road_index, direction)
    car_queue[road_index][direction].Add(car)
    match traffic_state:
        case 0:
            if (road_index == 1 or road_index == 2) and direction == 's' and car_queue[road_index]['s'].NumQueue() <= 1: car_queue[road_index]['s'].Remove()
            if road_index == 1 and direction == 'r' and car_queue[road_index]['r'].NumQueue() <= 1 and pedestrian_queue[4].NumQueue() <= 0: car_queue[road_index]['r'].Remove()
            if road_index == 2 and direction == 'r' and car_queue[road_index]['r'].NumQueue() <= 1 and pedestrian_queue[3].NumQueue() <= 0: car_queue[road_index]['r'].Remove()
        case 1:
            if (road_index == 1 or road_index == 2) and direction == 'l' and car_queue[road_index]['l'].NumQueue() <= 1: car_queue[road_index]['l'].Remove()
        case 2: pass
        case 3:
            if (road_index == 3 or road_index == 4) and direction == 's' and car_queue[road_index]['s'].NumQueue() <= 1: car_queue[road_index]['s'].Remove()
            if road_index == 3 and direction == 'r' and car_queue[road_index]['r'].NumQueue() <= 1 and pedestrian_queue[1].NumQueue() <= 0: car_queue[road_index]['r'].Remove()
            if road_index == 4 and direction == 'r' and car_queue[road_index]['r'].NumQueue() <= 1 and pedestrian_queue[2].NumQueue() <= 0: car_queue[road_index]['r'].Remove()
            if road_index == 3 and direction == 'l' and car_queue[road_index]['l'].NumQueue() <= 1 and car_queue[4]['s'].NumQueue() <= 0 and pedestrian_queue[2].NumQueue() <= 0: car_queue[road_index]['l'].Remove()
            if road_index == 4 and direction == 'l' and car_queue[road_index]['l'].NumQueue() <= 1 and car_queue[3]['s'].NumQueue() <= 0 and pedestrian_queue[1].NumQueue() <= 0: car_queue[road_index]['l'].Remove()
        case 4:
            if (road_index == 3 or road_index == 4) and direction == 's' and car_queue[road_index]['s'].NumQueue() <= 1: car_queue[road_index]['s'].Remove()
            if road_index == 3 and direction == 'r' and car_queue[road_index]['r'].NumQueue() <= 1: car_queue[road_index]['r'].Remove()
            if road_index == 4 and direction == 'r' and car_queue[road_index]['r'].NumQueue() <= 1: car_queue[road_index]['r'].Remove()
            if road_index == 3 and direction == 'l' and car_queue[road_index]['l'].NumQueue() <= 1 and car_queue[4]['s'].NumQueue() <= 0: car_queue[road_index]['l'].Remove()
            if road_index == 4 and direction == 'l' and car_queue[road_index]['l'].NumQueue() <= 1 and car_queue[3]['s'].NumQueue() <= 0: car_queue[road_index]['l'].Remove()
        case _: pass
    SimFunctions.Schedule(Calendar, f'car_arrival_{road_index}_{direction}', get_car_inter_arrival_time(road_index, direction))

def pedestrian_passthrough(road_index: int):
    n = pedestrian_queue[road_index].NumQueue()
    for i in range(n): pedestrian_queue[road_index].Remove()
    match traffic_state:
        case 0:
            if road_index == 4:
                if car_queue[1]['r'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_1_r', get_car_passthrough_time(1, 'r', True))
            if road_index == 3:
                if car_queue[2]['r'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_2_r', get_car_passthrough_time(2, 'r', True))
        case 3 | 4:
            if road_index == 2:
                if car_queue[4]['r'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_4_r', get_car_passthrough_time(4, 'r', True))
                if car_queue[4]['s'].NumQueue() <= 0 and car_queue[3]['l'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_3_l', get_car_passthrough_time(3, 'l', True))
            if road_index == 1:
                if car_queue[3]['r'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_3_r', get_car_passthrough_time(3, 'r', True))
                if car_queue[3]['s'].NumQueue() <= 0 and car_queue[4]['l'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_4_l', get_car_passthrough_time(4, 'l', True))    
        case _: pass

def pedestrian_arrival(road_index: int):
    pedestrian = pedestrian_entity(road_index)
    pedestrian_queue[road_index].Add(pedestrian)
    match traffic_state:
        case 0:
            if road_index == 3 or road_index == 4: SimFunctions.Schedule(Calendar, f'pedestrian_passthrough_{road_index}', get_pedestrian_passthrough_time(road_index))
        case 2 | 3:
            if road_index == 1 or road_index == 2: SimFunctions.Schedule(Calendar, f'pedestrian_passthrough_{road_index}', get_pedestrian_passthrough_time(road_index))
        case _: pass
    SimFunctions.Schedule(Calendar, f'pedestrian_arrival_{road_index}', get_pedestrian_inter_arrival_time(road_index))

def traffic_state_transform():
    global traffic_state
    traffic_state = (traffic_state + 1) % 5
    match traffic_state:
        case 0:
            if pedestrian_queue[3].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'pedestrian_passthrough_3', get_pedestrian_passthrough_time(3))
            elif car_queue[2]['r'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_2_r', get_car_passthrough_time(2, 'r', True))
            if pedestrian_queue[4].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'pedestrian_passthrough_4', get_pedestrian_passthrough_time(4))
            elif car_queue[1]['r'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_1_r', get_car_passthrough_time(1, 'r', True))
            if car_queue[1]['s'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_1_s', get_car_passthrough_time(1, 's', True))
            if car_queue[2]['s'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_2_s', get_car_passthrough_time(2, 's', True))
        case 1:
            if car_queue[1]['l'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_1_l', get_car_passthrough_time(1, 'l', True))
            if car_queue[2]['l'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_2_l', get_car_passthrough_time(2, 'l', True))
        case 2:
            if pedestrian_queue[1].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'pedestrian_passthrough_1', get_pedestrian_passthrough_time(1))
            if pedestrian_queue[2].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'pedestrian_passthrough_2', get_pedestrian_passthrough_time(2))
        case 3:
            if pedestrian_queue[1].NumQueue() <= 0 and car_queue[3]['r'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_3_r', get_car_passthrough_time(3, 'r', True))
            if pedestrian_queue[2].NumQueue() <= 0 and car_queue[4]['r'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_4_r', get_car_passthrough_time(4, 'r', True))
            if pedestrian_queue[1].NumQueue() <= 0 and car_queue[3]['s'].NumQueue() <= 0 and car_queue[4]['l'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_4_l', get_car_passthrough_time(4, 'l', True))
            if pedestrian_queue[2].NumQueue() <= 0 and car_queue[4]['s'].NumQueue() <= 0 and car_queue[3]['l'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_3_l', get_car_passthrough_time(3, 'l', True))
            if car_queue[3]['s'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_3_s', get_car_passthrough_time(3, 's', True))
            if car_queue[4]['s'].NumQueue() > 0: SimFunctions.Schedule(Calendar, f'car_passthrough_4_s', get_car_passthrough_time(4, 's', True))
        case 4: pass
        case _: pass
    SimFunctions.Schedule(Calendar, 'traffic_state_transform', traffic_cycle[traffic_state])

# ==========================================
# 視覺化輸出函數
# ==========================================
def print_intersection_state():
    state_desc = {
        0: "[LIGHT: GREEN] Guangfu Rd. (East-West)",
        1: "[LIGHT: LEFT TURN] Guangfu Rd.",
        2: "[LIGHT: RED] All Stop / [PED: GREEN]",
        3: "[LIGHT: GREEN] Jiangong Rd. (North-South)",
        4: "[LIGHT: GREEN] Jiangong Rd. / [PED: RED]"
    }

    q3s, q3l, q3r = car_queue[3]['s'].NumQueue(), car_queue[3]['l'].NumQueue(), car_queue[3]['r'].NumQueue()
    q4s, q4l, q4r = car_queue[4]['s'].NumQueue(), car_queue[4]['l'].NumQueue(), car_queue[4]['r'].NumQueue()
    q1s, q1l, q1r = car_queue[1]['s'].NumQueue(), car_queue[1]['l'].NumQueue(), car_queue[1]['r'].NumQueue()
    q2s, q2l, q2r = car_queue[2]['s'].NumQueue(), car_queue[2]['l'].NumQueue(), car_queue[2]['r'].NumQueue()
    qp1, qp2 = pedestrian_queue[1].NumQueue(), pedestrian_queue[2].NumQueue()
    qp3, qp4 = pedestrian_queue[3].NumQueue(), pedestrian_queue[4].NumQueue()

    buffer = []
    buffer.append(f"\033[H")
    buffer.append(f"Time: {SimClasses.Clock:10.1f} sec\033[K\n")
    buffer.append(f"Status: {state_desc.get(traffic_state, 'Unknown')}\033[K\n")
    buffer.append("="*60 + "\033[K\n")
    buffer.append(f"                [3] Jiangong (N)\033[K\n")
    buffer.append(f"          S:{q3s:<3} L:{q3l:<3} R:{q3r:<3} | Ped:{qp3}\033[K\n")
    buffer.append("               │   │   │\033[K\n")
    buffer.append("               │ ↓ │ ↑ │\033[K\n")
    buffer.append("───────────────┘   └───└───────────────\033[K\n")
    buffer.append(f"[1] Guangfu (W) ->      <- [2] Guangfu (E)\033[K\n")
    buffer.append(f"S:{q1s:<3} R:{q1r:<3}                 S:{q2s:<3} R:{q2r:<3}\033[K\n")
    buffer.append(f"L:{q1l:<3} Ped:{qp1:<2}                L:{q2l:<3} Ped:{qp2:<2}\033[K\n")
    buffer.append("───────────────┐   ┌───┌───────────────\033[K\n")
    buffer.append("               │ ↑ │ ↓ │\033[K\n")
    buffer.append("               │   │   │\033[K\n")
    buffer.append(f"          S:{q4s:<3} L:{q4l:<3} R:{q4r:<3} | Ped:{qp4}\033[K\n")
    buffer.append(f"                [4] Jiangong (S)\033[K\n")
    buffer.append("="*60 + "\033[K\n")
    buffer.append("INFINITE SIMULATION MODE (Press Ctrl+C to Exit)\033[K\n")
    
    sys.stdout.write("".join(buffer))
    sys.stdout.flush()

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    sys.stdout.write("\033[?25l") # Hide Cursor

    print(f"Warming up... processing {WARMUP_DURATION} seconds of simulation (please wait)...")
    SimFunctions.SimFunctionsInit(Calendar)

    for i in range(1,5):
        SimFunctions.Schedule(Calendar, f'pedestrian_arrival_{i}', get_pedestrian_inter_arrival_time(i))
        for j in ['s', 'r', 'l']:
            SimFunctions.Schedule(Calendar, f'car_arrival_{i}_{j}', get_car_inter_arrival_time(i, j))
    
    SimFunctions.Schedule(Calendar, 'traffic_state_transform', traffic_cycle[0])

    # 用來控制暖身期間進度顯示的頻率
    next_print_time = 0 

    try:
        while True:
            if Calendar.N() <= 0: break
            NextEvent = Calendar.Remove()
            SimClasses.Clock = NextEvent.EventTime
            
            # 判斷是否在暖身期
            if SimClasses.Clock < WARMUP_DURATION:
                # 暖身期：不畫圖，不 sleep，只顯示簡單進度
                if SimClasses.Clock >= next_print_time:
                    progress = (SimClasses.Clock / WARMUP_DURATION) * 100
                    sys.stdout.write(f"\rProgress: {progress:.1f}% ({SimClasses.Clock:.0f}/{WARMUP_DURATION:.0f}s)")
                    sys.stdout.flush()
                    next_print_time += 500 # 每 500 模擬秒更新一次進度文字
            else:
                # 視覺化模式：開始畫圖與延遲
                print_intersection_state()
                time.sleep(VIS_DELAY)

            match NextEvent.EventType.split('_'):
                case ['traffic', 'state', 'transform']: traffic_state_transform()
                case ['car', 'passthrough', road, direction]: car_passthrough(int(road), direction)
                case ['car', 'arrival', road, direction]: car_arrival(int(road), direction)
                case ['pedestrian', 'passthrough', road]: pedestrian_passthrough(int(road))
                case ['pedestrian', 'arrival', road]: pedestrian_arrival(int(road))
                case _: pass

    except KeyboardInterrupt:
        sys.stdout.write("\033[?25h") # Show Cursor
        print("\n\nSimulation stopped by user.")
        sys.exit(0)