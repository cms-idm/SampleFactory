#!/usr/bin/env bash
cmsrel CMSSW_12_6_5
cd CMSSW_12_6_5/src
cmsenv
cd ../..
crab submit -c crab.py
