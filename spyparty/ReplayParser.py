#!/usr/bin/env python

import struct
import datetime
import uuid

FILE_VERSION = 3

RESULT_MAP = {
    0: "Missions Win",
    1: "Time Out",
    2: "Spy Shot",
    3: "Civilian Shot"
}


def endian_swap(value):
    return struct.unpack("<I", struct.pack(">I", value))[0]

# LOL
# TODO: since level IDs are generated based on the hash of the level file, multiple
#       ids will map to the same level.  This table is definitely incomplete
LEVEL_MAP = {
    endian_swap(0x26C3303A): "BvB High-Rise",
    endian_swap(0xAAFA9659): "BvB (New Art) Ballroom",
    endian_swap(0x2519125B): "New Art Ballroom",
    endian_swap(0xA1C5561A): "High-Rise",
    endian_swap(0x5EAAB328): "Gallery",
    endian_swap(0x750C0A29): "Courtyard 2",
    endian_swap(0x83F59536): "Panopticon",
    endian_swap(0x91A0BEA8): "Veranda",
    endian_swap(0xBC1F89B8): "Balcony",
    endian_swap(0x4073020D): "Crowded Pub",
    endian_swap(0xF3FF853B): "Pub",
    endian_swap(0xB0E7C209): "Old Ballroom",
    endian_swap(0x6B68CFB4): "Courtyard 1",
    endian_swap(0x8FE37670): "Double Modern",
    endian_swap(0x206114E6): "Modern"
}

MODE_MAP = {
    0: "k",
    1: "p",
    2: "a"
}


class ReplayParser:
    def __init__(self, filename):
        self.filename = filename
        self.bytes_read = None

    def _unpack_missions(self, offset):
        data = self._unpack_int(offset)
        missions = []
        if data & (1 << 0):
            missions.append("Bug Ambassador")
        if data & (1 << 1):
            missions.append("Contact Double Agent")
        if data & (1 << 2):
            missions.append("Transfer Microfilm")
        if data & (1 << 3):
            missions.append("Swap Statue")
        if data & (1 << 4):
            missions.append("Inspect Statues")
        if data & (1 << 5):
            missions.append("Seduce Target")
        if data & (1 << 6):
            missions.append("Purloin Guest List")
        if data & (1 << 7):
            missions.append("Fingerprint Ambassador")

        return missions

    @staticmethod
    def _get_game_type(info):
        mode = info >> 28
        available = (info & 0x0FFFC000) >> 14
        required = info & 0x00003FFF

        real_mode = MODE_MAP[mode]
        if real_mode == "k":
            return "k" + str(available)

        return "%s%d/%d" % (real_mode, required, available)

    def _check_magic_number(self):
        return self.bytes_read[:4] == "RPLY"

    def _check_file_version(self):
        return self.bytes_read[4:8] == 3

    def _read_bytes(self, start, length):
        return self.bytes_read[start:(start + length)]

    def _unpack_short(self, start):
        return struct.unpack('H', self._read_bytes(start, 2))[0]

    def _unpack_int(self, start):
        return struct.unpack('I', self._read_bytes(start, 4))[0]

    def _unpack_byte(self, offset):
        return struct.unpack('B', self.bytes_read[offset])[0]

    def _unpack_float(self, offset):
        return struct.unpack('f', self._read_bytes(offset, 4))[0]

    def parse(self):
        with open(self.filename, "rb") as f:
            self.bytes_read = f.read(80 + 2 * 33)

        if not self._check_magic_number():
            raise Exception("Unknown File")

        if not self._check_magic_number():
            raise Exception("Unknown replay file format")

        spy_name_len = ord(self.bytes_read[0x2E])
        sniper_name_len = ord(self.bytes_read[0x2F])

        spy_name = self._read_bytes(0x50, spy_name_len)
        sniper_name = self._read_bytes(0x50 + spy_name_len, sniper_name_len)

        result = RESULT_MAP[self._unpack_int(0x30)]

        replay_map = LEVEL_MAP[self._unpack_int(0x38)]

        selected_missions = self._unpack_missions(0x3C)
        picked_missions = self._unpack_missions(0x40)
        completed_missions = self._unpack_missions(0x44)

        sequence_number = self._unpack_short(0x2C)
        match_id = self._unpack_short(0x2A)

        start_time = datetime.datetime.fromtimestamp(self._unpack_int(0x28))

        duration = int(self._unpack_float(0x14))
        game_type = self._get_game_type(self._unpack_int(0x34))

        # TODO: this I assume is the long string of ASCII in the filename...not sure
        #       how the mapping works
        game_uuid = uuid.UUID(bytes=self.bytes_read[0x18:0x18+16])

        return {
            'spy': spy_name,
            'sniper': sniper_name,
            'map': replay_map,
            'game_type': game_type,
            'selected_missions': selected_missions,
            'picked_missions': picked_missions,
            'completed_missions': completed_missions,
            'duration': duration,
            'result': result,
            'game_time': start_time,
            'sequence_number': sequence_number,
            'match_id': match_id,
            'uuid': str(game_uuid)
        }
