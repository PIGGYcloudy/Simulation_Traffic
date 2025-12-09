#############################
#          路口示意          #
#############################
#          │ 清  |
#          │ 大  |
#          │  3  |
#          │  ↓  |
# ─────────┘     └─────────
# 交流道 1 →      ← 2 市區 
# ─────────┐     ┌─────────
#          │  ↑  |
#          │  4  |
#          │ 清  |
#          │ 夜  |
import SimClasses
import SimFunctions
import SimRNG
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
import os
RNGseed = SimRNG.InitializeRNSeed()

# Second
RunLength = 10800.
Warmup = 3600.

n_reps = 30

WaitTimeCar = {
    1: {'s': SimClasses.DTStat(), 'r': SimClasses.DTStat(), 'l': SimClasses.DTStat()},
    2: {'s': SimClasses.DTStat(), 'r': SimClasses.DTStat(), 'l': SimClasses.DTStat()},
    3: {'s': SimClasses.DTStat(), 'r': SimClasses.DTStat(), 'l': SimClasses.DTStat()},
    4: {'s': SimClasses.DTStat(), 'r': SimClasses.DTStat(), 'l': SimClasses.DTStat()}
}

WaitTimeCarAvg = {
    1: {'s': [], 'r': [], 'l': []},
    2: {'s': [], 'r': [], 'l': []},
    3: {'s': [], 'r': [], 'l': []},
    4: {'s': [], 'r': [], 'l': []}
}

QueueLengthCarAvg = {
    1: {'s': [], 'r': [], 'l': []},
    2: {'s': [], 'r': [], 'l': []},
    3: {'s': [], 'r': [], 'l': []},
    4: {'s': [], 'r': [], 'l': []}
}

WaitTimePedestrian = {
    1: SimClasses.DTStat(),
    2: SimClasses.DTStat(),
    3: SimClasses.DTStat(),
    4: SimClasses.DTStat()
}

WaitTimePedestrianAvg = {
    1: [],
    2: [],
    3: [],
    4: []
}

QueueLengthPedestrianAvg = {
    1: [],
    2: [],
    3: [],
    4: []
    
}

Calendar = SimClasses.EventCalendar()
SimClasses.Clock = 0

traffic_state = 0

# time unit : second
# traffic light cycle : j = (j + 1) % 5
## 0:光復路綠燈             CONSTANT
## 1:光復路左轉燈           CONSTANT
## 2:建功路紅燈行人綠燈     CONSTANT
## 3:建功路綠燈             CONSTANT
## 4:建功路綠燈行人紅燈     CONSTANT
traffic_cycle = {
    0 : 93.,
    1 : 20.,
    2 : 12.,
    3 : 14.,
    4 : 12.
}

# s: 直走 r: 右轉 l: 左轉 (beta : second / # car)
car_arrival_parameters = {
    1: {'s': 3.0457*2, 'r': 43.2277, 'l': 40.3497},
    2: {'s': 3.0817*2, 'r': 35.6083, 'l': 259.7403},
    3: {'s': 129.8701, 'r': 55.0459, 'l': 181.8182},
    4: {'s': 363.6364, 'r': 53.4283, 'l': 72.6392}
}

# s: 直走 r: 右轉 l: 左轉 (mu, var)
t_car_warmup_parameters = {
    1 : {'s':(3.5, 0.99**2), 'r':(3.5, 0.99**2), 'l':(3.5, 0.99**2)},
    2 : {'s':(2.81, 0.91**2), 'r':(2.81, 0.91**2), 'l':(2.81, 0.91**2)},
    3 : {'s':(5.56, 2.12**2), 'r':(5.56, 2.12**2), 'l':(5.56, 2.12**2)},
    4 : {'s':(7, 1.13**2), 'r':(7, 1.13**2), 'l':(7, 1.13**2)}
}

# 飽和車流後續車輛通過平均花費(mu, var)
t_passthrough_parameters = {
    1 : {'s':(2.34, 1.02**2), 'r':(2.34, 1.02**2), 'l':(2.34, 1.02**2)},
    2 : {'s':(2.24, 0.87**2), 'r':(2.24, 0.87**2), 'l':(2.24, 0.87**2)},
    3 : {'s':(3.4, 1.65**2), 'r':(3.4, 1.65**2), 'l':(3.4, 1.65**2)},
    4 : {'s':(3.58, 1.74**2), 'r':(3.58, 1.74**2), 'l':(3.58, 1.74**2)}
}

# exponential (beta : second / # person)
pedestrian_arrival_parameters = {
    1: 22.1341,
    2: 21.3529,
    3: 14.1797,
    4: 17.2857
}

# LogNormal(mu, var)
pedestrian_passthrough_parameters = {
    1: (17.00, 7.82**2),
    2: (17.00, 7.82**2),
    3: (14.97, 10.77**2),
    4: (14.97, 10.77**2)
}

car_queue = {
    1: {'s': SimClasses.FIFOQueue(), 'r': SimClasses.FIFOQueue(), 'l': SimClasses.FIFOQueue()},
    2: {'s': SimClasses.FIFOQueue(), 'r': SimClasses.FIFOQueue(), 'l': SimClasses.FIFOQueue()},
    3: {'s': SimClasses.FIFOQueue(), 'r': SimClasses.FIFOQueue(), 'l': SimClasses.FIFOQueue()},
    4: {'s': SimClasses.FIFOQueue(), 'r': SimClasses.FIFOQueue(), 'l': SimClasses.FIFOQueue()}
}

pedestrian_queue= {
    1: SimClasses.FIFOQueue(),
    2: SimClasses.FIFOQueue(),
    3: SimClasses.FIFOQueue(),
    4: SimClasses.FIFOQueue()
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

def get_car_inter_arrival_time(road_index: int, direction: str) -> float:
    """
    get_car_inter_arrival_time 的 Docstring
    
    :param road_index: [1, 2, 3, 4]
    :type road_index: int
    :param direction: ['s', 'r', 'l']
    :type direction: str
    :return: 下輛車要經過多久到達
    :rtype: float
    """
    return SimRNG.Expon(car_arrival_parameters[road_index][direction], 1)

def get_car_passthrough_time(road_index: int, direction: str, start_car: bool = False) -> float:
    if start_car:
        return max(SimRNG.Normal(t_car_warmup_parameters[road_index][direction][0], t_car_warmup_parameters[road_index][direction][1], 1), 0.)
    else:
        return max(SimRNG.Normal(t_passthrough_parameters[road_index][direction][0], t_passthrough_parameters[road_index][direction][1], 1), 0.)


def get_pedestrian_inter_arrival_time(road_index: int) -> float:
    """
    get_pedestrian_inter_arrival_time 的 Docstring
    
    :param road_index: [1, 2, 3, 4]
    :type road_index: int
    :return: 下個行人要經過多久到達
    :rtype: float
    """
    return SimRNG.Expon(pedestrian_arrival_parameters[road_index], 1)

def get_pedestrian_passthrough_time(road_index: int) -> float:
    return SimRNG.Lognormal(pedestrian_passthrough_parameters[road_index][0], pedestrian_passthrough_parameters[road_index][1], 1)

def car_passthrough(road_index: int, direction: str):
    if car_queue[road_index][direction].NumQueue() <= 0:
        return
    car = car_queue[road_index][direction].Remove()
    WaitTimeCar[road_index][direction].Record(SimClasses.Clock - car.CreateTime)
    
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
        case 2:
            pass
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
        case _:
            pass

def car_arrival(road_index: int, direction: str):
    car = car_entity(road_index, direction)
    car_queue[road_index][direction].Add(car)

    match traffic_state:
        case 0:
            if (road_index == 1 or road_index == 2) and direction == 's' and car_queue[road_index]['s'].NumQueue() <= 1:
                car = car_queue[road_index]['s'].Remove()
                WaitTimeCar[road_index]['s'].Record(SimClasses.Clock - car.CreateTime)
            if road_index == 1 and direction == 'r' and car_queue[road_index]['r'].NumQueue() <= 1 and pedestrian_queue[4].NumQueue() <= 0:
                car = car_queue[road_index]['r'].Remove()
                WaitTimeCar[road_index]['r'].Record(SimClasses.Clock - car.CreateTime)
            if road_index == 2 and direction == 'r' and car_queue[road_index]['r'].NumQueue() <= 1 and pedestrian_queue[3].NumQueue() <= 0:
                car = car_queue[road_index]['r'].Remove()
                WaitTimeCar[road_index]['r'].Record(SimClasses.Clock - car.CreateTime)
        case 1:
            if (road_index == 1 or road_index == 2) and direction == 'l' and car_queue[road_index]['l'].NumQueue() <= 1:
                car = car_queue[road_index]['l'].Remove()
                WaitTimeCar[road_index]['l'].Record(SimClasses.Clock - car.CreateTime)
        case 2:
            pass
        case 3:
            if (road_index == 3 or road_index == 4) and direction == 's' and car_queue[road_index]['s'].NumQueue() <= 1:
                car = car_queue[road_index]['s'].Remove()
                WaitTimeCar[road_index]['s'].Record(SimClasses.Clock - car.CreateTime)
            if road_index == 3 and direction == 'r' and car_queue[road_index]['r'].NumQueue() <= 1 and pedestrian_queue[1].NumQueue() <= 0:
                car = car_queue[road_index]['r'].Remove()
                WaitTimeCar[road_index]['r'].Record(SimClasses.Clock - car.CreateTime)
            if road_index == 4 and direction == 'r' and car_queue[road_index]['r'].NumQueue() <= 1 and pedestrian_queue[2].NumQueue() <= 0:
                car = car_queue[road_index]['r'].Remove()
                WaitTimeCar[road_index]['r'].Record(SimClasses.Clock - car.CreateTime)
            if road_index == 3 and direction == 'l' and car_queue[road_index]['l'].NumQueue() <= 1 and car_queue[4]['s'].NumQueue() <= 0 and pedestrian_queue[2].NumQueue() <= 0:
                car = car_queue[road_index]['l'].Remove()
                WaitTimeCar[road_index]['l'].Record(SimClasses.Clock - car.CreateTime)
            if road_index == 4 and direction == 'l' and car_queue[road_index]['l'].NumQueue() <= 1 and car_queue[3]['s'].NumQueue() <= 0 and pedestrian_queue[1].NumQueue() <= 0:
                car = car_queue[road_index]['l'].Remove()
                WaitTimeCar[road_index]['l'].Record(SimClasses.Clock - car.CreateTime)
        case 4:
            if (road_index == 3 or road_index == 4) and direction == 's' and car_queue[road_index]['s'].NumQueue() <= 1:
                car = car_queue[road_index]['s'].Remove()
                WaitTimeCar[road_index]['s'].Record(SimClasses.Clock - car.CreateTime)
            if road_index == 3 and direction == 'r' and car_queue[road_index]['r'].NumQueue() <= 1:
                car = car_queue[road_index]['r'].Remove()
                WaitTimeCar[road_index]['r'].Record(SimClasses.Clock - car.CreateTime)
            if road_index == 4 and direction == 'r' and car_queue[road_index]['r'].NumQueue() <= 1:
                car = car_queue[road_index]['r'].Remove()
                WaitTimeCar[road_index]['r'].Record(SimClasses.Clock - car.CreateTime)
            if road_index == 3 and direction == 'l' and car_queue[road_index]['l'].NumQueue() <= 1 and car_queue[4]['s'].NumQueue() <= 0:
                car = car_queue[road_index]['l'].Remove()
                WaitTimeCar[road_index]['l'].Record(SimClasses.Clock - car.CreateTime)
            if road_index == 4 and direction == 'l' and car_queue[road_index]['l'].NumQueue() <= 1 and car_queue[3]['s'].NumQueue() <= 0:
                car = car_queue[road_index]['l'].Remove()
                WaitTimeCar[road_index]['l'].Record(SimClasses.Clock - car.CreateTime)
        case _:
            pass
    SimFunctions.Schedule(Calendar, f'car_arrival_{road_index}_{direction}', get_car_inter_arrival_time(road_index, direction))

def pedestrian_passthrough(road_index: int):
    n = pedestrian_queue[road_index].NumQueue()
    for i in range(n):
        pedestrian = pedestrian_queue[road_index].Remove()
        WaitTimePedestrian[road_index].Record(SimClasses.Clock - pedestrian.CreateTime)

    match traffic_state:
        case 0:
            if road_index == 4:
                if car_queue[1]['r'].NumQueue() > 0:
                    SimFunctions.Schedule(Calendar, f'car_passthrough_1_r', get_car_passthrough_time(1, 'r', True))
            if road_index == 3:
                if car_queue[2]['r'].NumQueue() > 0:
                    SimFunctions.Schedule(Calendar, f'car_passthrough_2_r', get_car_passthrough_time(2, 'r', True))
        case 3 | 4:
            if road_index == 2:
                if car_queue[4]['r'].NumQueue() > 0: 
                    SimFunctions.Schedule(Calendar, f'car_passthrough_4_r', get_car_passthrough_time(4, 'r', True))
                if car_queue[4]['s'].NumQueue() <= 0 and car_queue[3]['l'].NumQueue() > 0:
                    SimFunctions.Schedule(Calendar, f'car_passthrough_3_l', get_car_passthrough_time(3, 'l', True))
            if road_index == 1:
                if car_queue[3]['r'].NumQueue() > 0:
                    SimFunctions.Schedule(Calendar, f'car_passthrough_3_r', get_car_passthrough_time(3, 'r', True))
                if car_queue[3]['s'].NumQueue() <= 0 and car_queue[4]['l'].NumQueue() > 0:
                    SimFunctions.Schedule(Calendar, f'car_passthrough_4_l', get_car_passthrough_time(4, 'l', True))    
        case _:
            pass

def pedestrian_arrival(road_index: int):
    pedestrian = pedestrian_entity(road_index)
    pedestrian_queue[road_index].Add(pedestrian)
    match traffic_state:
        case 0:
            if road_index == 3 or road_index == 4:
                SimFunctions.Schedule(Calendar, f'pedestrian_passthrough_{road_index}', get_pedestrian_passthrough_time(road_index))
        case 2 | 3:
            if road_index == 1 or road_index == 2:
                SimFunctions.Schedule(Calendar, f'pedestrian_passthrough_{road_index}', get_pedestrian_passthrough_time(road_index))
        case _:
            pass
    SimFunctions.Schedule(Calendar, f'pedestrian_arrival_{road_index}', get_pedestrian_inter_arrival_time(road_index))

def traffic_state_transform():
    global traffic_state
    traffic_state = (traffic_state + 1) % 5
    match traffic_state:
        case 0:
            if pedestrian_queue[3].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'pedestrian_passthrough_3', get_pedestrian_passthrough_time(3))
            elif car_queue[2]['r'].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_2_r', get_car_passthrough_time(2, 'r', True))

            if pedestrian_queue[4].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'pedestrian_passthrough_4', get_pedestrian_passthrough_time(4))
            elif car_queue[1]['r'].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_1_r', get_car_passthrough_time(1, 'r', True))

            if car_queue[1]['s'].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_1_s', get_car_passthrough_time(1, 's', True))
            if car_queue[2]['s'].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_2_s', get_car_passthrough_time(2, 's', True))
        case 1:
            if car_queue[1]['l'].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_1_l', get_car_passthrough_time(1, 'l', True))
            if car_queue[2]['l'].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_2_l', get_car_passthrough_time(2, 'l', True))
        case 2:
            if pedestrian_queue[1].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'pedestrian_passthrough_1', get_pedestrian_passthrough_time(1))
            if pedestrian_queue[2].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'pedestrian_passthrough_2', get_pedestrian_passthrough_time(2))
        case 3:
            if pedestrian_queue[1].NumQueue() <= 0 and car_queue[3]['r'].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_3_r', get_car_passthrough_time(3, 'r', True))
            if pedestrian_queue[2].NumQueue() <= 0 and car_queue[4]['r'].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_4_r', get_car_passthrough_time(4, 'r', True))

            if pedestrian_queue[1].NumQueue() <= 0 and car_queue[3]['s'].NumQueue() <= 0 and car_queue[4]['l'].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_4_l', get_car_passthrough_time(4, 'l', True))
            if pedestrian_queue[2].NumQueue() <= 0 and car_queue[4]['s'].NumQueue() <= 0 and car_queue[3]['l'].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_3_l', get_car_passthrough_time(3, 'l', True))
            
            if car_queue[3]['s'].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_3_s', get_car_passthrough_time(3, 's', True))
            if car_queue[4]['s'].NumQueue() > 0:
                SimFunctions.Schedule(Calendar, f'car_passthrough_4_s', get_car_passthrough_time(4, 's', True))
        case 4:
            pass
        case _:
            pass
    SimFunctions.Schedule(Calendar, 'traffic_state_transform', traffic_cycle[traffic_state])

def calculate_confidence_interval(data, confidence=0.95):
    """
    計算一組數據的平均值與半寬 (Half-width)
    回傳: (mean, half_width)
    """
    n = len(data)
    if n <= 1:
        return np.mean(data), 0.0
    
    m = np.mean(data)
    se = stats.sem(data) # 標準誤 (Standard Error)
    # 使用 t 分布計算臨界值 (t_critical)
    h = se * stats.t.ppf((1 + confidence) / 2., n-1)
    return m, h

if __name__ == "__main__":
    for _n in range(n_reps):
        # one rep
        SimFunctions.SimFunctionsInit(Calendar)

        for i in range(1,5):
            SimFunctions.Schedule(Calendar, f'pedestrian_arrival_{i}', get_pedestrian_inter_arrival_time(i))
            for j in ['s', 'r', 'l']:
                SimFunctions.Schedule(Calendar, f'car_arrival_{i}_{j}', get_car_inter_arrival_time(i, j))
        
        SimFunctions.Schedule(Calendar, 'traffic_state_transform', traffic_cycle[0])
        
        SimFunctions.Schedule(Calendar, 'EndSimulation', RunLength)
        SimFunctions.Schedule(Calendar, 'ClearIt', Warmup)

        while Calendar.N() > 0:
            NextEvent = Calendar.Remove()
            SimClasses.Clock = NextEvent.EventTime
            
            match NextEvent.EventType.split('_'):
                case ['EndSimulation']:
                    break

                case ['ClearIt']:
                    SimFunctions.ClearStats()

                case ['traffic', 'state', 'transform']:
                    traffic_state_transform()
                
                case ['car', 'passthrough', road, direction]:
                    car_passthrough(int(road), direction)
                
                case ['car', 'arrival', road, direction]:
                    car_arrival(int(road), direction)
                
                case ['pedestrian', 'passthrough', road]:
                    pedestrian_passthrough(int(road))
                
                case ['pedestrian', 'arrival', road]:
                    pedestrian_arrival(int(road))
                    
                case _:
                    pass
        
        for i in range(1,5):
            WaitTimePedestrianAvg[i].append(WaitTimePedestrian[i].Mean())
            for j in ['s', 'r', 'l']:
                WaitTimeCarAvg[i][j].append(WaitTimeCar[i][j].Mean())
                QueueLengthCarAvg[i][j].append(car_queue[i][j].Mean())
    
    road_map = {
        1: "Guangfu Rd. (Westbound)",  # 1: 光復路往西
        2: "Guangfu Rd. (Eastbound)",  # 2: 光復路往東
        3: "Jiangong Rd. (Northbound)", # 3: 建功路往北
        4: "Jiangong Rd. (Southbound)"  # 4: 建功路往南
    }

    dir_map = {
        's': 'Straight', # 直走
        'r': 'Right',    # 右轉
        'l': 'Left'      # 左轉
    }

    if not os.path.exists('figure'):
        os.makedirs('figure')

    # 設定 matplotlib (移除中文字體設定，使用預設英文)
    # plt.rcParams['font.sans-serif'] = ['Microsoft JhengHei']  <-- Removed
    plt.rcParams['axes.unicode_minus'] = False

    # --- Plot 1: CI Convergence Process ---
    print("Generating CI Convergence Plots...")

    ci_evolution_car = { i: { j: {'means': [], 'half_widths': []} for j in ['s', 'r', 'l'] } for i in range(1, 5) }
    ci_evolution_ped = { i: {'means': [], 'half_widths': []} for i in range(1, 5) }
    
    replication_counts = range(2, n_reps + 1)

    for k in replication_counts:
        for i in range(1, 5):
            # Pedestrian
            mean, h = calculate_confidence_interval(WaitTimePedestrianAvg[i][:k])
            ci_evolution_ped[i]['means'].append(mean)
            ci_evolution_ped[i]['half_widths'].append(h)
            
            # Car
            for j in ['s', 'r', 'l']:
                mean, h = calculate_confidence_interval(WaitTimeCarAvg[i][j][:k])
                ci_evolution_car[i][j]['means'].append(mean)
                ci_evolution_car[i][j]['half_widths'].append(h)

    # Plot Car Convergence (One file per road)
    for i in range(1, 5):
        plt.figure(figsize=(10, 5)) # Slightly wider for English labels
        for j in ['s', 'r', 'l']:
            means = np.array(ci_evolution_car[i][j]['means'])
            half_widths = np.array(ci_evolution_car[i][j]['half_widths'])
            
            plt.plot(replication_counts, means, label=f'{dir_map[j]}')
            plt.fill_between(replication_counts, means - half_widths, means + half_widths, alpha=0.2)
            
        plt.title(f'{road_map[i]} Car Wait Time CI Convergence')
        plt.xlabel('Number of Replications')
        plt.ylabel('Avg Wait Time (s)')
        plt.legend(loc='upper right')
        plt.grid(True, linestyle='--', alpha=0.7)
        plt.tight_layout()
        plt.savefig(f'figure/ci_evolution_car_road_{i}.png')
        # plt.show()

    # Plot Pedestrian Convergence
    plt.figure(figsize=(10, 5))
    for i in range(1, 5):
        means = np.array(ci_evolution_ped[i]['means'])
        half_widths = np.array(ci_evolution_ped[i]['half_widths'])
        
        plt.plot(replication_counts, means, label=f'{road_map[i]}')
        plt.fill_between(replication_counts, means - half_widths, means + half_widths, alpha=0.2)

    plt.title('Pedestrian Wait Time CI Convergence')
    plt.xlabel('Number of Replications')
    plt.ylabel('Avg Wait Time (s)')
    plt.legend()
    plt.grid(True, linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('figure/ci_evolution_pedestrian.png')
    # plt.show()

    # --- Plot 2: Final Bar Charts with Error Bars ---
    print("Generating Final Result Bar Charts...")

    # Car Wait Time
    # 使用 List Comprehension 建立標籤，加入換行符號 \n 讓 X 軸標籤比較整齊
    final_car_labels = [f'{road_map[i].split(".")[0]}.\n{dir_map[j]}' for i in range(1, 5) for j in ['s', 'r', 'l']]
    final_car_data = [calculate_confidence_interval(WaitTimeCarAvg[i][j]) for i in range(1, 5) for j in ['s', 'r', 'l']]
    final_car_means = [d[0] for d in final_car_data]
    final_car_errors = [d[1] for d in final_car_data]

    plt.figure(figsize=(16, 8))
    # 使用不同顏色區分路口
    bar_colors = ['skyblue']*3 + ['lightgreen']*3 + ['salmon']*3 + ['wheat']*3
    
    plt.bar(np.arange(len(final_car_labels)), final_car_means, yerr=final_car_errors, capsize=5, color=bar_colors, edgecolor='black', alpha=0.8)
    
    plt.title(f'Car Average Wait Time (95% CI, n={n_reps})', fontsize=14)
    plt.xlabel('Intersection & Direction', fontsize=12)
    plt.ylabel('Avg Wait Time (s)', fontsize=12)
    plt.xticks(np.arange(len(final_car_labels)), final_car_labels, rotation=0, fontsize=9)
    plt.grid(axis='y', linestyle='--', alpha=0.5)
    
    # 建立 Legend 說明顏色代表的路口
    from matplotlib.patches import Patch
    legend_elements = [
        Patch(facecolor='skyblue', edgecolor='black', label='Guangfu Rd. (W)'),
        Patch(facecolor='lightgreen', edgecolor='black', label='Guangfu Rd. (E)'),
        Patch(facecolor='salmon', edgecolor='black', label='Jiangong Rd. (N)'),
        Patch(facecolor='wheat', edgecolor='black', label='Jiangong Rd. (S)')
    ]
    plt.legend(handles=legend_elements, loc='upper right')
    
    plt.tight_layout()
    plt.savefig('figure/final_ci_car_wait_time.png')
    # plt.show()

    # Pedestrian Wait Time
    final_ped_labels = [road_map[i] for i in range(1, 5)]
    final_ped_data = [calculate_confidence_interval(WaitTimePedestrianAvg[i]) for i in range(1, 5)]
    final_ped_means = [d[0] for d in final_ped_data]
    final_ped_errors = [d[1] for d in final_ped_data]

    plt.figure(figsize=(10, 6))
    plt.bar(final_ped_labels, final_ped_means, yerr=final_ped_errors, capsize=5, color='lightgray', edgecolor='black')
    plt.title(f'Pedestrian Average Wait Time (95% CI, n={n_reps})')
    plt.ylabel('Avg Wait Time (s)')
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.tight_layout()
    plt.savefig('figure/final_ci_pedestrian_wait_time.png')
    # plt.show()

    print("Done. All figures saved in 'figure/' directory.")