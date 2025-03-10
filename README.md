# BPReveal
BPReveal is a suite of tools for building and interpreting sequence-to-profile
models of biological data. The model architectures are based on chrombpnet,
which is in turn based on BPNet.

# Components
BPReveal is designed as a set of command-line tools that can be flexibly
combined for many analysis tasks. A precise specification for each tool can be
found in the documentation.

You can find a tutorial for training a model on transcription factor data in
mouse in [this document](doc/demos/osknExample.pdf)

## Organization
BPReveal follows a traditional Unix-style directory structure:
- `bin` contains the executables. This is added to your path when you use one
  of the provided scripts to build a conda environment.
- `doc` contains examples of using the package along with a formal
  specification of all the file types and programs.
    - `doc/demos` contains demonstrations of fun things you can do with
      BPReveal.
    - `doc/presentations` contains (you guessed it!) presentations related to
      BPReveal.
- `pkg` is a silly folder that is added to your python search path, letting you
  `import bpreveal.utils` without having to mess about with $PYTHONPATH. You
  can ignore it.
- `src` contains all the programs.
    - `src/schematools` contains the json schema that are used to validate the
      input to the programs.
    - `src/internal` contains source code that must be compiled using the f2py
      routines in numpy.
    - `src/tools` contains a hodgepodge of scripts that are useful for specific
      tasks. These are not actively maintained and tested, but may be useful.
- `test` contains the files that are used in the demonstration notebooks. Note
  that `test` is not committed to the git repository - it's many gigabytes of
  data files. If you're on the Stowers network, you can find this directory at
  `/n/projects/cm2363/bpreveal/test`.


## Documentation

You can find the documentation [here](https://mmtrebuchet.github.io/bpreveal/index.html).
The BPReveal project uses Sphinx to generate documentation. If you want to build
the documentation, make sure that `INSTALL_DEVTOOLS=true` in the install script,
then run `make html` or `make latexpdf` in the doc directory.
Documentation will be in
`doc/_build/html/index.html` or `doc/_build/latex/bpreveal.pdf`.

If you're at Stowers, then the documentation will be included in the
repositories that I maintain at /n/projects/cm2363/public-bpreveal.

# Installing
To install BPReveal, EDIT and then run one of the `buildConda` scripts in the
root directory. If you're using the Cerebro cluster at Stowers, run
`buildCondaCerebro.slurm`. If you're installing BPReveal on a local machine,
run `buildCondaLocal.zsh`.

## License

BPReveal is released under the GNU GPL, either version 2 of that license or
(at your option) any later version. A copy of the license can be found in
the COPYING file.
