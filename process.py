import pandas as pd
import matplotlib.pyplot as plt
import re
import numpy as np


class Data_process():
    def __init__(self, path, target_lane:int = 2, following_time:float = 15) -> None:
        '''
        数据筛选类
        参数：
        traget_lane：目标车道
        following_ti0me：跟随时间限制
        '''
        self.path = path
        self.data = pd.read_csv(path)
        self.lane = target_lane
        self.time = following_time

    def lane_selecter(self) -> pd.DataFrame:
        self.data = self.data[self.data['laneId'] == self.lane]
        return self.data
    
    def car_following_selecter(self) -> pd.DataFrame:
        self.data = self.data[self.data["followingId"] != 0]
        return self.data
    
    def time_selecter(self) -> pd.DataFrame:
        self.lane_selecter()
        self.car_following_selecter()
        time_selected = self.data.groupby(['id', 'followingId']).count()['frame']
        time_selected = time_selected[time_selected > self.time * 25].sort_values(ascending=False)
        return time_selected

    def distance_selector(self) -> dict:
        '''
        返回值：
        以跟车对为键，片段为值的字典
        '''
        temp = self.time_selecter()
        self.__init__(self.path, self.lane, self.time)
        self.lane_selecter()
        distance = {}
        for car_pair in temp.index:
            front_car = self.data[(self.data['id']==car_pair[0]) & (self.data['followingId']==car_pair[1])]
            following_car = self.data[self.data['id']==car_pair[1]]
            same_frame = following_car[following_car['frame'].isin(front_car['frame'])]
            d = abs(same_frame['x'].reset_index(drop=True)-front_car[front_car['frame'].isin(same_frame['frame'])]['x'].reset_index(drop=True))
            d.rename('distance', inplace=True)
            d = pd.concat([d, same_frame['x'].reset_index(drop=True), 
                           front_car[front_car['frame'].isin(same_frame['frame'])]['x'].reset_index(drop=True),
                           same_frame['frame'].reset_index(drop=True)], ignore_index=True, axis=1)
            d.columns = ['distance',  'following_x', 'front_x', 'frame']
            d['front_speed'] = abs(d['front_x'].diff() * 25)
            d['front_a'] = abs(d['front_speed'].diff() / 0.04)
            d['following_speed'] = abs(d['following_x'].diff() * 25)
            d['following_a'] = abs(d['following_speed'].diff() / 0.04)
            d['frame'] = same_frame['frame'].reset_index(drop=True)
            d['front_id'] = [car_pair[0]] * len(d)
            d['following_id'] = [car_pair[1]] * len(d)
            d = d.bfill()
            if sum((d['distance'] >= 10) & (d['distance'] <= 125)) > self.time * 25:
                distance[car_pair] = d
            else:
                continue
        return distance
    
    def plot_following(self, pair:tuple=(215, 217))  -> None:
        plt.rcParams['font.sans-serif'] = ['SimHei']
        df = self.distance_selector()[pair]
        plt.plot((df['frame'] / 25), df['front_x'], label=f'前导车辆-{pair[0]}', color='#6495ed')
        plt.plot((df['frame'] / 25), df['following_x'], label=f'跟随车辆-{pair[1]}', color='#e76a83')
        plt.legend()
        return None
    
    def data_merge(self) -> tuple:
        '''
        数据匹配
        输出属性：x、width、speed、class、feature
        返回值：元组 0:合并之后完整的DataFrame, 1:合并之和同之前的字典
        '''
        pattern_ = ".+\d{2}_"
        get_path = re.search(pattern_, self.path).group()
        tracks_data = pd.read_csv(fr"{get_path}tracksMeta.csv")
        data = self.distance_selector()
        for pair in data.keys():
            data[pair]['front_width'] = tracks_data[tracks_data['id'] == pair[0]]['width'].repeat(len(data[pair])).reset_index(drop=True)
            data[pair]['following_width'] = tracks_data[tracks_data['id'] == pair[1]]['width'].repeat(len(data[pair])).reset_index(drop=True)
            data[pair]['front_class'] = tracks_data[tracks_data['id'] == pair[0]]['class'].repeat(len(data[pair])).reset_index(drop=True)
            data[pair]['following_class'] = tracks_data[tracks_data['id'] == pair[1]]['class'].repeat(len(data[pair])).reset_index(drop=True)
            data[pair]['front_feature'] = np.full([len(data[pair]), 1], np.nan)
            data[pair]['following_feature'] = np.full([len(data[pair]), 1], np.nan)
        mix_data = pd.DataFrame([])
        for piece in data.values():
            mix_data = pd.concat([piece, mix_data], ignore_index=True)
        return mix_data, data
    
    def position_trans(self) -> tuple:
        '''
        x坐标归一化
        返回值：归一后的x坐标(tuple, 0:front, 1:following)
        '''
        x_data = self.distance_selector()
        data = self.data_merge()[1]
        for pair in x_data.keys():
            x_data[pair].drop(index=[0], inplace=True)
            data[pair].drop(index=[0], inplace=True)
            x_data[pair]['following_x'] = x_data[pair]['following_x'].apply(lambda x: abs(x-x_data[pair]['following_x'][1]))
            x_data[pair]['front_x'] = x_data[pair]['following_x'] + x_data[pair]['distance']
            data[pair]['front_x'] =  x_data[pair]['front_x']
            data[pair]['following_x'] =  x_data[pair]['following_x']
        mix_data_trans = pd.DataFrame([])
        for piece in data.values():
            mix_data_trans = pd.concat([piece, mix_data_trans], ignore_index=True)
        return mix_data_trans, data

    def save_csv(self, path:str = 'dataset', how='single') -> pd.DataFrame:  # path只需要传入文件夹的路径即可，不需要对文件命名
        pattern = '\d{2}_tracks\.csv'
        name = re.search(pattern, self.path).group()
        data = self.position_trans()
        if how == "mix":
            data[0].to_csv(f"{path}\car_following_{name}")
        elif how == "single":
            data_dict = self.position_trans()[1]
            for key in data_dict.keys():
                data_dict[key].to_csv(rf"{path}\{key}_{name}")
        return (lambda how: data[0] if how=="mix" else data_dict)(how)
