
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
        is_list = False
        self.top_group = {}
        curr_group = self.top_group
        old_group = None
        curr_list = None
        just_closed_groups = False
        situations = False
        for line in data.split('\n'):
            tokens = line.split()
            if len(tokens) == 0:
                continue
            if tokens[0] == '}':
                if situations:
                    pass
                elif is_list and not just_closed_groups:
                    curr_list.append(curr_group)
                    just_closed_groups = True
                    continue
                else:
                    curr_group = old_group
                    old_group = None
                    just_closed_groups = False
                    situations = False
                    is_list = False
                    continue

            just_closed_groups = False
            if len(tokens) < 2:
                continue
            if tokens[0] == "groups":
                assert is_list

                curr_group = {}
            elif tokens[0] == "group":
                # we found a new group
                situations = False
                if tokens[1] == 'situations':
                    old_group = curr_group
                    curr_group[tokens[1]] = []
                    curr_list = curr_group[tokens[1]]
                    is_list = True
                    situations = True
                elif tokens[1] in LIST_GROUPS:
                    old_group = curr_group
                    curr_group[tokens[1]] = []
                    curr_list = curr_group[tokens[1]]
                    is_list = True
                else:
                    old_group = curr_group
                    curr_group[tokens[1]] = {}
                    curr_group = curr_group[tokens[1]]
                    is_list = False
            else:
                if situations:
                    curr_list.append(tokens[3])
                else:
                    data = ' '.join(tokens[3:])
                    if data[0] == '"' and data[-1] == '"':
                        data = data[1:-1]

                    if tokens[1] not in BANNED_FIELDS:
                        curr_group[tokens[1]] = data

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


