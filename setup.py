from sysconfig import get_path

from pybind11 import get_include
from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

ext_modules = [
    Pybind11Extension(
        "_kaldialign",
        ["kaldialign/kaldi_align.cpp", "kaldialign/kaldialign.cpp"],
        extra_compile_args=([f"-I{get_include()}", f"-I{get_path('include')}"]),
    ),
]


setup(
    name="kaldialign",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
