#!/usr/bin/env bash

src_path=$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P)

python3 -m venv .venv
source .venv/bin/activate

pip3 install git+https://github.com/antonblanchard/vlsiffra@292ac2aa4747cb7e0b1cde656a8f6161e0e953f0
pip3 install amaranth-yosys

declare -A techs=( ["asap7"]="asap7sc7p5t_rvt" ["sky130hd"]="sky130hd" ["none"]="none")

for tech in asap7 sky130hd none
do
for algo in hancarlson brentkung inferred koggestone ripple
do
echo "$tech / ${techs[$tech]} - $algo"
vlsi-multiplier --bits=64 \
    --algorithm=$algo \
    --tech=$tech \
    --register-post-ppa \
    --register-post-ppg \
    --output=${src_path}/src/src/main/resources/mult_${algo}_${techs[$tech]}.v
done
echo "$tech / ${techs[$tech]} - brentkung (mac)"
vlsi-multiplier --bits=64 \
    --multiply-add \
    --algorithm=brentkung \
    --tech=$tech \
    --register-post-ppa \
    --register-post-ppg \
    --output=${src_path}/src/src/main/resources/mac_brentkung_${techs[$tech]}.v
done

pushd ${src_path}/src/src/main/resources/
sed -i 's|/.*/scgallery/scgallery/designs/mock_alu/||g' *.v
popd

deactivate
rm -rf .venv
