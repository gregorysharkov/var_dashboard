'''Module for formatting tables in Excel'''

from typing import List, Tuple

from xlsxwriter import worksheet

from src.report_elements import ReportTable, WorksheetChart


def insert_table(
    worksheet: worksheet,  # type: ignore
    report_table: ReportTable,
) -> None:
    '''
    writes a given table and formats it as a table

    Args:
        data: data to be inserted
    '''
    report_table.data.reset_index(inplace=True)

    start_col, start_row = report_table.range[0]
    end_col, end_row = report_table.range[1]
    end_col = end_col - 1

    worksheet.add_table(  # type: ignore
        start_row, start_col,
        end_row, end_col,
        {
            'data': report_table.data.values,
            'name': report_table.table_name,
            'columns': [
                {
                    'header': colname,
                    'format': report_table.values_format,
                }
                for colname in report_table.data.columns
            ],
            'autofilter': False,
            'banded_rows': False,
            'style': 'Table Style Medium 16',
        }
    )


def insert_chart(
    workbook, worksheet,
    worksheet_chart: WorksheetChart,
    # table_name: str, columns: List[str], categories: str,
    # position: Tuple[int, int],
    # size: Tuple[int, int] = (950, 425),
) -> None:
    '''
    inserts a chart to the worksheet

    Args:
        workbook: active workbook
        worksheet: active worksheet
        position: tuple with x and y coordinates
        size: tuple with width and height
    '''
    chart = workbook.add_chart({
        'type': 'column',
        'subtype': 'stacked',
    })
    chart.set_title({
        'name': worksheet_chart.categories_name,
        'overlay': True,
    })

    for column in worksheet_chart.columns:
        add_series(chart, worksheet_chart.table_name,
                   column, worksheet_chart.categories_name)

    position = worksheet_chart.position
    size = worksheet_chart.size
    chart.set_legend({'position': 'bottom'})
    chart.set_size({'width': size[0], 'height': size[1]})
    chart.set_style(37)
    worksheet.insert_chart(row=position[1], col=position[0], chart=chart)


def add_series(chart, table_name: str, column_name: str, categories: str) -> None:
    '''adds a series to the given chart'''

    chart.add_series({
        'values': f'={table_name}[{column_name}]',
        'categories': f'={table_name}[{categories}]',
        'name': table_name,
    })
