# pylint: disable=C0116
'''
base class for the report item
responsible for calculating position of an item
depending on the initial position or the stap element.
one of them has to be defined
'''
from dataclasses import dataclass
from functools import cached_property
from typing import Any, Optional, Tuple

from src.report_items.snap_operations import OPERATION_MAP, SnapType


@dataclass
class ReportItem:
    '''class is responsible for calculating position of the element'''
    initial_position: Optional[Tuple[int, int]] = None
    snap_element: Optional[Any] = None
    snap_mode: Optional[SnapType] = None
    margin: Optional[int] = 2

    @cached_property
    def position(self) -> Tuple[int, int]:
        if self.initial_position:
            return self.initial_position

        if self.snap_element and self.snap_mode:
            parent_position = self.snap_element.position
            shifter = OPERATION_MAP.get(self.snap_mode)
            return shifter(parent_position, self.snap_element, self.margin)

        raise NotImplementedError(
            'Could not find position of the element. Neither'
            ' initial position nor linked element are set.'
        )
