from typing import Dict, List

import src.excel_utils.excel_utils as eu
import src.excel_utils.report_group_operations as rgo
from src.excel_utils.header import insert_header
from src.excel_utils.set_up_workbook import set_up_workbook
from src.excel_utils.sheet_format import format_dashboard_worksheet
from src.layouts.layouts import ExposureDashboardLayout

from ..report_items.snap_operations import SnapType
from ..report_items.worksheet_chart import WorksheetChart

SHEET_NAME = 'ExpReport'


def generate_exp_report_sheet(writer, data: List[Dict]) -> None:
    '''generates exposure report'''
    layout = ExposureDashboardLayout()
    styles, worksheet = set_up_workbook(writer, sheet_name=SHEET_NAME)
    insert_header(worksheet, styles, layout)

    report_tables = []
    report_charts = []

    first_row_tables = rgo.init_report_group(
        styles=styles,
        table_names=['strategy_exposure', 'strategy_beta_exposure'],
        tables=[
            data[0].get('Strategy exposure'),
            data[0].get('Strategy Beta Exposure')
        ],  # type: ignore
        inner_snap_mode=SnapType.RIGHT,
        inner_margin=1,
        initial_position=(1, 4),  # type: ignore
    )

    report_tables.extend(first_row_tables)
    strategy_chart = WorksheetChart(
        snap_element=report_tables[0],
        snap_mode=SnapType.DOWN,
        initial_rows=15,
        page_layout=layout,
        table_name='strategy_exposure',
        columns=['Long', 'Short'],
        categories_name='Strategy Exposure',
        title='Strategy Exposure',
        axis_format='percentage',
    )
    report_charts.append(strategy_chart)

    ancor_element = report_tables[0]
    for row in data[1:]:
        row_tables, row_chart = rgo.init_2_table_row_with_chart(
            styles=styles,
            layout=layout,
            global_snap_to=ancor_element,
            left_name=list(row.keys())[0],
            left_table=list(row.values())[0],
            right_name=list(row.keys())[1],
            right_table=list(row.values())[1],
            chart_columns=['Long', 'Short'],
        )
        ancor_element = row_tables[0]
        report_tables.extend(row_tables)
        report_charts.append(row_chart)

    for table in report_tables:
        eu.insert_table(worksheet, table)

    for report_chart in report_charts:
        eu.insert_chart(writer, worksheet, report_chart)

    format_dashboard_worksheet(worksheet, layout)
