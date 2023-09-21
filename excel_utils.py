'''Module for formatting tables in Excel'''

from pandas import DataFrame, ExcelWriter


def format_table(
    data: DataFrame,
    writer: ExcelWriter,
    sheet_name: str,
    start_col: int,
    start_row: int,
    table_name: str | None = None,
) -> None:
    '''
    writes a given table and formats it as a table
    '''

    data.to_excel(writer, sheet_name=sheet_name,
                  startcol=start_col, startrow=start_row)
    worksheet = writer.sheets[sheet_name]
    max_row, max_col = data.shape
    max_row = max_row + start_row
    max_col = max_col + start_col
    worksheet.add_table(
        start_row, start_col, max_row, max_col,
        {
            'name': table_name,
            'columns': [{'header': colname} for colname in data.columns],
        }
    )
