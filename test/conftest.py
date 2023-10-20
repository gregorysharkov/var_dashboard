# pylint: disable=missing-docstring,W0621,C0103,B101
import pandas as pd
import pytest

from src.calculation_engine import PortfolioVarCalculator


@pytest.fixture
def prices_table():
    return pd.DataFrame({
        "Asset 1": [100, 106, 116, 123, 125, 133, 133, 124, 126, 121],
        "Asset 2": [200, 200, 200, 201, 199, 199, 196, 195, 195, 196],
        "Asset 3": [300, 310, 304, 311, 318, 315, 307, 315, 308, 311],
    })


@pytest.fixture
def positions_table():
    return pd.DataFrame({
        'VaRTicker': ['Asset 1', 'Asset 2', 'Asset 3', 'Asset 1'],
        'Exposure': [100, 200, 300, 100]
    })


@pytest.fixture
def var_calculator(prices_table, positions_table):
    return PortfolioVarCalculator(
        prices_table=prices_table,
        positions_table=positions_table
    )
