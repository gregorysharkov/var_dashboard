'''creates pnl report sheet'''
from typing import Dict

import pandas as pd

import src.excel_utils.excel_utils as eu
from src.excel_utils.header import insert_header
from src.excel_utils.set_up_workbook import set_up_workbook
from src.excel_utils.sheet_format import format_dashboard_worksheet
from src.layouts.layouts import DashboardLayout

from ..report_items.report_table import ReportTable
from ..report_items.snap_operations import SnapType
from ..report_items.worksheet_chart import WorksheetChart

PNLDATA_SHEET_NAME = 'PNLReport'


def generate_pnlreport_sheet(
    writer,
    data_dict: Dict[str, pd.DataFrame]
) -> None:
    '''generates pnl report sheet'''

    layout = DashboardLayout()
    styles, worksheet = set_up_workbook(writer, sheet_name=PNLDATA_SHEET_NAME)
    insert_header(worksheet, styles, layout)

    daily_returns_chart = WorksheetChart(
        initial_position=(1, 5),
        initial_rows=20,
        table_name='aum_clean',
        columns=['Daily Return', ],
        categories_name='index',
        page_layout=layout,
        title='Daily vs. Cumulative Returns',
        axis_format='percentage',
    )

    cumulative_returns_chart = WorksheetChart(
        initial_position=(1, 5),
        initial_rows=10,
        table_name='aum_clean',
        columns=['Cumulative return', ],
        categories_name='index',
        page_layout=layout,
    )
    eu.insert_dual_axis_chart(
        writer, worksheet, daily_returns_chart, cumulative_returns_chart)

    return_analysis_stats = ReportTable(
        data=data_dict.get('return_analysis_stats'),  # type: ignore
        values_format=styles.get('percentage'),
        table_name='return_analysis_stats',
        initial_position=(1, 27),
    )
    eu.insert_table(worksheet, return_analysis_stats)

    comparative_analysis_stats = ReportTable(
        data=data_dict.get('comparative_analysis_stats'),  # type: ignore
        values_format=styles.get('percentage'),
        table_name='comparative_analysis_stats',
        snap_element=return_analysis_stats,
        snap_mode=SnapType.RIGHT,
        margin=5
    )
    eu.insert_table(worksheet, comparative_analysis_stats)

    volatility_stats = WorksheetChart(
        snap_element=return_analysis_stats,
        snap_mode=SnapType.DOWN,
        margin=2,
        table_name='aum_clean',
        columns=['Volatility', '20D Volatility'],
        categories_name='index',
        stacked=False,
        title='Rolling 20 Day Volatility vs. Rolling 1 Year Volatility',
        axis_format='percentage',
        page_layout=layout,
        initial_rows=20,
    )

    eu.insert_chart(
        writer,
        worksheet,
        volatility_stats,
        chart_type='line',
        stacked=False,
    )

    volatility_budget = WorksheetChart(
        snap_element=return_analysis_stats,
        snap_mode=SnapType.DOWN,
        margin=24,
        table_name='aum_clean',
        columns=['20D Volatility', 'Volatility Budget'],
        categories_name='index',
        stacked=False,
        title='Volatility Budget',
        axis_format='percentage',
        page_layout=layout,
        initial_rows=20,
    )
    eu.insert_chart(
        writer,
        worksheet,
        volatility_budget,
        chart_type='line',
        stacked=False,
    )
    format_dashboard_worksheet(worksheet, layout)
