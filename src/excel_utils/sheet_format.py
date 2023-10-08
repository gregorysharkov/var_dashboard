'''format of the excel sheet after all reports have been placed'''


def format_dashboard_worksheet(worksheet, layout) -> None:
    '''formats the dashboard worksheet after all reports have been placed'''
    for col in layout.NUMERIC_COLUMNS:
        worksheet.set_column(f'{col}:{col}', layout.NUMERIC_COLUMNS_WIDTH)

    for col in layout.CATEGORY_COLUMNS:
        worksheet.set_column(f'{col}:{col}', layout.CATEGORY_COLUMNS_WIDTH)

    for col in layout.SIDE_COLUMNS:
        worksheet.set_column(f'{col}:{col}', layout.SIDE_COLUMNS_WIDTH)

    for col in layout.MIDDLE_COLUMNS:
        worksheet.set_column(f'{col}:{col}', layout.MIDDLE_COLUMNS_WIDTH)

    worksheet.set_zoom(80)
    worksheet.hide_gridlines(2)
    worksheet.repeat_rows(0, 4)
    worksheet.print_area(0, 0, 250, len(layout.columns)+1)
    worksheet.fit_to_pages(1, 0)
