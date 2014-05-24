"""
An example of using reproducible for a simple two-step problem.
This code was taken from Greg von Winckel's website:
http://www.scientificpython.net/pyblog/solving-differential-equations-with-the-pseudospectral-method

It solves the ODE
dy/dx + y = exp(-x)
y(0) = 0
on the domain [0, 1]

using a psuedospectral method that represents the solution as a sum of
lagrange interpolating polynomials.

This examples requires numpy and matplotlib.
"""

import numpy as np
from operator import mul
from scipy.linalg import solve
from reproducible import Reproducible
import matplotlib.pyplot as plt

def diffmat(x): # x is an ordered array of grid points
  n = np.size(x)
  e = np.ones((n, 1))
  Xdiff = np.outer(x, e) - np.outer(e, x) + np.identity(n)
  xprod = -reduce(mul,Xdiff) # product of rows
  W = np.outer(1 / xprod, e)
  D = W / (W.T * Xdiff)
  d = 1 - sum(D)
  for k in range(0,n):  # Set diagonal elements
    D[k,k] = d[k]
  return -D.T

def setup_points(data):
    print "Setting up points"
    n = 20
    x = 0.5 * (1 - np.cos(np.pi * np.arange(n + 1) / n))
    data['n'] = n
    data['x'] = x

def assemble_system(data):
    print "Assembling system"
    D = diffmat(data['x'])
    I = np.identity(data['n'] + 1)
    A = D + I
    f = np.exp(-data['x'])
    data['A'] = A
    data['f'] = f

def solve_system(data):
    print "Solving system"
    y = np.zeros(data['n'] + 1)
    y[1:] = solve(data['A'][1:, 1:], data['f'][1:])
    data['y'] = y

def plot_solution(data):
    """
    Plot the final result
    Try changing this plotting function and re-running the code.
    The previous three steps will not be re-run.
    """
    print "Error: " + str(max(abs(data['y'] - data['x'] * data['f'])))
    plt.plot(data['x'], data['y'])
    plt.show()

model = Reproducible("pseudospectral")
model.add_step(setup_points)
model.add_step(assemble_system)
model.add_step(solve_system)
# Using always = True forces the step to run even if the function has
# not changed. This is nice for a plotting function.
model.add_step(plot_solution, always = True)
model.run()

