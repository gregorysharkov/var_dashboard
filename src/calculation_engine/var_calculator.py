# pylint: disable=too-many-function-args
'''
functions that calculate different vars
calculate total portfolio var of all positions
calculate vars
    per position
    per country
    per industry
    per marketcap
    per fund
    per strat (fund)
'''

import logging
from typing import Any, Dict

import pandas as pd
from scipy.stats import norm
from tqdm import tqdm

from src.calculation_engine import GroupVarCalculator, PortfolioVarCalculator
from src.calculation_engine.constants import GROUP_LEVELS

# from tqdm import tqdm

logger = logging.getLogger(__name__)


QUANTILES = {
    '95': norm.ppf(.95),
    '99': norm.ppf(.99),
}

OUTPUT_COLUMNS = ['strat', 'var_type',
                  'var_subtype', 'attribute_value', 'var_value']


def calculate_vars(
    prices: pd.DataFrame,
    positions: pd.DataFrame
) -> pd.DataFrame:
    '''
    This function calculates the isolated and component VaR
    for given quantiles, positions and prices
    it returns a dataframe that has columns for each quantile
    per var type (isolated and component)
    '''
    return_data = pd.DataFrame(
        columns=['group', 'var_type', 'var_confidence', 'attribute', 'var'])

    var_calculators = _set_up_var_calculators(prices, positions)

    for group, calculator in tqdm(var_calculators.items(), 'Estimating VAR'):
        for quantile_name, quantile in QUANTILES.items():
            # add group totals
            return_data = _add_row(
                data=return_data,
                group=group,
                var_type='portfolio',
                confidence=quantile_name,
                attribute='total',
                var=calculator.portfolio_var(quantile)
            )
            logger.info(f'finished estimating portfolio var for {group}')
            # add isloated vars
            return_data = _add_sub_table(
                data=return_data,
                new_vars=calculator.isolated_var(quantile),
                group=group,
                var_type='isolated',
                confidence=quantile_name
            )
            logger.info(f'finished estimating isolated var for {group}')
            # add component_vars
            return_data = _add_sub_table(
                data=return_data,
                new_vars=calculator.component_var(quantile),
                group=group,
                var_type='component',
                confidence=quantile_name
            )
            # add incremental_vars
            return_data = _add_sub_table(
                data=return_data,
                new_vars=calculator.incremental_var(quantile),
                group=group,
                var_type='incremental',
                confidence=quantile_name
            )
            logger.info(
                f'finished estimating incremental var for group {group}')
    return return_data


def _add_row(
    data: pd.DataFrame,
    group: str,
    var_type: str,
    confidence: str,
    attribute: str,
    var: float
) -> pd.DataFrame:
    '''add a new row to the var dataframe'''

    new_row = {
        'group': [group],
        'var_type': [var_type],
        'var_confidence': [confidence],
        'attribute': [attribute],
        'var': [var],
    }

    return_data = pd.concat([
        data,
        pd.DataFrame(new_row)
    ], ignore_index=True)
    # data[len(data)] = new_row

    return return_data


def _add_sub_table(
    data: pd.DataFrame,
    new_vars: pd.Series,
    group: str,
    var_type: str,
    confidence: str
) -> pd.DataFrame:
    '''
    adds new set of lines, each corresponding to an attribute value with the
    corresponding var value    
    '''
    return_data = new_vars\
        .to_frame(name='var')\
        .reset_index()\
        .rename(
            columns={new_vars.index.name: 'attribute'}
        )

    return_data['group'] = group
    return_data['var_type'] = var_type
    return_data['var_confidence'] = confidence

    return_data = pd.concat([
        data,
        return_data[['group', 'var_type',
                     'var_confidence', 'attribute', 'var']]
    ])
    return return_data


def _set_up_var_calculators(prices, positions) -> Dict[str, Any]:
    '''set up classes for portfolio var calculations'''

    var_calculators = {
        'total': PortfolioVarCalculator(
            prices_table=prices,
            positions_table=positions,
        ),
    }

    var_calculators.update({
        key: GroupVarCalculator(value, prices, positions)
        for key, value in GROUP_LEVELS.items()
    })  # type: ignore

    return var_calculators
