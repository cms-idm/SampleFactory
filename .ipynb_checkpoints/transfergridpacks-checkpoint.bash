mkdir -p /uscms/home/reshmar/nobackup/sampleFactory/SampleFactory/gridpacks2022

xrdfs root://cmseos.fnal.gov ls /store/group/lpcmetx/iDMe/gridpacks/ \
| grep 'CMSSW_13_0_13_tarball\.tar\.xz$' \
| while read file; do
    echo "Copying $(basename "$file")"
    xrdcp "root://cmseos.fnal.gov/$file" \
        /uscms/home/reshmar/nobackup/sampleFactory/SampleFactory/gridpacks2022/
done