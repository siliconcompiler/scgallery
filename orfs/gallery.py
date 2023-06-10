#!/usr/bin/env python3

import os
import sys
from scgallery import Gallery


def _adjust_corners(chip):
    if chip.get('option', 'pdk') == 'skywater130':
        # Only typical is run on ORFS
        chip.schema._remove('constraint', 'timing', 'slow')
        chip.schema._remove('constraint', 'timing', 'fast')

    elif chip.get('option', 'pdk') == 'asap7':
        # Only fast is run on ORFS
        chip.schema._remove('constraint', 'timing', 'slow')
        chip.schema._remove('constraint', 'timing', 'typical')

    elif chip.get('option', 'pdk') == 'freepdk45':
        # No adjustments
        pass


def _adjust_parameters(chip):
    chip.set('constraint', 'coremargin', 1.0)

    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'strategy', 'DELAY4',
             clobber=False)
    chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'autoname', 'false',
             clobber=False)

    chip.set('tool', 'openroad', 'task', 'place', 'var', 'rsz_buffer_inputs', 'true',
             clobber=False)
    chip.set('tool', 'openroad', 'task', 'place', 'var', 'rsz_buffer_outputs', 'true',
             clobber=False)
    chip.set('tool', 'openroad', 'task', 'place', 'var', 'gpl_enable_skip_io', 'true',
             clobber=False)

    if chip.get('option', 'pdk') == 'freepdk45':
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'abc_constraint_load',
                 '3.898e-3',
                 clobber=False)
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'abc_constraint_driver',
                 'BUF_X1',
                 clobber=False)
    elif chip.get('option', 'pdk') == 'skywater130':
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'abc_constraint_load',
                 '5e-3',
                 clobber=False)
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'abc_constraint_driver',
                 'sky130_fd_sc_hd__buf_1',
                 clobber=False)
    elif chip.get('option', 'pdk') == 'asap7':
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'abc_constraint_load',
                 '3.898e-3',
                 clobber=False)
        chip.set('tool', 'yosys', 'task', 'syn_asic', 'var', 'abc_constraint_driver',
                 'BUFx2_ASAP7_75t_R',
                 clobber=False)


def _rules_file(design):
    rules = os.path.join(os.path.dirname(__file__),
                         'designs',
                         design,
                         'rules.json')
    if os.path.exists(rules):
        return rules
    return None


def _add_sdc(chip):
    mainlib = chip.get('asic', 'logiclib')[0]
    sdc = os.path.join(os.path.dirname(__file__),
                       'designs',
                       chip.design,
                       'constraints',
                       f'{mainlib}.sdc')
    if os.path.exists(sdc):
        chip.schema._remove('input', 'constraint', 'sdc')
        chip.input(sdc)


class ORFSGallery(Gallery):

    def __init__(self, path=None):
        super().__init__(name="ORFS", path=path)
        self.set_jobname_suffix('orfs')

        self.remove_design('zerosoc_flat')
        self.remove_design('zerosoc_hierarchy')
        self.remove_design('openmsp430')
        self.remove_design('heartbeat')

        for design in self.get_designs():
            self.add_design_setup(design, _add_sdc)
            self.add_design_setup(design, _adjust_corners)
            self.add_design_setup(design, _adjust_parameters)

            rules = _rules_file(design)
            if rules:
                self.clear_design_rules(design)
                self.add_design_rule(design, rules)


if __name__ == "__main__":
    sys.exit(ORFSGallery.main())
