# Retained detector limitations

The topology proposal is superseded. These corrections remain relevant to the
retained [synthetic results](detector-results.md); they do not authorize further
work on the detector.

The earlier proposal attributed the crossing failure to the filter using a paper
about Frangi vesselness. That attribution was not established: this implementation
uses a Sato-like ridge response and separately rejects low-elongation components.
The responsible stage could be the ridge response, quantile mask or component
rejection. It remains unresolved by the recorded evidence.

The proposed branch extraction operated after component acceptance. It could not
recover a component already rejected at that stage. The recorded river-bank
false corridor also leaves road identity unresolved by geometry alone.

The [original proposal and correction](https://github.com/500ft/informal-road-mapping/blob/f6d485d5434d7797d1b42855ea3f524e64eed37e/docs/specs/phase-2-topology-followup/plan.md)
retain the literature attribution and unimplemented alternatives. The
[claim ledger](../../literature/claim-ledger.md) retains the wider scientific
corrections. Neither is an active task queue.
