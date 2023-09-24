from typing import Dict, List

import pandas as pd

import excel_utils as eu
from src.report_elements import ReportTable
from src.report_items.format_dashboard_worksheet import format_dashboard_worksheet
from src.report_items.insert_header import insert_header
from src.report_items.set_up_workbook import set_up_workbook

from .layouts import PositionsDashboardLayout

SHEET_NAME = 'PositionsSummary'


def generate_positions_summary_sheet(writer, data: pd.DataFrame) -> None:
    '''generates var report'''

    layout = PositionsDashboardLayout()
    styles, worksheet = set_up_workbook(writer, sheet_name=SHEET_NAME)
    insert_header(worksheet, styles, layout)

    raw_formats = [None, 'integer', 'percentage'] + \
        ['float']*2 + ['percentage', 'currency'] + ['currency', 'percentage']*2
    formats = [styles.get(fmt) for fmt in raw_formats]
    report_table = ReportTable(
        initial_position=(1, 4),
        data=data,
        table_name='position_summary',
        values_format=formats,
    )

    eu.insert_table(worksheet, report_table)

    format_dashboard_worksheet(worksheet, layout)
