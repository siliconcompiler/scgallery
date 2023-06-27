#!/usr/bin/env python3
# Copyright 2020 Silicon Compiler Authors. All Rights Reserved.

import os
from scgallery.designs.heartbeat import heartbeat as design
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
                "values": [10, 40],
            },
            {
                "key": ['tool', 'yosys', 'task', 'syn_asic', 'var', 'hier_threshold'],
                "values": [10, 1000],
                "type": 'int',
                "step": "syn",
                "index": "0"
            },
            {
                "key": ['tool', 'yosys', 'task', 'syn_asic', 'var', 'strategy'],
                "values": ['', 'AREA0', 'DELAY0', 'AREA3', 'DELAY4'],
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
                "type": 'int'
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
        experiments=4,
        parallel_limit=2
    )
    chip.summary()


if __name__ == '__main__':
    main()
