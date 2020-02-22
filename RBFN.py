import random
import math
import numpy as np

class RBFN:
    def __init__(self, num_neuron, data_dim):
        self.num_neuron = num_neuron + 1
        self.data_dim = data_dim
        self.dev_max = 15
        self.list_neuron = [G_neuron(self.data_dim, is_constant=True if j == 0 else False, dev_max = self.dev_max) 
                            for j in range(self.num_neuron)]

    def output(self, data):
        def denormalize(val):
            return max(min(40*val, 40), -40)

        data = np.asarray(data)
        if len(data) != self.data_dim:
            raise IndexError("data dimention must be %d, while it's %d" %(self.data_dim, len(data)))
        out = 0
        for neuron in self.list_neuron:
           out += neuron.output(data)
        return denormalize(out)
    def update_parameters(self, parameters):
        '''
        parameters: parameters of RBFN which been optimized by GA
            ( w0, w1 ,w2 , …, wj , m11, …, m1i, m21, …, m2i, …, mj1,…, mji, σ1, σ2, …, σj)
        '''
        self.list_neuron[0].weight = parameters[0]
        weights = parameters[1:self.num_neuron]
        means = parameters[self.num_neuron : -(self.num_neuron-1)]
        devs = parameters[-(self.num_neuron-1):]
        
        weight_neurons = self.list_neuron[1:]
        for i in range(self.num_neuron-1):
            weight_neurons[i].weight = weights[i]
            weight_neurons[i].means = np.asarray(means[i*self.data_dim : (i+1)*self.data_dim])
            weight_neurons[i].dev = devs[i]
    def load_parameters(self, parameters):
        '''
        parameters: (w0, w1, m11, m12,.. σ1, w2, m21, m22, ... ,σ2... wj, mj1, ... σj)
        '''
        if len(parameters) != self.num_neuron:
            raise IndexError("neuron num incorrect")
        if len(parameters[1]) != self.data_dim + 2:
            raise IndexError("data dim incorrect")
        else:
            self.list_neuron[0].weight = parameters[0][0]
            parameters = parameters[1:]
            for n, neuron in enumerate(self.list_neuron[1:]):
                neuron.weight = parameters[n][0]
                neuron.means = np.asarray(parameters[n][1:-1])
                neuron.dev = parameters[n][-1]
class G_neuron:
    def __init__(self, data_dim, dev_max, means=None, is_constant = False):
        self.is_constant = is_constant
        self.data_dim = data_dim
        if not self.is_constant:
            self.means = means 
            self.dev_max = dev_max
            self.dev = random.uniform(0, self.dev_max)
        else:
            self.means = None
            self.dev = None
        self.weight = random.uniform(-1,1)

    def output(self, data):
        if self.is_constant:
            return self.weight
        else:
            if self.means is None: 
                self.means = np.random.uniform(-40, 40, size=self.data_dim)
            return self.weight*self.__Gaussian_kernel(data)
        
    def __Gaussian_kernel(self, data):
        if self.dev == 0:
            return 0
        else:
            return math.exp(-(data-self.means).dot(data-self.means)/(2*self.dev**2))
        