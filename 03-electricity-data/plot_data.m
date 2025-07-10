function plot_data(Parameters, Load_Measure, Renewable_Measure, Load_Forecast, Renewable_Forecast, Load_Measure_Delta, Renewable_Measure_Delta, Load_Forecast_Delta, Renewable_Forecast_Delta, export_data_plot, print_labels, simID, visibility_option)
    
    CountryCodes = Parameters{1};
    Na = Parameters{7};
    
    
    number_of_days = Parameters{17};
    IterationSegments = Parameters{4};
    SegmentsInHour = Parameters{16};
    CISO_Import = Parameters{25};
    % For one day plot
    N = number_of_days*IterationSegments*SegmentsInHour*24;

    % For more days, but requieres different xlabels
    % N = Parameters{9};

    % Color Map
        plotColors = jet(Na);
    


    %% Labels Legend

        labels = char(zeros(Na, 9));
        for i = 1:Na
            if CountryCodes(i) < 10
                labels(i,:) = ['0', num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
            else
                labels(i,:) = [num2str(CountryCodes(i)), ' $|$ ',  CISO_Import(i,1:2)];
            end
        end
    
    

    %% Measured Load Curve (w_1)
    
        f1 = figure('visible',visibility_option);
        f1.Position = [100 100 1380 820];
        xlim([0 N])
        ylim([1.05*min(min(Load_Measure(:,1:N+1))) 1.05*max(max(Load_Measure(:,1:N+1)))])
        grid on
        hold on
        k = 1;
        for i = 1:Na
            stairs(0:N,Load_Measure(i,1:N+1),'-','LineWidth',1.5,'Color', plotColors(k,:))
            k = k + 1;
        end
    
        % tit = title('Load curve measure','Interpreter','latex');
            
        xlab = xlabel('Hours','Interpreter','latex');
        ylab = ylabel('GW','Interpreter','latex');
        xticks(0:IterationSegments*SegmentsInHour*number_of_days:N);
        num_ticks = number_of_days*24;
        x_ticks_markers = cell(0);
        for i=0:number_of_days:num_ticks
            x_ticks_markers = [x_ticks_markers,int2str(i)];
        end
        xticklabels(x_ticks_markers);
        % xticks(0:number_of_days:num_ticks);
        % xticks(0:IterationSegments*SegmentsInHour:N);
        % disp(x_ticks_markers)
        % xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
        ax = gca;
        ax.YAxis.Exponent = 0;
        
        if print_labels == true
            leg = legend(labels,'Location','eastoutside','Interpreter','latex');
            leg.FontSize = 14*2;
        end

        set(f1.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
        
        tit.FontSize = 20*2;
        xlab.FontSize = 18*2;
        ylab.FontSize = 18*2;
        
        f1.CurrentAxes.Box = 'on';
    
        hold off
    

    %% Measured Renewable Generation (w_2)
    
        f2 = figure('visible',visibility_option);
        f2.Position = [100 100 1380 820];
        xlim([0 N])
        ylim([1.05*min(min(Renewable_Measure(:,1:N+1))) 1.05*max(max(Renewable_Measure(:,1:N+1)))])
        grid on
        hold on
        k = 1;
        for i = 1:Na
            stairs(0:N,Renewable_Measure(i,1:N+1),'-','LineWidth',1.5,'Color', plotColors(k,:))
            k = k + 1;
        end
    
        % tit = title('Renewable generation measure','Interpreter','latex');
            
        xlab = xlabel('Hours','Interpreter','latex');
        ylab = ylabel('GW','Interpreter','latex');
        xticks(0:IterationSegments*SegmentsInHour*number_of_days:N);
        % xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
        xticklabels(x_ticks_markers);
        ax = gca;
        ax.YAxis.Exponent = 0;
        if print_labels == true
            leg = legend(labels,'Location','eastoutside','Interpreter','latex');
            leg.FontSize = 14*2;
        end

        set(f2.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
        
        tit.FontSize = 20*2;
        xlab.FontSize = 18*2;
        ylab.FontSize = 18*2;
        
        f2.CurrentAxes.Box = 'on';
    
        hold off
  

    %% Forecast of Load Curve (w_1)
    
        f3 = figure('visible',visibility_option);
        f3.Position = [100 100 1380 820];
        xlim([0 N])
        ylim([1.05*min(min(Load_Forecast(:,1:N+1))) 1.05*max(max(Load_Forecast(:,1:N+1)))])
        grid on
        hold on
        k = 1;
        for i = 1:Na
            stairs(0:N,Load_Forecast(i,1:N+1),'-','LineWidth',1.5,'Color', plotColors(k,:))
            k = k + 1;
        end
    
        % tit = title('Load curve forecast','Interpreter','latex');
            
        xlab = xlabel('Hours','Interpreter','latex');
        ylab = ylabel('GW','Interpreter','latex');
        xticks(0:IterationSegments*SegmentsInHour*number_of_days:N);
        % xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
        xticklabels(x_ticks_markers);
        ax = gca;
        ax.YAxis.Exponent = 0;
        % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
        % leg.FontSize = 14*2;

        set(f3.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
        
        tit.FontSize = 20*2;
        xlab.FontSize = 18*2;
        ylab.FontSize = 18*2;
        
        f3.CurrentAxes.Box = 'on';
    
        hold off
  

    %% Forecast of Renewable Generation (w_2)
    
        f4 = figure('visible',visibility_option);
        f4.Position = [100 100 1380 820];
        xlim([0 N])
        ylim([1.05*min(min(Renewable_Forecast(:,1:N+1))) 1.05*max(max(Renewable_Forecast(:,1:N+1)))])
        grid on
        hold on
        k = 1;
        for i = 1:Na
            stairs(0:N,Renewable_Forecast(i,1:N+1),'-','LineWidth',1.5,'Color', plotColors(k,:))
            k = k + 1;
        end
    
        % tit = title('Renewable generation forecast','Interpreter','latex');
            
        xlab = xlabel('Hours','Interpreter','latex');
        ylab = ylabel('GW','Interpreter','latex');
        xticks(0:IterationSegments*SegmentsInHour*number_of_days:N);
        % xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
        xticklabels(x_ticks_markers);
        ax = gca;
        ax.YAxis.Exponent = 0;
        % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
        % leg.FontSize = 14*2;

        set(f4.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
        
        tit.FontSize = 20*2;
        xlab.FontSize = 18*2;
        ylab.FontSize = 18*2;
        
        f4.CurrentAxes.Box = 'on';
    
        hold off
 

    %% w1 -- Measured Load Curve Increments 
    
        f5 = figure('visible',visibility_option);
        f5.Position = [100 100 1380 820];
        xlim([0 N])
        ylim([1.05*min(min(Load_Measure_Delta(:,1:N+1))) 1.05*max(max(Load_Measure_Delta(:,1:N+1)))])
        grid on
        hold on
        k = 1;
        for i = 1:Na
            stairs(0:N,Load_Measure_Delta(i,1:N+1),'-','LineWidth',1.5,'Color', plotColors(k,:))
            k = k + 1;
        end
    
        % tit = title('Load curve measure increments','Interpreter','latex');
            
        xlab = xlabel('Hours','Interpreter','latex');
        ylab = ylabel('GW','Interpreter','latex');
        xticks(0:IterationSegments*SegmentsInHour*number_of_days:N);
        % xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
        xticklabels(x_ticks_markers);
        ax = gca;
        ax.YAxis.Exponent = 0;
        % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
        % leg.FontSize = 14*2;

        set(f5.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
        
        tit.FontSize = 20*2;
        xlab.FontSize = 18*2;
        ylab.FontSize = 18*2;
        
        f5.CurrentAxes.Box = 'on';
    
        hold off


    %% w2 -- Measured Renewabble Generation Increments
    
        f6 = figure('visible',visibility_option);
        f6.Position = [100 100 1380 820];
        xlim([0 N])
        ylim([1.05*min(min(Renewable_Measure_Delta(:,1:N+1))) 1.05*max(max(Renewable_Measure_Delta(:,1:N+1)))])
        grid on
        hold on
        k = 1;
        for i = 1:Na
            stairs(0:N,Renewable_Measure_Delta(i,1:N+1),'-','LineWidth',1.5,'Color', plotColors(k,:))
            k = k + 1;
        end
    
        % tit = title('Renewable generation measure increments','Interpreter','latex');
            
        xlab = xlabel('Hours','Interpreter','latex');
        ylab = ylabel('GW','Interpreter','latex');
        xticks(0:IterationSegments*SegmentsInHour*number_of_days:N);
        % xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
        xticklabels(x_ticks_markers);
        ax = gca;
        ax.YAxis.Exponent = 0;
        % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
        % leg.FontSize = 14*2;

        set(f6.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
        
        tit.FontSize = 20*2;
        xlab.FontSize = 18*2;
        ylab.FontSize = 18*2;
        
        f6.CurrentAxes.Box = 'on';
    
        hold off
    
    
    %% w1 -- Forecast of Load Curve
    
        f7 = figure('visible',visibility_option);
        f7.Position = [100 100 1380 820];
        xlim([0 N])
        ylim([1.05*min(min(Load_Forecast_Delta(:,1:N+1))) 1.05*max(max(Load_Forecast_Delta(:,1:N+1)))])
        grid on
        hold on
        k = 1;
        for i = 1:Na
            stairs(0:N,Load_Forecast_Delta(i,1:N+1),'-','LineWidth',1.5,'Color', plotColors(k,:))
            k = k + 1;
        end
    
        % tit = title('Load curve forecast increments','Interpreter','latex');
            
        xlab = xlabel('Hours','Interpreter','latex');
        ylab = ylabel('GW','Interpreter','latex');
        xticks(0:IterationSegments*SegmentsInHour*number_of_days:N);
        % xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
        xticklabels(x_ticks_markers);
        ax = gca;
        ax.YAxis.Exponent = 0;
        % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
        % leg.FontSize = 14*2;

        set(f7.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
        
        tit.FontSize = 20*2;
        xlab.FontSize = 18*2;
        ylab.FontSize = 18*2;
        
        f7.CurrentAxes.Box = 'on';
    
        hold off
    

    %% w2 -- Forecast of Renewabble Generation Increments
    
        f8 = figure('visible',visibility_option);
        f8.Position = [100 100 1380 820];
        xlim([0 N])
        ylim([1.05*min(min(Renewable_Forecast_Delta(:,1:N+1))) 1.05*max(max(Renewable_Forecast_Delta(:,1:N+1)))])
        grid on
        hold on
        k = 1;
        for i = 1:Na
            stairs(0:N,Renewable_Forecast_Delta(i,1:N+1),'-','LineWidth',1.5,'Color', plotColors(k,:))
            k = k + 1;
        end
    
        % tit = title('Renewable generation forecast increments','Interpreter','latex');
            
        xlab = xlabel('Hours','Interpreter','latex');
        ylab = ylabel('GW','Interpreter','latex');
        xticks(0:IterationSegments*SegmentsInHour*number_of_days:N);
        % xticklabels({'0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24'});
        xticklabels(x_ticks_markers);
        ax = gca;
        ax.YAxis.Exponent = 0;
        % leg = legend(labels,'Location','eastoutside','Interpreter','latex');
        % leg.FontSize = 14*2;

        set(f8.CurrentAxes, 'FontName', 'Times New Roman', 'FontSize', 14*2)
        
        tit.FontSize = 20*2;
        xlab.FontSize = 18*2;
        ylab.FontSize = 18*2;
        
        f8.CurrentAxes.Box = 'on';
    
        hold off    
       



%% Export Graphic

if export_data_plot == true

        exportgraphics(f1,[simID,'0A_MeasuredLoad.png'],'Resolution',300)
        exportgraphics(f2,[simID,'0B_MeasuredRenewable.png'],'Resolution',300)
        exportgraphics(f3,[simID,'0C_ForecastLoad.png'],'Resolution',300)
        exportgraphics(f4,[simID,'0D_ForecastRenewable.png'],'Resolution',300)
        exportgraphics(f5,[simID,'0E_MeasuredLoadIncrements.png'],'Resolution',300)
        exportgraphics(f6,[simID,'0F_MeasuredRenewableIncrements.png'],'Resolution',300)
        exportgraphics(f7,[simID,'0G_ForecastLoadIncrements.png'],'Resolution',300)
        exportgraphics(f8,[simID,'0H_ForecastRenewableIncrements.png'],'Resolution',300)

end    