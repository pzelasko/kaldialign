import os
from io import open
from os import path
from setuptools import Extension
from setuptools import find_packages
from setuptools import setup
from sys import platform

try:
    from Cython.Build import cythonize
except ImportError:
    cythonize = None

# https://cython.readthedocs.io/en/latest/src/userguide/source_files_and_compilation.html#distributing-cython-modules
def no_cythonize(extensions, **_ignore):
    for extension in extensions:
        sources = []
        for sfile in extension.sources:
            path, ext = os.path.splitext(sfile)
            if ext in (".pyx", ".py"):
                if extension.language == "c++":
                    ext = ".cpp"
                else:
                    ext = ".c"
                sfile = path + ext
            sources.append(sfile)
        extension.sources[:] = sources
    return extensions


COMPILE_ARGS = [
    "-std=c++11",
    "-Wno-register",
    "-Wno-unused-function",
    "-Wno-unused-local-typedefs",
    "-funsigned-char",
]
if platform.startswith("darwin"):
    COMPILE_ARGS.append("-stdlib=libc++")
    COMPILE_ARGS.append("-mmacosx-version-min=10.7")


kaldialign = Extension(
    name="kaldialign",
    language="c++",
    extra_compile_args=COMPILE_ARGS,
    include_dirs=[os.path.dirname(os.path.abspath(__file__)) + "/extensions"],
    sources=["extensions/align.pyx", "extensions/kaldi_align.cpp"],
)
extensions = [kaldialign]

CYTHONIZE = bool(int(os.getenv("CYTHONIZE", 0))) and cythonize is not None


if CYTHONIZE:
    compiler_directives = {"language_level": 3, "embedsignature": True}
    extensions = cythonize(extensions, compiler_directives=compiler_directives)
else:
    extensions = no_cythonize(extensions)


__version__ = "0.2"


this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, "README.md"), encoding="utf8") as source:
    long_description = source.read()


def main() -> None:
    setup(
        name="kaldialign",
        version=__version__,
        author="Piotr Żelasko",
        author_email="pzelasko@jhu.edu",
        description="Kaldi alignment methods wrapped into Python",
        long_description=long_description,
        long_description_content_type="text/markdown",
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
        license="Apache 2.0",
        extras_require={
            'dev': ['pytest', 'Cython']
        },
        ext_modules=extensions,
        packages=find_packages(exclude=["tests"]),
        zip_safe=False,
    )


if __name__ == "__main__":
    main()
