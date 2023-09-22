from typing import Any

ALIGN_CENTER = 'center'
DARK_BLUE_COLOR = '#44546A'
WHIE_COLOR = '#FFFFFF'
TEXT_FONT = 'Arial'
TEXT_SIZE = 8

SOLID_BORDER_INDEX = 1
DASHED_BORDER_INDEX = 4

CURRENCY_FORMAT = '"$"# ##0_);[Red]("$"# ##0)'
PERCENTAGE_FORMAT = '# ##0.00%_);[Red](# ##0.00%)'


def add_header_style(workbook) -> Any:
    '''adds table style for a header for a given workbook'''

    style = workbook.add_format()
    style.set_align(ALIGN_CENTER)
    style.set_bg_color(DARK_BLUE_COLOR)
    style.set_bold(True)
    style.set_font_name(TEXT_FONT)
    style.set_font_color(WHIE_COLOR)
    style.set_size(TEXT_SIZE)

    style.set_border(SOLID_BORDER_INDEX)
    style.set_border_color(DARK_BLUE_COLOR)
    return style


def add_table_body_format(workbook) -> Any:
    '''adds table body format'''

    style = workbook.add_format()
    style.set_border(DASHED_BORDER_INDEX)
    style.set_border_color(DARK_BLUE_COLOR)
    return style


def add_body_frame_format(workbook) -> Any:
    '''adds solid frame to outer'''

    style = workbook.add_format()
    style.set_top(SOLID_BORDER_INDEX)
    style.set_top_color(DARK_BLUE_COLOR)
    style.set_bottom(SOLID_BORDER_INDEX)
    style.set_bottom_color(DARK_BLUE_COLOR)
    style.set_left(SOLID_BORDER_INDEX)
    style.set_left_color(DARK_BLUE_COLOR)
    style.set_right(SOLID_BORDER_INDEX)
    style.set_right_color(DARK_BLUE_COLOR)


def _add_num_format(workbook, format) -> Any:
    '''adds number format'''

    style = workbook.add_format()
    style.set_num_format(format)
    return style


def add_currency_format(workbook) -> Any:
    '''adds currency format'''

    return _add_num_format(workbook, CURRENCY_FORMAT)


def add_percentage_format(workbook) -> Any:
    '''adds currency format'''

    return _add_num_format(workbook, PERCENTAGE_FORMAT)
