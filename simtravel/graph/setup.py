from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize

# setup(
#     ext_modules=cythonize([Extension("pygraphs", ["pygraphs.pyx", "graphs.c"])])
# )



from distutils.core import setup, Extension
from Cython.Build import cythonize

ext_type = Extension("pygraphs",
                     sources=["pygraphs.pyx",
                              "graphs.c"], include_dirs=["."])

setup(name="graphs_prueba",
      ext_modules = cythonize([ext_type]))