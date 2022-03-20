import scipy.stats as stats
import numpy as np


class Constant:
    """ Returns a constant value always """
    def __init__(self, value) -> None:
        self.value = value

    def rvs(self, size):
        return np.ones((size, ))*self.value

class Timer:
    """ Discrete distribution which returns 0 until <steps> steps 
        have been taken then returns 1. Good for modeling constant 
        customer lifetimes"""
    def __init__(self, steps) -> None:
        self.steps = steps

    def rvs(self, size):
        steps -= 1
        return np.ones((size, ))*(self.steps <= 0)


class DiscreteBeta:
    """ Takes a beta distribution and descretises it. Allows for 
        plant requests to have different distributions """
    def __init__(self, alpha, beta, buckets) -> None:
        self.dist = stats.beta(alpha, beta)
        self.buckets = buckets
    
    def rvs(self, size):
        array = self.dist.rvs(size)
        np.fix(array*self.buckets).astype("int32")
        return array

class Distribution:

    _distributions = {
        "beta":stats.beta,
        "erlang":stats.erlang,
        "gaussian":stats.norm,
        "poisson":stats.poisson,
        "uniform":stats.uniform,
        "skew-norm":stats.skewnorm,
        "power":stats.powerlaw,
        "logistic":stats.logistic,
        "lognorm":stats.lognorm,
        "chi2":stats.chi2,
        "constant":Constant,
        "binomial":stats.bernoulli,
        "timer":Timer
    }

    def __init__(self, name, parameters) -> None:
        self.distribution = Distribution._distributions[name](**parameters)
        self.name = name
        self.parameters = parameters

    def get_single(self):
        return self.distribution.rvs(size=1)[0]

    def get_array(self, size):
        if size == 0: return np.array([])
        return self.distribution.rvs(size=size)

    def update_param(self, params):
        self.distribution = Distribution._distributions[self.name](**params)
        self.parameters = params

    