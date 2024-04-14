from hyperopt import fmin, tpe, hp  
import numpy as np 
import pandas as pd
from math import sqrt
import re
import os


class IDM2():

    def __init__(self,
                 max_acceleration:float,    # 最大加速度(m/s^2)
                 desired_velocity:float,    # 期望速度 (m/s)
                 s0:float,                  # 静止期望跟车距离(m)
                 T:float,                   # 车头时距(s)
                 b:float,                   # 舒适减速度(m/s^2)
                 delta:float=4.0,               # 加速度指数
                 ) -> None:
        self.max_acceleration = max_acceleration
        self.desired_velocity = desired_velocity
        self.delta = delta
        self.s0 = s0
        self.b = b
        self.T = T

    def simulate(self,
                     time_step:float,                  # 时间间隔
                     leader_length:float,              # 引导车车长
                     leader_velocity:pd.Series,        # 引导车速度列表 
                     leader_position:pd.Series,        # 引导车位置列表
                     follower_length:float,            # 跟驰车车长
                     follower_velocity:pd.Series,      # 跟驰车初始速度
                     follower_position:pd.Series,      # 跟驰车初始位置
                     lane:int=2
                     )-> pd.DataFrame:
        
        follower_forecast_position = np.zeros(len(leader_position))
        follower_forecast_velocity = np.zeros(len(leader_velocity))

        if lane <= 3:
            for i in range(len(leader_position)-1):
                s_ = self.s0 + max(0, self.T * follower_velocity[i] + ((follower_velocity[i] * 
                                                                        (follower_velocity[i] - leader_velocity[i])) / (2 * sqrt(self.max_acceleration * self.b))))
                a = self.max_acceleration * (1 - (follower_velocity[i] / self.desired_velocity) ** self.delta - 
                                             (s_ / (leader_position[i] - follower_position[i] - leader_length))**2)
                follower_forecast_velocity[i] = follower_velocity[i] + a * time_step
                follower_forecast_position[i] = follower_position[i] + follower_forecast_velocity[i] * time_step + 0.5 * a * (time_step**2)
        else:
            for i in range(len(leader_position)-1):
                s_ = self.s0 + max(0, self.T * follower_velocity[i] + ((follower_velocity[i] * 
                                                                        (follower_velocity[i] - leader_velocity[i])) / (2 * sqrt(self.max_acceleration * self.b))))
                a = self.max_acceleration * (1 - (follower_velocity[i] / self.desired_velocity) ** self.delta - 
                                             (s_ / (leader_position[i] - follower_position[i] - follower_length))**2)
                follower_forecast_velocity[i] = follower_velocity[i] + a * time_step
                follower_forecast_position[i] = follower_position[i] + follower_forecast_velocity[i] * time_step + 0.5 * a * (time_step**2)

        return abs(leader_position[1:] - follower_forecast_position[:-1])
    

class TPE():
    def __init__(self, path:str='dataset',
                 space={'max_acceleration': hp.uniform('max_acceleration', 0.5, 3),
                        'desired_velocity': hp.uniform('desired_velocity', 22.22, 33.33),
                        's0': hp.uniform('s0', 0.2, 2),
                        'T': hp.uniform('T', 0.8, 2),
                        'b': hp.uniform('b', 0.5, 4)}) -> None:
        self.path = path
        self.space = space

    def extract_data(self) -> dict:
        pattern = re.compile(r"\((\d+), (\d+)\)_(\d+)_tracks\.csv")
        data = pd.DataFrame([])
        data_dict = {}
        for filename in os.listdir(self.path):
            match = pattern.match(filename)
            if match:
                temp = pd.read_csv(rf"dataset/{filename}")
                data = pd.concat([data, temp])
                data_dict[filename[:-4]] = temp
        data.reset_index(inplace=True, drop=True)
        return data_dict
    
    def RMSPE_(self, data, max_acceleration, desired_velocity, s0, T, b):
        idm = IDM2(max_acceleration, desired_velocity, s0, T, b)
        y_pred = idm.simulate(0.04, data['front_width'][0], data['front_speed'], data['front_x'], data['following_width'][0], data['following_speed'][0], data['following_x'][0])
        y_true = np.array(data['distance'])
        y_pred = np.array(y_pred)
        y_true = np.clip(y_true, a_min=1e-8, a_max=None)  # 避免除以零  
        percent_error = (y_true - y_pred) / y_true
        mspe = np.mean(np.square(percent_error))
        return np.sqrt(mspe)
    
    def RMSPE2(self, data, args):
        idm = IDM2(args['max_acceleration'], args['desired_velocity'], args['s0'], args['T'], args['b'])
        y_pred = idm.simulate(0.04, data['front_width'][0], data['front_speed'], data['front_x'], data['following_width'][0], data['following_speed'], data['following_x'])
        y_true = np.array(data['distance'])[1:]
        y_pred = np.array(y_pred)
        y_true = np.clip(y_true, a_min=1e-8, a_max=None)  # 避免除以零  
        percent_error = (y_true - y_pred) / y_true
        mspe = np.mean(np.square(percent_error))
        return np.sqrt(mspe)
    
t = TPE(path="dataset/train")

def mean_rmspe2(args):
    temp_dict = t.extract_data()
    rmspe = np.array([])
    for key in temp_dict.keys():
        rmspe = np.append(rmspe, t.RMSPE2(temp_dict[key], args=args))
    return rmspe.mean()

space={'max_acceleration': hp.uniform('max_acceleration', 0.1, 5),
       'desired_velocity': hp.uniform('desired_velocity', 10, 50),
       's0': hp.uniform('s0', 0.1, 10),
       'T': hp.uniform('T', 0.1, 5),
       'b': hp.uniform('b', 0.1, 5)}

def tpe_2(loop=1000):
    best = fmin(fn=mean_rmspe2,
                space=space,  
                algo=tpe.suggest,  
                max_evals=loop)
    return best

print(mean_rmspe2({'max_acceleration':0.972478, 'desired_velocity':33.231694, 's0':0.211538, 'T':0.805561, 'b':0.554205}))

print(tpe_2())