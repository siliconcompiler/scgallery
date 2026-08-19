// Elaborates the Rocket tile that the tiny_rocket gallery design synthesizes.
//
// rocket-chip is not vendored into the gallery: sbt resolves it from Maven
// Central. 1.2.6 is the newest rocket-chip published there, and the newest that
// still generates Verilog with the Scala FIRRTL compiler that ships inside
// chisel3. Later rocket-chip elaborates through firtool (CIRCT), which is not
// one of the tools the gallery's flows install.
//
// scalaVersion is a 2.12 release newer than the 2.12.10 rocket-chip 1.2.6 was
// built against, which is binary compatible with it and, unlike 2.12.10, has a
// compiler that runs on JDKs past 17.

organization := "edu.berkeley.cs"

scalaVersion := "2.12.20"

libraryDependencies += "edu.berkeley.cs" %% "rocketchip" % "1.2.6"
