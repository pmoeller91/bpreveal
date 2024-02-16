#!/usr/bin/env python3
"""Scans for motifs given importance scores.

This program scans over the contribution scores you calculated with
:py:mod:`interpretFlat<bpreveal.interpretFlat>` and looks for matches to motifs
called by modiscolite. It can be run with a quantile JSON from
:py:mod:`motifSeqletCutoffs<bpreveal.motifSeqletCutoffs>`, or you can include
the settings for that program inside the JSON for this one, in which case it
will perform the seqlet analysis first and save those results for you. If you
include a ``seqlet-cutoff-settings`` block in the config, it will run the
:py:mod:`motifSeqletCutoffs<bpreveal.motifSeqletCutoffs>` tools, and if you
don't include that, you must include a ``seqlet-cutoff-json`` file with the
appropriate cutoffs. It is an error to specify both ``seqlet-cutoff-settings``
and ``seqlet-cutoff-json``.

Configuration Json
------------------

BNF
^^^


.. highlight:: none

.. literalinclude:: ../../doc/bnf/motifScan.bnf


Parameter Notes
^^^^^^^^^^^^^^^

scan-contrib-h5
    The output of :py:mod:`interpretFlat<bpreveal.interpretFlat>` and contains
    contribution scores. All of the regions in this file will be scanned.

num-threads
    The number of parallel workers to use.
    Due to the streaming architecture of this program, the minimum value of
    ``num-threads`` is 3. I have found that this program scales very well up to
    70 cores, and haven't tested it beyond that.

hits-tsv
    Where would you like the hit data stored?

seqlet-cutoff-settings
    See :py:mod:`motifSeqletCutoffs<bpreveal.motifSeqletCutoffs>` for the
    specification of this block.

Quantile json
-------------

If you don't run the seqlet cutoffs during the scan, you need to provide a JSON
file containing the information for each pattern. This file is generated by
:py:mod:`motifSeqletCutoffs<bpreveal.motifSeqletCutoffs>` and saved to the name
``quantile-json`` in the configuration to that script.

BNF
^^^

::

    <quantile-json> ::=
        [<list-of-scan-patterns> ]

    <list-of-scan-patterns> ::=
        <scan-pattern>
      | <scan-pattern>, <list-of-scan-pattern>

    <scan-pattern> ::=
        {"metacluster-name" : <string>,
        "pattern-name" : <string>,
        "short-name" : <string>
        "cwm" : <motif-array>,
        "pssm" : <motif-array>,
        "seq-match-cutoff" : <float-or-null>,
        "contrib-match-cutoff" : <float-or-null>,
        "contrib-magnitude-cutoff" : <float-or-null>}

    <motif-array> ::=
        [ <list-of-base-arrays> ]

    <list-of-base-arrays> ::=
        <base-array>
      | <base-array>, <list-of-base-arrays>

    base-array ::=
        [<float>, <float>, <float>, <float>]

Parameter notes
^^^^^^^^^^^^^^^

In the quantile JSON, we find the actual numerical cutoffs for scanning.

metacluster-name, pattern-name
    These are from the modisco hdf5 file.
short-name
    is a convenient name for this motif, and is
    entirely up to you.
    The short name will be used to populate the name column in the generated
    bed and csv files.
cwm
    An array of shape (length, 4) that contains the cwm of
    the motif.
    It is used to calculate the Jaccard similarity and the L1 score.
pssm
    The sequence-based information content at each
    position, and is used to calculate sequence match scores.

seq-match-cutoff, contrib-match-cutoff, contrib-magnitude-cutoff
    The three cutoff values are the actual scores, *not quantile values*. These
    are calculated by
    :py:mod:`motifSeqletCutoffs<bpreveal.motifSeqletCutoffs>`. You could set
    these manually, but why would you?

    seq-match: Cutoff where a sequence must have a PSSM score higher than the
    original TF-MoDISco pattern seqlets' quantile value.

    contrib-match: Cutoff where a sequence must have a CWM score higher than the
    original TF-MoDISco pattern seqlets' quantile value.

    contrib-match: Cutoff where a sequence must have contribution (L1 magnitude)
    higher than the original TF-MoDISco pattern seqlets' quantile value.

    Note: Setting any of these cutoff values to 0 will mean that no value can
    be less that the lowest seqlet. Setting a cutoff to 0 is not the same as
    setting a cutoff to None.

Output Specification
--------------------

For the generated tsv file, see
:py:mod:`motifAddQuantiles<bpreveal.motifAddQuantiles>`. If you include a
``quantile-json`` in your ``seqlet-cutoff-settings``, then running
:py:mod:`motifScan<bpreveal.motifScan>` will save out the cutoff JSON.


API
---

"""
import logging
from bpreveal import motifUtils
from bpreveal import utils
import json


def main(config):
    """Run the scan.

    :param config: A JSON object matching the motifScan specification.
    """
    utils.setVerbosity(config["verbosity"])
    if "seqlet-cutoff-settings" in config:
        assert "seqlet-cutoff-json" not in config, "You cannot name a seqlet-cutoff-json to " \
            "read in the config file if you also specify seqlet-cutoff-settings."

        logging.info("Modisco seqlet analysis requested. Starting.")
        cutoffConfig = config["seqlet-cutoff-settings"]
        # First, make the pattern objects.
        tsvFname = None
        if "seqlets-tsv" in cutoffConfig:
            tsvFname = cutoffConfig["seqlets-tsv"]
        scanPatternDict = motifUtils.seqletCutoffs(cutoffConfig["modisco-h5"],
                                                   cutoffConfig["modisco-contrib-h5"],
                                                   cutoffConfig["patterns"],
                                                   cutoffConfig["seq-match-quantile"],
                                                   cutoffConfig["contrib-match-quantile"],
                                                   cutoffConfig["contrib-magnitude-quantile"],
                                                   cutoffConfig["trim-threshold"],
                                                   cutoffConfig["trim-padding"],
                                                   cutoffConfig["background-probs"],
                                                   tsvFname
                                                   )
        logging.info("Analysis complete.")
        if "quantile-json" in cutoffConfig:
            # You specified a quantile-json inside the cutoffs config.
            # Even though it isn't necessary since we just pass scanPatternDict
            # to the scanner directly, go ahead and save out the quantile json file.
            # In this case, save out the results of the seqlet analysis.
            logging.info("Saving pattern json.")
            with open(cutoffConfig["quantile-json"], "w") as fp:
                json.dump(scanPatternDict, fp, indent=4)
    else:
        # We didn't have quantile-settings, so we'd better have quantile-json.
        # (In this case, we're reading quantile-json)
        logging.debug("Loading scanner parameters.")
        with open(config["seqlet-cutoff-json"], "r") as fp:
            scanPatternDict = json.load(fp)

    scanConfig = config["scan-settings"]
    logging.info("Beginning motif scan.")
    motifUtils.scanPatterns(scanConfig["scan-contrib-h5"],
                            scanPatternDict,
                            scanConfig["hits-tsv"],
                            scanConfig["num-threads"])


if __name__ == "__main__":
    import sys
    with open(sys.argv[1], "r") as configFp:
        configJson = json.load(configFp)
    import bpreveal.schema
    bpreveal.schema.motifScan.validate(configJson)
    main(configJson)
