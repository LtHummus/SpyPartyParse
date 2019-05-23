#!/usr/bin/env python

import sys

from spyparty.ReplayParser import ReplayParser


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "No file specified"
        sys.exit(1)

    filename = sys.argv[1]
    parser = ReplayParser(filename)
    results = parser.parse()

    print results
