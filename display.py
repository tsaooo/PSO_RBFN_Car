import math

import matplotlib.style
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from matplotlib.patches import Circle, Rectangle, Arrow
from matplotlib.lines import Line2D

from PyQt5.QtWidgets import QSizePolicy

matplotlib.style.use('seaborn')
class Plot_canvas(FigureCanvas):
    def __init__(self):
        fig = Figure(figsize = (4,4), dpi = 100)
        self.ax = fig.add_subplot(111)
        super().__init__(fig)
        FigureCanvas.setSizePolicy(self,
                                   QSizePolicy.Expanding,
                                   QSizePolicy.Expanding)
        FigureCanvas.updateGeometry(self)
        self.radars = []
    
    def init_walls(self, pos_angle, ends, fin_pos):
        self.ax.cla()
        self.ax.plot(*zip(*ends), color ='k' )  # zip equals to tranpose, * eauals to depack                     
        finish_area = Rectangle(xy = (fin_pos[0][0],fin_pos[1][1]), 
                                width= fin_pos[1][0] - fin_pos[0][0],
                                height= fin_pos[1][1] - fin_pos[0][1],
                                color = 'red')
        self.ax.add_artist(finish_area)
        pos = tuple(pos_angle[:2])
        angle = math.radians(pos_angle[2])
        self.car = Circle(pos, radius = 3, color = 'mediumblue')
        self.head = Arrow(pos[0], pos[1], dx = 5*math.cos(angle), dy = 5*math.sin(angle),
                        facecolor = 'gold', edgecolor = 'k')
        self.ax.add_artist(self.car)
        self.ax.add_artist(self.head)
        self.draw()
    def update_car(self, pos_angle, inters):
        self.car.remove()
        self.head.remove()

        pos = tuple(pos_angle[:2])
        angle = math.radians(pos_angle[2])
        self.car = Circle(pos, radius = 3, color = 'mediumblue')
        self.head = Arrow(pos[0], pos[1], dx = 5*math.cos(angle), dy = 5*math.sin(angle),
                        facecolor = 'gold', edgecolor = 'k')
        if self.radars:
            for radar in self.radars:
                radar.remove()
        self.radars = [Line2D(*zip(pos,inter), linestyle = '-', color= 'gray') for inter in inters]
        for radar in self.radars:
            self.ax.add_line(radar)
        self.ax.add_artist(self.car)
        self.ax.add_artist(self.head)
        self.draw()
    def collide(self):
        self.car.set_color('darkred')
        self.draw()
    def show_path(self, path_x , path_y):
        self.path = Line2D(path_x, path_y, linewidth = 6, solid_capstyle = 'round', 
                    solid_joinstyle = 'round', alpha = 0.75, color ='gray' )
        self.ax.add_line(self.path)
        self.draw()