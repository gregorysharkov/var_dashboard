from typing import Dict

import src.excel_utils.excel_utils as eu
import src.excel_utils.report_group_operations as rgo
from src.excel_utils.header import insert_header
from src.excel_utils.set_up_workbook import set_up_workbook
from src.excel_utils.sheet_format import format_dashboard_worksheet
from src.layouts.layouts import WideDashboardLayout

from ..report_items.report_table import ReportTable
from ..report_items.snap_operations import SnapType
from ..report_items.worksheet_chart import WorksheetChart

SHEET_NAME = 'FactorExposures'


def generate_factor_exposures_sheet(
    writer,
    data: Dict,
) -> None:
    layout = WideDashboardLayout()
    styles, worksheet = set_up_workbook(writer, sheet_name=SHEET_NAME)
    insert_header(worksheet, styles, layout)

    data.get('macro_factor_decomp_df').set_index(
        'Macro Factor Sensitivity', inplace=True)
    macro_factor_decomp_df = ReportTable(
        data=data.get('macro_factor_decomp_df'),  # type: ignore
        table_name='macro_factor_decomp_df_fe',
        values_format=styles.get('percentage'),
        initial_position=(1, 4),
    )
    eu.insert_table(worksheet, macro_factor_decomp_df)

    macro_sensitivity_chart = WorksheetChart(
        table_name='macro_factor_decomp_df_fe',
        columns=['FactorExp', ],
        categories_name='Macro Factor Sensitivity',
        snap_element=macro_factor_decomp_df,
        snap_mode=SnapType.RIGHT,
        page_layout=layout,
        margin=1,
        axis_format='percentage',
    )
    eu.insert_series_bar_chart(writer, worksheet, macro_sensitivity_chart)

    data.get('sector_factor_decomp_df').set_index(
        'Sector Sensitivities', inplace=True)
    sector_factor_decomp_df = ReportTable(
        data=data.get('sector_factor_decomp_df'),  # type: ignore
        table_name='sector_factor_decomp_df_fe',
        values_format=styles.get('percentage'),
        snap_element=macro_factor_decomp_df,
        snap_mode=SnapType.DOWN,
    )
    eu.insert_table(worksheet, sector_factor_decomp_df)
    sector_sensitivity_chart = WorksheetChart(
        table_name='sector_factor_decomp_df_fe',
        columns=['FactorExp', ],
        categories_name='Sector Sensitivites',
        snap_element=sector_factor_decomp_df,
        snap_mode=SnapType.RIGHT,
        page_layout=layout,
        margin=1,
        axis_format='percentage',
    )
    eu.insert_series_bar_chart(writer, worksheet, sector_sensitivity_chart)

    format_dashboard_worksheet(worksheet, layout)

    grouped_top = rgo.group_items(
        data.get('risk_factor_exposure_top_n_list'), 2  # type: ignore
    )
    grouped_bottom = rgo.group_items(
        data.get('risk_factor_exposure_bottom_n_list'), 2  # type: ignore
    )

    report_tables = []
    ancor_element = sector_factor_decomp_df
    row_number = 1
    for top, bottom in zip(grouped_top, grouped_bottom):
        row_group_tables = rgo.init_row(
            styles, ancor_element, top, bottom, row_number
        )
        report_tables.extend(row_group_tables)
        ancor_element = row_group_tables[0]
        row_number = row_number + 1

    for report_table in report_tables:
        eu.insert_table(worksheet, report_table)
