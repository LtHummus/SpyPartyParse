
import sys
import lzma
from EventTypes import JOURNAL_EVENTS

STATE_START = "STATE_START"
STATE_FOUND_GROUP_TOKEN = "STATE_FOUND_GROUP_TOKEN"

LIST_GROUPS = {'objects', 'missions', 'events'}

BANNED_FIELDS = {
    'GL_RENDERER',
    'GL_VENDOR',
    'GL_VERSION',
    'Adapter',
    'MachineName',
    'MachineUserName',
    'WindowHeight',
    'WindowWidth'
}


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
            if len(tokens) == 0:
                continue
            if tokens[0] == '}':
                if self.situations:
                    pass
                elif self.is_list and not self.just_closed_groups:
                    self.curr_list.append(self.curr_group)
                    self.just_closed_groups = True
                    continue
                else:
                    self.curr_group = self.old_group
                    self.old_group = None
                    self.just_closed_groups = False
                    self.situations = False
                    self.is_list = False
                    continue

            self.just_closed_groups = False
            if len(tokens) < 2:
                continue
            if tokens[0] == "groups":
                assert self.is_list

                self.curr_group = {}
            elif tokens[0] == "group":
                # we found a new group
                self.situations = False
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
            else:
                if self.situations:
                    self.curr_list.append(tokens[3])
                else:
                    data = ' '.join(tokens[3:])
                    if data[0] == '"' and data[-1] == '"':
                        data = data[1:-1]

                    if tokens[1] not in BANNED_FIELDS:
                        self.curr_group[tokens[1]] = data

        # for security concerns, delete PII
        del self.top_group['spyparty_journal']['CPUIDs']



if __name__ == '__main__':
    filename = sys.argv[1]

    with lzma.open(filename, 'rt') as uncompressed:
        raw = str(uncompressed.read())

    journal = JournalParser(raw).top_group

    original_game_duration = float(journal['spyparty_journal']['OriginalGameDuration'])
    for event in journal['spyparty_journal']['events']:
        game_time = original_game_duration - float(event['GameTime'])
        minutes, seconds = divmod(game_time, 60)
        event_description = JOURNAL_EVENTS[event['Event3CC']]

        if event['Event3CC'] == 'STf':
            event_description %= int(event['Value'])

        if event['Event3CC'].startswith('AT'):
            # potential format string attack
            event_description = event_description % (journal['spyparty_journal']['situations'][int(event['Situation'])])

        print("%02d:%04.1f -- %s" % (minutes, seconds, event_description))


