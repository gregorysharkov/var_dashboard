from typing import Dict, List

import src.excel_utils.excel_utils as eu
import src.excel_utils.report_group_operations as rgo
from src.excel_utils.header import insert_header
from src.excel_utils.set_up_workbook import set_up_workbook
from src.excel_utils.sheet_format import format_dashboard_worksheet
from src.layouts.layouts import NarrowDashboardLayout

from ..report_items.snap_operations import SnapType

SHEET_NAME = 'VaRReport'


def generate_var_report_sheet(writer, data: List[Dict]) -> None:
    '''generates var report'''

    layout = NarrowDashboardLayout()
    styles, worksheet = set_up_workbook(writer, sheet_name=SHEET_NAME)
    insert_header(worksheet, styles, layout)

    report_tables = []
    report_charts = []

    first_row_tables = rgo.init_report_group(
        styles=styles,
        table_names=['var_top10', 'var_bottom10'],
        tables=[
            data[0].get('var_top10'),
            data[0].get('var_bottom10')
        ],  # type: ignore
        inner_snap_mode=SnapType.RIGHT,
        inner_margin=2,
        initial_position=(1, 5),  # type: ignore
    )

    report_tables.extend(first_row_tables)

    ancor_item = report_tables[0]
    next_row_margin = 2
    for table_name, table_data in data[1].items():
        row_table, row_chart = rgo.init_table_with_chart(
            styles=styles,
            layout=layout,
            global_snap_to=ancor_item,
            table_name=table_name,
            table_data=table_data,
            chart_columns=['Inc95', 'Inc99'],
            next_row_margin=next_row_margin,
        )
        next_row_margin = 18
        ancor_item = row_table
        report_tables.append(row_table)
        report_charts.append(row_chart)

    for table in report_tables:
        eu.insert_table(worksheet, table)

    for report_chart in report_charts:
        eu.insert_chart(writer, worksheet, report_chart, stacked=False)

    format_dashboard_worksheet(worksheet, layout)
