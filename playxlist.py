#!/usr/bin/python3
"""Module for playx."""

import argparse
import os


def parse():
    """Parse the arguments."""
    parser = argparse.ArgumentParser()

    parser.add_argument('playlist',
                        help="Playlist file to read from",
                        default=None, type=str)

    args = parser.parse_args()
    return args


def read_and_play(file):
    """Read from file and play the songs."""
    print("Reading songs from {}...".format(file))
    READ_STREAM = open(file, 'r')

    while True:
        line = READ_STREAM.readline()

        if not line:
            print("End of playlist, quitting now!")
            break

        if '\n' in line:
            line = line.replace('\n', '')

        cmd = 'python main.py "{}"'.format(line)
        os.system(cmd)


def run_oncall():
    """Run on program call."""
    args = parse()

    file = args.playlist

    read_and_play(file)


run_oncall()
