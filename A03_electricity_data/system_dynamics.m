function [A, B, D, Area_Matrices] = system_dynamics(Parameters)


%% Definition of the state dynamics

DT = Parameters{2};
Na = Parameters{7};

Adj = Parameters{21};
Adj_W = Parameters{22};

KLine = Parameters{27};

Kp = Parameters{10};
Tp = Parameters{11};
nc = Parameters{12};
nd = Parameters{13};



A = zeros(5*Na);
B = zeros(5*Na,3*Na);
D = zeros(5*Na,2*Na);

Area_Matrices = cell(Na,1);


for i = 1:Na
    
    Kii = 0;

    for k = 1:Na
        if Adj(i,k) == 1 
            Kii = Kii + ((DT*Kp(i))/Tp(i))*(KLine/Adj_W(i,k));
        end
    end

    Ai = [1    DT*2*pi          0    0   0;
          -Kii (1 - (DT/Tp(i))) 0    0   0;
          0    0                1    0   0;
          0    0                0    1   0;
          -Kii 0                0    0   1];

    Bi = [0 0 0; (DT*Kp(i))/Tp(i) -(DT*Kp(i))/Tp(i) (DT*Kp(i))/Tp(i); 0 DT*nc(i) -DT*nd(i); DT 0 0; 0 0 0];

    Di = [0 0;
          -(DT*Kp(i))/Tp(i) (DT*Kp(i))/Tp(i);
          0 0;
          0 0;
          0 0];    
        
    A((i-1)*5+1:i*5,(i-1)*5+1:i*5) = Ai;
    B((i-1)*5+1:i*5,(i-1)*3+1:i*3) = Bi;
    D((i-1)*5+1:i*5,(i-1)*2+1:i*2) = Di;
    
    for k = 1:Na
        if Adj(i,k) == 1 
            A((i-1)*5+2,(k-1)*5+1) = ((DT*Kp(i))/Tp(i))*(KLine/Adj_W(i,k));
            A((i-1)*5+5,(k-1)*5+1) = ((DT*Kp(i))/Tp(i))*(KLine/Adj_W(i,k));
        end
    end

    Area_Matrices{i} = {A((i-1)*5+1:i*5,:),B((i-1)*5+1:i*5,(i-1)*3+1:i*3),D((i-1)*5+1:i*5,(i-1)*2+1:i*2)};

end



end
