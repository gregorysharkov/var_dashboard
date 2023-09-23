from typing import Dict

import pandas as pd

import excel_utils as eu
from src.report_items.format_dashboard_worksheet import \
    format_dashboard_worksheet
from src.report_items.insert_header import insert_header
from src.report_items.set_up_workbook import set_up_workbook

from ..report_elements import ReportTable, WorksheetChart
from ..snap_operations import SnapType
from .layouts import NarrowDashboardLayout

PNLDATA_SHEET_NAME = 'PNLReport'


def generate_pnlreport_sheet(writer, data_dict: Dict[str, pd.DataFrame]) -> None:
    '''generates pnl report sheet'''

    layout = NarrowDashboardLayout()
    styles, worksheet = set_up_workbook(writer, sheet_name=PNLDATA_SHEET_NAME)
    insert_header(worksheet, styles, layout)

    daily_returns_chart = WorksheetChart(
        initial_position=(1, 5),
        initial_rows=20,
        table_name='aum_clean',
        columns=['Daily Return',],
        categories_name='index',
        page_layout=layout,
        title='Daily vs. Cumulative Returns',
    )

    cumulative_returns_chart = WorksheetChart(
        initial_position=(1, 5),
        initial_rows=10,
        table_name='aum_clean',
        columns=['Cumulative return',],
        categories_name='index',
        page_layout=layout,
    )
    eu.insert_dual_axis_chart(
        writer, worksheet, daily_returns_chart, cumulative_returns_chart)

    return_analysis_stats = ReportTable(
        data=data_dict.get('return_analysis_stats'),
        values_format=styles.get('percentage'),
        table_name='return_analysis_stats',
        initial_position=(1, 27),
    )
    eu.insert_table(worksheet, return_analysis_stats)

    comparative_analysis_stats = ReportTable(
        data=data_dict.get('comparative_analysis_stats'),
        values_format=styles.get('percentage'),
        table_name='comparative_analysis_stats',
        snap_element=return_analysis_stats,
        snap_mode=SnapType.RIGHT,
        margin=2
    )
    eu.insert_table(worksheet, comparative_analysis_stats)

    format_dashboard_worksheet(worksheet, layout)
