from typing import Dict, List

import src.excel_utils.excel_utils as eu
import src.excel_utils.report_group_operations as rgo
from src.excel_utils.header import insert_header
from src.excel_utils.set_up_workbook import set_up_workbook
from src.excel_utils.sheet_format import format_dashboard_worksheet
from src.layouts.layouts import StressDashboardLayout
from src.report_items.report_table import ReportTable

from ..report_items.snap_operations import SnapType

SHEET_NAME = 'Options&Stress'


def generate_options_stress_sheet(writer, data: List[Dict]) -> None:
    '''generates var report'''

    layout = StressDashboardLayout()
    styles, worksheet = set_up_workbook(writer, sheet_name=SHEET_NAME)
    insert_header(worksheet, styles, layout)

    report_tables = []
    formatted_report_tables = []

    table_names = rgo.group_items(list(data[0].keys()), 2)  # type: ignore
    table_data = rgo.group_items(list(data[0].values()), 2)  # type: ignore

    initial_position = (2, 6)
    global_snap_to = None

    for row_names, row_data in zip(table_names, table_data):
        row_tables = rgo.init_report_group(
            styles=styles,
            table_names=[f'os_{tbl}' for tbl in row_names],
            tables=row_data,
            inner_snap_mode=SnapType.RIGHT,
            inner_margin=2,
            initial_position=initial_position,  # type: ignore
            global_snap_to=global_snap_to,
            global_margin=2,
            format_name='currency'
        )
        report_tables.extend(row_tables)
        initial_position = None
        global_snap_to = row_tables[0]

    formatted_report_tables = rgo.init_report_group(
        styles=styles,
        table_names=list(data[1].keys()),
        tables=list(data[1].values()),
        inner_snap_mode=SnapType.DOWN,
        inner_margin=4,
        global_snap_to=report_tables[-2],
        global_snap_mode=SnapType.DOWN,
        global_margin=7,
        format_name='black_percentage'
    )

    for table in report_tables:
        eu.insert_table(worksheet, table)

    table_labels = [
        'Price & Volatility Stress Test P&L',
        'Beta & Volatility Stress Test P&L',
        'Price & Volatility Stress Test Net Exposure',
    ]
    top_captions = ['Price Shock', 'Price * Beta Shock', 'Price Shock']
    right_caption = 'Volatility Shock'
    for formatted_table, caption, label in zip(
        formatted_report_tables,
        top_captions,
        table_labels,
    ):
        eu.insert_table(worksheet, formatted_table)
        eu.apply_conditional_formatting(worksheet, formatted_table)
        eu.merge_above(
            worksheet=worksheet,
            table=formatted_table,
            style=styles.get('merged_horizontal'),
            text=caption,
        )
        eu.merge_to_left(
            worksheet,
            formatted_table,
            styles.get('merged_vertical'),
            right_caption,
        )
        eu.insert_text(worksheet, formatted_table, label)

    format_dashboard_worksheet(worksheet, layout)
