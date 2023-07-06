#!/usr/bin/env python3
# Copyright 2020 Silicon Compiler Authors. All Rights Reserved.

import os
from scgallery.designs.ibex import ibex as design
from siliconcompiler.targets import asap7_demo


def main():
    '''Simple asicflow example.'''

    chip = design.setup(target=asap7_demo, use_cmd_file=False)
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'flatten', 'false')
    chip.set('option', 'credentials', os.path.join(os.path.dirname(__file__), 'azure.cred'))
    chip.set('option', 'remote', True)

    chip.optimize_parameters(
        [
            {
                "key": ['constraint', 'density'],
                "values": [10, 80],
            },
            {
                "key": ['tool', 'yosys', 'task', 'syn_asic', 'var', 'hier_threshold'],
                "values": [10, 1000],
                "type": 'int',
                "step": "syn",
                "index": "0"
            },
            {
                "key": ['tool', 'yosys', 'task', 'syn_asic', 'var', 'flatten'],
                "values": ['true', 'false'],
                "type": 'enum',
                "step": "syn",
                "index": "0"
            },
            {
                "key": ['tool', 'yosys', 'task', 'syn_asic', 'var', 'strategy'],
                "values": ['', 'AREA0', 'AREA1', 'AREA2', 'AREA3', 'DELAY0', 'DELAY1', 'DELAY2', 'DELAY3', 'DELAY4'],
                "type": 'enum',
                "step": "syn",
                "index": "0"
            },
            {
                "key": ['tool', 'openroad', 'task', 'place', 'var', 'place_density'],
                "values": [0.70, 0.95],
                "type": 'float',
                "step": "place",
                "index": "0"
            },
            {
                "key": ['tool', 'openroad', 'task', 'cts', 'var', 'cts_cluster_diameter'],
                "values": [10, 100],
                "type": 'int',
                "step": "cts",
                "index": "0"
            },
            {
                "key": ['tool', 'openroad', 'task', 'cts', 'var', 'cts_distance_between_buffers'],
                "values": [10, 100],
                "type": 'int',
                "step": "cts",
                "index": "0"
            },
            {
                "key": ['tool', 'openroad', 'task', 'cts', 'var', 'rsz_repair_tns'],
                "values": [0, 100],
                "type": 'float',
                "step": "cts",
                "index": "0"
            }
        ],
        [
            {
                "key": ["metric", "setupslack"],
                "target": "max",
                "step": "export",
                "index": "1"
            },
            # {
            #     "key": ["metric", "holdslack"],
            #     "target": "max",
            #     "step": "export",
            #     "index": "1"
            # }
        ],
        experiments=64,
        parallel_limit=16
    )
    chip.summary()


if __name__ == '__main__':
    main()
