import FWCore.ParameterSet.Config as cms
import os

# LHE producer
#gridpackPath = "root://cmseos.fnal.gov//store/group/lpcmetx/iDMe/gridpacks_UL_final/iDMe_Mchi-42p0_dMchi-4p0_mZDinput-120p0_1jet_icckw1_drjj0_xptj80_xqcut20_slc7_amd64_gcc820_CMSSW_10_6_28_tarball.tar.xz" 

## Kyungmin: GeneratorInterface/LHEInterface/data/run_generic_tarball_xrootd.sh does not exist for CMSSW_10_6_26 that is the GEN step for Run2; boh gotta use some detour
gridpackPath_prefix = "root://eoscms.cern.ch//eos/cms/store/group/cmst3/group/l1tr/kypark/SampleFactory/gridpacks/"
gridpackPath = "iDMe_Mchi-42p0_dMchi-4p0_mZDinput-120p0_1jet_icckw1_drjj0_xptj80_xqcut20_slc7_amd64_gcc820_CMSSW_10_6_28_tarball.tar.xz"

nEvents = 50000

externalLHEProducer = cms.EDProducer("ExternalLHEProducer",
    args = cms.vstring(os.getcwd() + '/' + gridpackPath),
    nEvents = cms.untracked.uint32(nEvents),
    numberOfParameters = cms.uint32(1),
    outputFile = cms.string('cmsgrid_final.lhe'),
    generateConcurrently = cms.untracked.bool(True),
    scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_cvmfs.sh')
    #scriptName = cms.FileInPath('GeneratorInterface/LHEInterface/data/run_generic_tarball_xrootd.sh') # doesnt work boh
)


## Hadronizer fragment for iDMe LLP
## There is also a gen-level filter on both MET and jet pT 
## (80 GeV for both) which can be enabled/disabled in the last 
## line, by commenting out one definition of ProductionFilterSequence 
## and uncommenting the other.

from Configuration.Generator.Pythia8CommonSettings_cfi import *
from Configuration.Generator.MCTunes2017.PythiaCP5Settings_cfi import *
from Configuration.Generator.PSweightsPythia.PythiaPSweightsSettings_cfi import *

# Hadronizer configuration
generator = cms.EDFilter("Pythia8ConcurrentHadronizerFilter",
        maxEventsToPrint = cms.untracked.int32(1),
        pythiaPylistVerbosity = cms.untracked.int32(1),
        filterEfficiency = cms.untracked.double(1.0),
        pythiaHepMCVerbosity = cms.untracked.bool(False),
        comEnergy = cms.double(13000.),
        PythiaParameters = cms.PSet(
            pythia8CommonSettingsBlock,
            pythia8CP5SettingsBlock,
            pythia8PSweightsSettingsBlock,
            processParameters = cms.vstring(
                'SLHA:keepSM = on',
                'SLHA:minMassSM = 10.',
                # Very important to enable override!
                'SLHA:allowUserOverride = on',
                #'RHadrons:allow = on',
                #'RHadrons:allowDecay = on',
                'ParticleDecays:limitTau0 = on',
                'ParticleDecays:tau0Max = 1000.1',
                'LesHouches:setLifetime = 2',
                'ParticleDecays:allowPhotonRadiation = on',
                # Set decay channel of dark photon to chi2+chi1
                '32:mayDecay = true',
                '32:oneChannel = 1 1.0 0 1000023 1000022',
                # Set decay length of chi2
                '1000023:mWidth = 0.1973269804e-12', # must set decay length by width; doing it by tau0 has not worked in the past
                #'1000023:tau0 = 1', # try setting tau0 directly
                # Set decay channels of chi2 (only mu or e+mu)
                '1000023:oneChannel = 1 1.0 0 1000022 11 -11'#,
                ),
            parameterSets = cms.vstring('pythia8CommonSettings',
                'pythia8CP5Settings',
                'processParameters',
                'pythia8PSweightsSettings',
                )
            )
        )

#     Filter setup
# ------------------------
# https://github.com/cms-sw/cmssw/blob/CMSSW_8_0_X/PhysicsTools/HepMCCandAlgos/python/genParticles_cfi.py

tmpGenParticles = cms.EDProducer("GenParticleProducer",
        saveBarCodes = cms.untracked.bool(True),
        src = cms.InputTag("generator", "unsmeared"),
        abortOnUnknownPDGCode = cms.untracked.bool(False)
        )

# https://github.com/cms-sw/cmssw/blob/CMSSW_8_0_X/RecoJets/Configuration/python/GenJetParticles_cff.py
# https://github.com/cms-sw/cmssw/blob/CMSSW_8_0_X/RecoMET/Configuration/python/GenMETParticles_cff.py
tmpGenParticlesForJetsNoNu = cms.EDProducer("InputGenJetsParticleSelector",
        src = cms.InputTag("tmpGenParticles"),
        ignoreParticleIDs = cms.vuint32(1000022,1000023,12,14,16),
        partonicFinalState = cms.bool(False),
        excludeResonances = cms.bool(False),
        excludeFromResonancePids = cms.vuint32(12, 13, 14, 16),
        tausAsJets = cms.bool(False)
        )

# https://github.com/cms-sw/cmssw/blob/CMSSW_8_0_X/RecoJets/JetProducers/python/GenJetParameters_cfi.py
GenJetParameters = cms.PSet(
        src            = cms.InputTag("tmpGenParticlesForJetsNoNu"),
        srcPVs         = cms.InputTag(''),
        jetType        = cms.string('GenJet'),
        jetPtMin       = cms.double(3.0),
        inputEtMin     = cms.double(0.0),
        inputEMin      = cms.double(0.0),
        doPVCorrection = cms.bool(False),
        # pileup with offset correction
        doPUOffsetCorr = cms.bool(False),
        # if pileup is false, these are not read:
        nSigmaPU = cms.double(1.0),
        radiusPU = cms.double(0.5),  
        # fastjet-style pileup     
        doAreaFastjet = cms.bool(False),
        doRhoFastjet = cms.bool(False),
        # if doPU is false, these are not read:
        Active_Area_Repeats = cms.int32(5),
        GhostArea = cms.double(0.01),
        Ghost_EtaMax = cms.double(6.0),
        Rho_EtaMax = cms.double(4.5),
        useDeterministicSeed = cms.bool(True),
        minSeed = cms.uint32( 14327 )
        )

# https://github.com/cms-sw/cmssw/blob/CMSSW_8_0_X/RecoJets/JetProducers/python/ak4GenJets_cfi.py
tmpAk4GenJetsNoNu = cms.EDProducer("FastjetJetProducer",
        GenJetParameters,
        jetAlgorithm = cms.string("AntiKt"),
        rParam       = cms.double(0.4)
        )

genHTFilter = cms.EDFilter("GenHTFilter",
        src = cms.InputTag("tmpAk4GenJetsNoNu"), #GenJet collection as input
        jetPtCut = cms.double(80.0), #GenJet pT cut for HT
        jetEtaCut = cms.double(5.0), #GenJet eta cut for HT
        genHTcut = cms.double(80.0) #genHT cut
        )

tmpGenMetTrue = cms.EDProducer("GenMETProducer",
        src = cms.InputTag("tmpGenParticlesForJetsNoNu"),
        onlyFiducialParticles = cms.bool(False), ## Use only fiducial GenParticles
        globalThreshold = cms.double(0.0), ## Global Threshold for input objects
        usePt   = cms.bool(True), ## using Pt instead Et
        applyFiducialThresholdForFractions = cms.bool(False),
        )
genMETfilter1 = cms.EDFilter("CandViewSelector",
        src = cms.InputTag("tmpGenMetTrue"),
        cut = cms.string("pt > 80")
        )

genMETfilter2 = cms.EDFilter("CandViewCountFilter",
        src = cms.InputTag("genMETfilter1"),
        minNumber = cms.uint32(1),
        )

## Choose to enable or disable the MET and jet gen-level filters
#ProductionFilterSequence = cms.Sequence(generator)
ProductionFilterSequence = cms.Sequence(generator*tmpGenParticles *
        tmpGenParticlesForJetsNoNu * tmpAk4GenJetsNoNu * genHTFilter *
        tmpGenMetTrue * genMETfilter1 * genMETfilter2)

