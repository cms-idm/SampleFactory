#!/usr/bin/env python3

import glob
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta


EOS = "root://cmseos.fnal.gov"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M%S"


def get_value(text, name):
    match = re.search(
        rf"{re.escape(name)}\s*=\s*['\"]([^'\"]+)['\"]",
        text
    )

    if not match:
        raise ValueError(f"Could not find {name}")

    return match.group(1)


def get_job_time(crab_file):
    """
    Read the timestamp from the directory containing crab.py.

    Example:
    .../2022_Mchi-105p0_dMchi-10p0_ctau-1/20260722_153936/crab.py
                                                   ^^^^^^^^^^^^^^^
    """
    timestamp = os.path.basename(os.path.dirname(crab_file))

    try:
        return datetime.strptime(timestamp, TIMESTAMP_FORMAT)
    except ValueError:
        return None


def find_recent_crab_files(days):
    cutoff = datetime.now() - timedelta(days=days)
    recent_files = []

    for crab_file in glob.glob("jobs/**/crab.py", recursive=True):
        job_time = get_job_time(crab_file)

        if job_time and job_time >= cutoff:
            recent_files.append(crab_file)

    return recent_files


def make_filelist(crab_file):
    print(f"\nProcessing:\n{crab_file}")

    with open(crab_file) as f:
        text = f.read()

    try:
        request = get_value(text, "config.General.requestName")
        outdir = get_value(text, "config.Data.outLFNDirBase")
        tag = get_value(text, "config.Data.outputDatasetTag")
    except ValueError as error:
        print(f"Skipped: {error}")
        return False

    eos_dir = f"{outdir.rstrip('/')}/{request}/{tag}"

    result = subprocess.run(
        ["xrdfs", EOS, "ls", "-R", eos_dir],
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(f"Could not read EOS directory:\n{eos_dir}")

        if result.stderr.strip():
            print(result.stderr.strip())

        return False

    root_files = sorted({
        path.strip()
        for path in result.stdout.splitlines()
        if path.strip().endswith(".root")
    })

    if not root_files:
        print(f"No ROOT files found under:\n{eos_dir}")
        return False

    os.makedirs("TxtFiles2022", exist_ok=True)

    output_txt = os.path.join(    "TxtFiles2022",     f"{tag}_files.txt" )

    with open(output_txt, "w") as f:
        for path in root_files:
            f.write(f"{EOS}/{path.lstrip('/')}\n")

    print(f"Created: {output_txt}")
    print(f"Number of ROOT files: {len(root_files)}")

    return True


def main():
    # Process one explicitly provided crab.py, regardless of its age.
    if len(sys.argv) == 2 and sys.argv[1].endswith("crab.py"):
        crab_files = [sys.argv[1]]

    # Otherwise, process recent jobs.
    else:
        try:
            days = int(sys.argv[1]) if len(sys.argv) == 2 else 7
        except ValueError:
            sys.exit(
                "Usage:\n"
                "  python make_filelist.py\n"
                "  python make_filelist.py DAYS\n"
                "  python make_filelist.py /path/to/crab.py"
            )

        crab_files = find_recent_crab_files(days)

        if not crab_files:
            sys.exit(
                f"No crab.py files found from the last {days} days.\n"
                "Run this script from the SampleFactory directory."
            )

        print(
            f"Found {len(crab_files)} jobs created "
            f"within the last {days} days."
        )

    created = 0

    for crab_file in sorted(crab_files, key=get_job_time):
        if not os.path.isfile(crab_file):
            print(f"File not found: {crab_file}")
            continue

        if make_filelist(os.path.abspath(crab_file)):
            created += 1

    print("\nFinished.")
    print(f"File lists created: {created}")
    print(f"Jobs checked: {len(crab_files)}")


if __name__ == "__main__":
    main()