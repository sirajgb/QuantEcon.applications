"""
Filename: log_linear_growth_model.py
Authors: John Stachurski, Thomas Sargent

The log linear growth model, wrapped as classes.  For use with the
optgrowth.py module.
"""

import numpy as np
import matplotlib.pyplot as plt
from optgrowth import bellman_operator
from quantecon import compute_fixed_point
from joblib import Memory

memory = Memory(cachedir='./joblib_cache')

@memory.cache
def compute_value_function_cached(grid, beta, alpha, shocks):
    """
    Compute the value function by iterating on the Bellman operator.
    The work is done by QuantEcon's compute_fixed_point function.
    """
    Tw = np.empty(len(grid))
    initial_w = 5 * np.log(grid) - 25

    v_star = compute_fixed_point(bellman_operator, 
            initial_w, 
            1e-4,  # error_tol
            100,   # max_iter
            True,  # verbose
            5,     # print_skip
            grid,
            beta,
            np.log,
            lambda k: k**alpha,
            shocks,
            Tw=Tw,
            compute_policy=False)
    return v_star


class LogLinearGrowthModel:
    """
    Stores parameters and computes solutions for the basic log utility / Cobb
    Douglas production growth model.  Shocks are lognormal.
    """
    def __init__(self, 
            alpha=0.65,         # Productivity parameter
            beta=0.95,          # Discount factor
            mu=1,               # First parameter in lognorm(mu, sigma)
            sigma=0.1,          # Second parameter in lognorm(mu, sigma)
            grid_max=8, 
            grid_size=150):

        self.alpha, self.beta, self.mu, self.sigma = alpha, beta, mu, sigma
        self.grid = np.linspace(1e-6, grid_max, grid_size)
        self.shocks = np.exp(mu + sigma * np.random.randn(250))

    def compute_value_function(self, show_plot=False):
        """
        Calls compute_value_function_cached and optionally adds a plot.
        """
        v_star = compute_value_function_cached(self.grid, 
                                                   self.beta,
                                                   self.alpha,
                                                   self.shocks)
        if show_plot:
            fig, ax = plt.subplots()
            ax.plot(self.grid, v_star, lw=2, alpha=0.6, label='value function')
            ax.legend(loc='lower right')
            plt.show()

        return v_star

    def compute_greedy(self, w=None, show_plot=False):
        """
        Compute the w-greedy policy on the grid points given w
        (the value of the input function on grid points).  If w is not
        supplied, use the approximate optimal value function.
        """
        if w is None:
            w = self.compute_value_function()

        Tw, sigma = bellman_operator(w, 
                                    self.grid,  
                                    self.beta,  
                                    np.log,
                                    lambda k: k**self.alpha,
                                    self.shocks,
                                    compute_policy=True)

        if show_plot:
            fig, ax = plt.subplots()
            ax.plot(self.grid, sigma, lw=2, alpha=0.6, label='approximate policy function')
            cstar = (1 - self.alpha * self.beta) * self.grid
            ax.plot(self.grid, cstar, lw=2, alpha=0.6, label='true policy function')
            ax.legend(loc='upper left')
            plt.show()

        return sigma

