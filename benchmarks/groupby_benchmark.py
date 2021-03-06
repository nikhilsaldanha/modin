from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

import logging
import argparse
import ray
import os
import modin.pandas as pd

from utils import time_logger


parser = argparse.ArgumentParser(description='groupby benchmark')
parser.add_argument('--path', dest='path', help='path to the csv data file')
parser.add_argument('--logfile', dest='logfile', help='path to the log file')
args = parser.parse_args()
file = args.path
file_size = os.path.getsize(file)

if not os.path.exists(os.path.split(args.logfile)[0]):
    os.makedirs(os.path.split(args.logfile)[0])

logging.basicConfig(filename=args.logfile, level=logging.INFO)

df = pd.read_csv(file)
blocks = df._block_partitions.flatten().tolist()
ray.wait(blocks, len(blocks))

with time_logger("Groupby + sum aggregation on axis=0: {}; Size: {} bytes"
                 .format(file, file_size)):
    df_groupby = df.groupby('1')
    blocks = df_groupby.sum()._block_partitions.flatten().tolist()
    ray.wait(blocks, len(blocks))

with time_logger("Groupby mean on axis=0: {}; Size: {} bytes"
                 .format(file, file_size)):
    blocks = df_groupby.mean()._block_partitions.flatten().tolist()
    ray.wait(blocks, len(blocks))
