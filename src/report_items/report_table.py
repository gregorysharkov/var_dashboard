'''
class is a concrete realization a ReportItem, made for a table
it should have the following attributes:
* data: a dataframe to be inserted
* values_format either one, or several excel styles defined for this workbook
* table_name. excel name of the table inserted. Will be used to create references
'''
from dataclasses import dataclass
from typing import Any, Tuple

import pandas as pd

from src.report_items.report_item import ReportItem


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
    header_style: str = 'centered_header'

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
