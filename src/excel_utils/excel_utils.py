'''Module for formatting tables in Excel'''
# pylint: disable=W0621

from itertools import cycle
from typing import Callable

import pandas as pd
from xlsxwriter import worksheet

from src.report_items.report_table import ReportTable
from src.report_items.worksheet_chart import WorksheetChart


def insert_text(worksheet, table, text) -> None:
    '''adds text 2 rows above the given cell'''
    col, row = table.position
    row -= 2
    col -= 1
    worksheet.write(row, col, text)


def merge_above(worksheet, table: ReportTable, style, text) -> None:
    '''inserts a text above the given element'''

    (start_col, start_row), (end_col, end_row) = table.range  # type: ignore

    start_row -= 1

    worksheet.merge_range(start_row, start_col-1,
                          start_row, end_col-1, text, style)


def merge_to_left(worksheet, table: ReportTable, style, text) -> None:
    '''inserts merged range to the left'''
    # pylint: disable=W0621
    (start_col, start_row), (end_col, end_row) = table.range

    worksheet.merge_range(start_row, start_col-1,
                          end_row, start_col-1,
                          text, style
                          )


def insert_table(
    worksheet: worksheet,  # type: ignore
    report_table: ReportTable,
    date_index: bool = False
) -> None:
    '''
    writes a given table and formats it as a table

    Args:
        data: data to be inserted
    '''
    # TODO: this should not be here... Need a wrapper
    if date_index:
        report_table.data.reset_index(inplace=True)
        report_table.data.iloc[:, 0] = pd.to_datetime(
            report_table.data.iloc[:, 0],
            format=r'%Y-%m-%d'
        )
    else:
        report_table.data.reset_index(inplace=True)

    report_table.data.columns = [str(col) for col in report_table.data.columns]

    start_col, start_row = report_table.range[0]
    end_col, end_row = report_table.range[1]  # type: ignore
    end_col = end_col - 1

    worksheet.add_table(  # type: ignore
        start_row, start_col,
        end_row, end_col,
        {
            'data': report_table.data.values,
            'name': report_table.table_name,
            'columns': _set_column_types(report_table),
            'autofilter': False,
            'banded_rows': False,
            'style': 'Table Style Medium 16',
        }
    )


def apply_conditional_formatting(
    worksheet,
    report_table,
    include_first_col: bool = True
) -> None:
    '''applies conditional formatting to a specific table'''

    start_col, start_row = report_table.range[0]
    if include_first_col:
        start_col = start_col + 1
    end_col, end_row = report_table.range[1]  # type: ignore

    worksheet.conditional_format(
        start_row, start_col, end_row, end_col,
        {
            'type': '3_color_scale',
            'min_value': -1,
            'max_value': 1,
            'max_type': 'max',
            'min_color': 'red',
            'mid_color': 'white',
            'max_color': 'green',
            'mid_type': 'num',
            'mid_value': 0,
        }
    )


def _set_column_types(report_table):
    '''wrapper for calling the proper collumn type setter'''

    if isinstance(report_table.values_format, list):
        return _set_manual_column_types(report_table)

    return _set_static_column_types(report_table)


def _set_static_column_types(report_table):
    '''generates a dictionary of formats'''
    return_list = []

    data = report_table.data
    data_types = [str(x) for x in list(data.dtypes)]
    for column, column_type in zip(data.columns, data_types):
        column_format = report_table.date_format \
            if 'date' in column_type else report_table.values_format
        return_list.append({
            'header': column,
            'format': column_format,
        })

    return return_list


def _set_manual_column_types(report_table):
    '''sets each column a type specified in a list of values format'''

    return_list = []
    for column, value_format in zip(
        report_table.data.columns,
        report_table.values_format
    ):
        return_list.append({
            'header': column,
            'format': value_format,
        })

    return return_list


def insert_columns_chart(
    workbook, worksheet,
    worksheet_chart: WorksheetChart,
    stacked: bool = True,
) -> None:
    '''
    inserts a chart to the worksheet

    Args:
        workbook: active workbook
        worksheet: active worksheet
        position: tuple with x and y coordinates
        size: tuple with width and height
    '''
    chart, position = _create_column_chart(workbook, worksheet_chart, stacked)
    worksheet.insert_chart(row=position[1], col=position[0], chart=chart)


def insert_series_bar_chart(
    workbook, worksheet,
    worksheet_chart: WorksheetChart,
) -> None:
    '''inserts a chart whose x axis is a time axis'''

    chart, position = _set_series_bar_chart(workbook, worksheet_chart)
    worksheet.insert_chart(row=position[1], col=position[0], chart=chart)


def insert_dual_axis_chart(
    workbook,
    worksheet,
    worksheet_chart_bars,
    worksheet_chart_line
) -> None:
    '''adds dual axis chart'''

    bar_chart, bar_chart_position = _set_series_bar_chart(
        workbook, worksheet_chart_bars)
    series_chart, _ = _set_series_line_chart(
        workbook, worksheet_chart_line)
    bar_chart.combine(series_chart)
    worksheet.insert_chart(
        row=bar_chart_position[1], col=bar_chart_position[0], chart=bar_chart)


def _set_series_line_chart(workbook, worksheet_chart):
    '''adds a line that follows values'''

    chart = _create_stacked_line_chart_type(workbook)
    _set_chart_title(worksheet_chart, chart)
    _add_bar_series(worksheet_chart, chart, _add_time_series)
    position = _format_chart(worksheet_chart, chart)
    return chart, position


def _set_series_bar_chart(workbook, worksheet_chart):
    '''adds time series chart'''

    chart = _create_bar_chart_type(workbook)
    _set_chart_title(worksheet_chart, chart)
    _add_bar_series(worksheet_chart, chart, _add_time_series)
    position = _format_chart(worksheet_chart, chart)
    return chart, position


def _create_column_chart(workbook, worksheet_chart, stacked=True):
    chart = _create_bar_chart_type(workbook, stacked)
    _set_chart_title(worksheet_chart, chart)
    position = _format_chart(worksheet_chart, chart)
    _add_bar_series(worksheet_chart, chart, _add_series)
    return chart, position


def _create_bar_chart_type(workbook, stacked=True):
    chart_options = {'type': 'column', }
    if stacked:
        chart_options.update({'subtype': 'stacked', })
    chart = workbook.add_chart(chart_options)

    return chart


def _create_stacked_line_chart_type(workbook):
    chart = workbook.add_chart({
        'type': 'line',
        'subtype': 'stacked',
    })
    return chart


def _set_chart_title(worksheet_chart, chart):
    chart_title = worksheet_chart.title \
        if worksheet_chart.title else worksheet_chart.categories_name
    chart.set_title({
        'name': chart_title,
        'overlay': True,
    })


def _add_bar_series(worksheet_chart, chart, series_setter: Callable):
    color_generator = cycle(['#ED7D31', '#4472C4'])
    for column in worksheet_chart.columns:
        series_setter(chart, worksheet_chart.table_name,  # type: ignore
                      column, worksheet_chart.categories_name,
                      next(color_generator))


def _format_chart(worksheet_chart, chart):
    '''formats axis'''
    position = worksheet_chart.position
    size = worksheet_chart.size
    chart.set_legend({'position': 'bottom'})
    chart.set_size({'width': size[0], 'height': size[1]})
    # chart.set_style(11)
    return position


def _add_series(
    chart,
    table_name: str,
    column_name: str,
    categories: str,
    color: str
) -> None:
    '''adds a series to the given chart'''
    chart.add_series({
        'values': f'={table_name}[{column_name}]',
        'categories': f'={table_name}[{categories}]',
        'name': column_name,
        'fill': {'color': color},
    })


def _add_time_series(
    chart,
    table_name: str,
    column_name: str,
    categories,
    color: str
) -> None:
    '''adds time series to the given chart'''
    chart.add_series({
        'values': f'={table_name}[{column_name}]',
        'categories': f'={table_name}[{categories}]',
        'name': column_name,
        'fill': {'color':  color},
    })
    chart.set_x_axis({'date_axis': True})
