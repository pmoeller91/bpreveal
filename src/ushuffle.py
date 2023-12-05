import numpy as np
import bpreveal.internal.libushuffle as libushuffle
from bpreveal.utils import ONEHOT_AR_T
import threading

# The ushuffle implementation in C makes heavy use of global variables.
# To avoid multiple threads trampling over each other and causing races,
# declare a lock that must be obtained before ushuffle code is run.
# Note that this is a THREADING lock, not a MULTIPROCESSING lock.
# With multiprocessing, each process has its own copy of the global variables
# in ushuffle, so there's no need for a lock between processes.
_SHUFFLE_LOCK = threading.Lock()

def shuffleString(sequence: str, kmerSize: int, numShuffles: int = 1) -> list[str]:
    """Given a string sequence, perform a shuffle that maintains
    the kmer distribution.
    This is adapted from ushuffle.
    sequence should be a string in ASCII, but it should theoretically work
    on multi-byte encoded utf-8 characters so long as the kmerSize is at least
    as long as the longest byte sequence for a character in the input.
    (Please don't rely on this random fact!)

    Returns a list of shuffled strings.
    """
    ar = np.frombuffer(sequence.encode('utf-8'), dtype=np.int8)
    with _SHUFFLE_LOCK:
        shuffledArrays = libushuffle.shuffleStr(ar, kmerSize, numShuffles)
    ret = []
    for i in range(numShuffles):
        ret.append(shuffledArrays[i].tobytes().decode('utf-8'))
    return ret

def shuffleOHE(sequence: ONEHOT_AR_T, kmerSize: int, numShuffles: int = 1) -> ONEHOT_AR_T:
    """Given a one-hot encoded sequence, perform a shuffle that
    maintains the kmer distribution.
    sequence should have shape (length, alphabetLength)
    for DNA, alphabetLength = 4. It is an error to have an alphabet length of more than 8.
    Internally, this function packs the bits at each position into a character, and the
    resulting string is shuffled and then unpacked. For this reason, it is possible to have
    more than one letter be hot at one position, or even to have no letters hot at a position.
    For example, this one-hot encoded sequence is valid input:

    Pos A C G T
    0   1 0 0 0
    1   0 1 0 0
    2   1 0 1 0
    3   0 1 1 1
    4   0 0 0 0

    This is adapted from ushuffle.
    Returns an array of shape (numShuffles, length, alphabetLength)
    """
    assert sequence.shape[1] <= 8, "Cannot ushuffle a one-hot encoded sequence with "\
                                   "an alphabet of more than 8 characters."
    with _SHUFFLE_LOCK:
        shuffledSeqs = libushuffle.shuffleOhe(sequence, kmerSize, numShuffles)
    return shuffledSeqs
