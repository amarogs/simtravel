import numpy as np
import matplotlib.pyplot as plt


city_size = np.array([36, 72 , 108])

x = np.linspace(0,3*len(city_size),len(city_size))

# Conpute the data to be plotted from the elapsed time measured.
elapsed_python = np.load("Tests/acceleration/elapsed_python.npy") 
elapsed_python = np.min(elapsed_python, axis=1)

reference = elapsed_python/elapsed_python

elapsed_cython = np.load("Tests/acceleration/elapsed_cython.npy") 
elapsed_cython = np.min(elapsed_cython, axis=1)
acc_cython = elapsed_python/elapsed_cython

elapsed_all = np.load("Tests/acceleration/elapsed_full.npy")
elapsed_all = np.min(elapsed_all, axis=1) 
acc_all = elapsed_python/elapsed_all

#
plt.figure(figsize=(5,4))
# Plot the data into a bar plot.
plt.bar(x -1, reference,width=1, label="Python puro", color="#F4CA9F")
plt.bar(x, acc_cython, width=1, label="Cython algunas partes", color="#3E8D7E"), 
plt.bar(x+1, acc_all, width=1, label="Cython en todo", color="#C95813")

# Configure the axis
plt.xticks(ticks=x, labels=city_size)
plt.xlabel("Longitud de la ciudad")
plt.ylabel("Aceleración respecto a Python puro")
plt.legend(fontsize="x-small")

plt.tight_layout()

plt.show()
