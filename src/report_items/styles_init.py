'''intiates styles to the workbook'''

from typing import Any, Dict

from ..styles import table_styles as ts


def set_styles(workbook) -> Dict[str, Any]:
    '''sets all necessary styles and returns a styles' dictionary'''

    styles_dict = {
        'header': ts.add_header_style(workbook),
        'table_body': ts.add_table_body_format(workbook),
        'table_frame': ts.add_body_frame_format(workbook),
        'currency': ts.add_currency_format(workbook),
        'percentage': ts.add_percentage_format(workbook),
    }

    return styles_dict
