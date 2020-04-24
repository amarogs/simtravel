import numpy as np
import matplotlib.pyplot as plt


tam = np.array([36, 72 , 108])
python = np.load("elapsed_python.npy") 
python = np.min(python, axis=1)

n_python = python/python

cython = np.load("elapsed_cython.npy") 
cython = np.min(cython, axis=1)
n_cython = python/cython

full = np.load("elapsed_full.npy")
full = np.min(full, axis=1) 
n_full = python/full

plt.bar(tam, n_python, label="Python puro")
plt.bar(tam+10, n_cython, label="Cython algunas partes")
plt.bar(tam+20, n_full, label="Cython todo")
plt.legend()

plt.show()
