from typing import Dict


class DashboardLayout:
    '''class stores information about page layout'''
    NUMERIC_COLUMNS_WIDTH = 12
    CATEGORY_COLUMNS_WIDTH = 26
    SIDE_COLUMNS_WIDTH = 8
    MIDDLE_COLUMNS_WIDTH = 8
    PIXELS_PER_WIDTH = 80/12
    PIXELS_PER_HEIGHT = 20
    TOTAL_COLS = 15

    CATEGORY_COLUMNS = ['B', 'J', ]
    NUMERIC_COLUMNS = ['C', 'D', 'E', 'F',
                       'G', 'H', 'K', 'L', 'M', 'N', 'O', 'P']
    MIDDLE_COLUMNS = ['I', ]
    SIDE_COLUMNS = ['A', 'Q', ]

    @property
    def widths(self) -> Dict[str, int]:
        '''returns a sorted dictionary of column length'''

        return_dict = {}
        return_dict.update({
            col: self.CATEGORY_COLUMNS_WIDTH for col in self.CATEGORY_COLUMNS
        })

        return_dict.update({
            col: self.SIDE_COLUMNS_WIDTH for col in self.SIDE_COLUMNS
        })

        return_dict.update({
            col: self.MIDDLE_COLUMNS_WIDTH for col in self.MIDDLE_COLUMNS
        })

        return_dict.update({
            col: self.NUMERIC_COLUMNS_WIDTH for col in self.NUMERIC_COLUMNS
        })

        # type: ignore
        return {key: return_dict.get(key) for key in sorted(return_dict.keys())}

    def pixels_to_right_edge(self, start_col: int) -> float:
        '''
        returns number of pixels till the right
        border starting from the n'th column
        '''

        return sum(list(self.widths.values())[start_col:]) * self.PIXELS_PER_WIDTH

    def pixels_to_bottom(self, n_row: int) -> float:
        '''returns number of pixels for a given number of rows'''

        return n_row * self.PIXELS_PER_HEIGHT
