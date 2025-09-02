#!/usr/bin/env bash

src_path=$(cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P)

python3 -m venv .venv
source .venv/bin/activate

pip3 install git+https://github.com/antonblanchard/vlsiffra@292ac2aa4747cb7e0b1cde656a8f6161e0e953f0
pip3 install amaranth-yosys==0.25.0.0.post75

for algo in hancarlson brentkung inferred koggestone ripple
do
echo "$algo"
vlsi-multiplier --bits=64 \
    --algorithm=$algo \
    --tech=none \
    --register-post-ppa \
    --register-post-ppg \
    --output=${src_path}/src/src/main/resources/mult_${algo}_none.v
done
echo "brentkung (mac)"
vlsi-multiplier --bits=64 \
    --multiply-add \
    --algorithm=brentkung \
    --tech=none \
    --register-post-ppa \
    --register-post-ppg \
    --output=${src_path}/src/src/main/resources/mac_brentkung_none.v
done

pushd ${src_path}/src/src/main/resources/
sed -i 's|/.*/scgallery/scgallery/designs/mock_alu/||g' *.v
popd

deactivate
rm -rf .venv
