#!/usr/bin/env python3

from scgallery import GalleryDesign
from siliconcompiler import ASICProject
from siliconcompiler.targets import asap7_demo
from lambdalib.ramlib import Spram
from siliconcompiler.tools.yosys.syn_asic import ASICSynthesis
from siliconcompiler.tools import get_task


class WallyDesign(GalleryDesign):
    def __init__(self):
        super().__init__("wally")
        self.set_dataroot("extra", __file__)
        self.set_dataroot("wally",
                          "git+https://github.com/openhwgroup/cvw",
                          tag="e0af0e68a32edd8eb98abc31c8b2b7b04fbd29b9")

        with self.active_fileset("rtl"):
            with self.active_dataroot("wally"):
                self.add_file("src/cvw.sv")
            with self.active_dataroot("extra"):
                self.set_topmodule("wallypipelinedcorewrapper")
                self.add_file("extra/wallypipelinedcorewrapper.sv")
            with self.active_dataroot("wally"):
                self.add_file([
                    'src/fpu/fmtparams.sv',
                    'src/fpu/fcvt.sv',
                    'src/fpu/fround.sv',
                    'src/fpu/fregfile.sv',
                    'src/fpu/fhazard.sv',
                    'src/fpu/fsgninj.sv',
                    'src/fpu/fclassify.sv',
                    'src/fpu/unpackinput.sv',
                    'src/fpu/fcmp.sv',
                    'src/fpu/fli.sv',
                    'src/fpu/packoutput.sv',
                    'src/fpu/unpack.sv',
                    'src/fpu/fctrl.sv',
                    'src/fpu/fpu.sv',
                    'src/mdu/divstep.sv',
                    'src/mdu/mul.sv',
                    'src/mdu/div.sv',
                    'src/mdu/mdu.sv',
                    'src/mmu/hptw.sv',
                    'src/mmu/pmachecker.sv',
                    'src/mmu/mmu.sv',
                    'src/mmu/adrdecs.sv',
                    'src/mmu/pmpadrdec.sv',
                    'src/mmu/adrdec.sv',
                    'src/mmu/pmpchecker.sv',
                    'src/rvvi/rvvisynth.sv',
                    'src/rvvi/priorityaomux.sv',
                    'src/rvvi/csrindextoaddr.sv',
                    'src/rvvi/packetizer.sv',
                    'src/rvvi/triggergen.sv',
                    'src/rvvi/regchangedetect.sv',
                    'src/uncore/clint_apb.sv',
                    'src/uncore/plic_apb.sv',
                    'src/uncore/uncore.sv',
                    'src/uncore/spi_fifo.sv',
                    'src/uncore/uartPC16550D.sv',
                    'src/uncore/spi_controller.sv',
                    'src/uncore/uart_apb.sv',
                    'src/uncore/ram_ahb.sv',
                    'src/uncore/ahbapbbridge.sv',
                    'src/uncore/gpio_apb.sv',
                    'src/uncore/rom_ahb.sv',
                    'src/uncore/spi_apb.sv',
                    'src/generic/or_rows.sv',
                    'src/generic/adder.sv',
                    'src/generic/aplusbeq0.sv',
                    'src/generic/mux.sv',
                    'src/generic/neg.sv',
                    'src/generic/onehotdecoder.sv',
                    'src/generic/counter.sv',
                    'src/generic/priorityonehot.sv',
                    'src/generic/binencoder.sv',
                    'src/generic/prioritythermometer.sv',
                    'src/generic/arrs.sv',
                    'src/generic/csa.sv',
                    'src/generic/lzc.sv',
                    'src/generic/decoder.sv',
                    'src/ieu/alu.sv',
                    'src/ieu/controller.sv',
                    'src/ieu/regfile.sv',
                    'src/ieu/comparator.sv',
                    'src/ieu/shifter.sv',
                    'src/ieu/datapath.sv',
                    'src/ieu/extend.sv',
                    'src/ieu/ieu.sv',
                    'src/cache/cacheLRU.sv',
                    'src/cache/cache.sv',
                    'src/cache/cachefsm.sv',
                    'src/cache/subcachelineread.sv',
                    'src/cache/cacheway.sv',
                    'src/wally/wallypipelinedsoc.sv',
                    'src/wally/wallypipelinedcore.sv',
                    'src/privileged/csri.sv',
                    'src/privileged/csrsr.sv',
                    'src/privileged/privdec.sv',
                    'src/privileged/privpiperegs.sv',
                    'src/privileged/csrs.sv',
                    'src/privileged/trap.sv',
                    'src/privileged/csrm.sv',
                    'src/privileged/csr.sv',
                    'src/privileged/privmode.sv',
                    'src/privileged/privileged.sv',
                    'src/privileged/csru.sv',
                    'src/privileged/csrc.sv',
                    'src/hazard/hazard.sv',
                    'src/ebu/ahbcacheinterface.sv',
                    'src/ebu/busfsm.sv',
                    'src/ebu/ahbinterface.sv',
                    'src/ebu/ebu.sv',
                    'src/ebu/buscachefsm.sv',
                    'src/ebu/ebufsmarb.sv',
                    'src/ebu/controllerinput.sv',
                    'src/lsu/subwordread.sv',
                    'src/lsu/dtim.sv',
                    'src/lsu/swbytemask.sv',
                    'src/lsu/endianswap.sv',
                    'src/lsu/align.sv',
                    'src/lsu/subwordwrite.sv',
                    'src/lsu/lsu.sv',
                    'src/lsu/lrsc.sv',
                    'src/lsu/amoalu.sv',
                    'src/lsu/atomic.sv',
                    'src/ifu/irom.sv',
                    'src/ifu/ifu.sv',
                    'src/ifu/spill.sv',
                    'src/ifu/decompress.sv'])

                self.add_file([
                    'src/fpu/fma/fmaexpadd.sv',
                    'src/fpu/fma/fmamult.sv',
                    'src/fpu/fma/fma.sv',
                    'src/fpu/fma/fmaadd.sv',
                    'src/fpu/fma/fmalza.sv',
                    'src/fpu/fma/fmasign.sv',
                    'src/fpu/fma/fmaalign.sv',
                    'src/fpu/fdivsqrt/fdivsqrtuslc2.sv',
                    'src/fpu/fdivsqrt/fdivsqrtfgen4.sv',
                    'src/fpu/fdivsqrt/fdivsqrtcycles.sv',
                    'src/fpu/fdivsqrt/fdivsqrt.sv',
                    'src/fpu/fdivsqrt/fdivsqrtuslc4cmp.sv',
                    'src/fpu/fdivsqrt/fdivsqrtfgen2.sv',
                    'src/fpu/fdivsqrt/fdivsqrtstage4.sv',
                    'src/fpu/fdivsqrt/fdivsqrtuotfc4.sv',
                    'src/fpu/fdivsqrt/fdivsqrtpostproc.sv',
                    'src/fpu/fdivsqrt/fdivsqrtiter.sv',
                    'src/fpu/fdivsqrt/fdivsqrtstage2.sv',
                    'src/fpu/fdivsqrt/fdivsqrtfsm.sv',
                    'src/fpu/fdivsqrt/fdivsqrtpreproc.sv',
                    'src/fpu/fdivsqrt/fdivsqrtuotfc2.sv',
                    'src/fpu/fdivsqrt/fdivsqrtuslc4.sv',
                    'src/fpu/fdivsqrt/fdivsqrtexpcalc.sv',
                    'src/fpu/postproc/postprocess.sv',
                    'src/fpu/postproc/round.sv',
                    'src/fpu/postproc/fmashiftcalc.sv',
                    'src/fpu/postproc/normshift.sv',
                    'src/fpu/postproc/cvtshiftcalc.sv',
                    'src/fpu/postproc/shiftcorrection.sv',
                    'src/fpu/postproc/roundsign.sv',
                    'src/fpu/postproc/divshiftcalc.sv',
                    'src/fpu/postproc/specialcase.sv',
                    'src/fpu/postproc/resultsign.sv',
                    'src/fpu/postproc/negateintres.sv',
                    'src/fpu/postproc/flags.sv',
                    'src/mmu/tlb/tlbmixer.sv',
                    'src/mmu/tlb/tlb.sv',
                    'src/mmu/tlb/tlbcamline.sv',
                    'src/mmu/tlb/tlbramline.sv',
                    'src/mmu/tlb/tlbram.sv',
                    'src/mmu/tlb/tlbcontrol.sv',
                    'src/mmu/tlb/vm64check.sv',
                    'src/mmu/tlb/tlbcam.sv',
                    'src/mmu/tlb/tlblru.sv',
                    'src/generic/flop/flopr.sv',
                    'src/generic/flop/flopenl.sv',
                    'src/generic/flop/flop.sv',
                    'src/generic/flop/synchronizer.sv',
                    'src/generic/flop/flopenrc.sv',
                    'src/generic/flop/flopen.sv',
                    'src/generic/flop/flopenr.sv',
                    'src/generic/mem/rom1p1r.sv',
                    'src/generic/mem/rom1p1r_128x32.sv',
                    'src/generic/mem/ram1p1rwbe.sv',
                    'src/generic/mem/ram2p1r1wbe.sv',
                    'src/generic/mem/rom1p1r_128x64.sv',
                    'src/generic/mem/ram1p1rwe.sv',
                    'src/ieu/sha/sha512_64.sv',
                    'src/ieu/sha/sha512_32.sv',
                    'src/ieu/sha/sha256.sv',
                    'src/ieu/bmu/bitmanipalu.sv',
                    'src/ieu/bmu/bmuctrl.sv',
                    'src/ieu/bmu/clmul.sv',
                    'src/ieu/bmu/zbc.sv',
                    'src/ieu/bmu/byteop.sv',
                    'src/ieu/bmu/popcnt.sv',
                    'src/ieu/bmu/ext.sv',
                    'src/ieu/bmu/cnt.sv',
                    'src/ieu/bmu/bitreverse.sv',
                    'src/ieu/bmu/zbb.sv',
                    'src/ieu/kmu/zbkx.sv',
                    'src/ieu/kmu/packer.sv',
                    'src/ieu/kmu/zknh64.sv',
                    'src/ieu/kmu/zknde32.sv',
                    'src/ieu/kmu/zknde64.sv',
                    'src/ieu/kmu/zknh32.sv',
                    'src/ieu/kmu/zipper.sv',
                    'src/ieu/kmu/zbkb.sv',
                    'src/ieu/aes/aes64ks2.sv',
                    'src/ieu/aes/aesinvmixcolumns32.sv',
                    'src/ieu/aes/aes32d.sv',
                    'src/ieu/aes/aessbox8.sv',
                    'src/ieu/aes/aesmixcolumns32.sv',
                    'src/ieu/aes/rconlut32.sv',
                    'src/ieu/aes/aesinvsbox8.sv',
                    'src/ieu/aes/galoismultforward8.sv',
                    'src/ieu/aes/aessbox32.sv',
                    'src/ieu/aes/aesinvmixcolumns8.sv',
                    'src/ieu/aes/aesinvshiftrows64.sv',
                    'src/ieu/aes/aesmixcolumns8.sv',
                    'src/ieu/aes/aes64e.sv',
                    'src/ieu/aes/aes64ks1i.sv',
                    'src/ieu/aes/aesshiftrows64.sv',
                    'src/ieu/aes/rotate.sv',
                    'src/ieu/aes/galoismultinverse8.sv',
                    'src/ieu/aes/aes64d.sv',
                    'src/ieu/aes/aes32e.sv',
                    'src/ieu/aes/aesinvsbox64.sv',
                    'src/ifu/bpred/localrepairbp.sv',
                    'src/ifu/bpred/btb.sv',
                    'src/ifu/bpred/icpred.sv',
                    'src/ifu/bpred/localbpbasic.sv',
                    'src/ifu/bpred/RASPredictor.sv',
                    'src/ifu/bpred/bpred.sv',
                    'src/ifu/bpred/twoBitPredictor.sv',
                    'src/ifu/bpred/gshare.sv',
                    'src/ifu/bpred/satCounter2.sv',
                    'src/ifu/bpred/localaheadbp.sv',
                    'src/ifu/bpred/gsharebasic.sv'])

                self.add_idir("config/shared")
            with self.active_dataroot("extra"):
                self.add_idir("extra/config")
                self.add_file("extra/lambda.v")
                self.add_depfileset(Spram(), "rtl")

        with self.active_dataroot("extra"):
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

        self.add_target_setup("freepdk45_nangate45", self.setup_freepdk45)
        self.add_target_setup("asap7_asap7sc7p5t_rvt", self.setup_asap7)
        self.add_target_setup("ihp130_sg13g2_stdcell", self.setup_ihp130)
        self.add_target_setup("gf180_gf180mcu_fd_sc_mcu7t5v0", self.setup_gf180)
        self.add_target_setup("gf180_gf180mcu_fd_sc_mcu9t5v0", self.setup_gf180)
        self.add_target_setup("skywater130_sky130hd", self.setup_skywater130)

    def setup_freepdk45(self, project: ASICProject):
        get_task(project, filter=ASICSynthesis).set("var", "use_slang", True)
        get_task(project, filter=ASICSynthesis).set("var", "flatten", False)
        get_task(project, filter=ASICSynthesis).set("var", "auto_flatten", False)

    def setup_asap7(self, project: ASICProject):
        project.constraint.area.set_density(30)
        get_task(project, filter=ASICSynthesis).set("var", "use_slang", True)
        get_task(project, filter=ASICSynthesis).set("var", "flatten", False)
        get_task(project, filter=ASICSynthesis).set("var", "auto_flatten", False)

    def setup_ihp130(self, project: ASICProject):
        get_task(project, filter=ASICSynthesis).set("var", "use_slang", True)
        get_task(project, filter=ASICSynthesis).set("var", "flatten", False)
        get_task(project, filter=ASICSynthesis).set("var", "auto_flatten", False)

    def setup_gf180(self, project: ASICProject):
        get_task(project, filter=ASICSynthesis).set("var", "use_slang", True)
        get_task(project, filter=ASICSynthesis).set("var", "flatten", False)
        get_task(project, filter=ASICSynthesis).set("var", "auto_flatten", False)

    def setup_skywater130(self, project: ASICProject):
        get_task(project, filter=ASICSynthesis).set("var", "use_slang", True)
        get_task(project, filter=ASICSynthesis).set("var", "flatten", False)
        get_task(project, filter=ASICSynthesis).set("var", "auto_flatten", False)


if __name__ == '__main__':
    project = ASICProject(WallyDesign())
    project.add_fileset("rtl")
    project.add_fileset("sdc.asap7sc7p5t_rvt")
    asap7_demo(project)
    project.design.process_setups("asap7_asap7sc7p5t_rvt", project)

    project.run()
    project.summary()
