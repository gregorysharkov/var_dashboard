from src.report_items.styles_init import set_styles


def set_up_workbook(workbook, sheet_name: str):

    styles = set_styles(workbook)
    if sheet_name not in workbook.sheetnames:
        workbook.add_worksheet(sheet_name)

    worksheet = workbook.get_worksheet_by_name(sheet_name)
    return styles, worksheet
