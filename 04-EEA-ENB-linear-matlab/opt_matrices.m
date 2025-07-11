function [Atm, Btm, Fc, Hc, Hn, d, ed, Qd, Rd, Dd, Ed, Dc] = opt_matrices(Parameters)
%% Parameters
    ControlSequenceDivision = Parameters{29};
    Nu = size(ControlSequenceDivision,1);
    DT = Parameters{2};
    Na = Parameters{7};
    Np = Parameters{8};
    Kp = Parameters{10};
    Tp = Parameters{11};
    nc = Parameters{12};
    nd = Parameters{13};
    A = Parameters{21};
    AW = Parameters{22};
    KLine = Parameters{27};
    % N = Parameters{9};
    PowerAngleLimit = Parameters{5};
    FrequencyLimit = Parameters{6};
    CountryCodes = Parameters{1};
    CapacitiesData = Parameters{26};
    BatteryCapacityScaling = Parameters{15};
    ub = Parameters{24};
    ESS_cap = ub*BatteryCapacityScaling;
    
    Ac = Parameters{16};
    Bc = Parameters{17};
    % Ec = Parameters{18};

%% Preallocation
    Atm = zeros(5*Na);
    Btm = zeros(5*Na,3*Na);
    Dtm = zeros(5*Na,2*Na);

    Fc = zeros(5*Na*Np,5*Na);
    Hn = zeros(5*Na,3*Na*Np); 

    
    Qd = zeros(5*Na*Np); 
    Rd = zeros(3*Na*Nu);
     
    Dd = [];
    d = []; 
    
    Ed = zeros(8*Na*Np,5*Na*Np);
    ed = zeros(8*Na*Np,1);

%% COmputation of the optimization matrices

    m = 1;
    for i = 1:Na

        Ai = [1 DT*2*pi          0 0 0;
              0 (1 - (DT/Tp(i))) 0 0 0;
              0 0                1 0 0;
              0 0                0 1 0;
              0 0                0 0 1];
         
        Atm((i-1)*5+1:i*5,(i-1)*5+1:i*5) = Ai;  

        Bi = [0 0 0 ; (DT*Kp(i))/Tp(i) -(DT*Kp(i))/Tp(i) (DT*Kp(i))/Tp(i); 0 DT*nc(i) -DT*nd(i); DT 0 0; 0 0 0];
        Di = [0 0;
              -(DT*Kp(i))/Tp(i) (DT*Kp(i))/Tp(i);
              0 0 ;
              0 0 ;
              0 0];    
        

        Btm((i-1)*5+1:i*5,(i-1)*3+1:i*3) = Bi;
        Dtm((i-1)*5+1:i*5,(i-1)*2+1:i*2) = Di; 

        Ei = [-1/PowerAngleLimit   0                  0                0                                         0;
               1/PowerAngleLimit   0                  0                0                                         0;
               0                  -1/FrequencyLimit   0                0                                         0;
               0                   1/FrequencyLimit   0                0                                         0;
               0                   0                 -1                0                                         0;
               0                   0                  1/(ESS_cap(1,m)) 0                                         0;
               0                   0                  0               -1                                         0;
               0                   0                  0                1/(CapacitiesData(CountryCodes(i))/1000)  0];
        
        ei = [1;
              1
              1;
              1;
              0;
              1;
              0;
              1];
        
        Ek((i-1)*8+1:i*8,(i-1)*5+1:i*5) = Ei;
        ek((i-1)*8+1:i*8,1) = ei;

        m = m + 2;
    end 

    for i = 1:Np
        Qd((i-1)*5*Na+1:i*5*Na,(i-1)*5*Na+1:i*5*Na) = Ac;
       
        Ed((i-1)*8*Na+1:i*8*Na,(i-1)*5*Na+1:i*5*Na) = Ek;
        ed((i-1)*8*Na+1:i*8*Na,1) = ek;
    end

    for i = 1:Nu
        Rd((i-1)*3*Na+1:i*3*Na,(i-1)*3*Na+1:i*3*Na) = Bc;
    end

    k = 1;

    for i = 2:5:5*Na
        m = 1;
        Kii = 0;
        for j = 1:5:5*Na
            if A(k,m) == 1
                Atm(i,j) = -(DT*Kp(k))/Tp(k)*(KLine/(AW(k,m)));
                Atm(i+3,j) = DT*(KLine/(AW(k,m)));
                Kii = Kii + (KLine/(AW(k,m)));
            end
            m = m + 1;
        end
        Atm(i,i) = Atm(i,i) + (DT*Kp(k))/Tp(k)*Kii;
        Atm(i+3,i) = Atm(i+3,i) - DT*Kii;
        k = k + 1;
    end


    Dc = zeros(5*Na*Np,2*Na*Np);

    for i = 1:Np
        Fc((i-1)*5*Na+1:i*5*Na,:) = Atm^(i);     
        for j = 1:Np
            if i-j >= 0
                HcRaw((i-1)*5*Na+1:i*5*Na,(j-1)*3*Na+1:j*3*Na) = Atm^(i-j)*Btm;
                Dc((i-1)*5*Na+1:i*5*Na,(j-1)*2*Na+1:j*2*Na) = Atm^(i-j)*Dtm;
            end
        end
    end

    Hc = zeros(5*Na*Np,3*Na*Nu); 

    for i = 1:Np   
        idx = 1;
        for j = 1:Nu
            PartialMatrix = zeros(5*Na,3*Na);
            for k = idx:idx+ControlSequenceDivision(j)-1 
                PartialMatrix = PartialMatrix + HcRaw((i-1)*5*Na+1:i*5*Na,(k-1)*3*Na+1:k*3*Na);                
            end
            idx = idx + ControlSequenceDivision(j);
            Hc((i-1)*5*Na+1:i*5*Na,(j-1)*3*Na+1:j*3*Na) = PartialMatrix;
        end
        
    end

    for j = 1:Np+1
        Hn(:,(j-1)*3*Na+1:j*3*Na) = Atm^(Np-j+1)*Btm;
    end


end