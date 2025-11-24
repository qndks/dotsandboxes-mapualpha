from setuptools import setup, Extension
import pybind11

include_dirs = [
    pybind11.get_include(),
    pybind11.get_include(user=True),
    "."
]

ext_modules = [
    Extension(
        "MapuAlpha",            
        ["main.cpp", "DotsAndBoxesState.cpp", "common.cpp"],    
        include_dirs=include_dirs,
        language="c++",
        extra_compile_args = [
            "-O3",
            "-std=c++17",
        ]
    ),
]

setup(
    name="MapuAlpha",
    version="0.0.1",
    ext_modules=ext_modules,
)