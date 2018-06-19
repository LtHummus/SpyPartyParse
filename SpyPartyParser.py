#!/usr/bin/env python

import sys

from spyparty.ReplayParser import ReplayParser


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "No file specified"
        sys.exit(1)

    filename = sys.argv[1]
    with open(filename, "rb") as f:
        bytes_read = f.read(80 + 2 * 33)

        parser = ReplayParser(bytes_read)
        results = parser.parse()

        print results
