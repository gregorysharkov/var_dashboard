import pandas as pd

import src.excel_utils.excel_utils as eu
from src.excel_utils.set_up_workbook import set_up_workbook
from src.excel_utils.sheet_format import format_dashboard_worksheet
from src.layouts.layouts import CorrelationDashboardLayout
from src.report_items.report_table import ReportTable

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
