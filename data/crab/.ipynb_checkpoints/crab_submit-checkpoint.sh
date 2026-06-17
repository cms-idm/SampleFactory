#!/usr/bin/env bash
cmsrel CMSSW_13_2_10
cd CMSSW_13_2_10/src
cmsenv
cd ../..
crab submit -c crab.py
