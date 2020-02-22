from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
import numpy as np
import time

from env import Car, Wall

class Run(QThread):
    sig_paint_car = pyqtSignal(list, list, list, float )
    sig_paint_init = pyqtSignal(list, list, tuple)
    sig_collide = pyqtSignal()        
    sig_log = pyqtSignal(dict)
    def __init__(self, dataset, rbfn = None, exist_path = None):
        super().__init__()
        self.rbfn = rbfn
        self.dataset = dataset
        self.exist_path = exist_path
        for key, value in self.dataset.items():
            if type(value) is list: self.dataset[key] = [tuple(map(float, v)) for v in value]
            elif type(value) is tuple: self.dataset[key] = tuple(map(float, value))
            else : self.dataset[key] = float(value)
        self.log = {
                'x': [],
                'y': [],
                'front dist': [],
                'rignt dist': [],
                'left dist': [],
                'ouput wheel angle': []
                }
        self.car = Car(dataset['start_pos'],dataset['start_wheel_angle'])
        self.walls = []
        for end in dataset['walls'][:-1]:
            i = dataset['walls'].index(end) + 1
            end2 = dataset['walls'][i]            
            self.walls.append(Wall(end, end2))
        self.exit = False
        self.pause = False
        
    def run(self):
        delay_time = 0.1
        finish_line_x = (self.dataset['finishline_l'][0], self.dataset['finishline_r'][0])
        finish_line_y = (self.dataset['finishline_r'][1], self.dataset['finishline_l'][1])
        radar_inters = []
        radar_dists = []
        system_output = 90
        self.sig_paint_init.emit(self.car.get_pos_angle(), self.dataset['walls'], (self.dataset['finishline_l'],self.dataset['finishline_r']) )
        while True:
            if (finish_line_x[0] < self.car.pos[0] < finish_line_x[1]) and (finish_line_y[0] < self.car.pos[1] < finish_line_y[1] ):
                self.exit = True
            if self.car.check_collide(self.walls[:-1]):
                self.sig_collide.emit()
                self.exit = True
            if self.exit:
                break
            if self.pause:
                continue
            time.sleep(delay_time)

            sensor_result = self.car.sensor_dist(self.walls)
            front_dist = sensor_result[0][1]
            left_dist = sensor_result[1][1]
            right_dist = sensor_result[2][1]
            radar_inters = [sensor_result[0][0],sensor_result[1][0],sensor_result[2][0]]
            radar_dists = [front_dist, right_dist, left_dist]

            if self.rbfn.data_dim == 3:
                system_output = self.rbfn.output(radar_dists)
            else:
                radar_dists.insert(0, self.car.pos[1])
                radar_dists.insert(0, self.car.pos[0])
                system_output = self.rbfn.ouput(radar_dists)

            self.log['x'].append(self.car.pos[0])
            self.log['y'].append(self.car.pos[1])
            self.log['front dist'].append(sensor_result[0][1])
            self.log['rignt dist'].append(sensor_result[2][1])
            self.log['left dist'].append(sensor_result[2][1])
            self.log['ouput wheel angle'].append(system_output)

            self.sig_paint_car.emit(self.car.get_pos_angle(), radar_inters, radar_dists, system_output)
            self.car.move(system_output)
        self.sig_log.emit(self.log)
    @pyqtSlot()
    def paused(self):
        self.pause = not self.pause
    @pyqtSlot()
    def stop(self):
        self.exit = True
    def sig_connect(self, p_init, p_car, collide, log):
        self.sig_paint_car.connect(p_car)
        self.sig_paint_init.connect(p_init)
        self.sig_collide.connect(collide)
        self.sig_log.connect(log)