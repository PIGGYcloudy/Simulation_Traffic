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
RNGseed = SimRNG.InitializeRNSeed()

# Second
RunLength = 10800.
Warmup = 3600.

n_reps = 10

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
    1: {'s': 5, 'r': 5, 'l': 5},
    2: {'s': 5, 'r': 5, 'l': 5},
    3: {'s': 5, 'r': 5, 'l': 5},
    4: {'s': 5, 'r': 5, 'l': 5}
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

# 從 i 方向來的車，要直走straight、右轉right、左轉left，在t時間內能通過幾輛(n)
# t_window = t_warmup + (n - 1) * t_passthrough
# n = (t_windows - t_warmup) * 1/t_passthrough + 1
#
#       n           : 通過多少車                                       variable
# t_window          : 當下到下一次 minimize(行人要通過的時間, 紅燈)      Random variable
# t_warmup          : 第一輛車通過的時間                                Random variable ~ Normal(mu, var)
# t_passthrough     : 車流中每輛車花費時間(逐輛模擬)                    Random variable ~ Normal(mu, var)

# s: 直走 r: 右轉 l: 左轉 (mu, var)
t_car_warmup_parameters = {
    1 : {'s':(5, 1), 'r':(5, 1), 'l':(5, 1)},
    2 : {'s':(5, 1), 'r':(5, 1), 'l':(5, 1)},
    3 : {'s':(5, 1), 'r':(5, 1), 'l':(5, 1)},
    4 : {'s':(5, 1), 'r':(5, 1), 'l':(5, 1)}
}
# 飽和車流後續車輛通過平均花費(mu, var)
t_passthrough_parameters = {
    1 : {'s':(2, 1), 'r':(2, 1), 'l':(2, 1)},
    2 : {'s':(2, 1), 'r':(2, 1), 'l':(2, 1)},
    3 : {'s':(2, 1), 'r':(2, 1), 'l':(2, 1)},
    4 : {'s':(2, 1), 'r':(2, 1), 'l':(2, 1)}
}
# exponential (beta : second / # person)
pedestrian_arrival_parameters = {
    1: 5,
    2: 5,
    3: 5,
    4: 5
}
# Normal(mu, var)
pedestrian_passthrough_parameters = {
    1: (10, 2),
    2: (10, 2),
    3: (10, 2),
    4: (10, 2)
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
    return SimRNG.Expon(car_arrival_parameters[road_index][direction])

def get_car_passthrough_time(road_index: int, direction: str, start_car: bool = False) -> float:
    if start_car:
        return SimRNG.Normal(t_car_warmup_parameters[road_index][direction][0], t_car_warmup_parameters[road_index][direction][1])
    else:
        return SimRNG.Normal(t_passthrough_parameters[road_index][direction][0], t_passthrough_parameters[road_index][direction][1])


def get_pedestrian_inter_arrival_time(road_index: int) -> float:
    """
    get_pedestrian_inter_arrival_time 的 Docstring
    
    :param road_index: [1, 2, 3, 4]
    :type road_index: int
    :return: 下個行人要經過多久到達
    :rtype: float
    """
    return SimRNG.Expon(pedestrian_arrival_parameters[road_index])

def get_pedestrian_passthrough_time(road_index: int) -> float:
    return SimRNG.Normal(pedestrian_passthrough_parameters[road_index][0], pedestrian_passthrough_parameters[road_index][1])

# Not Yet Complete
def car_passthrough(road_index: int, direction: str):
    return

# Not yet complete 
def car_arrival(road_index: int, direction: str):
    car = car_entity(road_index, direction)
    car_queue[road_index][direction].Add(car)

    match traffic_state:
        case 0:
            if (road_index == 1 or road_index == 2):
                pass
        case 1:
            pass
        case 2:
            pass
        case 3:
            pass
        case 4:
            pass
        case _:
            pass
    SimFunctions.Schedule(Calendar, f'car_arrival_{road_index}_{direction}', get_car_inter_arrival_time(road_index, direction))
def pedestrian_passthrough(road_index: int):
    n = pedestrian_queue[road_index].NumQueue()
    for i in range(n):
        pedestrian = pedestrian_queue[road_index].Remove()
        WaitTimePedestrian[road_index].Record(SimClasses.Clock - pedestrian.CreateTime)    
    pedestrian_queue[road_index].ThisQueue = []

    match traffic_state:
        case 0:
            if road_index == 4:
                if car_queue[1]['r'].NumQueue() > 0:
                    SimFunctions.Schedule(Calendar, f'car_passthrough_1_r', get_car_passthrough_time(1, 'r', True))
            if road_index == 3:
                if car_queue[2]['r'].NumQueue() > 0:
                    SimFunctions.Schedule(Calendar, f'car_passthrough_2_r', get_car_passthrough_time(2, 'r', True))
        case 3:
            if road_index == 2:
                if car_queue[4]['r'].NumQueue() > 0: 
                    SimFunctions.Schedule(Calendar, f'car_passthrough_4_r', get_car_passthrough_time(4, 'r', True))
                if car_queue[3]['l'].NumQueue() > 0:
                    SimFunctions.Schedule(Calendar, f'car_passthrough_3_l', get_car_passthrough_time(3, 'l', True))
            if road_index == 1:
                if car_queue[3]['r'].NumQueue() > 0:
                    SimFunctions.Schedule(Calendar, f'car_passthrough_3_r', get_car_passthrough_time(3, 'r', True))
                if car_queue[4]['l'].NumQueue() > 0:
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


# Not yet complete
def traffic_state_transform():
    global traffic_state
    traffic_state = (traffic_state + 1) % 5
    match traffic_state:
        case 0:
            pass
        case 1:
            pass
        case 2:
            pass
        case 3:
            pass
        case 4:
            pass
        case _:
            pass
    SimFunctions.Schedule(Calendar, 'traffic_state_transform', traffic_cycle[traffic_state])

if __name__ == "__main__":
    pass
