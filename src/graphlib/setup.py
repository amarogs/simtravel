from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize


ext_type = Extension("pygraphFunctions",
                     sources=["pygraphFunctions.pyx",
                              "astarlattice.c"], include_dirs=["."])

setup(name="pygraphFunctions",
      ext_modules=cythonize([ext_type]))
