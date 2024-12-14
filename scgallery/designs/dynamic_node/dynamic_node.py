#!/usr/bin/env python3

from siliconcompiler import Chip
from siliconcompiler.targets import asap7_demo
from scgallery import Gallery


def setup():
    chip = Chip('dynamic_node')
    chip.set('option', 'entrypoint', 'dynamic_node_top_wrap')

    chip.register_source('OPDB',
                         path='git+https://github.com/PrincetonUniversity/OPDB.git',
                         ref='a80e536ba29779faed68e32d4a202f6b7a93bc9b')

    chip.input('modules/dynamic_node_2dmesh/NETWORK_2dmesh/dynamic_node_2dmesh.pickle.v',
               package='OPDB')

    return chip


if __name__ == '__main__':
    chip = setup()
    Gallery.design_commandline(chip, target=asap7_demo, module_path=__file__)

    chip.run()
    chip.summary()
