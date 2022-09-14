#!/usr/bin/python3

import argparse
import glob
import os
import shutil
import time


def make_free_space(path, min_used_pct):
    usage = shutil.disk_usage(path)

    def enough_free(used):
        used_pct = used / usage.total * 100
        return (used_pct < min_used_pct)

    removed = []
    if not enough_free(usage.used):
        files = sorted([(f, os.lstat(f)) for f in glob.glob(os.path.join(path, '*'), recursive=True) if os.path.isfile(f)], key=lambda x: x[1].st_ctime)
        used_space = usage.used
        for file_name, file_stat in files:
            os.remove(file_name)
            removed.append(file_name)
            used_space -= file_stat.st_size
            if enough_free(used_space):
                break
    return removed


def argument_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "path",
        help="path (directory) to monitor for usage",
        type=str,
    )
    parser.add_argument(
        "min_used_pct",
        help="keep disk usage below this percentage",
        type=float,
    )
    parser.add_argument(
        "--wait_time",
        help="wait this many seconds between runs",
        type=int,
        default=3600,
    )
    return parser



def main():
    args = argument_parser().parse_args()
    while True:
        make_free_space(args.path, args.min_used_pct)
        time.sleep(arg.wait_time)


if __name__ == '__main__':
    main()
