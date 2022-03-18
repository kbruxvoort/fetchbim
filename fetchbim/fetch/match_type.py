from enum import IntEnum


class MatchType(IntEnum):
    EQUALS = 0
    STARTS = 1
    ENDS = 2
    CONTAINS = 3
