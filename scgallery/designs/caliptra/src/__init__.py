import os
from siliconcompiler import Library


def __register(lib):
    lib.register_source(
        name='caliptra-rtl',
        path='git+https://github.com/chipsalliance/caliptra-rtl.git',
        ref='v1.0')


def __add_sources(lib, root, files):
    for src in files:
        lib.input(os.path.join(root, src))


def make_lib(name, root, files, idirs=None):
    lib = Library(name, package='caliptra-rtl', auto_enable=True)
    __register(lib)

    __add_sources(lib, root, files)

    if idirs:
        lib.add('option', 'idir', idirs)

    return lib
