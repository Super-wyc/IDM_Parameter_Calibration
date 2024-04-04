import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class IDM():

    def __init__(self,
                 max_acceleration:float,    # 最大加速度(m/s^2)
                 desired_velocity:float,    # 期望速度 (m/s)
                 s0:float,                  # 静止期望跟车距离(m)
                 T:float,                   # 车头时距(s)
                 b:float,                   # 舒适减速度(m/s^2)
                 delta:float=4.0,               # 加速度指数
                 ) -> None:
        self.max_acceleration=max_acceleration
        self.desired_velocity=desired_velocity
        self.delta=delta
        self.s0=s0
        self.T=T

    def IDM_simulate(self,
                     time_step:float,            # 时间间隔
                     leader_length:float,        # 引导车车长
                     leader_velocity:pd.Series,       # 引导车速度列表 
                     leader_position:pd.Series,       # 引导车位置列表
                     follower_length:float,      # 跟驰车车长
                     follower_initial_velocity:float,    # 跟驰车初始速度
                     follower_initial_position:float,     # 跟驰车初始位置
                     lane:int=2
                     )-> pd.DataFrame:
        
        if lane<=2:
            min_s=leader_length       # 恰好不相撞距离
        else:
            min_s=follower_length

        # 初始化跟驰车
        follower_position=np.zeros(leader_position)
        follower_velocity=np.zeros(leader_velocity)
        follower_velocity[0]=follower_initial_velocity
        follower_position[0]=follower_initial_position

        # 模拟
        for i in range(1,len(leader_position)):
            delta_v = leader_velocity[i-1]-follower_velocity[i-1]
            s_star = IDM.s0 + max(0, follower_velocity[i-1]*IDM.T + (follower_velocity[i-1]*delta_v)/(2*np.sqrt(IDM.max_acceleration*IDM.b)))
            s = leader_position[i-1] - follower_position[i-1] - min_s
            acceleration = IDM.max_acceleration * (1 - (follower_velocity[i-1]/IDM.desired_velocity)**IDM.delta - (s_star/s)**2)
            follower_velocity[i] = follower_velocity[i-1] + acceleration * time_step
            follower_position[i] = follower_position[i-1] + follower_velocity[i-1] * time_step + 0.5 * acceleration * time_step**2

        return follower_position