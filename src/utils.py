import logging

def setMemoryGrowth():
    import tensorflow as tf
    gpus = tf.config.list_physical_devices('GPU')
    try:
        tf.config.experimental.set_memory_growth(gpus[0], True)
        logging.info("GPU memory growth enabled.")
    except:
        logging.info(print("Not using GPU"))
        pass

def loadChromSizes(fname):
    #Read in a chrom sizes file and return a dictionary mapping chromosome name → size
    ret = dict()
    with open(fname, 'r') as fp:
        for line in fp:
            if(len(line) > 2):
                chrom, size = line.split()
                ret[chrom] = int(size)
    return ret


def setVerbosity(userLevel):
    levelMap = {"CRITICAL" : logging.CRITICAL,  
                "ERROR" : logging.ERROR,
                "WARNING" : logging.WARNING,
                "INFO" : logging.INFO,
                "DEBUG" : logging.DEBUG}
    logging.basicConfig(level=levelMap[userLevel])

def oneHotEncode(sequence):
    ret = np.empty((len(sequence),4), dtype='int8')
    ordSeq = np.fromstring(sequence, np.int8)
    ret[:,0] = (ordSeq == ord("A")) + (ordSeq == ord('a'))
    ret[:,1] = (ordSeq == ord("C")) + (ordSeq == ord('c'))
    ret[:,2] = (ordSeq == ord("G")) + (ordSeq == ord('g'))
    ret[:,3] = (ordSeq == ord("T")) + (ordSeq == ord('t'))
    assert (np.sum(ret) == len(sequence)), (sorted(sequence), sorted(ret.sum(axis=1)))
    return ret


