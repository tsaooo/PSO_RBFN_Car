import numpy as np
import random
class Particle:
    def __init__(self, m_range, data_dim, num_neuron, dev_max, rbfn, train_data, V_max=10):
        self.rbfn = rbfn
        self.train_data = train_data
        self.position_limit = wrapper(num_neuron, dev_max, m_range, data_dim)

        pos = np.random.uniform(-1,1,num_neuron)
        pos = np.append(pos, np.random.uniform(*m_range, data_dim*(num_neuron-1)))
        pos = np.append(pos, np.random.uniform(0, dev_max ,num_neuron-1))
        self.position = pos
        self.experience = self.position

        self.V_max = V_max
        self.velocity = np.random.uniform(-self.V_max, self.V_max, len(self.position))

        self.fitness = self.__fitting_func(rbfn, train_data)
        self.best_fitness = self.fitness

    def __fitting_func(self, rbfn, train_data):
        rbfn.update_parameters(self.position)
        sum_val = sum(abs(data["label"] - rbfn.output(data["data"])) for data in train_data)
        return sum_val/len(train_data)
    def update_fitness(self):
        self.fitness = self.__fitting_func(self.rbfn, self.train_data)
        if self.fitness < self.best_fitness:
            self.best_fitness = self.fitness
            self.experience = self.position
        return self.fitness
    def update_position(self, w, c, s, g_best):
        self.velocity = w*self.velocity + c*random.uniform(0,1)*(self.experience - self.position) + s*random.uniform(0,1)*(g_best - self.position)
        np.clip(self.velocity, -self.V_max, self.V_max, out=self.velocity)
        self.position += self.velocity
        self.position = self.position_limit(self.position)

def wrapper(num_neuron, dev_max, m_range, data_dim):
    def __position_limit(position):
        np.clip(position[:num_neuron],-1,1, out=position[:num_neuron])
        np.clip(position[num_neuron:-(num_neuron-1)],*m_range, out=position[num_neuron:-(num_neuron-1)])
        np.clip(position[-(num_neuron-1):],0,dev_max, out=position[-(num_neuron-1):])
        return position
    return __position_limit