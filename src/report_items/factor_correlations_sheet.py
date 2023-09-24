import pandas as pd

import excel_utils as eu
from src.report_elements import ReportTable
from src.report_items.format_dashboard_worksheet import \
    format_dashboard_worksheet
from src.report_items.set_up_workbook import set_up_workbook

from .layouts import CorrelationDashboardLayout

SHEET_NAME = 'FactorCorrels'


def generate_factor_correlations_sheet(writer, data: pd.DataFrame) -> None:
    '''generates positions breakdown report'''

    layout = CorrelationDashboardLayout()
    styles, worksheet = set_up_workbook(writer, sheet_name=SHEET_NAME)

    factor_correlations = ReportTable(
        initial_position=(0, 0),
        data=data,  # type: ignore
        values_format=styles.get('black_float'),
        table_name='factor_correlations_heatmap',
    )

    eu.insert_table(worksheet, factor_correlations)
    eu.apply_conditional_formatting(worksheet, factor_correlations)
    format_dashboard_worksheet(worksheet, layout)
