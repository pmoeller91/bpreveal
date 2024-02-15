#!/usr/bin/env python3
"""Trains up a residual model to remove an uninteresting signal from an experiment.

BNF
---

.. highlight:: none

.. literalinclude:: ../../doc/bnf/trainCombinedModel.bnf


Parameter Notes
---------------
Most of the parameters for the combined model are the same as for a solo
model, and they are described at
:py:mod:`trainSoloModel<bpreveal.trainSoloModel>`.

use-bias-counts
    Selects if you want to add the counts prediction from the transformation
    model, and the appropriateness of this flag will depend on the nature of
    your bias. If the bias is a constant background signal, then it makes sense
    to subtract the bias contribution to the counts. However, if your bias is
    multiplied by the underlying biology, then you probably shouldn't add in
    the bias counts since they won't affect the actual experiment.

transformation-model-file
    The name of the Keras model file generated by
    :py:mod:`trainTransformationModel<bpreveal.trainTransformationModel>`.

input-length
    The input size of the *residual* model, not the *solo* model. The solo
    model, having already been created, knows its own input length. If the solo
    model's input length is smaller than the ``input-length`` setting in this
    config file, the sequence input to the solo model will automatically be
    cropped down to match.

HISTORY
-------

Before BPReveal 3.0.0, the solo model had to have the same input length as
the residual model. An auto-cropdown feature was implemented by Melanie Weilert
to remove this restriction.

API
---
"""
import json
import bpreveal.internal.disableTensorflowLogging  # pylint: disable=unused-import # noqa
from bpreveal import utils
if __name__ == "__main__":
    utils.setMemoryGrowth()
from tensorflow import keras
import bpreveal.training
from bpreveal import models
from bpreveal import logUtils
# pylint: disable=duplicate-code


def main(config):
    """Build and train a combined model."""
    logUtils.setVerbosity(config["verbosity"])
    logUtils.debug("Initializing")
    inputLength = config["settings"]["architecture"]["input-length"]
    outputLength = config["settings"]["architecture"]["output-length"]
    regressionModel = utils.loadModel(
        config["settings"]["transformation-model"]["transformation-model-file"])
    regressionModel.trainable = False
    logUtils.debug("Loaded regression model.")
    combinedModel, residualModel, _ = models.combinedModel(
        inputLength, outputLength,
        config["settings"]["architecture"]["filters"],
        config["settings"]["architecture"]["layers"],
        config["settings"]["architecture"]["input-filter-width"],
        config["settings"]["architecture"]["output-filter-width"],
        config["heads"], regressionModel)
    losses, lossWeights = bpreveal.training.buildLosses(config["heads"])

    residualModel.compile(
        optimizer=keras.optimizers.Adam(learning_rate=config["settings"]["learning-rate"]),
        loss=losses, loss_weights=lossWeights)

    combinedModel.compile(
        optimizer=keras.optimizers.Adam(learning_rate=config["settings"]["learning-rate"]),
        loss=losses, loss_weights=lossWeights)

    logUtils.debug("Models compiled.")
    bpreveal.training.trainWithGenerators(combinedModel, config, inputLength, outputLength)
    combinedModel.save(config["settings"]["output-prefix"] + "_combined" + ".model")
    residualModel.save(config["settings"]["output-prefix"] + "_residual" + ".model")
    logUtils.info("Training job completed successfully.")


if __name__ == "__main__":
    import sys
    with open(sys.argv[1], "r") as configFp:
        configJson = json.load(configFp)
    import bpreveal.schema
    bpreveal.schema.trainCombinedModel.validate(configJson)
    main(configJson)
