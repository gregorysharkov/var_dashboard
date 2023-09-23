from typing import List

from src.report_elements import ReportTable
from src.snap_operations import SnapType


def init_group(
    global_snap_to: ReportTable,
    global_snap_mode: SnapType,
    global_margin: int,
    inner_snap_mode: SnapType,
    inner_margin: int,
    table_names: List[str],
    tables: List[str],
    styles
) -> List[ReportTable]:
    '''initiates a pair of connected tables and snaps them tho the element'''

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
    ancor_item = report_items[0]
    ancor_item.snap_element = global_snap_to
    ancor_item.snap_mode = global_snap_mode
    ancor_item.margin = global_margin
    report_items[0] = ancor_item

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
    '''initiates report items in one line'''

    row_data = []
    for top, bottom in zip(row_top_data, row_bot_data):
        row_data.append(top)
        row_data.append(bottom)

    row_table_names = [
        f"factor_exposure_{row_number}_{i+1}" for i in range(len(row_data))]

    row_group_tables = init_group(
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


def group_items(items: List[Any], n) -> List[List[Any]]:
    '''groups elements into groups of n elements'''
    return_list = []
    for idx in range(0, len(items), n):
        group_items = []
        for group_idx in range(min(len(items)-idx, n)):
            group_items.append(items[idx + group_idx])
        return_list.append(group_items)

    return return_list
