from typing import Any

TITLE_FONT_SIZE = 24
SUB_TITLE_FONT_SIZE = 16
DATE_FONT_SIZE = 16

ALIGNEMENT = 'right'


def add_header_title(workbook) -> Any:
    '''adds header of the report'''

    style = workbook.add_format()
    style.set_font_size(TITLE_FONT_SIZE)
    style.set_align(ALIGNEMENT)
    style.set_bold(True)

    return style


def add_header_sub_title(workbook) -> Any:
    '''adds header of the report'''

    style = workbook.add_format()
    style.set_font_size(SUB_TITLE_FONT_SIZE)
    style.set_align(ALIGNEMENT)

    return style


def add_header_date(workbook) -> Any:
    '''adds header of the report'''

    style = workbook.add_format()
    style.set_font_size(DATE_FONT_SIZE)
    style.set_align(ALIGNEMENT)
    style.set_bottom(5)

    return style
