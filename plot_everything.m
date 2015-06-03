clear all; close all; clc;
data = load('logasserv.txt');
data(:,1) = data(:,1) - data(1,1);
data2 = load('log_theta.txt');
data2(:,1) = data2(:,1) - data2(1,1);
figure;
plot(data(:,1), data(:,2), 'blue')
hold on;
plot(data(:,1), data(:,3), 'red')
plot(data(:,1), data(:,4), 'green')
plot(data(:,1), data(:,5), 'black')
legend('order left', 'real left', 'order right', 'real right')

figure;
plot(data(:,1), data(:,6), 'red')
hold on;
plot(data(:,1), data(:,7), 'blue')
legend('Erreur intégrale gauche', 'Erreur proportionnelle gauche')

figure;
plot(data(:,1), data(:,8), 'red')
hold on;
plot(data(:,1), data(:,9), 'blue')
legend('command left', 'command right')

figure
plot(data2(:,1), data2(:,2), 'red')
hold on
plot(data2(:,1), data2(:,3), 'blue')
legend('Target theta', 'real theta')

