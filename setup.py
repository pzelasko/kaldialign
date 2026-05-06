#!/usr/bin/env python3

import os
import platform
import re
import shlex
import subprocess
import sys
from pathlib import Path

import setuptools
from setuptools.command.build_ext import build_ext


def is_windows():
    return platform.system() == "Windows"


def cmake_extension(name, *args, **kwargs) -> setuptools.Extension:
    kwargs["language"] = "c++"
    sources = []
    return setuptools.Extension(name, sources, *args, **kwargs)


class BuildExtension(build_ext):
    def build_extension(self, ext: setuptools.extension.Extension):
        build_dir = Path(self.build_temp).resolve()
        os.makedirs(build_dir, exist_ok=True)

        # build/lib.<platform>-<python-version>
        os.makedirs(self.build_lib, exist_ok=True)

        kaldialign_dir = Path(__file__).parent.resolve()
        install_dir = Path(self.build_lib).resolve() / "kaldialign"

        cmake_args = shlex.split(os.environ.get("KALDIALIGN_CMAKE_ARGS", ""))
        make_args = shlex.split(os.environ.get("KALDIALIGN_MAKE_ARGS", ""))
        system_make_args = os.environ.get("MAKEFLAGS", "")

        if not cmake_args:
            cmake_args = ["-DCMAKE_BUILD_TYPE=Release"]

        if not make_args and system_make_args == "" and not is_windows():
            print("For fast compilation, run:")
            print('export KALDIALIGN_MAKE_ARGS="-j"; python setup.py install')
            make_args = ["-j4"]
            print("Setting make_args to '-j4'")

        if not any("PYTHON_EXECUTABLE" in arg for arg in cmake_args):
            print(f"Setting PYTHON_EXECUTABLE to {sys.executable}")
            cmake_args.append(f"-DPYTHON_EXECUTABLE={sys.executable}")
        if not any("Python_EXECUTABLE" in arg for arg in cmake_args):
            cmake_args.append(f"-DPython_EXECUTABLE={sys.executable}")

        cmake_args.append(f"-DCMAKE_INSTALL_PREFIX={install_dir}")

        configure_cmd = [
            "cmake",
            *cmake_args,
            "-B",
            str(build_dir),
            "-S",
            str(kaldialign_dir),
        ]
        build_cmd = [
            "cmake",
            "--build",
            str(build_dir),
            "--target",
            "install",
            "--config",
            "Release",
        ]

        if make_args:
            build_cmd.extend(["--", *make_args])
        elif is_windows():
            build_cmd.extend(["--", "-m"])

        print(f"configure command is:\n{' '.join(configure_cmd)}")
        print(f"build command is:\n{' '.join(build_cmd)}")

        try:
            subprocess.check_call(configure_cmd)
            subprocess.check_call(build_cmd)
        except subprocess.CalledProcessError as e:
            raise Exception(
                "\nBuild kaldialign failed. Please check the error message.\n"
                "You can ask for help by creating an issue on GitHub.\n"
                "\nClick:\n"
                "    https://github.com/pzelasko/kaldialign/issues/new\n"
            ) from e


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
    extras_require={"test": ["pytest"]},
    python_requires=">=3.10",
    keywords=[
        "natural language processing",
        "speech recognition",
        "machine learning",
    ],
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing :: Linguistic",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Mathematics",
    ],
    zip_safe=False,
    license="Apache-2.0",
    license_files=["LICENSE"],
)
