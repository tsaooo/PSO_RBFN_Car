import math
import numpy as np

class Car:
    def __init__(self, pos, angle, radius = 3):
        self.pos = np.asarray(pos).astype(float)
        self.angle = float(angle)
        self.radius = float(radius)
    def move(self, wheel_angle):
        c = math.radians(self.angle)
        t = math.radians(wheel_angle)
        self.pos[0] += math.cos(c+t) + math.sin(t)*math.sin(c)     # X-axis
        self.pos[1] += math.sin(c+t) - math.sin(t)*math.cos(c)     # Y-axis
        self.angle -= math.degrees(math.asin(2*math.sin(t)/self.radius))    # delta_angle
    def sensor_dist(self, walls):
        angle_l = math.radians((self.angle + 45)% 360) 
        angle_r = math.radians((self.angle - 45)% 360) 
        angle_f = math.radians((self.angle)% 360)
        sensors = [angle_f, angle_l, angle_r]
        sensor_result = []

        for sensor in sensors:
            inter_dists = []
            for wall in walls:
                inter = wall.radar_intersection(self.pos, sensor)
                if inter is not None:
                    dist = np.linalg.norm(self.pos - inter)
                    inter_dists.append((inter.tolist(), dist))
            min_ = min(inter_dists, key = lambda x: x[1] ) if inter_dists else None
            sensor_result.append(min_)
        return sensor_result
    def check_collide(self, walls):
        for wall in walls:
            dist = wall.car_dist(self.pos)
            if dist <= self.radius:
                return True
        return False
    def get_pos_angle(self):
        pos_angle = self.pos.tolist()
        pos_angle.append(self.angle)
        return pos_angle
                    
class Wall:
    def __init__(self, end, start):
        self.end = np.asarray(end).astype(float)
        self.start = np.asarray(start).astype(float)
        '''
        Wall is simply a line in plane determine by two endpoint 'end' 'start'
        store the line with parameter form p + l*t as well, which 'l' is direction vector determined by start to end
        '''
        self.vector = np.array(self.end - self.start)
    def radar_intersection(self, car_pos, direction):
        '''
        calculate the intersection of wall and sensor radar 

        car_pos : ndarray of the position of car
        direction : in radians
        coef : the coeficient of the parameter form equation
            p1 + l1*t = p2 + l2*s
        '''
        car_pos = np.asarray(car_pos).astype(float)
        vector_radar = np.array([math.cos(direction), math.sin(direction)])
        coefs = np.transpose([vector_radar, np.negative(self.vector)])       # l1*t - l2*s ^T
        if np.linalg.det(coefs) != 0:
            consts = np.array(self.start - car_pos)
            parameters = np.linalg.solve(coefs, consts)
            if(parameters[0] > 0 and 0 < parameters[1] < 1):
                inter = np.array(self.start) + parameters[1]*self.vector
                return inter
        else:
            return None # singular matrix or the intersection we didn't need
    def car_dist(self, pos):
        pos = np.asarray(pos).astype(float)
        n_vector = np.array([self.vector[1], np.negative(self.vector[0])])
        coefs = np.transpose([n_vector, np.negative(self.vector)])        
        consts = np.array(self.start - pos)
        parameters = np.linalg.solve(coefs, consts)
        if(parameters[0] > 0 and 0 < parameters[1] < 1):
            inter = np.array(self.start) + parameters[1]*self.vector
            dist = np.linalg.norm(pos - inter)
        else: dist = 7
        return dist
