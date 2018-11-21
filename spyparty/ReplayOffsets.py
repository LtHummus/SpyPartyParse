import struct

from abc import ABCMeta, abstractmethod


# TODO:
# right now, we just use this object as a store of offsets, and occasionally
# we actually extract data here (such as the name stuff). Ideally, we would extract
# the data _IN_ this class, so the client of this class doesn't need to know the widths
# of all of the fields. It's not an issue now because they are always the same, but
# in the future, this will be a problem.
class ReplayOffsets(object):

    @staticmethod
    def _unpack_short(bytes, start):
        return struct.unpack('H', bytes(start, 2))[0]

    @staticmethod
    def _unpack_int(bytes, start):
        return struct.unpack('I', bytes(start, 4))[0]

    @staticmethod
    def _unpack_byte(bytes, offset):
        return struct.unpack('B', bytes[offset])[0]

    @staticmethod
    def _unpack_float(bytes, offset):
        return struct.unpack('f', bytes(offset, 4))[0]

    @staticmethod
    def _read_bytes(bytes, start, length):
        return bytes[start:(start + length)]

    @abstractmethod
    def extract_number_offset(self):
        pass

    @abstractmethod
    def get_file_version_offset(self):
        pass

    @abstractmethod
    def get_protocol_version_offset(self):
        pass

    @abstractmethod
    def get_spy_party_version_offset(self):
        pass

    @abstractmethod
    def get_duration_offset(self):
        pass

    @abstractmethod
    def get_uuid_offset(self):
        pass

    @abstractmethod
    def get_timestamp_offset(self):
        pass

    @abstractmethod
    def get_sequence_number_offset(self):
        pass

    @abstractmethod
    def extract_spy_username(self, bytes):
        pass

    @abstractmethod
    def extract_sniper_username(self, bytes):
        pass

    def contains_display_names(self):
        return False

    def contains_guest_count(self):
        return False

    def contains_start_clock(self):
        return False

    def contains_map_variant(self):
        return False

    @abstractmethod
    def get_map_variant_offset(self):
        pass

    @abstractmethod
    def get_game_result_offset(self):
        pass

    @abstractmethod
    def get_game_type_offset(self):
        pass

    @abstractmethod
    def get_level_offset(self):
        pass

    @abstractmethod
    def get_selected_missions_offset(self):
        pass

    @abstractmethod
    def get_picked_missions_offset(self):
        pass

    @abstractmethod
    def get_completed_missions_offset(self):
        pass

    def extract_spy_display_name(self, bytes):
        pass

    def extract_sniper_display_name(self, bytes):
        pass

    def get_guest_count_offset(self):
        pass

    def get_start_duration_offset(self):
        pass
