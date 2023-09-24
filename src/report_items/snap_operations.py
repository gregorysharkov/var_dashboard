'''helper functions that help moving element reports to the right or down'''

from enum import Enum
from typing import Tuple

RIGHT_MARGIN = 1
BOTTOM_MARGIN = 1


class SnapType(Enum):
    RIGHT = 1
    DOWN = 2


def shift_right(position, left, margin: int = RIGHT_MARGIN) -> Tuple[int, int]:
    '''
    moves position of the table depending on the neighbour to the left
    '''
    left_range = left.range

    new_x = left_range[1][0] + margin
    old_y = position[1]
    return (new_x, old_y)


def shift_down(position, up, margin: int = BOTTOM_MARGIN) -> Tuple[int, int]:
    '''
    moves position of the table depending on the top neigbour
    '''
    up_range = up.range

    old_x = position[0]
    new_y = up_range[1][1] + margin

    return (old_x, new_y)


OPERATION_MAP = {
    SnapType.RIGHT: shift_right,
    SnapType.DOWN: shift_down,
}
