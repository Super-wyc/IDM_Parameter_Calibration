from hyperopt import fmin, tpe, hp  
import numpy as np 
import pandas as pd
from math import sqrt
import re
import os
import random



class Data():
    def __init__(self, path:str='dataset') -> None:
        self.path = path

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
    
    def dataset_split(self):
        data_dict = self.extract_data()
        keys = list(data_dict.keys())
        random.shuffle(keys)
        total_length = len(keys)
        train_length = int((total_length / 6) * 4)
        verify_length = int((total_length - train_length) / 2)
        train_keys = keys[:train_length]
        verify_keys = keys[train_length:train_length+verify_length]
        test_keys = keys[train_length+verify_length:]

        train_data = {key: data_dict[key] for key in train_keys}
        verify_data = {key: data_dict[key] for key in verify_keys}
        test_data = {key: data_dict[key] for key in test_keys}
        return train_data, verify_data, test_data
    
    def data_to_csv(self):
        all_data = self.dataset_split()
        for key in all_data[0].keys():
            all_data[0][key].to_csv(rf"{self.path}/train/{key}.csv")
        for key in all_data[1].keys():
            all_data[1][key].to_csv(rf"{self.path}/verify/{key}.csv")
        for key in all_data[2].keys():
            all_data[2][key].to_csv(rf"{self.path}/test/{key}.csv")

    

t = Data()

a = t.data_to_csv()