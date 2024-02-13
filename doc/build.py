#!/usr/bin/env python3
"""Builds the .rst files that autodoc will use to generate the documentation."""
import os
import sys
import re

filesText = ["workflow", "programs", "setup", "breakingChanges",
             "modelArchitectures", "countsLossReweighting", "pisa", "bnf"]

filesDevelopment = ["philosophy", "changelog", "releaseChecklist"]

# Things that take a json
filesMajor = ["interpretFlat.py", "interpretPisa.py", "makePredictionsBed.py",
              "makePredictionsFasta.py", "motifScan.py",
              "motifSeqletCutoffs.py", "prepareBed.py",
              "prepareTrainingData.py", "trainCombinedModel.py",
              "trainSoloModel.py", "trainTransformationModel.py"]
# Things that take command-line arguments
filesMinor = ["checkJson.py", "lengthCalc.py", "makeLossPlots.py", "metrics.py",
              "motifAddQuantiles.py", "predictToBigwig.py", "shapToBigwig.py",
              "shapToNumpy.py", "showModel.py"]

# Libraries that can't be executed on their own
filesApi = ["bedUtils.py", "callbacks.py", "gaOptimize.py", "generators.py",
            "interpretUtils.py", "jaccard.py", "layers.py", "logUtils.py",
            "losses.py", "models.py", "motifUtils.py", "schema.py",
            "ushuffle.py", "utils.py"]

filesToolsMinor = ["lossWeights.py", "revcompTools.py", "shiftBigwigs.py",
                   "tileGenome.py"]

filesToolsMajor = ["addNoise.py"]

filesApiTools = ["plots.py", "slurm.py", "addNoiseUtils.py"]


def makeHeader():
    with open("_generated/makeHeader", "w") as fp:
        allTargets = []
        for fname in filesMajor + filesMinor + filesApi:
            fp.write("_generated/{0:s}.rst: ../src/{0:s}.py build.py\n\t./build.py {0:s}\n\n".
                     format(fname[:-3]))
            allTargets.append("_generated/{0:s}.rst".format(fname[:-3]))
        for fname in filesApiTools + filesToolsMinor + filesToolsMajor:
            fp.write("_generated/{0:s}.rst: ../src/tools/{0:s}.py build.py\n\t./build.py {0:s}\n\n".
                     format(fname[:-3]))
            allTargets.append("_generated/{0:s}.rst".format(fname[:-3]))
        for fname in filesText + filesDevelopment:
            fp.write("_generated/{0:s}.rst: text/{0:s}.rst build.py\n\t./build.py {0:s}\n\n".
                     format(fname))
            allTargets.append("_generated/{0:s}.rst".format(fname))
        for fname in filesMajor + filesToolsMajor + ["base.xx"]:
            fp.write(
                "_generated/bnf/{0:s}.rst: build.py\n\t./build.py bnf\n\n".format(fname[:-3]))
            allTargets.append("_generated/bnf/{0:s}.rst".format(fname[:-3]))
        for fname in ["_generated/text.rst", "_generated/majorcli.rst",
                      "_generated/minorcli.rst", "_generated/api.rst",
                      "_generated/development.rst", "_generated/toolsapi.rst",
                      "_generated/toolsminor.rst", "_generated/toolsmajor.rst",
                      "index.rst"]:
            fp.write("{0:s}: build.py\n\t./build.py base\n\n".format(fname))
            allTargets.append("{0:s}".format(fname))
        fp.write("allGenerated = " + " ".join(allTargets) + "\n")


def makeCss():
    with open("_generated/static/custom-styles.css", "w") as fp:
        fp.write(".rst-content code.literal:not(code.xref) {\n")
        fp.write("    color: #205020;\n")
        fp.write("    background-color: #fbfbfb;\n")
        fp.write("}\n")
        fp.write('p {\n')
        fp.write('    font-family:"Libertinus Serif",serif;\n')
        fp.write('    font-feature-settings: "zero" on;\n')
        fp.write('}\n')
        fp.write('h1 {\n')
        fp.write('    font-family:"Libertinus Serif",serif;\n')
        fp.write('    font-feature-settings: "zero" on;\n')
        fp.write('}\n')
        fp.write('h2 {\n')
        fp.write('    font-family:"Libertinus Serif",serif;\n')
        fp.write('    font-feature-settings: "zero" on;\n')
        fp.write('}\n')
        fp.write('h3 {\n')
        fp.write('    font-family:"Libertinus Serif",serif;\n')
        fp.write('    font-feature-settings: "zero" on;\n')
        fp.write('}\n')
        fp.write('h4 {\n')
        fp.write('    font-family:"Libertinus Serif",serif;\n')
        fp.write('    font-feature-settings: "zero" on;\n')
        fp.write('}\n')
        fp.write('body {\n')
        fp.write('    font-family:"Libertinus Serif",serif;\n')
        fp.write('    font-feature-settings: "zero" on;\n')
        fp.write('}\n')
        fp.write("a:visited .pre {\n")
        fp.write("    color: #9B59B6;\n")
        fp.write("    background-color: #fbfbfb;\n")
        fp.write("}\n")
        fp.write(".rst-content code.xref {\n")
        fp.write("    color: #2980B9;\n")
        fp.write('    font-family:"Libertinus Mono",monospace;\n')
        fp.write('    font-feature-settings: "zero" on;\n')
        fp.write("    background-color: #fbfbfb;\n")
        fp.write("}\n")

def makeBase():
    with open("_generated/text.rst", "w") as fp:
        fp.write(".. Autogenerated by build.py\n")
        fp.write("\n********\nOverview\n********\n\n")
        fp.write("\n.. toctree::\n    :maxdepth: 2\n\n")
        for file in filesText:
            fp.write("    {0:s}\n".format(file))

    # Generate the three .rst files with pages for each module.
    with open("_generated/majorcli.rst", "w") as fp:
        fp.write(".. Autogenerated by build.py\n")
        fp.write("\n********\nMain CLI\n********\n\n")
        fp.write("\n.. toctree::\n    :maxdepth: 2\n\n")
        for file in filesMajor:
            fp.write("    {0:s}\n".format(file[:-3]))

    with open("_generated/minorcli.rst", "w") as fp:
        fp.write(".. Autogenerated by build.py\n")
        fp.write("\n***********\nUtility CLI\n***********\n\n")
        fp.write("\n.. toctree::\n    :maxdepth: 2\n\n")
        for file in filesMinor:
            fp.write("    {0:s}\n".format(file[:-3]))

    with open("_generated/toolsminor.rst", "w") as fp:
        fp.write(".. Autogenerated by build.py\n")
        fp.write("\n*********\nTools CLI\n*********\n\n")
        fp.write("\n.. toctree::\n    :maxdepth: 2\n\n")
        for file in filesToolsMinor:
            fp.write("    {0:s}\n".format(file[:-3]))

    with open("_generated/toolsmajor.rst", "w") as fp:
        fp.write(".. Autogenerated by build.py\n")
        fp.write("\n*********\nTools CLI\n*********\n\n")
        fp.write("\n.. toctree::\n    :maxdepth: 2\n\n")
        for file in filesToolsMajor:
            fp.write("    {0:s}\n".format(file[:-3]))

    with open("_generated/toolsapi.rst", "w") as fp:
        fp.write(".. Autogenerated by build.py\n")
        fp.write("\n*********\nTools API\n*********\n\n")
        fp.write("\n.. toctree::\n    :maxdepth: 2\n\n")
        for file in filesApiTools:
            fp.write("    {0:s}\n".format(file[:-3]))

    with open("_generated/api.rst", "w") as fp:
        fp.write(".. Autogenerated by build.py\n")
        fp.write("\n***\nAPI\n***\n\n")
        fp.write("\n.. toctree::\n    :maxdepth: 2\n\n")
        for file in filesApi:
            fp.write("    {0:s}\n".format(file[:-3]))

    with open("_generated/development.rst", "w") as fp:
        fp.write(".. Autogenerated by build.py\n")
        fp.write("\n***********\nDevelopment\n***********\n\n")
        fp.write("\n.. toctree::\n    :maxdepth: 2\n\n")
        for file in filesDevelopment:
            fp.write("    {0:s}\n".format(file))

    # Generate a single .rst index
    with open("index.rst", "w") as fpBig:
        fpBig.write(".. Autogenerated by build.py\n\n")
        headerStr = "BPReveal documentation"
        fpBig.write("{0:s}\n{1:s}\n\n".format(
            headerStr, '=' * len(headerStr)))
        with open("text/title.rst", "r") as inFp:
            for line in inFp:
                fpBig.write(line)
        fpBig.write("\n.. toctree::\n    :maxdepth: 2\n")
        fpBig.write("\n")
        fpBig.write("    _generated/text\n")
        fpBig.write("    _generated/majorcli\n")
        fpBig.write("    _generated/minorcli\n")
        fpBig.write("    _generated/api\n")
        fpBig.write("    _generated/development\n")
        fpBig.write("    _generated/toolsmajor\n")
        fpBig.write("    _generated/toolsminor\n")
        fpBig.write("    _generated/toolsapi\n")
        fpBig.write("\n\n.. include:: _generated/bnf/addNoise.rst\n")

        fpBig.write("\n\n*******\nIndices\n*******\n\n")
        fpBig.write(
            "* :ref:`genindex`\n* :ref:`modindex`\n* :ref:`search`\n")


def makeBnf():
    for fname in filesMajor + filesToolsMajor + ["base.xx"]:
        inFname = "bnf/{0:s}.bnf".format(fname[:-3])
        with open("_generated/bnf/{0:s}.rst".format(fname[:-3]), "w") as outFp, \
                open(inFname, "r") as inFp:
            for line in inFp:
                if m := re.match("[^<]*<([^>]*)> ::=", line):
                    # Create an anchor that I can jump to.
                    outFp.write('.. raw:: html\n\n')
                    outFp.write('    <a name="{0:s}"></a>\n\n'.format(m.group(1)))
                    outFp.write(".. _{0:s}:\n\n".format(m.group(1)))
                    outFp.write(".. highlight:: none\n\n")
                    outFp.write(".. parsed-literal::\n\n")
                    outFp.write("    " + line)
                else:
                    outFp.write("    ")
                    inName = False
                    curName = ''
                    for c in line:
                        if not inName:
                            outFp.write(c)
                            if c == '<':
                                inName = True
                        elif c == '>':
                            outFp.write(
                                ":ref:`{0:s}<{0:s}>`>".format(curName))
                            inName = False
                            curName = ''
                        else:
                            curName = curName + c


def tryBuildFile(fname, modName):
    with open("_generated/" + modName + ".rst", "w") as fp:
        fp.write(".. Autogenerated by build.py\n")
        lineBreak = '=' * len(modName)
        fp.write("\n{0:s}\n{1:s}\n\n".format(modName, lineBreak))

        if fname in filesMajor + filesToolsMajor:
            toolsAdd = "tools." if (fname in filesToolsMajor) else ""
            fp.write(".. automodule:: bpreveal.{0:s}\n    :members:\n\n".
                     format(toolsAdd + modName))
            fp.write(".. highlight:: python\n\n")

            fp.write("Schema\n------\n.. highlight:: json\n")
            fp.write(".. literalinclude:: ../../src/schematools/{0:s}.schema\n\n".
                     format(modName))
        elif fname in filesMinor + filesToolsMinor:
            toolsAdd = "tools." if (fname in filesToolsMinor) else ""
            fp.write("Help Info\n---------\n\n")
            fp.write(".. highlight:: none\n\n")
            fp.write(".. argparse::\n")
            fp.write("    :module: bpreveal.{0:s}\n".format(
                toolsAdd + modName))
            fp.write("    :func: getParser\n")
            fp.write("    :prog: {0:s}\n\n".format(modName))
            fp.write("Usage\n-----\n\n")
            fp.write("\n.. highlight:: python\n\n")
            fp.write(".. automodule:: bpreveal.{0:s}\n    :members:\n\n".
                     format(toolsAdd + modName))
        elif modName == "schema":
            fp.write(".. automodule:: bpreveal.{0:s}\n\n".
                     format(modName))
            fp.write(
                "    .. autodata:: schemaMap(dict[str, Draft7Validator])\n")
            fp.write("        :annotation:\n\n")
            for majorFile in filesMajor:
                fp.write("    .. autodata:: {0:s}(Draft7Validator)\n".format(
                    majorFile[:-3]))
                fp.write("        :annotation:\n\n")

        else:
            toolsAdd = "tools." if (fname in filesApiTools) else ""
            fp.write(".. automodule:: bpreveal.{0:s}\n    :members:\n\n".
                     format(toolsAdd + modName))
        fp.write("\n.. raw:: latex\n\n    \\clearpage\n")
        fp.write("\n.. raw:: latex\n\n    \\clearpage\n")


def main():
    if len(sys.argv) > 1:
        requestName = sys.argv[1]
    else:
        requestName = None
    # Prose

    if not os.path.exists("_generated"):
        os.mkdir("_generated")

    if not os.path.exists("_generated/static"):
        os.mkdir("_generated/static")

    if not os.path.exists("_generated/bnf"):
        os.mkdir("_generated/bnf")

    if not os.path.exists("_generated/templates"):
        os.mkdir("_generated/templates")

    # Always write a new header for the makefile.
    # In a bit of an incestuous daisy-chain, this program generates
    # a file called makeHeader in _generated, and then
    # the makefile includes it.
    # The makefile also has a rule to make makeHeader, which invokes
    # this script. It's amazing that it works!
    makeHeader()

    if requestName == "base":
        makeBase()
        makeCss()

    if requestName == "bnf":
        makeBnf()

    # Generate a .rst file for every module.
    for fname in filesMajor + filesMinor + filesApi + \
            filesToolsMinor + filesApiTools + filesToolsMajor:
        modName = fname[:-3]
        if modName == requestName:
            tryBuildFile(fname, modName)

    # Now copy over the prose documentation.
    #

    for fname in filesText + filesDevelopment:
        if fname == requestName:
            with open("_generated/{0:s}.rst".format(fname), "w") as fp:
                with open("text/{0:s}.rst".format(fname), "r") as inFp:
                    for line in inFp:
                        fp.write(line)


if __name__ == "__main__":
    main()
