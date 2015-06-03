__author__ = 'Fenix'

parsedic = {"x": 0,
            "y": 1,
            "id": 2,
            "serverip": 3,
            "serverport": 4}

parsetype = {"x": float,
             "y": float,
             "id": int,
             "serverip": str,
             "serverport": int}


def parse_mission_file(mission_file_name):
    with open(mission_file_name, 'r') as mission_file:
        res = [None for _ in range(5)]
        lines = mission_file.readlines()
        for line in lines:
            words = line.split("#")[0].replace(" ", "").split("=")
            if words[0].lower() in parsedic:
                res[parsedic[words[0].lower()]] = parsetype[words[0].lower()](words[1])
            else:
                raise ParseException(words[0])
        print "FILE PARSED"
        return res


def parse_position(word):
    # get word "AXX.XX", returns [errorcode, position]
    if len(word) != 6:
        return [1, 0]
    else:
        return [0, float(word[1:])]


class ParseException(Exception):
    def __init__(self, word):
        self.value = word

    def __str__(self):
        return "".join([self.value, " is not a supported word for configuration files"])