# pylint: disable=C0115
'''
worksheet chart is a container to store information
about a chart that will be inserted into the worksheet.
since we are talking about a chart, the we need to know
the following attributes:
* table_name (the one that ReportTable inserts into excel namespace)
* columns: names of excel table. Will be used to add series to the chart
* page_layout. Required to calculate number of pixels from start to the page end
* initial_number of rows. If the table is not snapped to another table, it is
possible to set up number of lines this chart should take on the sheet
* title. Optional if specified, will override the title of the chart. By
default will be using name of the column used for Axes categories.
* stacked. if yes, the excel utilities will generate a stacked chart.
'''
from dataclasses import dataclass
from typing import Any, List, Optional, Tuple

from src.report_items.report_item import ReportItem

from .snap_operations import SnapType


@dataclass
class WorksheetChart(ReportItem):
    table_name: Optional[str] = 'some_table'
    columns: Optional[List[str]] = None
    categories_name: str = 'Some table'
    page_layout: Optional[Any] = None
    initial_rows: int = 15
    title: str = None  # type: ignore
    stacked: bool = True
    axis_format: str = 'float'

    @property
    def size(self) -> Tuple[float, float]:
        '''calculates size of the chart depending'''

        width = self.page_layout.pixels_to_right_edge(self.position[0])

        # the image should take the whole width
        if (not self.snap_mode) or (self.snap_mode == SnapType.DOWN):

            height = self.page_layout.pixels_to_bottom(self.initial_rows)
            return (width, height)

        # otherwise we need to calculate width and
        # heigh depending on the snap item
        if not self.snap_element:
            height = 10
            return (width, height)

        height = self.page_layout.pixels_to_bottom(
            len(self.snap_element.data) + 1)
        return (width, height)
