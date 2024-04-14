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
    
    % 循环遍历所有CSV文件
    for k = 1:length(csvFiles)
    
        %disp(num2str(k))
    
        % 构建完整的文件路径
        filePath = fullfile(folderPath, csvFiles(k).name);
        % 使用readtable读取CSV文件
        data = readtable(filePath); 


          % 取特定类
        id=data.following_id(1);
        index=data_clurster(:,"following_id")==id;
        label=data_clurster(index,"following_feature");
        if(label~=0) 
            continue;
        end

        % 后车观测值
        follwer_x_obs=data.following_x(2:end);
        follwer_v_obs=data.following_speed(2:end);
        
    
        % IDM_simulate
        time_step=0.04;    %步长
        
    
        front_x=data.front_x(2:end);   %前车位置列表
        front_v=data.front_speed(2:end);   %前车速度列表
        front_length=data.front_width;  %前车长度
        
    
        min_s=front_length(1); %恰好不相撞距离
        


    
    
        s0=IDMmodel(1);
        t=IDMmodel(2);
        max_a=IDMmodel(3);
        b=IDMmodel(4);
        v=IDMmodel(5);

        delta_v=follwer_v_obs-front_v;
        s_star=s0+max(0,follwer_v_obs.*t+(follwer_v_obs.*delta_v)./(2*sqrt(max_a.*b)));
        s=front_x-follwer_x_obs- min_s;
        a=max_a*(1-(follwer_v_obs./v).^IDM_delta-(s_star./s).^2);
        follwer_v_sim=follwer_v_obs+a.*time_step;
        follwer_x_sim=follwer_x_obs+follwer_v_obs.*time_step+0.5*a.*time_step^2;
    
    
        %RMSPE计算  space
        RMSPE=calculate_RMSPE(front_x(2:end)-follwer_x_obs(2:end)-front_length(1),front_x(2:end)-follwer_x_sim(1:end-1)-front_length(1));
        RMSPE_total=RMSPE_total+RMSPE;
    end
    RMSPE_MEAN=RMSPE_total/length(csvFiles);
    obj_f=RMSPE_MEAN;
    disp(num2str(RMSPE_total))

    
    % RMSPE计算函数
    function RMSPE = calculate_RMSPE(x, y)
        % 检查x和y的长度是否相等
        if length(x) ~= length(y)
            error('x和y的长度必须相等。');
        end
        % 计算百分比误差
        percent_errors = ((y - x) ./ x).^2;
        % 计算均方根误差
        mse = mean(percent_errors);
        % 计算百分比均方根误差
        RMSPE = sqrt(mse) * 100;
    end