def format_dashboard_worksheet(worksheet, layout) -> None:
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
