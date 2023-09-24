from typing import Dict, List

import src.excel_utils.excel_utils as eu
import src.report_sheets.report_group_operations as rgo
from src.excel_utils.set_up_workbook import set_up_workbook
from src.report_items.report_elements import ReportTable
from src.report_sheets.format_dashboard_worksheet import format_dashboard_worksheet
from src.report_sheets.insert_header import insert_header

from ..report_items.snap_operations import SnapType
from .layouts import StressDashboardLayout

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

    # print(data[2].head())
    # sector_stress_test_table = ReportTable(
    #     data=data[2],  # type: ignore
    #     table_name='sector_stress_test',
    #     snap_element=formatted_report_tables[-1],
    #     snap_mode=SnapType.DOWN,
    #     margin=2,
    #     values_format='currency'
    # )

    # report_tables.append(sector_stress_test_table)

    for table in report_tables:
        eu.insert_table(worksheet, table)

    # eu.insert_text(worksheet, report_tables[-1], 'Sector Stress Test')

    table_labels = [
        'Price & Volatility Stress Test P&L',
        'Beta & Volatility Stress Test P&L',
        'Price & Volatility Stress Test Net Exposure',
    ]
    top_captions = ['Price Shock', 'Price * Beta Shock', 'Price Shock']
    right_caption = 'Volatility Shock'
    for formatted_table, caption, label in zip(formatted_report_tables, top_captions, table_labels):
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
