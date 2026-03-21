clear all
clc
close all

%% 01 - Austria 

% Read Raw Data
A = readmatrix('01_Load.csv');
B = readmatrix('01_Renewable.csv');
Craw = readmatrix('01_Capacity.csv');

% Build Aggregated Matrix
% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,2) A(1:96*11,3) B(1:96*11,2)+B(1:96*11,8) B(1:96*11,4)+B(1:96*11,10)];
% datawrite(1,end+1) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"01_Preprocessed.csv");

%% 02 - Belgium

% Read Raw Data
A = readmatrix('02_Load.csv');
Braw = readmatrix('02_Renewable.csv');
Craw = readmatrix('02_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,5)+Braw(i+1,8))-(Braw(i,2)+Braw(i,5)+Braw(i,8)))/4;
    delta4 = ((Braw(i+1,4)+Braw(i+1,7)+Braw(i+1,10))-(Braw(i,4)+Braw(i,7)+Braw(i,10)))/4;
    B(k,1)   = Braw(i,2)+Braw(i,5)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,5)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,5)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,5)+Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,4)+Braw(i,7)+Braw(i,10);
    B(k+1,2) = Braw(i,4)+Braw(i,7)+Braw(i,10)+1*delta4;
    B(k+2,2) = Braw(i,4)+Braw(i,7)+Braw(i,10)+2*delta4;
    B(k+3,2) = Braw(i,4)+Braw(i,7)+Braw(i,10)+3*delta4;
    
    k = k + 4;
end


% Build Aggregated Matrix
% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,2) A(1:96*11,3) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,end+1) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"02_Preprocessed.csv");

%% 03 Bulgaria

Araw = readmatrix('03_Load.csv');
Braw = readmatrix('03_Renewable.csv');
Craw = readmatrix('03_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,8))-(Braw(i,2)+Braw(i,8)))/4;
    delta4 = ((Braw(i+1,2)+Braw(i+1,8))-(Braw(i,2)+Braw(i,8)))/4;
    B(k,1)   = Braw(i,2)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,2)+Braw(i,8);
    B(k+1,2) = Braw(i,2)+Braw(i,8)+1*delta4;
    B(k+2,2) = Braw(i,2)+Braw(i,8)+2*delta4;
    B(k+3,2) = Braw(i,2)+Braw(i,8)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,end+1) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"03_Preprocessed.csv");

%% 04 Croatia

Araw = readmatrix('04_Load.csv');
Braw = readmatrix('04_Renewable.csv');
Craw = readmatrix('04_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,8))-(Braw(i,2)+Braw(i,8)))/4;
    delta4 = ((Braw(i+1,4)+Braw(i+1,10))-(Braw(i,4)+Braw(i,10)))/4;
    B(k,1)   = Braw(i,2)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,4)+Braw(i,10);
    B(k+1,2) = Braw(i,4)+Braw(i,10)+1*delta4;
    B(k+2,2) = Braw(i,4)+Braw(i,10)+2*delta4;
    B(k+3,2) = Braw(i,4)+Braw(i,10)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,end+1) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"04_Preprocessed.csv");


%% 05 Czech Republic

Araw = readmatrix('05_Load.csv');
Braw = readmatrix('05_Renewable.csv');
Craw = readmatrix('05_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2))-(Braw(i,2)))/4;
    delta4 = ((Braw(i+1,3))-(Braw(i,3)))/4;
    B(k,1)   = Braw(i,2)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+1*delta3;
    B(k+2,1) = Braw(i,2)+2*delta3;
    B(k+3,1) = Braw(i,2)+3*delta3;
    B(k,2)   = Braw(i,3);
    B(k+1,2) = Braw(i,3)+1*delta4;
    B(k+2,2) = Braw(i,3)+2*delta4;
    B(k+3,2) = Braw(i,3)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,end+1) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);
datawrite(isnan(datawrite)) = 0;

% Write Data
writematrix(datawrite,"05_Preprocessed.csv");


%% 06 Denmark

Araw = readmatrix('06_Load.csv');
Braw = readmatrix('06_Renewable.csv');
Craw = readmatrix('06_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,5)+Braw(i+1,8))-(Braw(i,2)+Braw(i,5)+Braw(i,8)))/4;
    delta4 = ((Braw(i+1,2)+Braw(i+1,5)+Braw(i+1,8))-(Braw(i,2)+Braw(i,5)+Braw(i,8)))/4;
    B(k,1)   = Braw(i,2)+Braw(i,5)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,5)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,5)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,5)+Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,2)+Braw(i,5)+Braw(i,8);
    B(k+1,2) = Braw(i,2)+Braw(i,5)+Braw(i,8)+1*delta4;
    B(k+2,2) = Braw(i,2)+Braw(i,5)+Braw(i,8)+2*delta4;
    B(k+3,2) = Braw(i,2)+Braw(i,5)+Braw(i,8)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,end+1) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"06_Preprocessed.csv");

%% 07 Estonia

Araw = readmatrix('07_Load.csv');
Braw = readmatrix('07_Renewable.csv');
Craw = readmatrix('07_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,8))-(Braw(i,2)+Braw(i,8)))/4;
    delta4 = ((Braw(i+1,2)+Braw(i+1,8))-(Braw(i,2)+Braw(i,8)))/4;
    B(k,1)   = Braw(i,2)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,2)+Braw(i,8);
    B(k+1,2) = Braw(i,2)+Braw(i,8)+1*delta4;
    B(k+2,2) = Braw(i,2)+Braw(i,8)+2*delta4;
    B(k+3,2) = Braw(i,2)+Braw(i,8)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,end+1) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"07_Preprocessed.csv");


%% 08 Finland

Araw = readmatrix('08_Load.csv');
Braw = readmatrix('08_Renewable.csv');
Craw = readmatrix('08_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,8))-(Braw(i,2)+Braw(i,8)))/4;
    delta4 = ((Braw(i+1,4)+Braw(i+1,10))-(Braw(i,4)+Braw(i,10)))/4;
    B(k,1)   = Braw(i,2)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,4)+Braw(i,10);
    B(k+1,2) = Braw(i,4)+Braw(i,10)+1*delta4;
    B(k+2,2) = Braw(i,4)+Braw(i,10)+2*delta4;
    B(k+3,2) = Braw(i,4)+Braw(i,10)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,end+1) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"08_Preprocessed.csv");

%% 09 France 

% Read Raw Data
Araw = readmatrix('09_Load.csv');
Braw = readmatrix('09_Renewable.csv');
Craw = readmatrix('09_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,8))-(Braw(i,2)+Braw(i,8)))/4;
    delta4 = ((Braw(i+1,4)+Braw(i+1,10))-(Braw(i,4)+Braw(i,10)))/4;
    B(k,1)   = Braw(i,2)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,4)+Braw(i,10);
    B(k+1,2) = Braw(i,4)+Braw(i,10)+1*delta4;
    B(k+2,2) = Braw(i,4)+Braw(i,10)+2*delta4;
    B(k+3,2) = Braw(i,4)+Braw(i,10)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,end+1) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"09_Preprocessed.csv");


%% 10 Germany

% Read Raw Data
A = readmatrix('10_Load.csv');
B = readmatrix('10_Renewable.csv');
Craw = readmatrix('10_Capacity.csv');

% Build Aggregated Matrix
% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,2) A(1:96*11,3) B(1:96*11,2)+B(1:96*11,5)+B(1:96*11,8) B(1:96*11,3)+B(1:96*11,6)+B(1:96*11,9)];
% datawrite(1,end+1) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"10_Preprocessed.csv");

%% 11 Greece

% Read Raw Data
Araw = readmatrix('11_Load.csv');
Braw = readmatrix('11_Renewable.csv');
Craw = readmatrix('11_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,8))-(Braw(i,2)+Braw(i,8)))/4;
    delta4 = ((Braw(i+1,3)+Braw(i+1,9))-(Braw(i,3)+Braw(i,9)))/4;
    B(k,1)   = Braw(i,2)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,3)+Braw(i,9);
    B(k+1,2) = Braw(i,3)+Braw(i,9)+1*delta4;
    B(k+2,2) = Braw(i,3)+Braw(i,9)+2*delta4;
    B(k+3,2) = Braw(i,3)+Braw(i,9)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,end+1) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"11_Preprocessed.csv");

%% 12 Hungary

% Read Raw Data
A = readmatrix('12_Load.csv');
B = readmatrix('12_Renewable.csv');
C = readmatrix('12_Capacity.csv');

% Build Aggregated Matrix
% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,2) A(1:96*11,3) B(1:96*11,2)+B(1:96*11,8) B(1:96*11,4)+B(1:96*11,10)];
% datawrite(1,end+1) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"12_Preprocessed.csv");


%% 13 Ireland

% Read Raw Data
Araw = readmatrix('13_Load.csv');
Braw = readmatrix('13_Renewable.csv');
Craw = readmatrix('13_Capacity.csv');

% Build Aggregated Matrix
k = 1;
j = 1;
for i=1:96*11/2
    delta1 = (Araw(i+1,2)-Araw(i,2))/2;
    delta2 = (Araw(i+1,3)-Araw(i,3))/2;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    
    k = k + 2;
end

k = 1;
for i=1:96*11/4
    
    delta3 = ((Braw(i+1,8))-(Braw(i,8)))/4;
    delta4 = ((Braw(i+1,8))-(Braw(i,8)))/4;
    B(k,1)   = Braw(i,8);
    B(k+1,1) = Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,8);
    B(k+1,2) = Braw(i,8)+1*delta4;
    B(k+2,2) = Braw(i,8)+2*delta4;
    B(k+3,2) = Braw(i,8)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,end+1) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"13_Preprocessed.csv");


%% 14 Italy

% Read Raw Data
Araw = readmatrix('14_Load.csv');
Braw = readmatrix('14_Renewable.csv');
Craw = readmatrix('14_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,8))-(Braw(i,2)+Braw(i,8)))/4;
    delta4 = ((Braw(i+1,4)+Braw(i+1,9))-(Braw(i,4)+Braw(i,9)))/4;
    B(k,1)   = Braw(i,2)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,4)+Braw(i,9);
    B(k+1,2) = Braw(i,4)+Braw(i,9)+1*delta4;
    B(k+2,2) = Braw(i,4)+Braw(i,9)+2*delta4;
    B(k+3,2) = Braw(i,4)+Braw(i,9)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,5) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"14_Preprocessed.csv");


%% 15 Latvia 

% Read Raw Data
Araw = readmatrix('15_Load.csv');
Braw = readmatrix('15_Renewable.csv');
Craw = readmatrix('15_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,8))-(Braw(i,8)))/4;
    delta4 = ((Braw(i+1,10))-(Braw(i,10)))/4;
    B(k,1)   = Braw(i,8);
    B(k+1,1) = Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,10);
    B(k+1,2) = Braw(i,10)+1*delta4;
    B(k+2,2) = Braw(i,10)+2*delta4;
    B(k+3,2) = Braw(i,10)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,end+1) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"15_Preprocessed.csv");


%% 16 Lithuania

% Read Raw Data
Araw = readmatrix('16_Load.csv');
Braw = readmatrix('16_Renewable.csv');
Craw = readmatrix('16_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,8))-(Braw(i,2)+Braw(i,8)))/4;
    delta4 = ((Braw(i+1,4)+Braw(i+1,10))-(Braw(i,4)+Braw(i,10)))/4;
    B(k,1)   = Braw(i,2)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,4)+Braw(i,10);
    B(k+1,2) = Braw(i,4)+Braw(i,10)+1*delta4;
    B(k+2,2) = Braw(i,4)+Braw(i,10)+2*delta4;
    B(k+3,2) = Braw(i,4)+Braw(i,10)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,5) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"16_Preprocessed.csv");


%% 17 Luxemburg (No Renewable)


% Read Raw Data
A = readmatrix('17_Load.csv');
Craw = readmatrix('17_Capacity.csv');

% Build Aggregated Matrix
% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,2) A(1:96*11,3) zeros(96*11,2)];
% datawrite(1,5) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

writematrix(datawrite,"17_Preprocessed.csv");

%% 18 Netherlands

% Read Raw Data
A = readmatrix('18_Load.csv');
B = readmatrix('18_Renewable.csv');
Craw = readmatrix('18_Capacity.csv');

% Build Aggregated Matrix
% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,2) A(1:96*11,3) B(1:96*11,2)+B(1:96*11,5)+B(1:96*11,8) B(1:96*11,3)+B(1:96*11,6)+B(1:96*11,9)];
% datawrite(1,5) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"18_Preprocessed.csv");

%% 19 Norway 

% Read Raw Data
Araw = readmatrix('19_Load.csv');
Braw = readmatrix('19_Renewable.csv');
Craw = readmatrix('19_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,8))-(Braw(i,2)+Braw(i,8)))/4;
    delta4 = delta3;
    B(k,1)   = Braw(i,2)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,8)+3*delta3;
    B(k,2)   = B(k,1);
    B(k+1,2) = B(k+1,1);
    B(k+2,2) = B(k+2,1);
    B(k+3,2) = B(k+3,1);
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,5) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"19_Preprocessed.csv");

%% 20 Poland


% Read Raw Data
Araw = readmatrix('20_Load.csv');
Braw = readmatrix('20_Renewable.csv');
Craw = readmatrix('20_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,8))-(Braw(i,2)+Braw(i,8)))/4;
    delta4 = ((Braw(i+1,4)+Braw(i+1,10))-(Braw(i,4)+Braw(i,10)))/4;
    B(k,1)   = Braw(i,2)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,4)+Braw(i,10);
    B(k+1,2) = Braw(i,4)+Braw(i,10)+1*delta4;
    B(k+2,2) = Braw(i,4)+Braw(i,10)+2*delta4;
    B(k+3,2) = Braw(i,4)+Braw(i,10)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,5) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"20_Preprocessed.csv");

%% 21 Portugal


% Read Raw Data
Araw = readmatrix('21_Load.csv');
Braw = readmatrix('21_Renewable.csv');
Craw = readmatrix('21_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,5)+Braw(i+1,8))-(Braw(i,2)+Braw(i,5)+Braw(i,8)))/4;
    delta4 = ((Braw(i+1,4)+Braw(i+1,7)+Braw(i+1,10))-(Braw(i,4)+Braw(i,7)+Braw(i,10)))/4;
    B(k,1)   = Braw(i,2)+Braw(i,5)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,5)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,5)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,5)+Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,4)+Braw(i,7)+Braw(i,10);
    B(k+1,2) = Braw(i,4)+Braw(i,7)+Braw(i,10)+1*delta4;
    B(k+2,2) = Braw(i,4)+Braw(i,7)+Braw(i,10)+2*delta4;
    B(k+3,2) = Braw(i,4)+Braw(i,7)+Braw(i,10)+3*delta4;
    
    k = k + 4;
end


% Build Aggregated Matrix
% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,end+1) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"21_Preprocessed.csv");

%% 22 Romania

% Read Raw Data
A = readmatrix('22_Load.csv');
B = readmatrix('22_Renewable.csv');
Craw = readmatrix('22_Capacity.csv');

% Build Aggregated Matrix
% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,2) A(1:96*11,3) B(1:96*11,2)+B(1:96*11,8) B(1:96*11,4)+B(1:96*11,10)];
% datawrite(1,end+1) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"22_Preprocessed.csv");

%% 23 Slovakia

% Read Raw Data
Araw = readmatrix('23_Load.csv');
Braw = readmatrix('23_Renewable.csv');
Craw = readmatrix('23_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,8))-(Braw(i,2)+Braw(i,8)))/4;
    delta4 = ((Braw(i+1,3)+Braw(i+1,9))-(Braw(i,3)+Braw(i,9)))/4;
    B(k,1)   = Braw(i,2)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,3)+Braw(i,9);
    B(k+1,2) = Braw(i,3)+Braw(i,9)+1*delta4;
    B(k+2,2) = Braw(i,3)+Braw(i,9)+2*delta4;
    B(k+3,2) = Braw(i,3)+Braw(i,9)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,5) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"23_Preprocessed.csv");


%% 24 Slovenia


% Read Raw Data
Araw = readmatrix('24_Load.csv');
Braw = readmatrix('24_Renewable.csv');
Craw = readmatrix('24_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2))-(Braw(i,2)))/4;
    delta4 = ((Braw(i+1,4))-(Braw(i,4)))/4;
    B(k,1)   = Braw(i,2);
    B(k+1,1) = Braw(i,2)+1*delta3;
    B(k+2,1) = Braw(i,2)+2*delta3;
    B(k+3,1) = Braw(i,2)+3*delta3;
    B(k,2)   = Braw(i,4);
    B(k+1,2) = Braw(i,4)+1*delta4;
    B(k+2,2) = Braw(i,4)+2*delta4;
    B(k+3,2) = Braw(i,4)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,5) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"24_Preprocessed.csv");

%% 25 Spain

% Read Raw Data
Araw = readmatrix('25_Load.csv');
Braw = readmatrix('25_Renewable.csv');
Craw = readmatrix('25_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,8))-(Braw(i,2)+Braw(i,8)))/4;
    delta4 = ((Braw(i+1,4)+Braw(i+1,10))-(Braw(i,4)+Braw(i,10)))/4;
    B(k,1)   = Braw(i,2)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,4)+Braw(i,10);
    B(k+1,2) = Braw(i,4)+Braw(i,10)+1*delta4;
    B(k+2,2) = Braw(i,4)+Braw(i,10)+2*delta4;
    B(k+3,2) = Braw(i,4)+Braw(i,10)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,5) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"25_Preprocessed.csv");

%% 26 Sweden

% Read Raw Data
Araw = readmatrix('26_Load.csv');
Braw = readmatrix('26_Renewable.csv');
Craw = readmatrix('26_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,8))-(Braw(i,2)+Braw(i,8)))/4;
    delta4 = ((Braw(i+1,4)+Braw(i+1,10))-(Braw(i,4)+Braw(i,10)))/4;
    B(k,1)   = Braw(i,2)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,8)+3*delta3;
    B(k,2)   = Braw(i,4)+Braw(i,10);
    B(k+1,2) = Braw(i,4)+Braw(i,10)+1*delta4;
    B(k+2,2) = Braw(i,4)+Braw(i,10)+2*delta4;
    B(k+3,2) = Braw(i,4)+Braw(i,10)+3*delta4;
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,5) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"26_Preprocessed.csv");

%% 27 Switzerland

% Read Raw Data
Araw = readmatrix('27_Load.csv');
Braw = readmatrix('27_Renewable.csv');
Craw = readmatrix('27_Capacity.csv');

% Build Aggregated Matrix
k = 1;
for i=1:96*11/4
    delta1 = (Araw(i+1,2)-Araw(i,2))/4;
    delta2 = (Araw(i+1,3)-Araw(i,3))/4;
    A(k,1)   = Araw(i,2);
    A(k+1,1) = Araw(i,2)+1*delta1;
    A(k+2,1) = Araw(i,2)+2*delta1;
    A(k+3,1) = Araw(i,2)+3*delta1;
    A(k,2)   = Araw(i,3);
    A(k+1,2) = Araw(i,3)+1*delta2;
    A(k+2,2) = Araw(i,3)+2*delta2;
    A(k+3,2) = Araw(i,3)+3*delta2;
    
    delta3 = ((Braw(i+1,2)+Braw(i+1,8))-(Braw(i,2)+Braw(i,8)))/4;
    delta4 = delta3;
    B(k,1)   = Braw(i,2)+Braw(i,8);
    B(k+1,1) = Braw(i,2)+Braw(i,8)+1*delta3;
    B(k+2,1) = Braw(i,2)+Braw(i,8)+2*delta3;
    B(k+3,1) = Braw(i,2)+Braw(i,8)+3*delta3;
    B(k,2)   = B(k,1);
    B(k+1,2) = B(k+1,1);
    B(k+2,2) = B(k+1,1);
    B(k+3,2) = B(k+1,1);
    
    k = k + 4;
end

% Load Forecast | Actual Load | Renewable Forecast | Actual Renewable 
datawrite = [A(1:96*11,1) A(1:96*11,2) B(1:96*11,1) B(1:96*11,2)];
% datawrite(1,5) = sum(Craw(1:11,2))+Craw(14,2)+Craw(15,2);

% Write Data
writematrix(datawrite,"27_Preprocessed.csv");
