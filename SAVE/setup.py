from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize


setup(
    ext_modules=cythonize([
        Extension("src.simulator.simulator", ["src/simulator/simulator.pyx"]), Extension(
            "src.simulator.cythonGraphFunctions", ["src/simulator/cythonGraphFunctions.pyx"]),
        Extension("src.simulator.simulation", ["src/simulator/simulation.pyx"]), 
        Extension("src.models.cities", ["src/models/cities.pyx"])
    ])
)
