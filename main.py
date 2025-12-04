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

# 從 i 方向來的車，要直走straight、右轉right、左轉left，在t時間內能通過幾輛(n)
# t_window = t_warmup + (n - 1) * t_passthrough
# n = (t_windows - t_warmup) * 1/t_passthrough + 1
#
#       n   : 通過幾量車                                       variable
# t_window  : 當下到下一次 minimize(行人要通過的時間, 紅燈)      Random variable
# t_warmup  : 第一輛車通過的時間                                Random variable ~ Normal(mu, sigma)
#   t_passthrough   : 車流中每輛車花費時間                              CONSTANT / Random variable ~ Normal(mu, sigma)

# s: 直走 r: 右轉 l: 左轉 (mu, sigma)
t_warmup_parameters = {
    1 : {'s':(5, 1), 'r':(5, 1), 'l':(5, 1)},
    2 : {'s':(5, 1), 'r':(5, 1), 'l':(5, 1)},
    3 : {'s':(5, 1), 'r':(5, 1), 'l':(5, 1)},
    4 : {'s':(5, 1), 'r':(5, 1), 'l':(5, 1)}
}
t_passthrough_parameters = {
    1 : {'s': 5, 'r': 5, 'l': 5},
    2 : {'s': 5, 'r': 5, 'l': 5},
    3 : {'s': 5, 'r': 5, 'l': 5},
    4 : {'s': 5, 'r': 5, 'l': 5}
}

def get_max_passthrough_car_cnt(t_window: float, road_index: int, direction: str):
    """
    get_max_passthrough_car_cnt 的 Docstring
    
    :param t_window: 到下次紅燈/行人通過的時間
    :type t_window: float
    :param road_index: [1, 2, 3, 4]
    :type road_index: int
    :param direction: ['s', 'r', 'l']
    :type direction: str
    """
    w_mu = t_warmup_parameters[road_index][direction][0]
    w_sigma = t_warmup_parameters[road_index][direction][1]
    t_warmup = rng.normal(w_mu, w_sigma)
    n = (t_window - t_warmup) / t_passthrough_parameters[road_index][direction] + 1
    return n


if __name__ == "__main__":
    pass
