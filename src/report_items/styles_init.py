'''intiates styles to the workbook'''

from typing import Any, Dict

from ..styles import header_styles as hs
from ..styles import table_styles as ts


def set_styles(workbook) -> Dict[str, Any]:
    '''sets all necessary styles and returns a styles' dictionary'''

    styles_dict = {
        'table_header': ts.add_header_style(workbook),
        'table_body': ts.add_table_body_format(workbook),
        'table_frame': ts.add_body_frame_format(workbook),
        'currency': ts.add_currency_format(workbook),
        'percentage': ts.add_percentage_format(workbook),
        'date': ts.add_date_format(workbook),
        'report_header_title': hs.add_header_title(workbook),
        'report_header_sub_title': hs.add_header_sub_title(workbook),
        'report_header_date': hs.add_header_date(workbook),
    }

    return styles_dict
