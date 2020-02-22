from PyQt5.QtWidgets import (QFrame, QHBoxLayout, QVBoxLayout,
                            QGroupBox, QPushButton, QComboBox,QStackedWidget,
                            QFormLayout, QLabel, QSlider, QSpinBox, QDoubleSpinBox, QFileDialog,
                            QProgressBar)
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt
from os.path import join

from simulator import Run
from RBFN import RBFN
from pso import PSO 
from pathlib import Path

class Information_frame(QFrame):
    def __init__(self, display):
        super().__init__()
        self.display_frame = display
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.load_map()
        self.load_data()
        self.thread_running = False
        self.trainning_option()
        self.running_option()
        self.PSO_RBFN_setting()
        self.trian_detail_setting()
        self.monitor_setting()
        self.__init_controller()
        self.running_threads = []
        self.rbfn = None
    def running_option(self):
        self.run_group = []
        group = QGroupBox("Simulation option")
        group_layout = QHBoxLayout()
        group.setLayout(group_layout)

        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self.start_simulation)
        self.pause_btn = QPushButton("Pause")
        self.pause_btn.setDisabled(True)
        self.stop_btn = QPushButton("Stop")
        self.stop_btn.setDisabled(True)

        self.save_btn = QPushButton("Save")
        self.save_btn.clicked.connect(self.save_data)
        self.save_btn.setDisabled(True)

        self.run_group.append(self.run_btn)
        self.run_group.append(self.pause_btn)
        self.run_group.append(self.stop_btn)
        self.run_group.append(self.save_btn)
        group_layout.addWidget(self.run_btn)
        group_layout.addWidget(self.pause_btn)
        group_layout.addWidget(self.stop_btn)
        group_layout.addWidget(self.save_btn)
        self.layout.addWidget(group)
    def trainning_option(self):
        self.train_group = []
        group = QGroupBox("Trainning option")
        group_layout = QHBoxLayout()
        group.setLayout(group_layout)

        self.train_btn = QPushButton("Train")
        self.train_btn.clicked.connect(self.start_tranning)
        self.stop_train_btn = QPushButton("Stop")
        self.stop_train_btn.setDisabled(True)
        self.save_param_btn = QPushButton("Save")
        self.save_param_btn.clicked.connect(self.save_params)
        self.save_param_btn.setEnabled(False)
        self.load_params_btn = QPushButton("Load")
        self.load_params_btn.clicked.connect(self.load_params)
        self.trainning_data_selector = QComboBox()
        self.trainning_data_selector.addItems(self.train_dataset.keys())
        
        self.train_group.append(self.train_btn)
        self.train_group.append(self.stop_train_btn)
        self.train_group.append(self.save_param_btn)
        self.train_group.append(self.trainning_data_selector)
        self.train_group.append(self.load_params_btn)
        group_layout.addWidget(self.train_btn)
        group_layout.addWidget(self.stop_train_btn)
        group_layout.addWidget(self.save_param_btn)
        group_layout.addWidget(self.load_params_btn)
        group_layout.addWidget(self.trainning_data_selector)
        

        self.layout.addWidget(group)
    def PSO_RBFN_setting(self):
        group = QGroupBox("GA parameters setting")
        group_layout = QFormLayout()
        group.setLayout(group_layout)
        self.iter_times = QSpinBox()
        self.iter_times.setRange(1,1000)
        self.iter_times.setValue(100)

        self.population_size = QSpinBox()
        self.population_size.setRange(1, 500)
        self.population_size.setValue(100)

        self.inertia_weight = QDoubleSpinBox()
        self.inertia_weight.setRange(0,1.5)
        self.inertia_weight.setValue(1.0)
        self.inertia_weight.setSingleStep(0.1)

        self.cognitive_weight = QDoubleSpinBox()
        self.cognitive_weight.setRange(0,5)
        self.cognitive_weight.setValue(2)
        self.cognitive_weight.setSingleStep(0.5)

        self.social_weight = QDoubleSpinBox()
        self.social_weight.setRange(0,5)
        self.social_weight.setValue(2)
        self.social_weight.setSingleStep(0.5)
        
        self.num_neuron = QSpinBox()
        self.num_neuron.setRange(1, 100)
        self.num_neuron.setValue(3)
        
        group_layout.addRow(QLabel("iterate times : "), self.iter_times)
        group_layout.addRow(QLabel("population size : "), self.population_size)
        group_layout.addRow(QLabel("inertia factor : "), self.inertia_weight)
        group_layout.addRow(QLabel("cognitive weight upper bound : "), self.cognitive_weight)
        group_layout.addRow(QLabel("social weight upper bound : "), self.social_weight)
        group_layout.addRow(QLabel("number of neuron : "), self.num_neuron)
        
        group.setLayout(group_layout)
        self.layout.addWidget(group)
    def trian_detail_setting(self):
        group = QGroupBox("Trainning detail for single iteration")
        group_layout = QFormLayout()

        self.current_iter = QLabel("0")
        self.min_error = QLabel("0.0")
        self.Gbest_error = QLabel("0.0")
        self.average_error = QLabel("0.0")
        self.train_progress = QProgressBar()
        self.current_iter.setAlignment(Qt.AlignCenter)
        self.Gbest_error.setAlignment(Qt.AlignCenter)
        self.min_error.setAlignment(Qt.AlignCenter)
        self.average_error.setAlignment(Qt.AlignCenter)

        group_layout.addRow(QLabel("Current iteration : "), self.current_iter)
        group_layout.addRow(QLabel("iter Min error : "), self.min_error)
        group_layout.addRow(QLabel("Swarm min error : "), self.Gbest_error)
        group_layout.addRow(QLabel("Average error of swarm : "), self.average_error)
        group_layout.addRow(self.train_progress)
        group.setLayout(group_layout)
        self.layout.addWidget(group)
    def monitor_setting(self):
        group = QGroupBox("Simulation imformation")
        group_layout = QFormLayout()

        self.l_car_pos = QLabel("0 , 0")
        self.l_front_dist = QLabel("0.0")
        self.label_l_dist = QLabel("0.0")
        self.label_r_dist = QLabel("0.0")
        self.l_car_angle = QLabel("0.0")
        self.l_wheel_angle = QLabel("0.0")

        self.l_car_pos.setAlignment(Qt.AlignCenter)
        self.l_front_dist.setAlignment(Qt.AlignCenter)
        self.label_l_dist.setAlignment(Qt.AlignCenter)
        self.label_r_dist.setAlignment(Qt.AlignCenter)
        self.l_car_angle.setAlignment(Qt.AlignCenter)
        self.l_wheel_angle.setAlignment(Qt.AlignCenter)
        group_layout.addRow(QLabel("Car position :"), self.l_car_pos)
        group_layout.addRow(QLabel("Car angle :"), self.l_car_angle)
        group_layout.addRow(QLabel("Front distance :"), self.l_front_dist)
        group_layout.addRow(QLabel("Left side distance :"), self.label_l_dist)
        group_layout.addRow(QLabel("Right side distance :"), self.label_r_dist)
        group_layout.addRow(QLabel("Wheel angle :"), self.l_wheel_angle)

        group.setLayout(group_layout)
        self.layout.addWidget(group)

    @pyqtSlot()
    def start_tranning(self):
        @pyqtSlot()
        def train_settting():
            for obj in self.run_group:
                obj.setDisabled(True)
            self.train_btn.setDisabled(True)
            self.stop_train_btn.setEnabled(True)

        self.train_progress.setMaximum(self.iter_times.value())
        current_data = self.trainning_data_selector.currentText()
        train_data = self.train_dataset[current_data]
        m_range = ( min(min(data["data"]) for data in train_data), max(max(data["data"]) for data in train_data))

        self.rbfn = RBFN(self.num_neuron.value(), len(train_data[0]["data"]))
        self.trainning_thread = PSO(train_data, self.iter_times.value(), self.population_size.value(), m_range, self.inertia_weight.value(),
                                    self.social_weight.value(), self.cognitive_weight.value(), self.rbfn)

        self.trainning_thread.sig_train_detail.connect(self.show_train_detail)
        self.stop_train_btn.clicked.connect(self.trainning_thread.stop)
        self.trainning_thread.started.connect(train_settting)
        self.trainning_thread.finished.connect(self.__reset_controller)

        self.running_threads.append(self.trainning_thread)
        self.thread_running = True
        self.trainning_thread.start()
        
    @pyqtSlot()
    def start_simulation(self):
        @pyqtSlot()
        def simulate_setting():
            for obj in self.train_group:
                obj.setDisabled(True)
            self.run_btn.setDisabled(True)
            self.pause_btn.setEnabled(True)
            self.stop_btn.setEnabled(True)
            self.save_btn.setDisabled(True)

        self.simulator_thread = Run(dataset = self.map, rbfn = self.rbfn)
        self.pause_btn.clicked.connect(self.simulator_thread.paused)
        self.stop_btn.clicked.connect(self.simulator_thread.stop)
        self.simulator_thread.started.connect(simulate_setting)
        self.simulator_thread.finished.connect(self.__reset_controller)
        self.simulator_thread.sig_connect(p_init = self.display_frame.init_walls, 
                                        p_car = self.move_car,
                                        collide = self.display_frame.collide,
                                        log = self.simulation_log)

        self.running_threads.append(self.simulator_thread)
        self.thread_running = True
        self.simulator_thread.start()

    def __init_controller(self):
        for widget in self.run_group:
            widget.setDisabled(True)
        self.stop_train_btn.setDisabled(True)
        self.save_param_btn.setDisabled(True)

    @pyqtSlot()
    def __reset_controller(self):
        self.simulate_allow = True if self.train_progress.value() == self.train_progress.maximum() else False
        for widget in self.run_group:
            widget.setEnabled(self.simulate_allow)
        for widget in self.train_group:
            widget.setEnabled(True)
        self.pause_btn.setDisabled(True)
        self.stop_btn.setDisabled(True)
        self.stop_train_btn.setDisabled(True)

    @pyqtSlot(int, float, float, float)
    def show_train_detail(self, time, min_err, gbest_err, avg_err):
        self.current_iter.setText(str(time))
        self.min_error.setText(str(min_err))
        self.Gbest_error.setText(str(gbest_err))
        self.average_error.setText(str(avg_err))
        self.train_progress.setValue(time)
    @pyqtSlot(list, list, list, float)
    def move_car(self, pos_angle, inters, dists, wheel_ouput):
        self.l_car_pos.setText("{:.3f},{:.3f}".format(*pos_angle[:2]))
        self.l_car_angle.setText(str(pos_angle[2]))
        self.l_front_dist.setText(str(dists[0]))
        self.label_r_dist.setText(str(dists[1]))
        self.label_l_dist.setText(str(dists[2]))
        self.l_wheel_angle.setText(str(wheel_ouput))

        self.display_frame.update_car(pos_angle, inters)
    @pyqtSlot(dict)
    def simulation_log(self, log):
        #TODO:
        self.log = log
        self.display_frame.show_path(self.log['x'], self.log['y'])
    @pyqtSlot()
    def save_data(self):
        #TODO:
        save_dir = QFileDialog.getExistingDirectory(self, 'Save As')
        path_4d = join(save_dir, 'train4D.txt')
        path_6d = join(save_dir, 'train6D.txt')
        data_lines = list(zip(*self.log.values()))
        with open(path_6d, 'w') as f6d:
            for line in data_lines:
                f6d.write("{:.3f} {:.3f} {:.3f} {:.3f} {:.3f} {:.3f}\n".format(
                    line[0], line[1], line[2], line[3], line[4], line[5]))
        
        with open(path_4d, 'w') as f4d:
            for l in data_lines:
                f4d.write("{:.3f} {:.3f} {:.3f} {:.3f}\n".format(
                    l[2], l[3], l[4], l[5]))
    @pyqtSlot()
    def save_params(self):
        save_dir = QFileDialog.getExistingDirectory(self, 'Save As')
        params_path = join(save_dir, "RBFN model params.txt")
        with open(params_path, 'w') as f:
            f.write("{:.3f}\n".format(self.rbfn.list_neuron[0].weight))
            for neuron in self.rbfn.list_neuron[1:]:
                f.write("{:.3f} ".format(neuron.weight))
                for mean in neuron.means:
                    f.write("{:.3f} ".format(mean))
                f.write("{:.3f}\n".format(neuron.dev))
    @pyqtSlot()
    def load_params(self):
        load_dir = QFileDialog.getOpenFileName(self, 'RBFN params file')[0]
        if(load_dir != ''):
            params = []
            with open(load_dir, 'r', encoding = 'utf8') as f:
                for line in f:
                    neuron_param = list(map(float, line.strip().split()))
                    params.append(neuron_param)
            num_neuron = len(params)
            data_dim = len(params[-1]) - 2

            if self.rbfn == None:
                self.rbfn = RBFN(num_neuron - 1 , data_dim)
            self.rbfn.load_parameters(params)
            self.train_progress.setValue(self.train_progress.maximum())
            self.__reset_controller() 
    def load_map(self, map_path = './maps/case01.txt'):
        data = []
        with open(map_path, 'r', encoding = 'utf8') as f:
            for line in f:
                data.append(tuple(line.strip().split(',')))
        self.map = {
            "start_pos" : data[0][:2],
            "start_wheel_angle" : data[0][2],
            "finishline_l" : data[1],
            "finishline_r" : data[2],
            "walls" : data[3:]
        }
    def load_data(self, folderpath = 'data'):
        self.train_dataset = {}
        folderpath = Path(folderpath)
        for f in folderpath.glob("*.txt"):
            with f.open() as data:
                content = []
                for line in data:
                    raw = tuple( map(float, line.strip().split()) )
                    content.append( { 'data': raw[:-1], 'label':raw[-1] })
            self.train_dataset[f.stem] = content
    
        

        



