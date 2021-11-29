import json
class MyPoint:
    def __init__(self, _x=0, _y=0):
        self.m_x = _x
        self.m_y = _y

    def setX(self, _x):
        self.m_x = _x

    def setY(self, _y):
        self.m_y = _y

    def getX(self):
        return self.m_x

    def getY(self):
        return self.m_y


class MyCurve:
    def __init__(self, _p1=None, _p2=None):
        self.m_p1 = _p1
        self.m_p2 = _p2

    def setP1(self, _p1):
        self.m_p1 = _p1

    def setP2(self, _p2):
        self.m_p2 = _p2

    def getP1(self):
        return self.m_p1

    def getP2(self):
        return self.m_p2


class MyModel:
    def __init__(self):
        self.grid_points = {} #Apenas pontos que estão dentro dos polígonos
        self.last_pat = None
        self.last_polygon = 0

    def addPoint(self, _p, _pat):
        if(_pat != self.last_pat):
            self.last_pat = _pat
            self.last_polygon += 1
            self.grid_points['polygon'+str(self.last_polygon)] = []

        self.grid_points['polygon'+str(self.last_polygon)].append({'x': _p.x(), 'y': _p.y()})

    def getPoints(self):
        response = []
        for i in range(self.last_polygon + 1):
            if 'polygon'+str(i) in self.grid_points:
                response += self.grid_points['polygon'+str(i)]
        return response

    def export_json(self):
        with open('data.json', 'w', encoding='utf-8') as outfile:
            json.dump(self.grid_points, outfile, ensure_ascii=False, indent=2)
            return True
