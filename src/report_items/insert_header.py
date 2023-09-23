from datetime import datetime


def insert_header(worksheet, styles, layout) -> None:
    '''inserts header to the worksheet'''

    active_columns = len(layout.CATEGORY_COLUMNS) + \
        len(layout.NUMERIC_COLUMNS) + len(layout.MIDDLE_COLUMNS)
    worksheet.merge_range(0, 1, 0, active_columns, 'Risk Report',
                          styles.get("report_header_title"))
    worksheet.merge_range(1, 1, 1, active_columns, 'Firm level',
                          styles.get('report_header_sub_title'))
    worksheet.merge_range(
        2, 1, 2, active_columns,
        datetime.now().strftime(r'%d/%m/%Y'),
        styles.get('report_header_date')
    )

    pass
