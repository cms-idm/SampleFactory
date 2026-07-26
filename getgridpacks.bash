#!/bin/bash

EOS=root://cmseos.fnal.gov
EOS_DIR=/store/group/lpcmetx/iDMe/gridpacks
OUTPUT=gridpacksfromEOS.txt

xrdfs $EOS ls $EOS_DIR \
| grep 'CMSSW_13_0_13_tarball\.tar\.xz$' \
| while read file; do
    echo "${EOS}/${file}"
done > "$OUTPUT"

echo "Created $OUTPUT"
echo "Number of files: $(wc -l < "$OUTPUT")"
