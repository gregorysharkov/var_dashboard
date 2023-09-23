from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

import pandas as pd

from .snap_operations import OPERATION_MAP, SnapType


@dataclass
class ReportItem:
    '''class is responsible for calculating position of the element'''
    initial_position: Optional[Tuple[int, int]] = None
    snap_element: Optional[Any] = None
    snap_mode: Optional[SnapType] = None
    margin: Optional[int] = 2

    @property
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


@dataclass
class ReportTable(ReportItem):
    '''
    class is responsible for storing table information
    calculates table start position and its range
    '''
    data: pd.DataFrame = None  # type: ignore
    values_format: Any = 'currency'
    date_format: Any = None
    table_name: str = 'some table'

    @property
    def range(self) -> Tuple[Tuple[int, int]]:
        '''
        returns range of the table
        coordinates x=columns, y=rows
        Returns
            tuple containing x,y of top-left and x,y of bottom-right
        '''

        return (
            # top left
            tuple(x for x in self.position),  # type: ignore
            # bottom right
            tuple(x+y for x, y in zip(self.position, self.data.shape[::-1]))
        )

    @property
    def header_range(self):
        '''
        returns coordinates of the row above the table
        the y coordinate stays the same, while the x should 
        start in start and finish in the end but should be shifted
        by 1
        '''
        start_position, end_position = self.range  # type: ignore
        return (
            (start_position[0]-1, start_position[1]),
            (start_position[0]-1, end_position[1]),
        )


@dataclass
class WorksheetChart(ReportItem):
    table_name: Optional[str] = 'some_table'
    columns: Optional[List[str]] = None
    categories_name: str = 'Some table'
    page_layout: Optional[Any] = None
    initial_rows: int = 15
    title: str = None

    @property
    def size(self) -> Tuple[float, float]:
        '''calculates size of the chart depending'''

        width = self.page_layout.pixels_to_right_edge(self.position[0])

        # the image should take the whole width
        if (not self.snap_mode) or (self.snap_mode == SnapType.DOWN):
            height = self.page_layout.pixels_to_bottom(self.initial_rows)
            return (width, height)

        # otherwise we need to calculate width and heigh depending on the snap item
        if not self.snap_element:
            height = 10
            return (width, height)

        height = self.page_layout.pixels_to_bottom(
            len(self.snap_element.data) + 1)
        return (width, height)
