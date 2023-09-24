from typing import Dict

import pandas as pd

import src.excel_utils.excel_utils as eu
from src.excel_utils.set_up_workbook import set_up_workbook

from ..report_items.report_table import ReportTable

PNLDATA_SHEET_NAME = 'FactorHeatMap'


def generate_factor_heatmap_sheet(writer, data_dict: Dict[str, pd.DataFrame]) -> None:
    '''generates a heatmap sheet'''

    styles, worksheet = set_up_workbook(writer, sheet_name=PNLDATA_SHEET_NAME)

    factor_heatmap = ReportTable(
        initial_position=(0, 0),
        data=data_dict.get('factor_heatmap'),  # type: ignore
        values_format=styles.get('black_percentage'),
        table_name='factor_heatmap',
    )

    eu.insert_table(worksheet, factor_heatmap)
    eu.apply_conditional_formatting(worksheet, factor_heatmap)
