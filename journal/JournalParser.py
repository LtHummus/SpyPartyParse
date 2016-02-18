
import sys
import json

STATE_START = "STATE_START"
STATE_FOUND_GROUP_TOKEN = "STATE_FOUND_GROUP_TOKEN"

LIST_GROUPS = {'objects', 'situations', 'missions', 'events'}


# THIS IS GARBAGE
class JournalParser:
    def __init__(self, data):
        self.state = STATE_START
        self.is_list = False
        self.top_group = {}
        self.curr_group = self.top_group
        for line in data.split('\n'):
            tokens = line.split()
            print tokens
            if len(tokens) < 2:
                continue
            if tokens[0] == "group":
                # we found a new group
                self.curr_group[tokens[1]] = {}
                self.curr_group = self.curr_group[tokens[1]]
            elif tokens[0] == "groups":
                pass  # TODO: fill this in

            else:
                data = ' '.join(tokens[3:])
                if data[0] == '"' and data[-1] == '"':
                    data = data[1:-1]

                self.curr_group[tokens[1]] = data


if __name__ == '__main__':
    filename = sys.argv[1]
    print filename

    with open(filename, 'r') as f:
        journal = f.read()

    journal = JournalParser(journal).top_group

    print json.dumps(journal)

