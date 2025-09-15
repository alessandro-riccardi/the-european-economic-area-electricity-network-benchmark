function [Atm, Btm, Fc, Hc, Hn, d, ed, Qd, Rd, Dd, Ed, Dc] = opt_matrices_DMPC(Parameters, control_agents_indexes_DMPC)
%% Parameters
    ControlSequenceDivision = Parameters{29};
    Nu = size(ControlSequenceDivision,1);
    DT = Parameters{2};
    
    Na = size(control_agents_indexes_DMPC, 2);
    Np = Parameters{8};
    Kp = Parameters{10};
    Tp = Parameters{11};
    nc = Parameters{12};
    nd = Parameters{13};
    A = Parameters{21};
    AW = Parameters{22};
    KLine = Parameters{27};
    
    PowerAngleLimit = Parameters{5};
    FrequencyLimit = Parameters{6};
    BatteryCapacityScaling = Parameters{15};
    ub = Parameters{24};
    ESS_cap = ub*BatteryCapacityScaling;
    

    Ac = zeros(3*Na);
    Bc = zeros(3*Na);

    for i = 1:Na
        Ac(3*(i-1)+1:3*(i-1)+3,3*(i-1)+1:3*(i-1)+3) = [100 0 0; 0 10 0; 0 0 1];
        Bc(3*(i-1)+1:3*(i-1)+3,3*(i-1)+1:3*(i-1)+3) = [1 0 0; 0 1 0; 0 0 1];
    end

%% Preallocation
    Atm = zeros(3*Na);
    Btm = zeros(3*Na,3*Na);
    Dtm = zeros(3*Na,2*Na);

    Fc = zeros(3*Na*Np,3*Na);
    Hn = zeros(3*Na,3*Na*Np); 

    
    Qd = zeros(3*Na*Np); 
    Rd = zeros(3*Na*Nu);
     
    Dd = [];
    d = []; 
    
    Ed = zeros(6*Na*Np,3*Na*Np);
    ed = zeros(6*Na*Np,1);

%% Computation of the optimization matrices

    
    for i = 1:Na
        
        agent_index = control_agents_indexes_DMPC(i);

        Ai = [1 DT*2*pi          0 ;
              0 (1 - (DT/Tp(agent_index))) 0 ;
              0 0                1];
         
        Atm((i-1)*3+1:i*3,(i-1)*3+1:i*3) = Ai;  

        Bi = [0 0 0 ; (DT*Kp(agent_index))/Tp(agent_index) -(DT*Kp(agent_index))/Tp(agent_index) (DT*Kp(agent_index))/Tp(agent_index); 0 DT*nc(agent_index) -DT*nd(agent_index)];
        Di = [0 0;
              -(DT*Kp(agent_index))/Tp(agent_index) (DT*Kp(agent_index))/Tp(agent_index);
              0 0];    
        

        Btm((i-1)*3+1:i*3,(i-1)*3+1:i*3) = Bi;
        Dtm((i-1)*3+1:i*3,(i-1)*2+1:i*2) = Di; 
        
        m = (agent_index-1)*3+1;

        Ei = [-1/PowerAngleLimit   0                  0;
               1/PowerAngleLimit   0                  0;
               0                  -1/FrequencyLimit   0;
               0                   1/FrequencyLimit   0;
               0                   0                 -1;
               0                   0                  1/(ESS_cap(1,m))];
        
        ei = [1;
              1
              1;
              1;
              0;
              1];
        
        Ek((i-1)*6+1:i*6,(i-1)*3+1:i*3) = Ei;
        ek((i-1)*6+1:i*6,1) = ei;

    end 

    for i = 1:Np
        Qd((i-1)*3*Na+1:i*3*Na,(i-1)*3*Na+1:i*3*Na) = Ac;
       
        Ed((i-1)*6*Na+1:i*6*Na,(i-1)*3*Na+1:i*3*Na) = Ek;
        ed((i-1)*6*Na+1:i*6*Na,1) = ek;
    end

    for i = 1:Nu
        Rd((i-1)*3*Na+1:i*3*Na,(i-1)*3*Na+1:i*3*Na) = Bc;
    end

    k = 1;

    for i = 2:3:3*Na
        m = 1;
        Kii = 0;
        for j = 1:3:3*Na
            agent_index1 = control_agents_indexes_DMPC(k);
            agent_index2 = control_agents_indexes_DMPC(m);
            if A(agent_index1,agent_index2) == 1
                Atm(i,j) = -(DT*Kp(agent_index1))/Tp(agent_index1)*(KLine/(AW(agent_index1,agent_index2)));
                Kii = Kii + (KLine/(AW(agent_index1,agent_index2)));
            end
            m = m + 1;
        end
        Atm(i,i) = Atm(i,i) + (DT*Kp(agent_index1))/Tp(agent_index1)*Kii;
        k = k + 1;
    end


    Dc = zeros(3*Na*Np,2*Na*Np);

    for i = 1:Np
        Fc((i-1)*3*Na+1:i*3*Na,:) = Atm^(i);     
        for j = 1:Np
            if i-j >= 0
                HcRaw((i-1)*3*Na+1:i*3*Na,(j-1)*3*Na+1:j*3*Na) = Atm^(i-j)*Btm;
                Dc((i-1)*3*Na+1:i*3*Na,(j-1)*2*Na+1:j*2*Na) = Atm^(i-j)*Dtm;
            end
        end
    end

    Hc = zeros(3*Na*Np,3*Na*Nu); 

    for i = 1:Np   
        idx = 1;
        for j = 1:Nu
            PartialMatrix = zeros(3*Na,3*Na);
            for k = idx:idx+ControlSequenceDivision(j)-1 
                PartialMatrix = PartialMatrix + HcRaw((i-1)*3*Na+1:i*3*Na,(k-1)*3*Na+1:k*3*Na);                
            end
            idx = idx + ControlSequenceDivision(j);
            Hc((i-1)*3*Na+1:i*3*Na,(j-1)*3*Na+1:j*3*Na) = PartialMatrix;
        end
        
    end

    for j = 1:Np+1
        Hn(:,(j-1)*3*Na+1:j*3*Na) = Atm^(Np-j+1)*Btm;
    end


end