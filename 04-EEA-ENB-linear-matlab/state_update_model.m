
%% State Update 
function [x_plus, Pedge, PedgeTotal] = state_update_model(x_h, u_h, w_h, Parameters)
    
%% Parameters
    DT = Parameters{2};
    Na = Parameters{7};
    Kp = Parameters{10};
    Tp = Parameters{11};
    nc = Parameters{12};
    nd = Parameters{13};
    A = Parameters{21};
    AW = Parameters{22};
    KLine = Parameters{27};
    % DAvg = Parameters{28};

%% Vectors preallocation
    x_plus = zeros(5*Na,1);
    Pedge = zeros(Na,Na);
    PedgeTotal = zeros(Na,1);
    Pdisp = zeros(Na,1);
    PESS_c = zeros(Na,1);
    PESS_d = zeros(Na,1);
    Pren = zeros(Na,1);
    Pload = zeros(Na,1);

%%    Vectors redefinition 

% Input separation in dipatchable sources and batteries power
% Disturbance separation in renewable sources and loads
    j = 1;
    k = 1;
    for i = 1:Na
        % Inputs
        Pdisp(i) = u_h(k,1);
        PESS_c(i) = u_h(k+1,1);
        PESS_d(i) = u_h(k+2,1);
        k=k+3;
        % Disturbances
        Pren(i) = w_h(j+1,1);
        Pload(i) = w_h(j,1);
        j=j+2;
    end


%% Areas Interactions
 
    m = 2;    
    for i = 1:Na    
        for j = 1:Na
            if A(i,j) == 1
                Pedge(i,j) = (KLine/(AW(i,j)))*(x_h(5*(j-1)+1,1)-x_h(5*(i-1)+1,1));
            else
                Pedge(i,j) = 0;
            end
            PedgeTotal(i) = PedgeTotal(i) + Pedge(i,j);
        end
        m = m + 2;
    end

%% State Dynamics Equations
    j = 1;
    m = 2;       
  
    for i = 1:Na
        x_j = [x_h(j,1);x_h(j+1,1);x_h(j+2,1);x_h(j+3,1);x_h(j+4,1)];
        u_j = [Pdisp(i);PESS_c(i);PESS_d(i)];
        w_j = [Pload(i);Pren(i);PedgeTotal(i)];
        
        
        Ai = [1 DT*2*pi          0 0 0;
              0 (1 - (DT/Tp(i))) 0 0 0;
              0 0                1 0 0;
              0 0                0 1 0;
              0 0                0 0 1];
          
        Wi = [0 0 0; 
              -(DT*Kp(i))/Tp(i) (DT*Kp(i))/Tp(i) -(DT*Kp(i))/Tp(i); 
              0 0 0;
              0 0 0;
              0 0 DT];

        Bi = [0 0 0 ; (DT*Kp(i))/Tp(i) -(DT*Kp(i))/Tp(i) (DT*Kp(i))/Tp(i); 0 DT*nc(i) -DT*nd(i); DT 0 0; 0 0 0];
                
    % Update Equation
        xplus_j = Ai*x_j + Bi*u_j + Wi*w_j;

        x_plus(j,1) = xplus_j(1,1);
        x_plus(j+1,1) = xplus_j(2,1);
        x_plus(j+2,1) = xplus_j(3,1);
        x_plus(j+3,1) = xplus_j(4,1);
        x_plus(j+4,1) = xplus_j(5,1);

        j = j+5;
        m = m+2;       
    end    
    
end