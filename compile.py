from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import os


cythonize_folders = ["metrics", "models", "simulator"]
ext_modules = []

for folder in cythonize_folders:
    path = os.path.join(".", "src", folder )
    files = list(filter(lambda x: not x.startswith("_") and (x[-3::]== ".py" or x[-3::]=="pyx"), os.listdir(path)))

    for source_file in files:
        source_file_path = os.path.join(path, source_file)
        module_name = source_file_path.split(".")[1][1::].replace("\\", ".")
        print("Creating {} with files: {}".format(module_name, source_file_path))
        ext_modules.append(Extension(module_name, [source_file_path]))

setup(ext_modules=cythonize(ext_modules))