# pylint: disable=uncallable-module
'''helper functions used during calculations'''

import logging
from typing import List

import numpy as np
import pandas as pd
from scipy.stats import norm

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)
PART_A_COLS = ["LD12TRUU Index", "SPX Index", "RIY less RTY", "RAG less RAV"]
INDEX_COLS = ["RIY Index", "RTY Index", "RAG Index", "RAV Index"]
FACTOR_OPERATIONS = {
    'RIY less RTY': ["RIY Index", "RTY Index"],
    'RAG less RAV': ["RAG Index", "RAV Index"],
}
CALL_VALUES = ['Call', 'C', 'c']
PUT_VALUES = ['Put', 'P', 'p']


def imply_smb_gmv(factor_returns: pd.DataFrame) -> pd.DataFrame:
    '''
    imply Small - Big, Growth - Value
    adds columns like RIY less RTY
    selects columns in the right order
    '''

    # add factor operation columns
    for target_col, source_cols in FACTOR_OPERATIONS.items():
        col_a, col_b = source_cols
        factor_returns[target_col] = factor_returns[col_a] - \
            factor_returns[col_b]

    stop_cols = INDEX_COLS + PART_A_COLS
    part_b_cols = [
        col for col in factor_returns.columns
        if col not in stop_cols
    ]

    return factor_returns[PART_A_COLS + part_b_cols]


def option_price(
    S: pd.Series,
    X: pd.Series,
    T: pd.Series,
    Vol: pd.Series,
    rf: float,
    type: pd.Series
) -> List[float]:
    '''some black magic happenning here'''
    # TODO: Make it readable

    price_list = []
    for idx in range(0, len(S)):
        d1 = (
            np.log(S.iloc[idx] / X.iloc[idx]) +  # type: ignore
            (rf + Vol.iloc[idx] ** 2 / 2) * T.iloc[idx]
        ) / (Vol.iloc[idx] * np.sqrt(T.iloc[idx]))
        d2 = d1 - Vol.iloc[idx] * np.sqrt(T.iloc[idx])
        if type.iloc[idx] in CALL_VALUES:
            price = S.iloc[idx] * norm.cdf(d1, 0, 1) - X.iloc[idx] * np.exp(
                -rf * T.iloc[idx]
            ) * norm.cdf(d2, 0, 1)
        elif type.iloc[idx] in PUT_VALUES:
            price = X.iloc[idx] * np.exp(-rf * T.iloc[idx]) * norm.cdf(
                -d2, 0, 1
            ) - S.iloc[idx] * norm.cdf(-d1, 0, 1)

        price_list.append(price)

    return price_list


def calculate_returns(data: pd.DataFrame):
    ''' calculates returns of a wide column
        containing only price values per factor
    '''

    return_data = data / data.shift(1) - 1
    return_data = return_data.iloc[1:, ]
    return return_data
