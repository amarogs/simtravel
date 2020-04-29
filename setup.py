from distutils.core import setup
from distutils.extension import Extension
from Cython.Build import cythonize
import os


cythonize_folders = ["metrics", "models", "simulator", "analysis", "app"]
ext_modules = []
split_by = "/"
if os.name != 'posix':
    split_by = "\\"

for folder in cythonize_folders:
    path = os.path.join(".", "src", folder )
    files = list(filter(lambda x: not x.startswith("_") and (x[-3::]== ".py" or x[-3::]=="pyx"), os.listdir(path)))

    for source_file in files:
        source_file_path = os.path.join(path, source_file)
        module_name = source_file_path.split(".")[1][1::].replace(split_by, ".")
        print("Creating {} with files: {}".format(module_name, source_file_path))
        ext_modules.append(Extension(module_name, [source_file_path]))

setup(
    name="simtravel",
    version="1.0",
    author="Amaro Garcia-Suarez",
    author_email="amagarsua@alum.us.es",
    ext_modules=cythonize(ext_modules))