import SimClasses
import SimFunctions
import SimRNG
import numpy as np
import matplotlib.pyplot as plt
rng = np.random.default_rng(seed=42)

# time unit : second

# traffic light cycle : j = (j + 1) % 4
## 0:光復路綠燈             CONSTANT
## 1:光復路左轉燈           CONSTANT
## 2:建功路行人綠燈         CONSTANT
## 3:建功路綠燈             CONSTANT
traffic_cycle = {
    0 : 1,
    1 : 1,
    2 : 1,
    3 : 1
}
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

# s: 直走 r: 右轉 l: 左轉 (beta : second / # car)
car_arrival_parameters = {
    1: {'s': 5, 'r': 5, 'l': 5},
    2: {'s': 5, 'r': 5, 'l': 5},
    3: {'s': 5, 'r': 5, 'l': 5},
}

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
    return rng.exponential(car_arrival_parameters[road_index][direction])

# 從 i 方向來的車，要直走straight、右轉right、左轉left，在t時間內能通過幾輛(n)
# t_window = t_warmup + (n - 1) * t_passthrough
# n = (t_windows - t_warmup) * 1/t_passthrough + 1
#
#       n           : 通過多少車                                       variable
# t_window          : 當下到下一次 minimize(行人要通過的時間, 紅燈)      Random variable
# t_warmup          : 第一輛車通過的時間                                Random variable ~ Normal(mu, sigma)
# t_passthrough     : 車流中每輛車花費時間                              Random variable ~ Normal(mu, sigma)

# s: 直走 r: 右轉 l: 左轉 (mu, sigma)
t_car_warmup_parameters = {
    1 : {'s':(5, 1), 'r':(5, 1), 'l':(5, 1)},
    2 : {'s':(5, 1), 'r':(5, 1), 'l':(5, 1)},
    3 : {'s':(5, 1), 'r':(5, 1), 'l':(5, 1)},
    4 : {'s':(5, 1), 'r':(5, 1), 'l':(5, 1)}
}
# 飽和車流後續車輛通過平均花費(mu, sigma)
t_passthrough_parameters = {
    1 : {'s':(2, 1), 'r':(2, 1), 'l':(2, 1)},
    2 : {'s':(2, 1), 'r':(2, 1), 'l':(2, 1)},
    3 : {'s':(2, 1), 'r':(2, 1), 'l':(2, 1)},
    4 : {'s':(2, 1), 'r':(2, 1), 'l':(2, 1)}
}

def get_car_passthrough_time(road_index: int, direction: str, first_car: bool = False) -> float:
    if first_car:
        return rng.normal(t_car_warmup_parameters[road_index][direction][0], t_car_warmup_parameters[road_index][direction][1])
    else:
        return rng.normal(t_passthrough_parameters[road_index][direction][0], t_passthrough_parameters[road_index][direction][1])

# exponential (beta : second / # person)
pedestrian_arrival_parameters = {
    1: 5,
    2: 5,
    3: 5,
    4: 5
}

def get_pedestrian_inter_arrival_time(road_index: int) -> float:
    """
    get_pedestrian_inter_arrival_time 的 Docstring
    
    :param road_index: [1, 2, 3, 4]
    :type road_index: int
    :return: 下個行人要經過多久到達
    :rtype: float
    """
    return rng.exponential(pedestrian_arrival_parameters[road_index])

# Normal(mu, sigma)
pedestrian_passthrough_parameters = {
    1: (10, 2),
    2: (10, 2),
    3: (10, 2),
    4: (10, 2)
}
def get_pedestrian_passthrough_time(road_index: int) -> float:
    return rng.normal(pedestrian_passthrough_parameters[road_index][0], pedestrian_passthrough_parameters[road_index][1])

if __name__ == "__main__":
    pass
