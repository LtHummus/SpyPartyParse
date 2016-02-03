#!/usr/bin/env python

import sys
import os

from spyparty.ReplayParser import ReplayParser

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "No file specified"
        sys.exit(1)

    replay = sys.argv[1]
    results = ReplayParser(replay).parse()

    print "Filename: {}".format(os.path.basename(replay))
    print "Game timestamp: {}".format(results['game_time'])
    print "Spy: {}".format(results['spy'])
    print "Sniper: {}".format(results['sniper'])
    print "Match ID: {}".format(results['match_id'])
    print "Game ID: {}".format(results['sequence_number'])
    print "Game result: {}".format(results['result'])
    print "Map: {}".format(results['map'])
    print "Game type: {}".format(results['game_type'])
    print "Game duration: {} seconds".format(results['duration'])
    print "Selected missions: {}".format(', '.join(results['selected_missions']))
    print "Picked missions: {}".format(', '.join(results['picked_missions']))
    print "Completed missions: {}".format(', '.join(results['completed_missions']))
