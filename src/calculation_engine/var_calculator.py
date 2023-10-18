'''functions that calculate different vars'''

import pandas as pd

from src.calculation_engine.portfolio_var_calculator import PortfolioVarCalculator


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
    calculator = PortfolioVarCalculator(
        prices_table=prices,
        positions_table=positions,
    )

    return pd.DataFrame({
        **calculator.isolated_var,
        **calculator.component_var,
    }, index=[0])
