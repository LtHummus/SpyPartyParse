#!/usr/bin/env python

import struct
import datetime
import base64

from ReplayVersion3Offsets import ReplayVersion3Offsets
from ReplayVersion4Offsets import ReplayVersion4Offsets
from ReplayVersion5Offsets import ReplayVersion5Offsets
from ReplayVersion6Offsets import ReplayVersion6Offsets

FILE_VERSION = 3

RESULT_MAP = {
    0: "Missions Win",
    1: "Time Out",
    2: "Spy Shot",
    3: "Civilian Shot"
}

VARIANT_MAP = {
    "Teien": [
        "BooksBooksBooks",
        "BooksStatuesBooks",
        "StatuesBooksBooks",
        "StatuesStatuesBooks",
        "BooksBooksStatues",
        "BooksStatuesStatues",
        "StatuesBooksStatues",
        "StatuesStatuesStatues"
    ],
    "Aquarium": ["Bottom", "Top"],
}


def endian_swap(value):
    return struct.unpack("<I", struct.pack(">I", value))[0]


# LOL
# TODO: since level IDs are generated based on the hash of the level file, multiple
#       ids will map to the same level.  This table is definitely incomplete
LEVEL_MAP = {
    endian_swap(0x26C3303A): "BvB High-Rise",
    endian_swap(0xAAFA9659): "BvB (New Art) Ballroom",
    endian_swap(0x2519125B): "Ballroom",
    endian_swap(0xA1C5561A): "High-Rise",
    endian_swap(0x5EAAB328): "Old Gallery",
    endian_swap(0x750C0A29): "Courtyard 2",
    endian_swap(0x83F59536): "Panopticon",
    endian_swap(0x91A0BEA8): "Old Veranda",
    endian_swap(0xBC1F89B8): "Old Balcony",
    endian_swap(0x4073020D): "Crowded Pub",
    endian_swap(0xF3FF853B): "Pub",
    endian_swap(0xB0E7C209): "Old Ballroom",
    endian_swap(0x6B68CFB4): "Courtyard 1",
    endian_swap(0x8FE37670): "Double Modern",
    endian_swap(0x206114E6): "Modern",
    0x6f81a558: "Veranda",
    0x9dc5bb5e: "Courtyard",
    0x168f4f62: "Library",
    0x1dbd8e41: "Balcony",
    0x7173b8bf: "Gallery",
    0x9032ce22: "Terrace",
    0x2e37f15b: "Moderne",
    0x79dfa0cf: "Teien",
    0x98e45d99: "Aquarium",
}

MODE_MAP = {
    0: "k",
    1: "p",
    2: "a"
}


HEADER_DATA_MINIMUM_BYTES = 416


class ReplayParser:
    def __init__(self, replay_file_path):
        with open(replay_file_path, "rb") as replay_file:
            bytes_read = bytearray(replay_file.read())

        if len(bytes_read) < HEADER_DATA_MINIMUM_BYTES:
            raise Exception("We require a minimum of %d bytes for replay parsing" % HEADER_DATA_MINIMUM_BYTES)
        self.bytes_read = bytes_read

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
            return "k" + str(required)

        return "%s%d/%d" % (real_mode, required, available)

    def _check_magic_number(self):
        return self.bytes_read[:4] == b"RPLY"

    def _check_file_version(self):
        read_file_version = self._unpack_int(0x04)

        if read_file_version == 3:
            return ReplayVersion3Offsets()
        elif read_file_version == 4:
            return ReplayVersion4Offsets()
        elif read_file_version == 5:
            return ReplayVersion5Offsets()
        elif read_file_version == 6:
            return ReplayVersion6Offsets()
        else:
            raise Exception("Unknown file version %d" % read_file_version)

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
        if not self._check_magic_number():
            raise Exception("Unknown File")

        ret = {}

        offsets = self._check_file_version()

        ret['spy_username'] = offsets.extract_spy_username(self.bytes_read)
        ret['sniper_username'] = offsets.extract_sniper_username(self.bytes_read)

        ret['result'] = RESULT_MAP[self._unpack_int(offsets.get_game_result_offset())]

        try:
            ret['level'] = LEVEL_MAP[self._unpack_int(offsets.get_level_offset())]
        except KeyError:
            read_hash = self._unpack_int(offsets.get_level_offset())
            raise Exception("Unknown map hash %x" % read_hash)

        ret['selected_missions'] = self._unpack_missions(offsets.get_selected_missions_offset())
        ret['picked_missions'] = self._unpack_missions(offsets.get_picked_missions_offset())
        ret['completed_missions'] = self._unpack_missions(offsets.get_completed_missions_offset())

        ret['sequence_number'] = self._unpack_short(offsets.get_sequence_number_offset())

        ret['start_time'] = datetime.datetime.fromtimestamp(self._unpack_int(offsets.get_timestamp_offset()))

        ret['duration'] = int(self._unpack_float(offsets.get_duration_offset()))
        ret['game_type'] = self._get_game_type(self._unpack_int(offsets.get_game_type_offset()))

        uuid_offset = offsets.get_uuid_offset()
        ret['uuid'] = base64.urlsafe_b64encode(self.bytes_read[uuid_offset:uuid_offset+16]).decode()

        if offsets.contains_map_variant():
            try:
                ret['map_variant'] = VARIANT_MAP[ret['level']][self._unpack_int(offsets.get_map_variant_offset())]
            except KeyError:
                pass

        if ret['uuid'].find('=') > 0:
            ret['uuid'] = ret['uuid'][:ret['uuid'].find('=')]

        if offsets.contains_display_names():
            ret['spy_displayname'] = offsets.extract_spy_display_name(self.bytes_read)
            ret['sniper_displayname'] = offsets.extract_sniper_display_name(self.bytes_read)
        else:
            ret['spy_displayname'] = ret['spy_username']
            ret['sniper_displayname'] = ret['sniper_username']

        if offsets.contains_guest_count():
            ret['guest_count'] = self._unpack_int(offsets.get_guest_count_offset())

        if offsets.contains_start_clock():
            ret['start_clock_seconds'] = self._unpack_int(offsets.get_start_duration_offset())

        return ret
