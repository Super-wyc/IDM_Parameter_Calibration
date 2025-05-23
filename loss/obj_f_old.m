% 目标函数计算
function obj_f = obj_f_old(IDMmodel)% IDM模型中待标定的五个参数：s0、t、a、b、v的初始值设定（无固定要求，这里为一组他人标定结果），单位：m，s，m/s2，m/s2，m/s

    IDM_delta=4.0;

    % 定义包含CSV文件的文件夹路径
    folderPath = 'dataset/train';
    % 获取文件夹中所有CSV文件的列表
    csvFiles = dir(fullfile(folderPath, '*.csv'));
    %目标函数
    RMSPE_total=0;

     % 索引待查
   % data_clurster=readtable('dataset\aftercluster\datawithcluster_lstm.csv');
    num=0;
    
    % 循环遍历所有CSV文件
    for k = 1:length(csvFiles)
    
        %disp(num2str(k))
    
        % 构建完整的文件路径
        filePath = fullfile(folderPath, csvFiles(k).name);
        % 使用readtable读取CSV文件
        data = readtable(filePath); 


          % 取特定类
      %  id=data.following_id(1);
       % label=data_clurster(data_clurster.following_id==id,"driving_style_lstm");
        %label=table2array(label);
        %if(label==0) 
                    
            % 后车观测值
            follwer_x_obs=data.following_x(2:end);
            
        
            % IDM_simulate
            time_step=0.04;    %步长
            
        
            front_x=data.front_x(2:end);   %前车位置列表
            front_v=data.front_speed(2:end);   %前车速度列表
            front_length=data.front_width;  %前车长度
            
        
            min_s=front_length(1); %恰好不相撞距离
            
    
    
            follwer_x_sim = zeros(length(data.following_x)-1,1); %后车位置预测
            follwer_v_sim = zeros(length(data.following_speed)-1,1); %后车速度预测
        
            follwer_x_init = data.following_x(2); % 获取实际轨迹中第二个时刻的后车位置
            follwer_v_init=data.following_speed(2); % 获取实际轨迹中第二个时刻的后车速度
            follwer_x_sim(1)=follwer_x_init;    %后车位置初始化
            follwer_v_sim(1)=follwer_v_init;    %后车速度初始化
        
            s0=IDMmodel(1);
            t=IDMmodel(2);
            max_a=IDMmodel(3);
            b=IDMmodel(4);
            v=IDMmodel(5);
        
        
            for i = 2:length(follwer_x_sim)
                delta_v=follwer_v_sim(i-1)-front_v(i-1);
                s_star=s0+max(0,follwer_v_sim(i-1)*t+(follwer_v_sim(i-1)*delta_v)/(2*sqrt(max_a*b)));
                s=front_x(i-1)-follwer_x_sim(i-1)- min_s;
                a=max_a*(1-(follwer_v_sim(i-1)/v)^IDM_delta-(s_star/s)^2);
                follwer_v_sim(i)=follwer_v_sim(i-1)+a*time_step;
                follwer_x_sim(i)=follwer_x_sim(i-1)+follwer_v_sim(i-1)*time_step+0.5*a*time_step^2;
            end
    
            num=num+1;
    
            %RMSPE计算  space
            RMSPE=calculate_RMSPE(front_x-follwer_x_obs,front_x-follwer_x_sim);
            RMSPE_total=RMSPE_total+RMSPE;
       % end
    end


    RMSPE_MEAN=RMSPE_total/num;
    obj_f=RMSPE_MEAN;
    disp(num2str(RMSPE_MEAN))
    disp(num)

end
    
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
   

 
    

