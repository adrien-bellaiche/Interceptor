__author__ = 'Fenix'


class C(object):
    def __init__(self):
        self._target = None


    @property
    def target(self):
        return self._target

    @target.setter
    def target(self, p):
        print "SETTER CALLED"
        self._target = p
        print 'Target set at ', self._target

    @target.getter
    def target(self):
        print 'getter accessed'
        return self._target

w = C()
w.target = -3

print w.target
