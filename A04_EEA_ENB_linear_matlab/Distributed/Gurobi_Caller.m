function result = Gurobi_Caller(H_QP,f_QP,A_QP,b_QP,lb,ub)

model.Q = sparse(H_QP); 
model.obj = f_QP';
model.A = sparse(A_QP);
model.rhs = b_QP;
model.sense = '<';
model.lb = lb;
model.ub = ub;
model.modelsense = 'min';
model.vtype = 'C';

gurobi_write(model, 'QP_MPC.lp');

params.outputflag = 0;
% params.method = 2;
params.method = 0;
params.OptimalityTol = 1e-9;

result = gurobi(model, params);


end