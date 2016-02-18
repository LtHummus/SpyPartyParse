# SpyPartyParse

## About

This repo is a collection of utilities for parsing various SpyParty files.  Right now there is only a parser for the headers of replay files.  The parser is incomplete as it will not parse older replay files successfully as the format has changed.  There are also some level IDs that are missing from the table in the parser.  Contributions on both fronts are welcome. 

## The Journal

We now have the ability to parse journal files (note that due to LZMA compression, Python 3 is required).  This is super super super early work in progress.  Right now, the sample parser just dumps out a list of events.  A lot of work is needed to make this fancier, the most notable omission is mapping character IDs to their names (i.e. so we can figure out who was cast as spy/sniper/etc).  This code is also fragile as all hell and is liable to break on new SpyParty revisions.

## Thanks

Thanks to checker for making the awesome game [SpyParty](http://www.spyparty.com).  And for helping a bit with the reverse engineering.  Also thanks to many members of the SpyParty community for their contributions.

## Disclaimer

This project is not affiliated with SpyParty at all and is not endorsed by anyone.