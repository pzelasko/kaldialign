#!/usr/bin/env python3

import os
import platform
import re
import sys
from pathlib import Path

import setuptools
from setuptools.command.build_ext import build_ext

cur_dir = os.path.dirname(os.path.abspath(__file__))


def is_windows():
    return platform.system() == "Windows"


def cmake_extension(name, *args, **kwargs) -> setuptools.Extension:
    kwargs["language"] = "c++"
    sources = []
    return setuptools.Extension(name, sources, *args, **kwargs)


class BuildExtension(build_ext):
    def build_extension(self, ext: setuptools.extension.Extension):
        build_dir = self.build_temp
        os.makedirs(build_dir, exist_ok=True)

        # build/lib.linux-x86_64-3.8
        os.makedirs(self.build_lib, exist_ok=True)

        kaldialign_dir = os.path.dirname(os.path.abspath(__file__))
        install_dir = Path(self.build_lib).resolve() / "kaldialign"

        cmake_args = os.environ.get("KALDIALIGN_CMAKE_ARGS", "")
        make_args = os.environ.get("KALDIALIGN_MAKE_ARGS", "")
        system_make_args = os.environ.get("MAKEFLAGS", "")

        if cmake_args == "":
            cmake_args = "-DCMAKE_BUILD_TYPE=Release"

        extra_cmake_args = f" -DCMAKE_INSTALL_PREFIX={install_dir}"

        if make_args == "" and system_make_args == "":
            print("For fast compilation, run:")
            print('export KALDIALIGN_MAKE_ARGS="-j"; python setup.py install')
            make_args = "-j4"
            print("Setting make_args to '-j4'")

        if "PYTHON_EXECUTABLE" not in cmake_args:
            print(f"Setting PYTHON_EXECUTABLE to {sys.executable}")
            cmake_args += f" -DPYTHON_EXECUTABLE={sys.executable}"

        cmake_args += extra_cmake_args

        if not is_windows():
            build_cmd = f"""
                cd {self.build_temp}

                cmake {cmake_args} {kaldialign_dir}

                make {make_args} install
            """
            print(f"build command is:\n{build_cmd}")

            ret = os.system(build_cmd)
            if ret != 0:
                raise Exception(
                    "\nBuild kaldialign failed. Please check the error message.\n"
                    "You can ask for help by creating an issue on GitHub.\n"
                    "\nClick:\n"
                    "    https://github.com/pzelasko/kaldialign/issues/new\n"
                )
            return

        # for windows
        build_cmd = f"""
            cmake {cmake_args} -B {self.build_temp} -S {cur_dir}
            cmake --build {self.build_temp} --target install --config Release -- -m
        """
        print(f"build command is:\n{build_cmd}")

        ret = os.system(f"cmake {cmake_args} -B {self.build_temp} -S {cur_dir}")
        if ret != 0:
            raise Exception("Failed to build kaldialign")

        ret = os.system(
            f"cmake --build {self.build_temp} --target install --config Release -- -m"
        )
        if ret != 0:
            raise Exception("Failed to build kaldialign")


def read_long_description():
    with open("README.md", encoding="utf8") as f:
        readme = f.read()
    return readme


def get_package_version():
    with open("CMakeLists.txt") as f:
        content = f.read()

    latest_version = re.search(r"set\(KALDIALIGN_VERSION (.*)\)", content).group(1)
    latest_version = latest_version.strip('"')
    return latest_version


with open("kaldialign/__init__.py", "a") as f:
    f.write(f"__version__ = '{get_package_version()}'\n")


setuptools.setup(
    name="kaldialign",
    version=get_package_version(),
    author="Piotr Żelasko",
    author_email="pzelasko@jhu.edu",
    package_dir={
        "kaldialign": "kaldialign",
    },
    packages=["kaldialign"],
    url="https://github.com/pzelasko/kaldialign",
    description="Kaldi alignment methods wrapped into Python",
    long_description=read_long_description(),
    long_description_content_type="text/markdown",
    ext_modules=[cmake_extension("_kaldialign")],
    cmdclass={"build_ext": BuildExtension},
    keywords=[
        "natural language processing",
        "speech recognition",
        "machine learning",
    ],
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    zip_safe=False,
    license="Apache licensed, as found in the LICENSE file",
)

# remove the line __dev_version__ from k2/python/k2/__init__.py
with open("kaldialign/__init__.py", "r") as f:
    lines = f.readlines()

with open("kaldialign/__init__.py", "w") as f:
    for line in lines:
        if "__version__" not in line:
            f.write(line)
