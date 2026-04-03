import subprocess
import re

gridpack = "iDMe_Mchi-42p0_dMchi-4p0_mZDinput-120p0_1jet_icckw1_drjj0_xptj80_xqcut20_slc7_amd64_gcc820_CMSSW_10_6_28_tarball.tar.xz"
gridpack_prefix = "root://cmseos.fnal.gov//store/group/lpcmetx/iDMe/gridpacks_UL_final/"

chain_json = "chain_RunIISummer20UL18GEN-RunIISummer20UL18MiniAODv2.json"
fragment = "iDMe_pythiaGenFragment_ctau-1.py"

num_evt_per_job = 2000
num_jobs = 10

max_minutes = 720 # 12 hours
max_memory = 5000

# Prepare crab submission
cmd = [
    "./runFactory.py",
    "-c", "data/chains/Run2/"+chain_json,
    "-f", "data/fragments/"+fragment,
    "-n", str(num_evt_per_job),
    "-j", str(num_jobs),
    "--minutes", str(max_minutes),
    "--memory", str(max_memory),
    "--crab",
    "--gridpack", gridpack,
    "--gridpack_prefix", gridpack_prefix
]

# Check 
total = num_evt_per_job * num_jobs

m = re.search(r"Mchi-[^_]+_dMchi-[^_]+", gridpack)
mass = m.group(0) if m else "unknown"

total = num_evt_per_job * num_jobs

print("\n================ SUBMISSION ================")
print(f"gridpack     : {gridpack}")
print(f"mass         : {mass}")
print(f"prefix       : {gridpack_prefix}")
print(f"chain        : {chain_json}")
print(f"fragment     : {fragment}")
print(f"events/job   : {num_evt_per_job}")
print(f"jobs         : {num_jobs}")
print(f"total events : {total}")
print("===========================================\n")

input("Press Enter to run the crab submission code")

# Submit
print("\nRunning command:\n")
print(" ".join(cmd))

subprocess.run(cmd, check=True)

