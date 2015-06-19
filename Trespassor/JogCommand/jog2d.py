import math

import pygame
from numpy import array

import pylygon


def poly_translate(p, tx, ty):
    pp = p.P
    ppt = array([(x + tx, y + ty) for (x, y) in pp])
    p.P = ppt
    return pylygon.Polygon(p)


def poly_rotate(p, theta):
    thetar = theta * math.pi / 180.0
    pp = p.P
    ppr = array([(x * math.cos(thetar) - y * math.sin(thetar),
                  x * math.sin(thetar) + y * math.cos(thetar)) for (x, y) in pp])
    p.P = ppr
    return pylygon.Polygon(p)


def sonar_beam(x, y, theta, head, rng):
    nbeam = 31
    beam = [(0.0, 0.0)]
    rng = 200.0
    for i in range(nbeam):
        ang = (i * 1 - 15.0) * math.pi / 180.0
        beam.append((rng * math.cos(ang), rng * math.sin(ang)))
    ply = (pylygon.Polygon(beam))
    # print ply
    ang = (theta - head)
    # print head, theta, ang, x, y
    plyr = poly_rotate(ply, ang)
    # print plyr
    ply = poly_translate(plyr, x, y)
    # print ply
    return ply


class Jog2d(object):
    def __init__(self):
        self.nel = 0
        self.tel = {}
        jog = pylygon.Polygon([(-50.0, -10.0), (-10.0, -30.0), (10.0, -30.0),
                               (18.0, -10.0), (20.0, 0.0), (18.0, 10.0),
                               (10.0, 30.0), (-10.0, 30.0), (-50.0, 10.0)])
        self.xg = 0.0
        self.yg = 0.0
        self.head = 90.0
        self.tel['main'] = {'poly': jog, 'x': self.xg, 'y': self.yg}

        gap = 1.0
        jog = pylygon.Polygon([(-50.0 - gap, -10.0 - gap), (-10.0 - gap, -30.0 - gap), (10.0 + gap, -30.0 - gap),
                               (18.0 + gap, -10.0 - gap), (20.0 + gap, 0.0 + gap), (18.0 + gap, 10.0 + gap),
                               (10.0 + gap, 30.0 + gap), (-10.0 - gap, 30.0 + gap), (-50.0 - gap, 10.0 + gap)])
        self.xg = 0.0
        self.yg = 0.0
        self.head = 90.0
        self.tel['mainGap'] = {'poly': jog, 'x': self.xg, 'y': self.yg}

        for i in range(4):
            ply = (pylygon.Polygon([(-5.0, -18.0 + i * 10),
                                    (5.0, -18.0 + i * 10),
                                    (5.0, -12.0 + i * 10),
                                    (-5.0, -12.0 + i * 10)]))
            xply = 0.0
            yply = -7.5 + i * 5
            nml = "led%1.1d" % (i + 1)
            self.tel[nml] = {'poly': ply, 'x': xply, 'y': yply}

        ply = (pylygon.Polygon([(18.0, -2.0), (22.0, -2.0),
                                (22.0, 2.0), (18.0, 2.0)]))
        xply = 20.0
        yply = 0.0
        nml = "sonarC"
        self.tel[nml] = {'poly': ply, 'x': xply, 'y': yply}

        ply = (pylygon.Polygon([(-2.0, 28.0), (2.0, 28.0),
                                (2.0, 32.0), (-2.0, 32.0)]))
        xply = 0.0
        yply = 30.0
        nml = "sonarL"
        self.tel[nml] = {'poly': ply, 'x': xply, 'y': yply}

        ply = (pylygon.Polygon([(-2.0, -32.0), (2.0, -32.0),
                                (2.0, -28.0), (-2.0, -28.0)]))
        xply = 0.0
        yply = -30.0
        nml = "sonarR"
        self.tel[nml] = {'poly': ply, 'x': xply, 'y': yply}

        xply = 20.0
        yply = 0.0
        rng = 200.0
        ply = sonar_beam(xply, yply, self.head, self.head, rng)
        nml = "beamsonarC"
        self.tel[nml] = {'poly': ply, 'x': xply, 'y': yply}

        xply = 0.0
        yply = -30.0
        rng = 200.0
        ply = sonar_beam(xply, yply, self.head - 90.0, self.head, rng)
        nml = "beamsonarL"
        self.tel[nml] = {'poly': ply, 'x': xply, 'y': yply}

        xply = 0.0
        yply = 30.0
        rng = 200.0
        ply = sonar_beam(xply, yply, self.head + 90.0, self.head, rng)
        nml = "beamsonarR"
        self.tel[nml] = {'poly': ply, 'x': xply, 'y': yply}

        self.nel = len(self.tel)

    def translate(self, tx, ty):
        for el in self.tel:
            vel = self.tel[el]
            ply = vel['poly']
            xply = vel['x']
            yply = vel['y']
            # print "translate ",el

            ply.P = array([(tx + p_x, ty + p_y) for (p_x, p_y) in ply.P])
            xply += tx
            yply += ty
            self.tel[el]['poly'] = ply
            self.tel[el]['x'] = xply
            self.tel[el]['y'] = yply
            # print self.tel[el]

        self.xg += tx
        self.yg += ty

    def rotate(self, theta):
        self.head += theta
        # print "heading is ",self.head
        thetarad = theta * math.pi / 180.0
        for el in self.tel:
            vel = self.tel[el]
            # print "before rot ",i, self.tel[i]
            ply = vel['poly']
            xply = vel['x']
            yply = vel['y']

            tx = - xply
            ty = - yply
            ply.P = array([(tx + p_x, ty + p_y) for (p_x, p_y) in ply.P])
            # print "tx1: ",tx,ty,ply.P

            plyr = ply.rotate(thetarad)
            plyr = poly_rotate(ply, theta)
            # print "rot: ",plyr.P

            tx = xply - self.xg
            ty = yply - self.yg
            txr = tx * math.cos(thetarad) - ty * math.sin(thetarad)
            tyr = tx * math.sin(thetarad) + ty * math.cos(thetarad)

            xplyr = self.xg + txr
            yplyr = self.yg + tyr
            #print "tx2: ",txr, tyr, xplyr, yplyr
            plyr.P = array([(xplyr + x, yplyr + y) for (x, y) in plyr.P])

            self.tel[el]['poly'] = plyr
            self.tel[el]['x'] = xplyr
            self.tel[el]['y'] = yplyr
            #print "after rot ",i, self.tel[i]

    def draw(self, screen, leds, sonar_hit):
        drawok = {}
        for el in self.tel:
            drawok[el] = False

        nm = 'mainGap'
        drawok[nm] = True
        ply = self.tel[nm]['poly']
        pygame.draw.polygon(screen, (255, 192, 127), ply.P, 0)
        pygame.draw.polygon(screen, (127, 95, 63), ply.P, 1)

        nm = 'main'
        drawok[nm] = True
        ply = self.tel[nm]['poly']
        pygame.draw.polygon(screen, (255, 127, 0), ply.P, 0)
        pygame.draw.polygon(screen, (127, 63, 0), ply.P, 1)

        for i in range(4):
            nm = "led%1.1d" % (i + 1)
            drawok[nm] = True
            ply = self.tel[nm]['poly']
            if leds[i] == 1:
                colorl = (255, 255, 0)
                if i >= 2:
                    colorl = (0, 255, 0)
                pygame.draw.polygon(screen, colorl, ply.P, 0)
            else:
                pygame.draw.polygon(screen, (31, 31, 31), ply.P, 0)
            pygame.draw.polygon(screen, (255, 255, 255), ply.P, 1)

        for nm in self.tel:
            if nm[0:9] == 'beamsonar':
                drawok[nm] = True
                ply = self.tel[nm]['poly']
                # print sonar_hit
                if sonar_hit[nm][0]:
                    pygame.draw.polygon(screen, (255, 0, 0), ply.P, 0)
                else:
                    pygame.draw.polygon(screen, (159, 127, 127), ply.P, 0)

        for nm in self.tel:
            if nm[0:5] == 'sonar':
                drawok[nm] = True
                ply = self.tel[nm]['poly']
                pygame.draw.polygon(screen, (0, 127, 255), ply.P, 0)

        for nm in self.tel:
            if drawok[nm] is False:
                ply = self.tel[nm]['poly']
                pygame.draw.polygon(screen, (31, 95, 31), ply.P, 0)
                pygame.draw.polygon(screen, (255, 255, 255), ply.P, 1)

    def obstacle(self, tobs):
        beam_hit = {}
        for el in self.tel:
            elname = el
            if elname[0:4] == "beam":
                ply = self.tel[el]['poly']
                dist = 511.0
                beam_hit[elname] = [False, dist]
                for obs in tobs:
                    oaxis = obs.collidepoly(ply)
                    if not oaxis is False:
                        hit = beam_hit[elname][0]
                        hit = hit or True
                        # print hit, beam_hit[elname]
                        sonar = "sonar" + elname[len(elname) - 1:len(elname)]
                        plyson = self.tel[sonar]['poly']
                        # print elname,sonar,oaxis
                        dson = obs.distance(plyson)
                        dists = math.sqrt(dson[0] * dson[0] + dson[1] * dson[1])
                        if dists < dist:
                            dist = dists
                        beam_hit[elname] = [hit, dist]
                        # print sonar,beam_hit[elname]
        return beam_hit

    def check_stopped(self, tobs):
        stopped = False
        ply = self.tel['mainGap']['poly']
        # print ply.P
        dobs = []
        deps = 3.0  # cannot go closer than 3 cm
        for obs in tobs:
            oaxis = obs.collidepoly(ply)
            # print oaxis
            if not oaxis is False:
                d = obs.distance(ply)
                dobs.append(math.sqrt(d[0] * d[0] + d[1] * d[1]))
                stopped = True
            else:
                dobs.append(1500)
        # print stopped, dobs
        return stopped


class Obstacle(object):
    def __init__(self, x0, y0, x1, y1):
        ply = pylygon.Polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        self.ply = ply

    def draw(self, screen, color=(0, 0, 0), outcolor=(255, 255, 255)):
        pygame.draw.polygon(screen, color, self.ply, 0)
        pygame.draw.polygon(screen, outcolor, self.ply, 1)


class Picture(object):
    def __init__(self, x0, y0, x1, y1):
        ply = pylygon.Polygon([(x0, y0), (x1, y0), (x1, y1), (x0, y1)])
        self.ply = ply

    def draw(self, screen, color=(0, 0, 0), outcolor=(255, 255, 255)):
        pygame.draw.polygon(screen, color, self.ply, 0)
        pygame.draw.polygon(screen, outcolor, self.ply, 1)


if __name__ == "__main__":
    a = Jog2d()
    print a.tel['main']
    a.translate(-20.0, 50.0)
    print a.tel['main']
    a.rotate(90.0)
    print a.tel['main']