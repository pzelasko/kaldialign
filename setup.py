from pybind11.setup_helpers import Pybind11Extension, build_ext
from setuptools import setup

ext_modules = [
    Pybind11Extension(
        "_kaldialign",
        ["kaldialign/kaldi_align.cpp", "kaldialign/kaldialign.cpp"],
    ),
]


setup(
    name="kaldialign",
    ext_modules=ext_modules,
    cmdclass={"build_ext": build_ext},
    zip_safe=False,
)
