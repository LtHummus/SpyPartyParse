
import sys
import json

STATE_START = "STATE_START"
STATE_FOUND_GROUP_TOKEN = "STATE_FOUND_GROUP_TOKEN"

LIST_GROUPS = {'objects', 'missions', 'events', 'situations'}


# THIS IS GARBAGE
class JournalParser:
    def __init__(self, data):
        self.state = STATE_START
        self.is_list = False
        self.top_group = {}
        self.curr_group = self.top_group
        self.old_group = None
        self.curr_list = None
        self.just_closed_groups = False
        self.situations = False
        for line in data.split('\n'):
            tokens = line.split()
            print tokens
            if len(tokens) == 0:
                continue
            if tokens[0] == '}':
                if self.situations:
                    print "ok"
                elif self.is_list and not self.just_closed_groups:
                    self.curr_list.append(self.curr_group)
                    self.just_closed_groups = True
                    continue
                else:
                    self.curr_group = self.old_group
                    self.old_group = None
                    continue

            self.just_closed_groups = False
            if len(tokens) < 2:
                continue
            if tokens[0] == "groups":
                assert self.is_list

                self.curr_group = {}
            elif tokens[0] == "group":
                # we found a new group
                if tokens[1] == 'situations':
                    self.old_group = self.curr_group
                    self.curr_group[tokens[1]] = []
                    self.curr_list = self.curr_group[tokens[1]]
                    self.is_list = True
                    self.situations = True
                elif tokens[1] in LIST_GROUPS:
                    self.old_group = self.curr_group
                    self.curr_group[tokens[1]] = []
                    self.curr_list = self.curr_group[tokens[1]]
                    self.is_list = True
                else:
                    self.old_group = self.curr_group
                    self.curr_group[tokens[1]] = {}
                    self.curr_group = self.curr_group[tokens[1]]
                    self.is_list = False
            elif tokens[0] == "groups":
                pass  # TODO: fill this in

            else:
                if self.situations:
                    self.curr_list.append(tokens[3])
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

