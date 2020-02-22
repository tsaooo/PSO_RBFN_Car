from PyQt5.QtCore import pyqtSignal, pyqtSlot, QThread
import numpy as np
import random
import math
import copy
from particle import Particle
from IPython import embed

class PSO(QThread):
    sig_train_detail = pyqtSignal(int, float, float, float)
    def __init__(self, train_data, iter_times, population_len, mean_range, inertia_weight, social_weight, cognitive_weight, rbfn):
        super().__init__()
        self.train_data = train_data
        self.iter_times = iter_times
        self.population_len = population_len
        self.optimized = rbfn

        self.inertia_weight = inertia_weight
        self.social_weight = social_weight
        self.cognitive_weight = cognitive_weight

        self.dev_max = rbfn.dev_max
        self.m_range = mean_range
        self.num_rbfn_neuron = self.optimized.num_neuron
        self.data_dim = self.optimized.data_dim
        self.population = []

        self.exit = False

    def run(self):
        for _ in range(self.population_len):
            self.population.append(Particle(self.m_range, self.data_dim, self.num_rbfn_neuron, self.dev_max, self.optimized, self.train_data))
        min_err = math.inf
        self.best_individual = copy.deepcopy(self.population[0])
        self.g_best = self.best_individual
        for t in range(self.iter_times):
            if self.exit:
                break
            self.update_best_fitness()
            min_err = self.best_individual.fitness
            self.sig_train_detail.emit(t+1, min_err, self.g_best.fitness, self.avg_err)

            for individual in self.population:
                individual.update_position(self.inertia_weight, self.cognitive_weight, self.social_weight, self.best_individual.position)

        self.update_best_fitness()
        self.sig_train_detail.emit(t+1, min_err, self.g_best.fitness, self.avg_err)
        
        self.optimized.update_parameters(self.best_individual.position)

    def update_best_fitness(self):
        sum_err = 0
        for individual in self.population:
            sum_err += individual.update_fitness()
            self.g_best = min(self.g_best, individual, key = lambda x: x.fitness)
        self.avg_err = sum_err/self.population_len
        if self.best_individual.fitness > self.g_best.fitness:
            self.best_individual = copy.deepcopy(self.g_best)
    @pyqtSlot()
    def stop(self):
        self.exit = True