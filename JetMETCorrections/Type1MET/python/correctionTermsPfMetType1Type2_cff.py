import FWCore.ParameterSet.Config as cms

##____________________________________________________________________________||
from JetMETCorrections.Configuration.JetCorrectionServices_cff import *

##____________________________________________________________________________||
# select PFCandidates ("unclustered energy") not within jets
# for Type 2 MET correction
from CommonTools.ParticleFlow.TopProjectors.pfNoJet_cfi import pfNoJet
# the new TopProjectors now work with Ptrs
# a conversion is needed if objects are not available
# add them upfront of the sequence
pfJetsPtrForMetCorr = cms.EDProducer("PFJetFwdPtrProducer",
   src = cms.InputTag("ak4PFJets")
)
# this one is needed only if the input file doesn't have it
# solved automatically with unscheduled execution
from RecoParticleFlow.PFProducer.pfLinker_cff import particleFlowPtrs
# particleFlowPtrs = cms.EDProducer("PFCandidateFwdPtrProducer",
#    src = cms.InputTag("particleFlow")
# )
# FIXME: THIS IS A WASTE, BUT NOT CLEAR HOW TO FIX IT CLEANLY: the module
# downstream operates with View<reco::Candidate>, I wish one could read
# it from std::vector<PFCandidateFwdPtr> directly
pfCandsNotInJetsPtrForMetCorr = pfNoJet.clone(
    topCollection = cms.InputTag('pfJetsPtrForMetCorr'),
    bottomCollection = cms.InputTag('particleFlowPtrs')
)
pfCandsNotInJetsForMetCorr = cms.EDProducer("PFCandidateFromFwdPtrProducer",
    src = cms.InputTag("pfCandsNotInJetsPtrForMetCorr")
)

##____________________________________________________________________________||
corrPfMetType1 = cms.EDProducer(
    "PFJetMETcorrInputProducer",
    src = cms.InputTag('ak4PFJets'),
    offsetCorrLabel = cms.string("ak4PFL1Fastjet"),
    jetCorrLabel = cms.string("ak4PFL1FastL2L3"), # NOTE: use "ak4PFL1FastL2L3" for MC / "ak4PFL1FastL2L3Residual" for Data
    jetCorrEtaMax = cms.double(9.9),
    type1JetPtThreshold = cms.double(10.0),
    skipEM = cms.bool(True),
    skipEMfractionThreshold = cms.double(0.90),
    skipMuons = cms.bool(True),
    skipMuonSelection = cms.string("isGlobalMuon | isStandAloneMuon")
)

##____________________________________________________________________________||
pfCandMETcorr = cms.EDProducer(
    "PFCandMETcorrInputProducer",
    src = cms.InputTag('pfCandsNotInJetsForMetCorr')
    )

##____________________________________________________________________________||
corrPfMetType2 = cms.EDProducer(
    "Type2CorrectionProducer",
    srcUnclEnergySums = cms.VInputTag(
        cms.InputTag('corrPfMetType1', 'type2'),
        cms.InputTag('corrPfMetType1', 'offset'),
        cms.InputTag('pfCandMETcorr')
    ),
    type2CorrFormula = cms.string("A"),
    type2CorrParameter = cms.PSet(
        A = cms.double(1.4)
        )
    )

##____________________________________________________________________________||
correctionTermsPfMetType1Type2 = cms.Sequence(
    pfJetsPtrForMetCorr +
    particleFlowPtrs +
    pfCandsNotInJetsPtrForMetCorr +
    pfCandsNotInJetsForMetCorr +
    pfCandMETcorr +
    corrPfMetType1 +
    corrPfMetType2
    )

##____________________________________________________________________________||
