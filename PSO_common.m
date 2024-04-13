clc;clear;
tic
% 定义需要优化的目标函数
obj_f = @(IDMModel)fun1(IDMModel);
numvars = 5;

% IDM模型中待标定的五个参数：s、t、a、b、v的初始值设定（无固定要求，这里为一组他人标定结果），单位：m，s，m/s2，m/s2，m/s
lb_IDM=[1.0 0.5 2.0 0.0001 20];  %变量下边界
ub_IDM=[5.0 1.5 4.0 4.0 100];  %变量上边界
%IDMModel_init = [3.073 0.8392 0.6814 0.9169 22.22];%初始取值

options = optimoptions('particleswarm', 'SwarmSize', 50, 'MaxIterations', 20,"PlotFcn","pswplotbestf"); 
[x, fval] = particleswarm(@obj_f,numvars,lb_IDM,ub_IDM,options);


% 访问结果并分析结果
fprintf('最小值: %f\n',fval);
fprintf('最小值对应的变量值: (%f,%f,%f,%f,%f)\n',x(1),x(2),x(3),x(4),x(5));  %x(1)~x(5)分别为s、t、a、b、v
toc
disp(['运行时间: ',num2str(toc)]);