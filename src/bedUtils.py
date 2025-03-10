"""Some utilities for dealing with bed files."""
from typing import Literal, Any
import multiprocessing
from collections import deque
import pybedtools
import pysam
import numpy as np
import pyBigWig
from bpreveal import logUtils
from bpreveal.logUtils import wrapTqdm
from bpreveal.internal import constants


def makeWhitelistSegments(genome: pysam.FastaFile,
                          blacklist: pybedtools.BedTool | None = None) -> pybedtools.BedTool:
    """Get a list of windows where it is safe to draw inputs for your model.

    :param genome: A FastaFile (pysam object, not a string filename!).
    :param blacklist: (Optional) A BedTool that gives additional regions that should
        be excluded.
    :return: A BedTool that contains the whitelisted regions.

    Given a genome file, go over each chromosome and see where the Ns are.
    Create a BedTool that contains all regions that don't contain N.
    For example, if your genome were
    ``ATATATATnnnnnnnATATATATATATnnn``,
    then this would return a BedTool corresponding to the regions containing
    As and Ts.

    ``blacklist``, if provided, is a bed file of regions that should be treated as though
    they contained N nucleotides.
    """
    segments = []

    logUtils.debug("Building segments.")
    blacklistsByChrom = {}
    if blacklist is not None:
        # We're going to iterate over blacklist several times,
        # so save it in case it's a streaming bedtool.
        blacklist.saveas()
        for blackInterval in blacklist:
            if blackInterval.chrom not in blacklistsByChrom:
                blacklistsByChrom[blackInterval.chrom] = []
            blacklistsByChrom[blackInterval.chrom].append(blackInterval)

    for chromName in wrapTqdm(sorted(genome.references), "INFO"):
        chromSeq = genome.fetch(chromName, 0, genome.get_reference_length(chromName))
        seqVector = np.fromstring(chromSeq, np.int8)  # type: ignore
        if chromName in blacklistsByChrom:
            for blackInterval in blacklistsByChrom[chromName]:
                if blackInterval.start >= seqVector.shape[0]:
                    continue
                endPt = min(seqVector.shape[0], blackInterval.end)
                seqVector[blackInterval.start:endPt] = ord("N")
        segments.extend(_findNonN(seqVector, chromName))
    return pybedtools.BedTool(segments)


def _findNonN(inSeq: np.ndarray, chromName: str) -> list[pybedtools.Interval]:
    """Return a list of Intervals consisting of all regions of the sequence that are not N.

    :param inSeq: an array of character values - not a one-hot encoded sequence::

        inSeq[i] = ord(dnaStr[i])

    :param chromName: Just the name of the chromosome, used to populate the chrom
        field in the returned Interval objects.

    :return: A list of Intervals where the sequence is NOT ``n`` or ``N``.
    """
    segments = []
    # All bases that are not N.
    isValid = np.logical_not(np.logical_or(inSeq == ord("N"), inSeq == ord("n")))
    # ends is 1 if this base is the end of a valid region, 0 otherwise.
    ends = np.empty(isValid.shape, dtype=np.bool_)
    # starts is 1 if this base is the beginning of a valid region, 0 otherwise.
    starts = np.empty(isValid.shape, dtype=np.bool_)
    starts[0] = isValid[0]
    ends[-1] = isValid[-1]

    ends[:-1] = np.logical_and(isValid[:-1], np.logical_not(isValid[1:]))
    starts[1:] = np.logical_and(isValid[1:], np.logical_not(isValid[:-1]))
    # the Poses are the actual indices where the start and end vectors are nonzero.
    endPoses = np.flatnonzero(ends)  # type: ignore
    startPoses = np.flatnonzero(starts)  # type: ignore
    for startPos, stopPos in zip(startPoses, endPoses):
        segments.append(pybedtools.Interval(chromName, startPos, stopPos + 1))
    return segments


def tileSegments(inputLength: int, outputLength: int,
                 segments: pybedtools.BedTool,
                 spacing: int) -> pybedtools.BedTool:
    """Tile the given segments with intervals.

    :param inputLength: The input-length of your model.
    :param outputLength: The output-length of your model, and also the length of the
        intervals in the returned ``BedTool``.
    :param segments: The regions of the genome that you'd like tiled.
    :param spacing: The distance *between* the windows.
    :return: A BedTool containing Intervals of length ``outputLength``.


    ``segments`` will often come from :func:`makeWhitelistSegments`.

    ``spacing`` is the distance between the *end* of one region and the *start* of the next.
    So to tile the whole genome, set ``spacing=0``. ``spacing`` may be negative, in which
    case the tiled regions will overlap.

    When this algorithm reaches the end of a segment, it will try to place an additional
    region if it can. For example, if your window is 30 bp long, with outputLength 6,
    inputLength 10, and spacing 5 you'd get::

        012345678901234567890123456789
        --xxxxxx-----xxxxxx---xxxxxx--

    The 2 bp padding on each end comes from the fact that
    ``(inputLength - outputLength) / 2 == 2``
    Note how the last segment is not 5 bp away from the second-to-last.

    """
    logUtils.debug("Beginning to trim segments. {0:d} segments alive.".format(len(segments)))
    padding = (inputLength - outputLength) // 2
    logUtils.debug("Calculated padding of {0:d}".format(padding))

    def shrinkSegment(s: pybedtools.Interval):
        newEnd = s.end - padding
        newStart = s.start + padding
        if newEnd - newStart < outputLength:
            return False
        return pybedtools.Interval(s.chrom, newStart, newEnd)

    shrunkSegments = pybedtools.BedTool(segments).each(shrinkSegment).saveas()
    logUtils.debug("Filtered segments. {0:d} survive.".format(shrunkSegments.count()))

    # Phase 3. Generate tiling regions.
    logUtils.debug("Creating regions.")
    regions = []
    for s in wrapTqdm(shrunkSegments, "INFO"):
        startPos = s.start
        endPos = startPos + outputLength
        while endPos < s.end:
            curRegion = pybedtools.Interval(s.chrom, startPos, endPos)
            regions.append(curRegion)
            startPos += spacing + outputLength
            endPos = startPos + outputLength
        if startPos < s.end:
            # We want another region inside this segment.
            endPos = s.end
            startPos = endPos - outputLength
            regions.append(pybedtools.Interval(s.chrom, startPos, endPos))
    logUtils.debug("Regions created, {0:d} across genome.".format(len(regions)))

    return pybedtools.BedTool(regions)


def createTilingRegions(inputLength: int, outputLength: int,
                        genome: pysam.FastaFile,
                        spacing: int) -> pybedtools.BedTool:
    """Create a list of regions that tile a genome.

    :param inputLength: The input-length of your model.
    :param outputLength: The output-length of your model.
    :param genome: A FastaFile (the pysam object, not a string!)
    :param spacing: The space you'd like *between* returned intervals.
    :return: A BedTool containing regions that tile the genome.

    The returned BedTool will contain regions that are outputLength wide,
    and all regions will be far enough away from any N nucleotides that
    there will be no Ns in the input to your model.
    spacing specifies the amount of space *between* the regions. A spacing of 0
    means that the regions should join end-to-end, while a spacing of -500 would indicate
    regions that overlap by 500 bp.
    See :func:`tileSegments` for details on how the regions are placed.

    """
    # Segments are regions of the genome that contain no N nucleotides.
    # These will be split into regions in the next phase.
    segments = makeWhitelistSegments(genome)
    return tileSegments(inputLength, outputLength, segments, spacing)


def resize(interval: pybedtools.Interval, mode: str, width: int,
           genome: pysam.FastaFile) -> pybedtools.Interval | Literal[False]:
    """Resize a given interval to a new size.

    :param interval: A pyBedTools Interval object.
    :param mode: One of ``"none"``, ``"center"``, or ``"start"``.
    :param width: How long the returned Interval will be.
    :param genome: A FastaFile (the pysam object, not a string)
    :return: A newly-allocated Interval of the correct size, or ``False``
        if resizing would run off the edge of a chromosome.

    Given an interval (a PyBedTools Interval object),
    return a new Interval that is at the same coordinate.

    mode is one of:

    * "none", meaning that no resizing is done. In that case, this function will
      check that the interval obeys stop-start == width. If an interval
      does not have the correct width, an assertion will fail.
    * "center", in which case the interval is resized around its center.
    * "start", in which case the start coordinate is preserved.

    The returned interval will obey x.end - x.start == width.
    It will preserve the chromosome, name, score, and strand
    information, but not other bed fields.
    """
    start = interval.start
    end = interval.end
    match mode:
        case "none":
            if end - start != width:
                assert False, \
                       "An input region is not the expected width: {0:s}".format(str(interval))
        case "center":
            center = (end + start) // 2
            start = center - width // 2
            end = start + width
        case "start":
            start = start - width // 2
            end = start + width
        case _:
            assert False, "Unsupported resize mode: {0:s}".format(mode)
    if start <= 0 or end >= genome.get_reference_length(interval.chrom):
        return False  # We're off the edge of the chromosome.
    return pybedtools.Interval(interval.chrom, start, end, name=interval.name,
                               score=interval.score, strand=interval.strand)


def getCounts(interval: pybedtools.Interval, bigwigs: list) -> float:
    """Get the total counts from all bigwigs at a given Interval.

    :param interval: A pyBedTools Interval.
    :param bigwigs: A list of opened pyBigWig objects (not strings!).
    :return: A single number giving the total reads from all bigwigs at
        the given interval.

    NaN entries in the bigwigs are treated as zero.
    """
    total = 0
    for bw in bigwigs:
        vals = np.nan_to_num(bw.values(interval.chrom, interval.start, interval.end))
        total += np.sum(vals)
    return total


def sequenceChecker(interval: pybedtools.Interval, genome: pysam.FastaFile) -> bool:
    """For the given interval, does it only contain A, C, G, and T?

    :param interval: The interval to check.
    :param genome: A FastaFile (pysam object, not a string!).
    :return: ``True`` if the sequence matches ``"^[ACGTacgt]*$"``,
        ``False`` otherwise.
    """
    seq = genome.fetch(interval.chrom, interval.start, interval.end)
    if len(seq.upper().lstrip("ACGT")) != 0:
        # There were letters that aren't regular bases. (probably Ns)
        return False
    return True


def lineToInterval(line: str) -> pybedtools.Interval | Literal[False]:
    """Take a line from a bed file and create a PyBedTools Interval object.

    :param line: The line from the bed file
    :return: A newly-allocated pyBedTools Interval object, or ``False`` if
        the line is not a valid bed line.
    """
    if len(line.strip()) == 0 or line[0] == "#":
        return False
    initInterval = pybedtools.cbedtools.create_interval_from_list(line.split())
    return initInterval


class ParallelCounter:
    """A class that queues up getCounts() jobs and runs them in parallel.

    This is used by the prepareBed scripts.

    :param bigwigNames: The name of the bigwig files to read from
    :param numThreads: How many parallel workers should be used?
    """

    def __init__(self, bigwigNames: list[str], numThreads: int):
        self.bigwigNames = bigwigNames
        self.numThreads = numThreads
        self.inQueue = multiprocessing.Queue()
        self.outQueue = multiprocessing.Queue()
        self.inFlight = 0
        self.outDeque = deque()
        self.numInDeque = 0
        self.threads = [multiprocessing.Process(
            target=_counterThread,
            args=(bigwigNames, self.inQueue, self.outQueue))
            for _ in range(numThreads)]
        [x.start() for x in self.threads]  # pylint: disable=expression-not-assigned

    def addQuery(self, query: tuple[str, int, int], idx: Any) -> None:
        """Add a region (chrom, start, end) to the task list.

        :param query: A tuple of (chromosome, start, end) giving the region to look at.
        :param idx: An index that will be returned with the results.
        """
        self.inQueue.put(query + (idx,), timeout=constants.QUEUE_TIMEOUT)
        self.inFlight += 1
        while not self.outQueue.empty():
            self.outDeque.appendleft(self.outQueue.get(timeout=constants.QUEUE_TIMEOUT))
            self.numInDeque += 1
            self.inFlight -= 1

    def done(self):
        """Wrap up the show - close the child threads."""
        for _ in range(self.numThreads):
            self.inQueue.put(None)
        [x.join() for x in self.threads]  # pylint: disable=expression-not-assigned

    def getResult(self):
        """Get the next result.

        :return: A tuple of (counts, idx), where counts is the total counts
            for the bigwigs and idx is the index of the region you gave to addQuery.

        Note that the results will NOT be given in order - you must look at the index
        values.
        """
        if self.inFlight and self.numInDeque == 0:
            self.outDeque.appendleft(self.outQueue.get(timeout=constants.QUEUE_TIMEOUT))
            self.numInDeque += 1
            self.inFlight -= 1
        self.numInDeque -= 1
        return self.outDeque.pop()


def _counterThread(bigwigFnames: list[str], inQueue: multiprocessing.Queue,
                   outQueue: multiprocessing.Queue) -> None:
    """Thread to sum up regions of the bigwigs.

    :param bigwigFnames: A list of file names to open.
    :param inQueue: The input queue, where queries will come from.
    :param outQueue: Where the calculated counts should be put.
    :return: None, but does put results in outQueue.

    The runner, :py:class:`~ParallelCounter`, will inject regions
    in the format ``tuple[str, int, int, Any]``, which contains, in order,

    1. Chromosome (``str``), the chromosome that the region is on.
    2. Start (``int``), the start coordinate, 0-based, inclusive.
    3. End (``int``), the end coordinate, 0-based, exclusive.
    4. Index, which will be passed back with the result.

    The results put counts data into ``outQueue``, with format
    ``tuple[int, Any]``, containing:

    1. Total counts, a float.
    2. Index, which is straight from the input queue.

    The total counts for a region is specified by::

        def total(chrom, start, end):
            total = 0.0
            for bw in bigwigs:
                total += sum(abs(bw.values(chrom, start, end)))
            return total

    """
    bwFiles = [pyBigWig.open(fname) for fname in bigwigFnames]
    outDeque = deque()
    inDeque = 0
    while True:
        query = inQueue.get(timeout=constants.QUEUE_TIMEOUT)
        match query:
            case (chrom, start, end, idx):
                r = getCounts(pybedtools.Interval(chrom, start, end), bwFiles)
                outDeque.appendleft((r, idx))
                inDeque += 1
                while outQueue.empty and inDeque > 0:
                    outQueue.put(outDeque.pop())
                    inDeque -= 1
            case None:
                break
    while inDeque:
        outQueue.put(outDeque[-1], timeout=constants.QUEUE_TIMEOUT)
        inDeque -= 1
    [x.close() for x in bwFiles]  # pylint: disable=expression-not-assigned
# Copyright 2022, 2023, 2024 Charles McAnany. This file is part of BPReveal. BPReveal is free software: You can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 2 of the License, or (at your option) any later version. BPReveal is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with BPReveal. If not, see <https://www.gnu.org/licenses/>.  # noqa
