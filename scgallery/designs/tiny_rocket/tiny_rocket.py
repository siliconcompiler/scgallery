#!/usr/bin/env python3

'''
Source: https://github.com/chipsalliance/rocket-chip

A single core RISC-V Rocket tile in the tiny configuration: RV32, no FPU, no
virtual memory, a 256 byte instruction cache and a 256 byte data scratchpad.

The RTL is elaborated from Chisel while the flow runs, the way mock_alu is.
rocket-chip is not vendored into the gallery, sbt resolves it from Maven Central
and src/build.sbt pins the version. src/src/main/scala/GenerateTinyRocket.scala
holds the subsystem that gets elaborated and the configuration that sizes the
tile's memories.

RocketTile is the synthesis top, so everything the subsystem wraps around it,
the buses and the CLINT, PLIC and debug module, is dropped by synthesis. The
tile is what the gallery wants to show, and a Rocket tile cannot be elaborated
on its own: its TileLink, interrupt and clock nodes only take shape once
diplomacy has resolved them against a subsystem.
'''

import math

import os.path

from lambdalib.ramlib import Spram

from siliconcompiler import ASIC, sc_open
from siliconcompiler.flows.asicflow import ASICFlow
from siliconcompiler.targets import asap7_demo
from siliconcompiler.tools.chisel import convert
from siliconcompiler.tools.openroad.macro_placement import MacroPlacementTask

from scgallery import GalleryDesign


# Where GenerateTinyRocket.scala is told to leave the shapes of the SRAMs that
# rocket-chip turned into black boxes, relative to the directory sbt runs in.
MEMORY_CONF = 'mems.conf'

# Smallest memory worth turning into a macro. The tile's two 64x32 data arrays
# clear this and become la_spram instances, its 4x25 instruction cache tag array
# does not and stays in flops, which is cheaper than a macro that small.
HARDEN_BITS = 1024


def read_memory_conf(path):
    """Reads the memory configuration written by FIRRTL's ReplSeqMem pass.

    Every line describes one SRAM that was replaced by a black box, in the form
    ``name <name> depth <n> width <n> ports <spec> mask_gran <n>``.

    Args:
        path (str): Path to the memory configuration file.

    Returns:
        List[Dict]: One entry per memory.
    """
    memories = []
    with sc_open(path) as conf:
        for line in conf:
            fields = line.split()
            if not fields:
                continue
            if fields[0] != 'name' or len(fields) % 2 != 0:
                raise ValueError(f'unexpected memory configuration: {line.strip()}')
            values = dict(zip(fields[::2], fields[1::2]))
            memories.append({
                'name': values['name'],
                'depth': int(values['depth']),
                'width': int(values['width']),
                'ports': values['ports'],
                'mask_gran': int(values.get('mask_gran', values['width']))})
    return memories


def generate_memory(memory):
    """Builds the Verilog for one of rocket-chip's SRAM black boxes.

    Memories at or above HARDEN_BITS are mapped onto lambdalib's la_spram, so the
    target's memory macros get used. Smaller ones get a behavioral model instead
    and synthesize into flops.

    Args:
        memory (Dict): One entry from read_memory_conf.

    Returns:
        str: Verilog source for the black box.
    """
    name = memory['name']
    depth = memory['depth']
    width = memory['width']
    gran = memory['mask_gran']

    # 'mrw' is a single masked read/write port, which is all the InferReadWrite
    # pass leaves behind for a Rocket tile.
    if memory['ports'] != 'mrw':
        raise ValueError(f'{name}: expected a masked read/write port, got {memory["ports"]}')
    if width % gran != 0:
        raise ValueError(f'{name}: {width} bits do not divide into {gran} bit mask groups')

    addr_width = max(1, math.ceil(math.log2(depth)))
    mask_bits = width // gran

    source = [
        f'module {name} (',
        '  input                 RW0_clk,',
        f'  input  [{addr_width - 1}:0] RW0_addr,',
        '  input                 RW0_en,',
        '  input                 RW0_wmode,',
        f'  input  [{mask_bits - 1}:0] RW0_wmask,',
        f'  input  [{width - 1}:0] RW0_wdata,',
        f'  output [{width - 1}:0] RW0_rdata',
        ');',
        '']

    if depth * width >= HARDEN_BITS:
        # la_spram masks either whole bytes or single bits. A mask that covers
        # the whole word, which is what rocket-chip asks for when it never
        # partially writes a row, is widened to a byte mask.
        if gran == 8:
            bytemask, wmask = 1, 'RW0_wmask'
        elif mask_bits == 1 and width % 8 == 0:
            bytemask, wmask = 1, f'{{{width // 8}{{RW0_wmask}}}}'
        elif gran == 1:
            bytemask, wmask = 0, 'RW0_wmask'
        else:
            raise ValueError(f'{name}: cannot map a {gran} bit write mask onto la_spram')

        source.extend([
            f'  // {depth}x{width}, hardened.',
            f'  la_spram #(.DW({width}), .AW({addr_width}), .BYTEMASK({bytemask})) mem (',
            '    .clk(RW0_clk),',
            '    .ce(RW0_en),',
            '    .we(RW0_wmode),',
            f'    .wmask({wmask}),',
            '    .addr(RW0_addr),',
            '    .din(RW0_wdata),',
            '    .dout(RW0_rdata),',  # codespell:ignore
            '    .selctrl(1\'b0),',
            '    .ctrl(\'b0),',
            '    .status());'])
    else:
        source.extend([
            f'  // {depth}x{width}, too small to be worth a macro.',
            f'  reg [{width - 1}:0] ram [{depth - 1}:0];',
            f'  reg [{addr_width - 1}:0] read_addr;',
            '  integer i;',
            '',
            '  always @(posedge RW0_clk) begin',
            '    if (RW0_en && !RW0_wmode) read_addr <= RW0_addr;',
            '    if (RW0_en && RW0_wmode) begin',
            f'      for (i = 0; i < {mask_bits}; i = i + 1)',
            '        if (RW0_wmask[i])',
            f'          ram[RW0_addr][i * {gran} +: {gran}] <= RW0_wdata[i * {gran} +: {gran}];',
            '    end',
            '  end',
            '',
            '  assign RW0_rdata = ram[read_addr];'])

    source.extend(['', 'endmodule', ''])
    return '\n'.join(source)


class RocketConvertTask(convert.ConvertTask):
    """Chisel conversion that finishes the elaborated RTL off for synthesis.

    Synthesis reads a single file, inputs/<topmodule>.v, whenever a conversion
    node feeds it, so everything it needs has to be in that file. Three things
    go in on top of the Verilog the base task collects:

    * the design's defines. Nothing else applies them once the flow's own
      elaboration node is gone, and rocket-chip hides thousands of blocks of
      simulation-only $fwrite and $fatal code behind `ifndef SYNTHESIS.
    * the SRAM black boxes rocket-chip left behind, built from the memory
      configuration FIRRTL wrote out.
    * la_spram and whichever implementation of it the target picked, which come
      from lambdalib and the PDK rather than from the Chisel build.
    """

    def _memory_libraries(self):
        """The project's filesets that hold memory RTL rather than the design."""
        for lib, fileset in self.project.get_filesets():
            if lib.name != self.project.design.name:
                yield lib, fileset

    def _memory_sources(self):
        """Paths to the memory RTL, in the order it should be written out.

        A file that several filesets share is only written once, since a repeated
        module definition is an error rather than a duplicate.
        """
        seen = set()
        for lib, fileset in self._memory_libraries():
            for filetype in ('verilog', 'systemverilog'):
                for path in lib.get_file(fileset=fileset, filetype=filetype):
                    if path not in seen:
                        seen.add(path)
                        yield lib, path

    def setup(self):
        super().setup()

        for lib, fileset in self._memory_libraries():
            for filetype in ('verilog', 'systemverilog'):
                if lib.has_file(fileset=fileset, filetype=filetype):
                    self.add_required_key(lib, 'fileset', fileset, 'file', filetype)

    def post_process(self):
        super().post_process()

        design = self.project.design
        defines = []
        for fileset in self.project.get('option', 'fileset'):
            defines.extend(design.get('fileset', fileset, 'define'))

        output = os.path.join('outputs', f'{self.design_topmodule}.v')
        with sc_open(output) as elaborated:
            rtl = elaborated.read()

        with open(output, 'w') as out:
            for define in defines:
                name, _, value = define.partition('=')
                out.write(f'`define {name} {value}'.rstrip() + '\n')

            out.write(rtl)

            for memory in read_memory_conf(MEMORY_CONF):
                out.write('\n')
                out.write(generate_memory(memory))

            for lib, path in self._memory_sources():
                out.write(f'\n// {lib.name}: {os.path.basename(path)}\n')
                with sc_open(path) as source:
                    out.write(source.read())


class ChiselFlow(ASICFlow):
    """asicflow with its elaboration node replaced by a Chisel build."""

    def __init__(self):
        super().__init__("asicflow-chisel")
        self.remove_node("elaborate")
        self.node("convert", RocketConvertTask())
        self.edge("convert", "synthesis")


class TinyRocketDesign(GalleryDesign):
    def __init__(self):
        super().__init__("tiny_rocket")
        self.set_dataroot("tiny_rocket", __file__)

        with self.active_dataroot("tiny_rocket"):
            with self.active_fileset("rtl"):
                self.set_topmodule("RocketTile")
                self.add_file("src/build.sbt")
                self.add_depfileset(Spram(), "rtl")
                self.add_define("SYNTHESIS")

            with self.active_fileset("sdc.asap7sc7p5t_rvt"):
                self.add_file("constraints/asap7sc7p5t_rvt.sdc")

            with self.active_fileset("sdc.gf180mcu_fd_sc_mcu7t5v0_5LM"):
                self.add_file("constraints/gf180mcu_fd_sc_mcu7t5v0.sdc")

            with self.active_fileset("sdc.gf180mcu_fd_sc_mcu9t5v0_5LM"):
                self.add_file("constraints/gf180mcu_fd_sc_mcu9t5v0.sdc")

            with self.active_fileset("sdc.nangate45"):
                self.add_file("constraints/nangate45.sdc")

            with self.active_fileset("sdc.sg13g2_stdcell_1p2"):
                self.add_file("constraints/sg13g2_stdcell.sdc")

            with self.active_fileset("sdc.sky130hd"):
                self.add_file("constraints/sky130hd.sdc")

        for target in ("asap7_asap7sc7p5t_rvt",
                       "freepdk45_nangate45",
                       "skywater130_sky130hd"):
            self.add_target_setup(target, self.setup_chisel)
        self.add_target_setup("ihp130_sg13g2_stdcell", self.setup_ihp130)
        self.add_target_setup("gf180_gf180mcu_fd_sc_mcu7t5v0", self.setup_gf180)
        self.add_target_setup("gf180_gf180mcu_fd_sc_mcu9t5v0", self.setup_gf180)

    def setup_chisel(self, project: ASIC):
        project.set_flow(ChiselFlow())
        task = convert.ConvertTask.find_task(project)
        task.set_chisel_application("GenerateTinyRocket")
        task.add_chisel_argument(["--memory-conf", MEMORY_CONF], clobber=True)

    def setup_ihp130(self, project: ASIC):
        self.setup_chisel(project)
        MacroPlacementTask.find_task(project).set_openroad_macroplacehalo(40, 60)

    def setup_gf180(self, project: ASIC):
        self.setup_chisel(project)
        MacroPlacementTask.find_task(project).set_openroad_macroplacehalo(20, 10)


if __name__ == '__main__':
    project = ASIC(TinyRocketDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    asap7_demo(project)
    project.design.process_setups("asap7_asap7sc7p5t_rvt", project)

    project.run()
    project.summary()
