function plot_results(simID, export_output_plot, x, u, w, PedgeTieLine, JVect, Parameters)
%% Parameters
    
    CountryCodes = Parameters{1};
    IterationSegments = Parameters{4};
    Na = Parameters{7};
    N = Parameters{9};
    CISO_Import = Parameters{25};
    

%% Color Map

    plotColors = jet(Na);
    
    
%% Power angle deviation from nominal value (x1)

    f1 = figure('visible','on');
    f1.Position = [100 100 1380 820];
    xlim([0 N])
    ylim([1.05*min(min(x(1:3:end,1:end))) 1.05*max(max(x(1:3:end,1:end)))])
    grid on
    hold on
        for i = 1:Na
            stairs(0:N,x(3*(i-1)+1,1:end),'-','LineWidth',1.5,'Color', plotColors(i,:))
        end
    tit = title('$x_1 = \Delta \delta(k)$ -- Power Angle Deviation','Interpreter','latex');
        
    labels = [];
    for i = 1:Na
        if CountryCodes(i) < 10
            labels = [labels; '0', num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
        else
            labels = [labels; num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
        end
    end
    xlab = xlabel('Hours','Interpreter','latex');
    ylab = ylabel('Deg','Interpreter','latex');
    xticks(0:IterationSegments:N);
    xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
    ax = gca;
    ax.YAxis.Exponent = 0;
    % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
    
    set(f1.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    
    tit.FontSize = 20*2;
    xlab.FontSize = 18*2;
    ylab.FontSize = 18*2;
    leg.FontSize = 14*2;
    f1.CurrentAxes.Box = 'on';

    hold off

    
%% Frequency deviation from nominal value (x2)

    f2 = figure('visible','on');
    f2.Position = [100 100 1380 820];
    xlim([0 N])
    ylim([1.05*min(min(x(2:3:end,1:end))) 1.05*max(max(x(2:3:end,1:end)))])
    grid on
    hold on
        for i = 1:Na
            stairs(0:N,x(3*(i-1)+2,1:end),'-','LineWidth',1.5, 'Color', plotColors(i,:))
        end
    tit = title('$x_2 = \Delta f(k)$ -- Frequency Deviation','Interpreter','latex');
    labels = [];
    for i = 1:Na
        if CountryCodes(i) < 10
            labels = [labels; '0', num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
        else
            labels = [labels; num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
        end
    end
    xlab = xlabel('Hour','Interpreter','latex');
    ylab = ylabel('Hz','Interpreter','latex');
    xticks(0:IterationSegments:N);
    xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
    ax = gca;
    ax.YAxis.Exponent = 0;
    % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
    
    set(f2.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    
    tit.FontSize = 20*2;
    xlab.FontSize = 18*2;
    ylab.FontSize = 18*2;
    leg.FontSize = 14*2;
    f2.CurrentAxes.Box = 'on';
    hold off


%% Energy stored in the batteries (x3)

    f3 = figure('visible','on');
    f3.Position = [100 100 1380 820];
    xlim([0 N])
    ylim([1.05*min(min(x(3:3:end,1:end))) 1.05*max(max(x(3:3:end,1:end)/30))])
    grid on
    hold on
        for i = 1:Na
            stairs(0:N,x(3*(i-1)+3,1:end)/30, '-', 'LineWidth', 1.5, 'Color', plotColors(i,:))
        end

    tit = title('$x_3 = e(k)$ -- Energy Stored','Interpreter','latex');
    labels = [];
    for i = 1:Na
        if CountryCodes(i) < 10
            labels = [labels; '0', num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
        else
            labels = [labels; num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
        end
    end
    xlab = xlabel('Hours','Interpreter','latex');
    ylab = ylabel('GWh','Interpreter','latex');
    xticks(0:IterationSegments:N);
    xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
    ax = gca;
    ax.YAxis.Exponent = 0;
    % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
    
    set(f3.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    
    tit.FontSize = 20*2;
    xlab.FontSize = 18*2;
    ylab.FontSize = 18*2;
    leg.FontSize = 14*2;
    f3.CurrentAxes.Box = 'on';
    hold off

%% Dispatchable generation (x4)
    % 
    % f11 = figure('visible','on');
    % f11.Position = [100 100 1380 820];
    % xlim([0 N])
    % ylim([1.05*min(min(x(4:5:end,1:end))) 1.05*max(max(x(4:5:end,1:end)))])
    % grid on
    % hold on
    %     for i = 1:Na
    %         stairs(0:N,x(5*(i-1)+4,1:end), '-', 'LineWidth', 1.5, 'Color', plotColors(i,:))
    %     end
    % 
    % tit = title('$x_4 = P^{disp}(k)$ -- Dispatchable Generation','Interpreter','latex');
    % labels = [];
    % for i = 1:Na
    %     if CountryCodes(i) < 10
    %         labels = [labels; '0', num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
    %     else
    %         labels = [labels; num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
    %     end
    % end
    % xlab = xlabel('Hours','Interpreter','latex');
    % ylab = ylabel('GW','Interpreter','latex');
    % xticks(0:IterationSegments:N);
    % xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
    % ax = gca;
    % ax.YAxis.Exponent = 0;
    % % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
    % 
    % set(f11.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    % 
    % tit.FontSize = 20*2;
    % xlab.FontSize = 18*2;
    % ylab.FontSize = 18*2;
    % leg.FontSize = 14*2;
    % f11.CurrentAxes.Box = 'on';
    % hold off

%% Tie Lines TRasmission (x5)

    % f12 = figure('visible','on');
    % f12.Position = [100 100 1380 820];
    % xlim([0 N])
    % ylim([1.05*min(min(x(5:5:end,1:end))) 1.05*max(max(x(5:5:end,1:end)))])
    % grid on
    % hold on
    %     for i = 1:Na
    %         stairs(0:N,x(5*(i-1)+5,1:end), '-', 'LineWidth', 1.5, 'Color', plotColors(i,:))
    %     end
    % 
    % tit = title('$x_5 = P^{tie}(k)$ -- Tie Lines Trasmission','Interpreter','latex');
    % labels = [];
    % for i = 1:Na
    %     if CountryCodes(i) < 10
    %         labels = [labels; '0', num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
    %     else
    %         labels = [labels; num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
    %     end
    % end
    % xlab = xlabel('Hours','Interpreter','latex');
    % ylab = ylabel('GW','Interpreter','latex');
    % xticks(0:IterationSegments:N);
    % xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
    % ax = gca;
    % ax.YAxis.Exponent = 0;
    % % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
    % 
    % set(f12.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    % 
    % tit.FontSize = 20*2;
    % xlab.FontSize = 18*2;
    % ylab.FontSize = 18*2;
    % leg.FontSize = 14*2;
    % f12.CurrentAxes.Box = 'on';
    % hold off


%% Power Dispatchable Generation (u1)

    f4 = figure('visible','on');
    f4.Position = [100 100 1380 820];
    grid on
    hold on
    xlim([0 N])
    ylim([1.05*min(min(u(1:3:end,1:end))) 1.05*max(max(u(1:3:end,1:end)))])
    
    k = 1;
	for i = 1:3:3*Na
        stairs(0:N-1,u(i,1:end),'-','LineWidth',1.5, 'Color', plotColors(k,:))
        k = k + 1;
	end
   
    tit = title('$u_1 = \Delta P^{disp}(k)$ -- Dispatchable Generation Variation','Interpreter','latex');
    labels = [];
    for i = 1:Na
        if CountryCodes(i) < 10
            labels = [labels; '0', num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
        else
            labels = [labels; num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
        end
    end
    xlab = xlabel('Hours','Interpreter','latex');
    ylab = ylabel('GW','Interpreter','latex');
    xticks(0:IterationSegments:N);
    xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
    ax = gca;
    ax.YAxis.Exponent = 0;
    % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
    
    set(f4.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    
    tit.FontSize = 20*2;
    xlab.FontSize = 18*2;
    ylab.FontSize = 18*2;
    leg.FontSize = 14*2;
    f4.CurrentAxes.Box = 'on';
    hold off

    
%% Power Batteries Charging (u2)

    f5 = figure('visible','on');
    f5.Position = [100 100 1380 820];
    grid on
    hold on
    xlim([0 N])
    ylim([1.05*min(min(u(2:3:end,1:end))) 1.05*max(max(u(2:3:end,1:end)))])
    
    k = 1;
    for i = 1:3:3*Na
        stairs(0:N-1,u(i+1,1:end),'-','LineWidth',1.5, 'Color', plotColors(k,:))
        k = k + 1;
    end
    tit = title('$u_2 = P^{ESS,c}(k)$ -- Energy Storage Charging Power','Interpreter','latex');
    labels = [];
    for i = 1:Na
        if CountryCodes(i) < 10
            labels = [labels; '0', num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
        else
            labels = [labels; num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
        end
    end
    xlab = xlabel('Hours','Interpreter','latex');
    ylab = ylabel('GW','Interpreter','latex');
    xticks(0:IterationSegments:N);
    xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
    ax = gca;
    ax.YAxis.Exponent = 0;
    % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
    
    set(f5.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    
    tit.FontSize = 20*2;
    xlab.FontSize = 18*2;
    ylab.FontSize = 18*2;
    leg.FontSize = 14*2;
    f5.CurrentAxes.Box = 'on';
    hold off

%% Power Batteries Charging Discharging (u3)

    f13 = figure('visible','on');
    f13.Position = [100 100 1380 820];
    grid on
    hold on
    xlim([0 N])
    ylim([1.05*min(min(u(3:3:end,1:end))) 1.05*max(max(u(3:3:end,1:end)))])
    
    k = 1;
	for i = 1:3:3*Na
        stairs(0:N-1,u(i+2,1:end),'-','LineWidth',1.5, 'Color', plotColors(k,:))
        k = k + 1;
    end
    tit = title('$u_3 = P^{ESS, d}(k)$ -- Energy Storage Discharging Power','Interpreter','latex');
    labels = [];
    for i = 1:Na
        if CountryCodes(i) < 10
            labels = [labels; '0', num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
        else
            labels = [labels; num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
        end
    end
    xlab = xlabel('Hours','Interpreter','latex');
    ylab = ylabel('GW','Interpreter','latex');
    xticks(0:IterationSegments:N);
    xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
    ax = gca;
    ax.YAxis.Exponent = 0;
    % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
    
    set(f13.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    
    tit.FontSize = 20*2;
    xlab.FontSize = 18*2;
    ylab.FontSize = 18*2;
    leg.FontSize = 14*2;
    f13.CurrentAxes.Box = 'on';
    hold off

%% Load Curve (w_1)

    f6 = figure('visible','on');
    f6.Position = [100 100 1380 820];
    grid on
    hold on
    k = 1;
    xlim([0 N])
    ylim([1.05*min(min(w(1:2:end,1:end))) 1.05*max(max(w(1:2:end,1:end)))])
    
	for i = 1:2:2*Na
        % stairs(0:N-1,w(i,1:N)+w_zero(i,1),'-','LineWidth',1.5,'Color', plotColors(k,:))
        stairs(0:N-1,w(i,1:N),'-','LineWidth',1.5,'Color', plotColors(k,:))
        k = k + 1;
	end
        
    tit = title('$w_1 = \Delta P^{load}(k)$ -- Load Curve Variation','Interpreter','latex');
    
    labels = [];
    for i = 1:Na
        if CountryCodes(i) < 10
            labels = [labels; '0', num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
        else
            labels = [labels; num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
        end
    end
    xlab = xlabel('Hours','Interpreter','latex');
    ylab = ylabel('GW','Interpreter','latex');
    xticks(0:IterationSegments:N);
    xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
    ax = gca;
    ax.YAxis.Exponent = 0;
    % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
    
    set(f6.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize',  14*2)
    
    tit.FontSize = 20*2;
    xlab.FontSize = 18*2;
    ylab.FontSize = 18*2;
    leg.FontSize = 14*2;
    f6.CurrentAxes.Box = 'on';
    hold off
        
%% Renewable Generation (w_2)

    f7 = figure('visible','on');
    f7.Position = [100 100 1380 820];
    grid on
    hold on
    xlim([0 N])
    ylim([1.05*min(min(w(2:2:end,1:end))) 1.05*max(max(w(2:2:end,1:end)))])
    k = 1;
	for i = 1:2:2*Na 
        % stairs(0:N-1,w(i+1,1:N)+w_zero(i+1,1),'-','LineWidth',1.5,'Color', plotColors(k,:))
        stairs(0:N-1,w(i+1,1:N),'-','LineWidth',1.5,'Color', plotColors(k,:))
        k = k + 1;
	end
            
    tit = title('$w_2 = \Delta P^{tie}(k)$ -- Renewable Generation Variation','Interpreter','latex');
    
    labels = [];
    for i = 1:Na
        if CountryCodes(i) < 10
            labels = [labels; '0', num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
        else
            labels = [labels; num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
        end
    end
    xlab = xlabel('Hours','Interpreter','latex');
    ylab = ylabel('GW','Interpreter','latex');
    xticks(0:IterationSegments:N);
    xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
    ax = gca;
    ax.YAxis.Exponent = 0;
    % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
    
    set(f7.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize',  14*2)
    
    tit.FontSize = 20*2;
    xlab.FontSize = 18*2;
    ylab.FontSize = 18*2;
    leg.FontSize = 14*2;
    f7.CurrentAxes.Box = 'on';
    hold off
    %% Tie Lines Interaction
    %     f9 = figure('visible','on');
    % f9.Position = [100 100 1380 820];
    % xlim([0 N])
    % ylim([1.05*min(min(PedgeTieLine(1:end,1:end))) 1.05*max(max(PedgeTieLine(1:end,1:end)))])
    % grid on
    % hold on
    %     for i = 1:Na
    %         stairs(0:N-1,PedgeTieLine(i,1:end),'-','LineWidth',1.5,'Color', plotColors(i,:))
    %     end
    % tit = title('$w_3 = \Delta P^{tie}(k)$ -- Tie Lines Power Variation','Interpreter','latex');
    % 
    % labels = [];
    % for i = 1:Na
    %     if CountryCodes(i) < 10
    %         labels = [labels; '0', num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
    %     else
    %         labels = [labels; num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
    %     end
    % end
    % xlab = xlabel('Hours','Interpreter','latex');
    % ylab = ylabel('GW','Interpreter','latex');
    % xticks(0:IterationSegments:N);
    % xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
    % ax = gca;
    % ax.YAxis.Exponent = 0;
    % % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
    % 
    % set(f9.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    % 
    % tit.FontSize = 20*2;
    % xlab.FontSize = 18*2;
    % ylab.FontSize = 18*2;
    % leg.FontSize = 14*2;
    % f9.CurrentAxes.Box = 'on';
    % 
    % hold off

%% Electrical Topology
    % 
    % f8 = figure('visible','on');
    % f8.Position = [50 50 950 950];
    % hold on
    % axis equal    
    % tit = title('Electrical Topology','Interpreter','latex');
    % 
    % 
    % MaxInteraction = max(max(AW));
    % 
    % 
	% for i = 1:Na
    %     for j = 1:Na
    %         if AW(i,j) > 0
    %             X = [CentoidPos(i,1) CentoidPos(j,1)];
    %             Y = [CentoidPos(i,2) CentoidPos(j,2)];
                    % LWidths = 1.5*(Davg/AW(i,j))/(Davg/MaxInteraction);
    %                 line(X,Y,'LineWidth',LWidths)
    %         end
    %     end
	% end
    % 
    % for i = 1:Na
    %     centerX = CentoidPos(i,1);
    %     centerY = CentoidPos(i,2);
    %     radius = 0.85;
    %     fs=9;
    %     FaceColor = 'white';
    %     rectangle('Position',[centerX - radius, centerY - radius, radius*2, radius*2],'Curvature',[1,1],'FaceColor',FaceColor,'EdgeColor','b','LineWidth',1.5);
    %     if CountryCodes(i) < 10
    %         label = [CISO_Import(i,1:2), '$|$0' , num2str(CountryCodes(i))];
    %     else
    %         label = [CISO_Import(i,1:2), '$|$' , num2str(CountryCodes(i))];
    %     end
    %     text(centerX,centerY,label,'Color','black','FontSize',fs,'HorizontalAlignment','center','Interpreter','latex')
    % end
    % 
	% set(gca,'position',[0.03 0.025 0.93 0.925],'units','normalized')
    % f8.CurrentAxes.Box = 'on';
    % f8.CurrentAxes.XTick = [];
    % f8.CurrentAxes.YTick = [];
    % tit.FontSize = 20;
    % hold off
    
%% Cost Function
        f10 = figure('visible','on');
    f10.Position = [100 100 1380 820];
    xlim([0 N])
    ylim([0 1.05*max(abs(JVect(1,1:end)))])
    grid on
    hold on
    
    

%         for i = 1:Na
            stairs(0:N,abs(JVect(1,1:end)),'-','LineWidth',1.5)
%         end
    tit = title('Cost Function','Interpreter','latex');
        
%     labels = [];
%     for i = 1:Na
%         if CountryCodes(i) < 10
%             labels = [labels; '0', num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
%         else
%             labels = [labels; num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
%         end
%     end
    xlab = xlabel('Hours','Interpreter','latex');
    xticks(0:IterationSegments:N);
    xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
    ax = gca;
    ax.YAxis.Exponent = 0;
%     ylab = ylabel('GW','Interpreter','latex');
    
%     leg = legend(labels,'Location','eastoutside','Interpreter','latex');
    
    set(f10.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
    
    tit.FontSize = 20*2;
    xlab.FontSize = 18*2;
    ylab.FontSize = 18*2;
    leg.FontSize = 14*2;
    f10.CurrentAxes.Box = 'on';

    hold off

%% Plot Legend

    % 
    % f14 = figure('visible','on');
    % f14.Position = [100 100 1380 820];
    % xlim([0 N])
    % ylim([1.05*min(min(x(1:5:end,1:end))) 1.05*max(max(x(1:5:end,1:end)))])
    % grid on
    % hold on
    %     for i = 1:Na
    %         stairs(0:N,x(5*(i-1)+1,1:end),'-','LineWidth',1.5,'Color', plotColors(i,:))
    %     end
    % tit = title('PLOT LEGEND','Interpreter','latex');
    % 
    % labels = [];
    % for i = 1:Na
    %     if CountryCodes(i) < 10
    %         labels = [labels; '0', num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
    %     else
    %         labels = [labels; num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
    %     end
    % end
    % % xlab = xlabel('Hours','Interpreter','latex');
    % % ylab = ylabel('Deg','Interpreter','latex');
    % % xticks(0:30:N);
    % % xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
    % % ax = gca;
    % % ax.YAxis.Exponent = 0;
    % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
    % 
    % set(f14.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14)
    % 
    % tit.FontSize = 20;
    % xlab.FontSize = 18;
    % ylab.FontSize = 18;
    % leg.FontSize = 14;
    % f14.CurrentAxes.Box = 'on';
    % 
    % hold off

    


%% Export Procedure
    
    if export_output_plot == true
        exportgraphics(f1,['SimulationOutput/',simID,'_X1.pdf'],'Resolution',300)
        exportgraphics(f2,['SimulationOutput/',simID,'_X2.pdf'],'Resolution',300)
        exportgraphics(f3,['SimulationOutput/',simID,'_X3.pdf'],'Resolution',300)
        % exportgraphics(f11,['SimulationOutput/',simID,'_X4.pdf'],'Resolution',300)
        % exportgraphics(f12,['SimulationOutput/',simID,'_X5.pdf'],'Resolution',300)
        exportgraphics(f4,['SimulationOutput/',simID,'_U1.pdf'],'Resolution',300)
        exportgraphics(f5,['SimulationOutput/',simID,'_U2.pdf'],'Resolution',300)
        exportgraphics(f13,['SimulationOutput/',simID,'_U3.pdf'],'Resolution',300)
        exportgraphics(f6,['SimulationOutput/',simID,'_W1.pdf'],'Resolution',300)
        exportgraphics(f7,['SimulationOutput/',simID,'_W2.pdf'],'Resolution',300)
        % exportgraphics(f8,['SimulationOutput/',simID,'_Topology.pdf'])
        % exportgraphics(f9,['SimulationOutput/',simID,'_Ptie.pdf'],'Resolution',300)
        exportgraphics(f10,['SimulationOutput/',simID,'_Cost.pdf'],'Resolution',300)
        % exportgraphics(f14,['SimulationOutput/',simID,'_PlotLegend.pdf'],'Resolution',300)
    end
  
end