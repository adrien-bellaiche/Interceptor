import time
import math
import sys
from JogCommand import jog2d
import pygame


def simu(ns, shared_regs, change_regs):
    print "simu started"
    twopi = 2.0 * math.pi
    pygame.init()
    xmax = 1000
    ymax = 600
    size = (xmax, ymax)
    screen = pygame.display.set_mode(size)

    tpict = []
    tpictply = []
    pict1 = jog2d.Picture(800, 50, 950, 200)
    tpict.append(pict1)
    tpictply.append(pict1.ply)

    tobs = []
    tobsply = []

    maze = False
    if maze:
        obs1 = jog2d.Obstacle(240, 20, 260, 450)
        tobs.append(obs1)
        tobsply.append(obs1.ply)

        obs2 = jog2d.Obstacle(490, 150, 510, 580)
        tobs.append(obs2)
        tobsply.append(obs2.ply)

        obs3 = jog2d.Obstacle(740, 20, 760, 450)
        tobs.append(obs3)
        tobsply.append(obs3.ply)

    obs_l = jog2d.Obstacle(0, 0, 10, ymax)
    tobs.append(obs_l)
    tobsply.append(obs_l.ply)

    obs_r = jog2d.Obstacle(xmax - 10, 0, xmax, ymax)
    tobs.append(obs_r)
    tobsply.append(obs_r.ply)

    obs_t = jog2d.Obstacle(11, 0, xmax - 11, 10)
    tobs.append(obs_t)
    tobsply.append(obs_t.ply)

    obs_b = jog2d.Obstacle(11, ymax - 10, xmax - 11, ymax)
    tobs.append(obs_b)
    tobsply.append(obs_b.ply)

    jog = jog2d.Jog2d()
    leds = [0, 0, 0, 0]  # leds off

    # init location
    xjog = 100
    yjog = 100
    xjogi = int(round(xjog))
    yjogi = int(round(yjog))
    jog.translate(xjogi, yjogi)

    # init heading
    hdjog0 = jog.head
    hdjog = 110.0
    angrot = (hdjog - hdjog0)
    jog.rotate(angrot)

    # init sonars
    sonar_hits = jog.obstacle(tobsply)
    sonar_set = []
    sonar_time = []
    for ison in range(5):
        sonar_set.append(False)
        sonar_time.append(time.time())
        addrs = 0x71 + ison
        for regs in [0, 2, 3]:
            st_reg = "i2c_0x%2.2x_%2.2d" % (addrs, regs)
            shared_regs[st_reg] = 0

    # init compass
    addrs = 0x60
    for regs in [1, 2, 3]:
        st_reg = "i2c_0x%2.2x_%2.2d" % (addrs, regs)
        shared_regs[st_reg] = 0

    # init motion and odometry
    motors_period_reg = 100
    odo_left_actual = 0.0
    odo_right_actual = 0.0
    motor_left_direction = 1.0
    motor_right_direction = 1.0
    wheel_diameter = (2.32 * 2.54e-2)
    wheel_radius = wheel_diameter / 2.0
    n_ticks = 576
    wheel_dist = 0.2
    motor_left_ang_speed = 0.0
    motor_right_ang_speed = 0.0
    motor_left_lin_speed = 0.0
    motor_right_lin_speed = 0.0
    motor_left_dead_zone = 17.0  # 11
    motor_right_dead_zone = 19.0  # 13
    revsec = 4  # revol/sec at maximum PWM
    motors_alpha = revsec * twopi / motors_period_reg
    ang_speed = 0.0
    shared_regs['fpga_0x06'] = motors_period_reg

    t = 0.0
    d_time = 0.05
    while ns.alive:
        start_time = time.time()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                ns.alive = False
                print "trying to close pygame window ... no action"
                sys.exit()

        # print "vJOG alive ",t
        #get the changes in JOG configuration 
        # and perform corresponding
        update_motors = False
        for keyval in change_regs:
            key = keyval[0]
            val = shared_regs[key]
            #print "vJOG",key,val,t
            change_regs.remove(keyval)

            # FPGA registers
            if key == 'fpga_0x18':  # leds
                #print "vJOG : leds"
                for il in range(4):
                    leds[il] = (val >> il) & 0x1
            elif key == 'fpga_0x20':  # odometer 1
                shared_regs[key] = int(odo_right_actual) & 65535
                #print "vJOG : odo1",shared_regs[key]
            elif key == 'fpga_0x22':  # odometer 2
                shared_regs[key] = int(odo_left_actual) & 65535
                #print "vJOG : od2",shared_regs[key]
            elif key == 'fpga_0x06':  # period PWM (100 = 0x64)
                #print "vJOG : period PWM"
                motors_period_reg = val - 1
                motors_alpha = revsec * twopi / motors_period_reg
                #print "motors_period_reg",motors_period_reg
            elif key == 'fpga_0x08':  # value PWM1 (0 to 99)
                #print "vJOG : value PWM1"
                update_motors = True
            elif key == 'fpga_0x0a':  # direction PWM1 (0: forward)
                #print "vJOG : direction PWM1"
                update_motors = True
            elif key == 'fpga_0x0c':  # value PWM2 (0 to 99)
                #print "vJOG : value PWM2"
                update_motors = True
            elif key == 'fpga_0x0e':  # direction PWM2 (0: forward)
                #print "vJOG : direction PWM2"
                update_motors = True

            if update_motors:
                motor_left_direction = 1.0
                if int(shared_regs['fpga_0x0a']) & 1:
                    motor_left_direction = -1.0

                motor_left_ang_speed = shared_regs['fpga_0x08']
                motor_left_ang_speed -= motor_left_dead_zone
                if motor_left_ang_speed < 0:
                    motor_left_ang_speed = 0.0
                if motor_left_ang_speed > motors_period_reg:
                    motor_left_ang_speed = motors_period_reg
                motor_left_ang_speed *= (motors_alpha * motor_left_direction)

                motor_right_direction = 1.0
                if int(shared_regs['fpga_0x0e']) & 1:
                    motor_right_direction = -1.0

                motor_right_ang_speed = shared_regs['fpga_0x0c']
                motor_right_ang_speed -= motor_right_dead_zone
                if motor_right_ang_speed < 0:
                    motor_right_ang_speed = 0.0
                if motor_right_ang_speed > motors_period_reg:
                    motor_right_ang_speed = motors_period_reg
                motor_right_ang_speed *= (motors_alpha * motor_right_direction)

            # Sonar started 
            if key == "i2c_0x73_00":  # sonarC (center) cmd
                if val == 81:
                    sonar_set[2] = True
                    sonar_time[2] = time.time()
                    v = int(round(sonar_hits['beamsonarC'][1]))
                    #print sonar_hits,v
                    shared_regs['i2c_0x73_02'] = (v >> 8) & 0xff
                    shared_regs['i2c_0x73_03'] = v & 0xff
            if key == "i2c_0x71_00":  # sonarL (left) cmd
                if val == 81:
                    sonar_set[0] = True
                    sonar_time[0] = time.time()
                    v = int(round(sonar_hits['beamsonarL'][1]))
                    #print sonar_hits,v
                    shared_regs['i2c_0x71_02'] = (v >> 8) & 0xff
                    shared_regs['i2c_0x71_03'] = v & 0xff
            if key == "i2c_0x75_00":  # sonarR (right) cmd
                if val == 81:
                    sonar_set[4] = True
                    sonar_time[0] = time.time()
                    v = int(round(sonar_hits['beamsonarR'][1]))
                    #print sonar_hits,v
                    shared_regs['i2c_0x75_02'] = (v >> 8) & 0xff
                    shared_regs['i2c_0x75_03'] = v & 0xff

        if sonar_set[2]:
            if (time.time() - sonar_time[2]) > 0.05:
                sonar_set[2] = False
        if sonar_set[0]:
            if (time.time() - sonar_time[0]) > 0.05:
                sonar_set[0] = False
        if sonar_set[4]:
            if (time.time() - sonar_time[4]) > 0.05:
                sonar_set[4] = False

        # update location (display in cm)
        thd = (90 - jog.head) * math.pi / 180.0
        dxy = wheel_radius * (motor_left_ang_speed + motor_right_ang_speed) / 2.0
        dx = dxy * math.cos(thd) * d_time
        dy = dxy * math.sin(thd) * d_time
        dthd = wheel_radius * (motor_left_ang_speed - motor_right_ang_speed) / wheel_dist
        dthd *= d_time

        xjog += (dx * 100.0)
        yjog -= (dy * 100.0)

        # check if robot locked
        stopped = jog.check_stopped(tobsply)
        # cannot move ... if stopped !!
        if stopped:
            #print t,"robot stopped cannot translate ",xjog, yjog, xjogBck, yjogBck
            xjog -= (dx * 100.0)
            yjog += (dy * 100.0)

        if xjog < 0:
            xjog = 0
        if xjog > xmax:
            xjog = xmax
        if yjog < 0:
            yjog = 0
        if yjog > xmax:
            yjog = xmax

        #rotate jog
        angrot = dthd * 180.0 / math.pi
        jog.rotate(angrot)

        # cannot rotate ... if stopped after rotation !!
        stopped = jog.check_stopped(tobsply)
        if stopped:
            angrot = -dthd * 180.0 / math.pi
            jog.rotate(angrot)
            #print "robot stopped cannot rotate ",jog.head
        #print "heading,rot, vx,vy ",jog.head,angrot,dx*100/d_time,dy*100/d_time
        #print "motor_left_ang_speed %f revols/s"%(motor_left_ang_speed/twopi)
        #print "motor_right_ang_speed %f revols/s"%(motor_right_ang_speed/twopi)
        #print "dmotorLeftAngle %f revol"%(d_time*motor_left_ang_speed/twopi)
        #print "dmotorRightAngle %f revol"%(d_time*motor_right_ang_speed/twopi)

        angular = abs(d_time * motor_left_ang_speed / twopi)
        odo_left_actual += (angular * n_ticks)
        angular = abs(d_time * motor_right_ang_speed / twopi)
        odo_right_actual += (angular * n_ticks)
        #print "odos",odo_left_actual,odo_right_actual

        keyor = 'fpga_0x20'  # odometer 1
        shared_regs[keyor] = int(odo_right_actual) & 65535
        #print "vJOG : odo1",shared_regs[keyor],odo_right_actual
        keyol = 'fpga_0x22'  # odometer 2
        shared_regs[keyol] = int(odo_left_actual) & 65535
        #print "vJOG : odo2",shared_regs[keyol],odo_left_actual

        # update IC2 compass
        jog.head = (jog.head % 360.0)
        shared_regs['i2c_0x60_01'] = int(round(jog.head * 256. / 360.0))
        hdjog10 = int(round(jog.head * 10.0))
        shared_regs['i2c_0x60_02'] = (hdjog10 >> 8) & 0xff
        shared_regs['i2c_0x60_03'] = hdjog10 & 0xff

        # translate JOG
        dxjogi = int(round(xjog - xjogi))
        dyjogi = int(round(yjog - yjogi))
        xjogi += dxjogi
        yjogi += dyjogi
        jog.translate(dxjogi, dyjogi)

        # display
        screen.fill((127, 127, 127))

        for obs in tobs:
            obs.draw(screen, (100, 100, 255))

        for pict in tpict:
            pict.draw(screen, (31, 255, 31))

        # update sonars
        sonar_hits = jog.obstacle(tobsply)
        jog.draw(screen, leds, sonar_hits)

        # both looks similar
        #pygame.display.update()
        pygame.display.flip()

        #print __name__,": leds" , leds

        # first pass in simu loop completed -> end of init  
        if not ns.endOfInit:
            ns.endOfInit = True
        t += d_time
        proc_time = time.time() - start_time
        dtrem = d_time - proc_time
        #print d_time,proc_time,dtrem
        if dtrem < 0:
            dtrem = 0.0
        time.sleep(dtrem)
    print "simu stopped", t