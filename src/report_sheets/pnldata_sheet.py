'''data sheet with pnl data'''
from typing import Dict

import pandas as pd

import src.excel_utils.excel_utils as eu
from src.excel_utils.set_up_workbook import set_up_workbook

from ..report_items.report_table import ReportTable

PNLDATA_SHEET_NAME = 'PNLData'


def generate_pnldata_sheet(writer, data_dict: Dict[str, pd.DataFrame]) -> None:
    '''generates pnl report sheet that is used later for dashboards'''

    styles, worksheet = set_up_workbook(writer, PNLDATA_SHEET_NAME)

    # TODO: this part should be a part of data generation
    table_name = 'aum_clean'
    table = _adjust_table(data_dict.get(table_name))  # type: ignore
    aum_clean = ReportTable(
        data=table,
        table_name=table_name,
        values_format=None,
        date_format=styles.get('date'),
        initial_position=(0, 0),
    )
    eu.insert_table(worksheet, aum_clean, date_index=True)


def _adjust_table(table: pd.DataFrame) -> pd.DataFrame:
    '''formats table for the output'''

    table = _add_cumulative_return_column(table, 'Cumulative return')
    table = _add_window_std(table, 'Volatility', 252)
    table = _add_window_std(table, '20D Volatility', 20)
    table = _add_volatility_budget(table, 'Volatility Budget')
    table.rename({'ret': 'Daily Return'}, axis=1, inplace=True)
    table.dropna(inplace=True)
    table.to_excel('output/pnl_data.xlsx')

    return table


def _add_cumulative_return_column(
    data: pd.DataFrame,
    col_name: str
) -> pd.DataFrame:
    '''adds cummulative return to the data'''

    data[col_name] = data.ret.cumsum()
    return data


def _add_window_std(
    data: pd.DataFrame,
    col_name: str,
    window_size: int
) -> pd.DataFrame:
    '''adds a column with a rolling window std'''

    data[col_name] = data.ret.rolling(window=window_size).std()
    data.reset_index(inplace=True)
    for i in range(window_size):
        data.loc[i, col_name] = data.ret[:i+1].std()

    data[col_name].fillna(0, inplace=True)
    data.set_index('PeriodEndDate', inplace=True)
    return data


def _add_volatility_budget(data: pd.DataFrame, col_name: str) -> pd.DataFrame:
    '''adds volatility budget to the table'''

    data[col_name] = data['20D Volatility'] / 10

    return data
