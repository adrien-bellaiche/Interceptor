clear all; close all; clc;
data = load('logasserv.txt');
data(:,1) = data(:,1) - data(1,1);
data2 = load('logtheta.txt');
data2(:,1) = data2(:,1) - data2(1,1);
data3 = load('logpos.txt');
data4 = load('logodometry.txt');

figure;
subplot 211
plot(data(:,1), data(:,2), 'blue')
hold on;
plot(data(:,1), data(:,3), 'red')
legend('order left', 'real left')
subplot 212
plot(data(:,1), data(:,4), 'green')
hold on;
plot(data(:,1), data(:,5), 'black')
legend('order right', 'real right')
title('Wheel speeds')

figure;
plot(data(:,1), data(:,6), 'red')
hold on;
plot(data(:,1), data(:,7), 'blue')
legend('Erreur intégrale gauche', 'Erreur proportionnelle gauche')
title('Erreur gauche')



figure;
plot(data4(:,1), 'blue');
hold on;
plot(data4(:,2), 'red');
title('Odometry')
legend('odometry left', 'odometry right')


figure;
plot(data(:,1), data(:,8), 'red')
hold on;
plot(data(:,1), data(:,9), 'blue')
legend('command left', 'command right')
title('Wheel command')

figure
plot(data2(:,1), mod(180/pi*data2(:,2) + 180, 360)-180, 'red')
hold on
plot(data2(:,1), mod(180/pi*data2(:,3) + 180, 360)-180, '+-blue')
legend('Target theta', 'real theta')
title('Theta')


figure;
plot(data3(:,1), data3(:,2), 'red');
axis equal
