
from typing import Dict

import pandas as pd

import excel_utils as eu
from src.report_items.set_up_workbook import set_up_workbook

from ..report_elements import ReportTable

PNLDATA_SHEET_NAME = 'PNLData'


def generate_pnldata_sheet(writer, data_dict: Dict[str, pd.DataFrame]) -> None:
    '''generates pnl report sheet that is used later for dashboards'''
    styles, worksheet = set_up_workbook(writer, PNLDATA_SHEET_NAME)

    table_name = 'aum_clean'
    table = data_dict.get(table_name)
    table['Cumulative return'] = table.ret.cumsum()
    table.rename({'ret': 'Daily Return'}, axis=1, inplace=True)
    aum_clean = ReportTable(
        data=table,
        table_name=table_name,
        values_format=None,
        date_format=styles.get('date'),
        initial_position=(0, 0),
    )
    eu.insert_table(worksheet, aum_clean, date_index=True)
