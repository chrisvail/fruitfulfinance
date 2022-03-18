import scipy.stats as stats
import numpy as np


class Constant:
    def __init__(self, value) -> None:
        self.value = value

    def rvs(self, size):
        return np.ones((size, ))*self.value


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
        "constant":Constant
    }

    def __init__(self, name, parameters) -> None:
        self.distribution = Distribution._distributions[name](**parameters)
        self.name = name
        self.parameters = parameters

    def get_single(self):
        return self.distribution.rvs(size=1)[0]

    def get_array(self, size):
        return self.distribution.rvs(size=size)

    def update_param(self, params):
        self.distribution = Distribution._distributions[self.name](**params)
        self.parameters = params

    