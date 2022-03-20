import yaml
import scipy.stats as stats
import matplotlib.pyplot as plt
import numpy as np

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
        # "constant":Constant,
        "binomial":stats.bernoulli,
        # "timer": Timer
    }
dists = []

if __name__ == '__main__':
    stream = open("config.yaml", 'r')
    dictionary = yaml.safe_load(stream)

    for system, params in dictionary['systems'].items():
        for key, value in params.items():
            if params[key]['name'] == 'gaussian':
                dist = _distributions[params[key]['name']](loc=params[key]['parameters']['mu'], scale=params[key]['parameters']['sigma'])
                dists.append([key, dist])
            elif params[key]['name'] == 'skew-norm':
                dist = _distributions[params[key]['name']](params[key]['parameters']['a'], loc=params[key]['parameters']['mu'], scale=params[key]['parameters']['sigma'])
                dists.append([key, dist])


fig, ax = plt.subplots(1, 1)
x = np.linspace(0, 10, 1000)

for param, dist in dists:
    ax.plot(x, dist.pdf(x), label=param)

ax.legend()
plt.show()