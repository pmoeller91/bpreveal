BPReveal is a suite of tools for working with sequence-to-profile models in the vein of
BPNet.

It incorporates bias correction in the style of chrombpnet-lite, but with added features
to regress out very complex biases.

It also incorporates a new interpretation tool, called :doc:`PISA<_generated/pisa>` (Pairwise
Interaction Shap Analysis) that lets you view a two-dimensional map of cause
and effect over a region.

The components of BPReveal are divided based on how you use them.

Main
    These components are command-line tools that take JSON files for configuration.
Utility
    These are command-line tools that take command-line flags.
API
    These are importable Python libraries.
Tools
    Tools are assorted programs that are occasionally useful, but not actively maintained.
    There are Main Tools, Utility Tools, and API tools.
Internal API
    These are used inside BPReveal, but are not needed for user code.


Authors
'''''''

* Charles McAnany, Ph.D.
* Melanie Weilert
* Haining Jiang
* Patrick Moeller
* Anshul Kundaje, Ph.D.
* Julia Zeitlinger, Ph.D.


Contact
'''''''

The principal contact is Charles McAnany. His Stowers address is cm2363@stowers.org, and
his personal address is bpreveal@charlesmcanany.com.

At Stowers, Melanie Weilert is an excellent resource, she is the staff bioinformatician
in the Zeitlinger lab.

If you're at Stowers and want to use BPReveal for a project, the fine folks in
Computational Biology are familiar with the package and can get you set up.


..
    Copyright 2022, 2023, 2024 Charles McAnany. This file is part of BPReveal. BPReveal is free software: You can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 2 of the License, or (at your option) any later version. BPReveal is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with BPReveal. If not, see <https://www.gnu.org/licenses/>.  # noqa  # pylint: disable=line-too-long
