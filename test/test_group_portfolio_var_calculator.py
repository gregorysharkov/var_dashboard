# pylint: disable=missing-docstring,W0621,C0103,B101
import numpy as np
from scipy.stats import norm

from src.calculation_engine import GroupVarCalculator

GROUP_COLUMN = 'Fund'
QUANTILE = norm.ppf(0.95)
TOL = 1e-2


def test_group_isolated_var(prices_table, grouped_positions_table):
    # create sample data
    calculator = GroupVarCalculator(
        group_column=GROUP_COLUMN,
        prices_table=prices_table,
        positions_table=grouped_positions_table,
    )

    # test isolated var
    isolated_var = calculator.isolated_var(QUANTILE)
    assert np.isclose(isolated_var['Fund 1'], 0.062406, rtol=TOL)
    assert np.isclose(isolated_var['Fund 2'], 0.063334, rtol=TOL)


def test_group_component_var(prices_table, grouped_positions_table):
    # create sample data
    calculator = GroupVarCalculator(
        group_column=GROUP_COLUMN,
        prices_table=prices_table,
        positions_table=grouped_positions_table,
    )

    # test component var
    component_var = calculator.component_var(QUANTILE)
    assert np.isclose(component_var['Fund 1'], 0.060499, rtol=TOL)
    assert np.isclose(component_var['Fund 2'], 0.060499, rtol=TOL)


def test_group_incremental_var(prices_table, grouped_positions_table):
    # create sample data
    calculator = GroupVarCalculator(
        group_column=GROUP_COLUMN,
        prices_table=prices_table,
        positions_table=grouped_positions_table,
    )

    # test isolated group calculators
    incremental_var = calculator.incremental_var(QUANTILE)
    assert np.isclose(incremental_var['Fund 1'], -0.0063395, rtol=TOL)
    assert np.isclose(incremental_var['Fund 2'], -0.004973, rtol=TOL)
