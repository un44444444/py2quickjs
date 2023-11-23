import glob
import sys

from setuptools import setup, Extension

CONFIG_VERSION = open("upstream-quickjs/VERSION").read().strip()
extra_link_args = []

if sys.platform == "win32":
    # To build for Windows:
    # 1. Install MingW-W64-builds from https://mingw-w64.org/doku.php/download
    #    It is important to change the default to 64-bit when installing if a
    #    64-bit Python is installed in windows.
    # 2. Put the bin/ folder inside x86_64-8.1.0-posix-seh-rt_v6-rev0 in your
    #    system PATH when compiling.
    # 3. The code below will moneky-patch distutils to work.
    import distutils.cygwinccompiler
    distutils.cygwinccompiler.get_msvcr = lambda: [] 
    # Make sure that pthreads is linked statically, otherwise we run into problems
    # on computers where it is not installed.
    extra_compile_args = ["-Werror=incompatible-pointer-types"]
    extra_link_args = ["-static"]
elif sys.platform == "linux2":
    extra_compile_args = ["-std=c99"]


def get_c_sources(include_headers=False):
    sources = [
        "module.c",
        "upstream-quickjs/cutils.c",
        "upstream-quickjs/libbf.c",
        "upstream-quickjs/libregexp.c",
        "upstream-quickjs/libunicode.c",
        "upstream-quickjs/quickjs.c",
    ]
    if include_headers:
        sources += [
            "upstream-quickjs/cutils.h",
            "upstream-quickjs/libbf.h",
            "upstream-quickjs/libregexp-opcode.h",
            "upstream-quickjs/libregexp.h",
            "upstream-quickjs/libunicode-table.h",
            "upstream-quickjs/libunicode.h",
            "upstream-quickjs/list.h",
            "upstream-quickjs/quickjs-atom.h",
            "upstream-quickjs/quickjs-opcode.h",
            "upstream-quickjs/quickjs.h",
            "upstream-quickjs/VERSION",
        ]
    return sources


_quickjs = Extension(
    '_quickjs',
    define_macros=[('_GNU_SOURCE', None), ('CONFIG_VERSION', '"%s"' % CONFIG_VERSION), ('CONFIG_BIGNUM', None)],
    # HACK.
    # See https://github.com/pypa/packaging-problems/issues/84.
    sources=get_c_sources(include_headers=("sdist" in sys.argv)),
    extra_compile_args=extra_compile_args,
    extra_link_args=extra_link_args)

long_description = """
Python wrapper around https://bellard.org/quickjs/ .

Translates types like `str`, `float`, `bool`, `list`, `dict` and combinations
thereof to and from Javascript.

QuickJS is currently thread-hostile, so this wrapper makes sure that all calls
to the same JS runtime comes from the same thead.
"""

setup(author="Petter Strandmark",
      author_email="petter.strandmark@gmail.com",
      maintainer="Stone C",
      maintainer_email="un44444444@gmail.com",
      name='py2quickjs',
      url='https://github.com/un44444444/py2quickjs',
      version='0.5.0',
      description='Wrapping the quickjs C library.',
      long_description=long_description,
      packages=["quickjs"],
      python_requires='>=2.7, <3',
      ext_modules=[_quickjs])
