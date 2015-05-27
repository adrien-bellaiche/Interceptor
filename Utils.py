__author__ = 'Fenix'


def parse_mission_file(mission_file_name):
    #TODO
    pass


def parse_position(word):
    # get word "AXX.XX", returns [errorcode, position]
    if len(word) != 6:
        return [1, 0]
    else:
        return [0,float(word[1:])]