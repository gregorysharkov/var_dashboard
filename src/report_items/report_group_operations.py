import re
from typing import Any, List, Optional, Tuple

import pandas as pd

from src.report_elements import ReportTable, WorksheetChart
from src.snap_operations import SnapType


def init_report_pair(
    styles,
    table_names: List[str],
    tables: List[str],
    inner_snap_mode: Optional[SnapType],
    inner_margin: int = 1,
    global_snap_to: Optional[ReportTable] = None,
    global_snap_mode: Optional[SnapType] = SnapType.DOWN,
    global_margin: Optional[int] = 1,
    initial_position: Optional[int] = None,
) -> List[ReportTable]:
    '''
    initiates a pair of connected tables and snaps them tho the element

    Args:
        styles: collection of workbook styles
        table_names: list of table names to be assigned to the excel tables
        tables: list of dataframes
        inner_snap_mode: how items should be snapped inside the group
        inner_margin: margin between elements of the group
    Snapping options:
        1. initial_potision: position of the first element in the group
        2. snapping element with mode and margin

    Returns:
        List of report tables connected to each other.
    '''

    # create_items
    report_items = []
    for table, data in zip(table_names, tables):
        report_item = ReportTable(
            data=data,  # type: ignore
            values_format=styles.get('percentage'),
            table_name=table,
        )
        report_items.append(report_item)

    # set item snapping
    if initial_position:
        report_items[0].initial_position = initial_position
    else:
        report_items[0].snap_element = global_snap_to
        report_items[0].snap_mode = global_snap_mode
        report_items[0].margin = global_margin

    # set concequent snapping
    for idx in range(1, len(report_items)):
        parent_item = report_items[idx-1]
        item = report_items[idx]
        item.snap_element = parent_item
        item.snap_mode = inner_snap_mode
        item.margin = inner_margin
        report_items[idx] = item

    return report_items  # type: ignore


def init_row(
    styles,
    global_snap_to: ReportTable,
    row_top_data: List[pd.DataFrame],
    row_bot_data: List[pd.DataFrame],
    row_number: int,
) -> List[ReportTable]:
    '''
    initiates report items in one line
    The first element is snapped down,
    all other elements are snapped to the right

    global_snap_to
          |
          V
    frist element —> second element –> etc
    '''

    row_data = []
    for top, bottom in zip(row_top_data, row_bot_data):
        row_data.append(top)
        row_data.append(bottom)

    row_table_names = [
        f"factor_exposure_{row_number}_{i+1}" for i in range(len(row_data))]

    row_group_tables = init_report_pair(
        global_snap_to=global_snap_to,
        global_snap_mode=SnapType.DOWN,
        global_margin=2,
        inner_snap_mode=SnapType.RIGHT,
        inner_margin=1,
        table_names=row_table_names,
        tables=row_data,
        styles=styles,
    )

    return row_group_tables


def init_2_table_row_with_chart(
    styles,
    layout,
    global_snap_to: ReportTable,
    left_name: str,
    left_table: pd.DataFrame,
    right_name: str,
    right_table: pd.DataFrame,
    chart_columns: List[str],
) -> Tuple[List[ReportTable], WorksheetChart]:
    '''
    inserts a section with to tables side by side
    and a chart below them

    The schema is the following

    global_snap_to
          |
          V
    |- first element    —> second element      -|
    |-  chart with series of the first element -|
    '''
    left_table_report = ReportTable(
        snap_element=global_snap_to,
        snap_mode=SnapType.DOWN,
        margin=18,
        data=left_table,
        table_name=re.sub(r'\W', '_', left_name.lower()),
        values_format=styles.get('percentage'),
    )
    right_table_report = ReportTable(
        snap_element=left_table_report,
        snap_mode=SnapType.RIGHT,
        margin=1,
        data=right_table,
        table_name=re.sub(r'\W', '_', right_name.lower()),
        values_format=styles.get('percentage'),
    )
    chart = WorksheetChart(
        snap_element=left_table_report,
        snap_mode=SnapType.DOWN,
        initial_rows=15,
        table_name=re.sub(r'\W', '_', left_name.lower()),
        columns=chart_columns,
        categories_name=left_name,
        page_layout=layout,
    )
    return [left_table_report, right_table_report], chart


def group_items(items: List[Any], n: int) -> List[List[Any]]:
    '''
    groups elements into groups of n elements
    The idea is to split a list of elements into 
    batches of size n
    '''
    return_list = []
    for idx in range(0, len(items), n):
        group_items = []
        for group_idx in range(min(len(items)-idx, n)):
            group_items.append(items[idx + group_idx])
        return_list.append(group_items)

    return return_list
