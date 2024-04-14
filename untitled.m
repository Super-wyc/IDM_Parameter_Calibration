clc;clear;
warning("off");
IDM_delta=4.0;
 IDMmodel=[1.899567935598683 0.5006225052694429 2.034889406658853 0.10370989621875638 33.62456626848502]; % IDM模型中待标定的五个参数：s0、t、a、b、v的初始值设定（无固定要求，这里为一组他人标定结果），单位：m，s，m/s2，m/s2，m/s

    
    % 定义包含CSV文件的文件夹路径
    folderPath = 'dataset/train';
    % 获取文件夹中所有CSV文件的列表
    csvFiles = dir(fullfile(folderPath, '*.csv'));
    %目标函数
    RMSPE_total=0;

     % 索引待查
    data_clurster=readtable('dataset\aftercluster\datawithcluster_lstm.csv');
    num=0;

    
        %disp(num2str(k))
    
        % 构建完整的文件路径
        filePath = fullfile(folderPath, csvFiles(1).name);
        % 使用readtable读取CSV文件
        data = readtable(filePath); 


          % 取特定类
        id=data.following_id(1);
        disp(id)
        label=data_clurster(data_clurster.following_id==id,"driving_style_lstm");
        label=table2array(label);
        if(label~=2)
            disp(id)
        end

  