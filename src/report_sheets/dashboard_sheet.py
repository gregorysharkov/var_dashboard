from typing import Dict

import src.excel_utils.excel_utils as eu
from src.excel_utils.header import insert_header
from src.excel_utils.set_up_workbook import set_up_workbook
from src.excel_utils.sheet_format import format_dashboard_worksheet
from src.layouts.layouts import DashboardLayout

from ..report_items.report_table import ReportTable
from ..report_items.snap_operations import SnapType
from ..report_items.worksheet_chart import WorksheetChart

SHEET_NAME = 'Dashboard'


def generate_dashboard_sheet(
    writer,
    data: Dict,
) -> None:
    '''generate elements on the dashboard sheet'''

    layout = DashboardLayout()
    styles, worksheet = set_up_workbook(writer, sheet_name=SHEET_NAME)
    insert_header(worksheet, styles, layout)
    report_tables = insert_dashboard_tables(data, styles, worksheet)
    _charts = insert_dashboard_charts(writer, layout, worksheet, report_tables)

    format_dashboard_worksheet(worksheet, layout)


def insert_dashboard_tables(data, styles, worksheet) -> Dict[str, ReportTable]:
    return_dict = {}
    table_name = 'var_structured_position_top10'
    var_top_10 = ReportTable(
        data=data.get(table_name),  # type: ignore
        table_name=table_name,
        initial_position=(1, 4),
        values_format=styles.get('percentage'),
    )
    eu.insert_table(worksheet, report_table=var_top_10)
    return_dict.update({table_name: var_top_10})

    table_name = 'var_structured_position_bottom10'
    var_bottom_10 = ReportTable(
        data=data.get(table_name),  # type: ignore
        table_name=table_name,
        values_format=styles.get('percentage'),
        snap_element=var_top_10,
        snap_mode=SnapType.RIGHT,
        margin=1,
    )
    eu.insert_table(worksheet, report_table=var_bottom_10)
    return_dict.update({table_name: var_bottom_10})

    table_name = 'fund_exp_pct_dashboard'
    data['fund_exp_pct_dashboard'].set_index(
        ["Fund Exposures %"], inplace=True)
    fund_exp_pct = ReportTable(
        data=data.get(table_name),  # type: ignore
        table_name=table_name,
        values_format=styles.get('percentage'),
        snap_element=var_top_10,
        snap_mode=SnapType.DOWN,
    )
    eu.insert_table(worksheet, report_table=fund_exp_pct)
    return_dict.update({table_name: fund_exp_pct})

    table_name = 'fund_exp_usd_dashboard'
    data['fund_exp_usd_dashboard'].set_index(
        ["Fund Exposures $"], inplace=True)
    fund_exp_usd = ReportTable(
        data=data.get(table_name),  # type: ignore
        table_name=table_name,
        values_format=styles.get('currency'),
        snap_element=fund_exp_pct,
        snap_mode=SnapType.RIGHT,
        margin=3,
    )
    eu.insert_table(worksheet, report_table=fund_exp_usd)
    return_dict.update({table_name: fund_exp_usd})

    table_name = 'sector_exposure_df'
    sector_exposure = ReportTable(
        data=data.get(table_name),  # type: ignore
        table_name=table_name,
        values_format=styles.get('percentage'),
        snap_element=fund_exp_pct,
        snap_mode=SnapType.DOWN,
    )
    eu.insert_table(worksheet, sector_exposure)
    return_dict.update({table_name: sector_exposure})

    table_name = 'macro_factor_decomp_df'
    macro_factor_decomp = ReportTable(
        data=data.get(table_name),  # type: ignore
        table_name=table_name,
        values_format=styles.get('percentage'),
        snap_element=sector_exposure,
        snap_mode=SnapType.DOWN,
    )
    eu.insert_table(worksheet, macro_factor_decomp)
    return_dict.update({table_name: macro_factor_decomp})

    table_name = 'sector_factor_decomp_df'
    sector_factor_decomp = ReportTable(
        data=data.get(table_name),  # type: ignore
        table_name=table_name,
        values_format=styles.get('percentage'),
        snap_element=macro_factor_decomp,
        snap_mode=SnapType.DOWN,
    )
    eu.insert_table(worksheet, sector_factor_decomp)
    return_dict.update({table_name: sector_factor_decomp})

    table_name = 'greek_sensitivities_calc'
    greek_sensitivities = ReportTable(
        data=data.get(table_name),  # type: ignore
        table_name=table_name,
        values_format=styles.get('currency'),
        snap_element=sector_factor_decomp,
        snap_mode=SnapType.DOWN,
    )
    eu.insert_table(worksheet, greek_sensitivities)
    return_dict.update({table_name: greek_sensitivities})

    table_name = 'options_premium_calc'
    options_premium = ReportTable(
        data=data.get(table_name),  # type: ignore
        table_name=table_name,
        values_format=styles.get('currency'),
        snap_element=greek_sensitivities,
        snap_mode=SnapType.RIGHT,
        margin=3,
    )
    eu.insert_table(worksheet, options_premium)
    return_dict.update({table_name: options_premium})

    return return_dict


def insert_dashboard_charts(writer, layout, worksheet, report_tables):
    charts = {}
    table_name = 'sector_exposure_df'
    sector_exposure_chart = WorksheetChart(
        table_name=table_name,
        columns=['Long', 'Short'],
        categories_name='Sector Exposure',
        snap_element=report_tables.get(table_name),
        snap_mode=SnapType.RIGHT,
        page_layout=layout,
        margin=1,
        axis_format='percentage',
    )
    eu.insert_chart(writer, worksheet, sector_exposure_chart)
    charts.update({table_name: sector_exposure_chart})

    table_name = 'macro_factor_decomp_df'
    macro_factor_sensitivity_chart = WorksheetChart(
        table_name=table_name,
        columns=['FactorExp', 'FactorVol'],
        categories_name='Macro Factor Sensitivity',
        snap_element=report_tables.get(table_name),
        snap_mode=SnapType.RIGHT,
        page_layout=layout,
        margin=1,
        axis_format='percentage',
    )
    eu.insert_chart(
        writer, worksheet, macro_factor_sensitivity_chart)
    charts.update({table_name: macro_factor_sensitivity_chart})

    table_name = 'sector_factor_decomp_df'
    sector_sensitivity_chart = WorksheetChart(
        table_name=table_name,
        columns=['FactorExp', 'FactorVol'],
        categories_name='Sector Sensitivities',
        snap_element=report_tables.get(table_name),
        snap_mode=SnapType.RIGHT,
        page_layout=layout,
        margin=1,
        axis_format='percentage',
    )
    eu.insert_chart(
        writer, worksheet, sector_sensitivity_chart)
    charts.update({table_name: sector_sensitivity_chart})
    return charts
