
from typing import Dict

import excel_utils as eu

from ..report_elements import ReportItem, ReportTable, WorksheetChart
from ..snap_operations import SnapType
from .layouts import DashboardLayout
from .styles_init import set_styles

SHEET_NAME = 'Dashboard'


def generate_dashboard_sheet(
    writer,
    data: Dict,
) -> None:
    '''generate elements on the dashboard sheet'''

    layout = DashboardLayout()
    styles, worksheet = set_up_workbook(writer, sheet_name=SHEET_NAME)
    insert_header(worksheet, styles)
    report_tables = insert_tables(data, styles, worksheet)

    table_name = 'sector_exposure_df'
    sector_exposure_chart = WorksheetChart(
        table_name=table_name,
        columns=['Long', 'Short'],
        categories_name='Sector Exposure',
        snap_element=report_tables.get(table_name),
        snap_mode=SnapType.RIGHT,
        page_layout=layout,
        margin=1,
    )
    eu.insert_chart(writer, worksheet, sector_exposure_chart)
    format_worksheet(worksheet, layout)


def set_up_workbook(workbook, sheet_name: str):

    styles = set_styles(workbook)
    if sheet_name not in workbook.sheetnames:
        workbook.add_worksheet(sheet_name)

    worksheet = workbook.get_worksheet_by_name(sheet_name)
    return styles, worksheet


def insert_header(worksheet, styles) -> None:
    '''inserts header to the worksheet'''
    pass


def insert_tables(data, styles, worksheet) -> Dict[str, ReportTable]:
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


def format_worksheet(worksheet, layout) -> None:
    for col in layout.NUMERIC_COLUMNS:
        worksheet.set_column(f'{col}:{col}', layout.NUMERIC_COLUMNS_WIDTH)

    for col in layout.CATEGORY_COLUMNS:
        worksheet.set_column(f'{col}:{col}', layout.CATEGORY_COLUMNS_WIDTH)

    for col in layout.SIDE_COLUMNS:
        worksheet.set_column(f'{col}:{col}', layout.SIDE_COLUMNS_WIDTH)

    for col in layout.MIDDLE_COLUMNS:
        worksheet.set_column(f'{col}:{col}', layout.MIDDLE_COLUMNS_WIDTH)

    worksheet.set_zoom(100)
