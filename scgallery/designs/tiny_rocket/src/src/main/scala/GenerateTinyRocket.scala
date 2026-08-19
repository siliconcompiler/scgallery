// See LICENSE.SiFive for license details.

// Elaborates the tiny Rocket subsystem that scgallery's tiny_rocket design
// synthesizes. RocketTile is the synthesis top, but a Rocket tile cannot be
// elaborated on its own: its TileLink, interrupt and clock nodes only take
// shape once diplomacy has resolved them against a subsystem. So the whole
// subsystem is elaborated here and everything outside RocketTile is dropped
// by synthesis.

import chisel3.fromIntToLiteral
import chisel3.stage.{ChiselGeneratorAnnotation, ChiselStage}

import firrtl.passes.memlib.{
  InferReadWrite,
  InferReadWriteAnnotation,
  ReplSeqMem,
  ReplSeqMemAnnotation
}
import firrtl.stage.RunFirrtlTransformAnnotation

import freechips.rocketchip.config.{Config, Parameters}
import freechips.rocketchip.diplomacy.{LazyModule, ValName}
import freechips.rocketchip.rocket.{DCacheParams, ICacheParams}
import freechips.rocketchip.subsystem.{
  CacheBlockBytes,
  HasAsyncExtInterrupts,
  HasExtInterruptsModuleImp,
  HasHierarchicalBusTopology,
  HasRTCModuleImp,
  RocketSubsystem,
  RocketSubsystemModuleImp,
  RocketTilesKey,
  SystemBusKey
}
import freechips.rocketchip.util.DontTouch

/** A Rocket subsystem without the boot ROM.
  *
  * This is freechips.rocketchip.system.ExampleRocketSystem minus the boot ROM and
  * the optional AXI4 ports. The boot ROM embeds a flattened device tree, which
  * rocket-chip builds by shelling out to dtc, and it holds nothing RocketTile
  * needs, so leaving it out keeps elaboration free of tools the gallery's flows
  * do not install. The reset vector the ROM would have supplied is tied off to
  * the address the ROM is mapped at.
  */
class TinyRocketSystem(implicit p: Parameters)
    extends RocketSubsystem
    with HasHierarchicalBusTopology
    with HasAsyncExtInterrupts {
  override lazy val module = new TinyRocketSystemModuleImp(this)
}

class TinyRocketSystemModuleImp[+L <: TinyRocketSystem](_outer: L)
    extends RocketSubsystemModuleImp(_outer)
    with HasRTCModuleImp
    with HasExtInterruptsModuleImp
    with DontTouch {
  global_reset_vector := 0x10040.U
}

/** Shrinks the tile's instruction cache and data scratchpad to the smallest
  * shape Rocket will build.
  *
  * Stock With1TinyCore asks for a 4 KiB instruction cache and a 16 KiB data
  * scratchpad. The gallery wants no more memory than it takes for the processor
  * to be representative, so both drop to four sets, 256 bytes each, which is the
  * shape the pre-generated netlist this design used to ship was built with.
  */
class WithMinimalTinyMemories
    extends Config((site, here, up) => {
      case RocketTilesKey =>
        up(RocketTilesKey, site).map { tile =>
          tile.copy(
            dcache = Some(
              DCacheParams(
                rowBits = site(SystemBusKey).beatBits,
                nSets = 4,
                nWays = 1,
                nTLBEntries = 4,
                nMSHRs = 0,
                blockBytes = site(CacheBlockBytes),
                scratch = Some(0x80000000L))),
            icache = Some(
              ICacheParams(
                rowBits = site(SystemBusKey).beatBits,
                nSets = 4,
                nWays = 1,
                nTLBEntries = 4,
                blockBytes = site(CacheBlockBytes))))
        }
    })

class TinyRocketConfig
    extends Config(
      new WithMinimalTinyMemories ++
        new freechips.rocketchip.system.TinyConfig)

object GenerateTinyRocket extends App {
  private val (options, rest) = args.span(_ != "--")
  private val chiselArgs = rest.drop(1)

  // The gallery reads the memory shapes back out of this file, so it is the one
  // that names it rather than this program picking a name of its own.
  private val memoryConf = options
    .sliding(2, 2)
    .collectFirst { case Array("--memory-conf", path) => path }
    .getOrElse(sys.error("--memory-conf <path> is required"))

  private implicit val valName: ValName = ValName("TinyRocketSystem")
  private implicit val p: Parameters = new TinyRocketConfig().toInstance

  new ChiselStage().execute(
    chiselArgs,
    Seq(
      ChiselGeneratorAnnotation(() => LazyModule(new TinyRocketSystem).module),
      // Fold matching read and write ports into single read/write ports, then
      // pull every remaining SRAM out into a <name>_ext black box and write its
      // shape to memoryConf. The gallery maps those black boxes onto lambdalib
      // memories.
      RunFirrtlTransformAnnotation(new InferReadWrite),
      InferReadWriteAnnotation,
      RunFirrtlTransformAnnotation(new ReplSeqMem),
      ReplSeqMemAnnotation("", memoryConf)
    )
  )
}
