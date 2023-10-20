# pylint: disable=missing-docstring,W0621,C0103,B101
import numpy as np
from scipy.stats import norm

QUANTILE = norm.ppf(0.95)
TOL = 1e-2


def test_portfolio_var(var_calculator):
    assert np.isclose(var_calculator.portfolio_var(
        QUANTILE), 0.028031, rtol=TOL)


def test_isolated_var(var_calculator):
    isolated_var = var_calculator.isolated_var(QUANTILE)

    assert np.isclose(isolated_var['Asset 1'], 0.086595, rtol=TOL)
    assert np.isclose(isolated_var['Asset 2'], 0.010989, rtol=TOL)
    assert np.isclose(isolated_var['Asset 3'], 0.038293, rtol=TOL)


def test_component_var(var_calculator):
    component_var = var_calculator.component_var(QUANTILE)
    assert np.isclose(component_var['Asset 1'], 0.008009, rtol=TOL)
    assert np.isclose(component_var['Asset 2'], 0.008009, rtol=TOL)
    assert np.isclose(component_var['Asset 3'], 0.012013, rtol=TOL)


def test_incremental_var(var_calculator):
    incremental_var = var_calculator.incremental_var(QUANTILE)
    assert np.isclose(incremental_var['Asset 1'], 0.003704, rtol=TOL)
    assert np.isclose(incremental_var['Asset 2'], -0.009347, rtol=TOL)
    assert np.isclose(incremental_var['Asset 3'], -0.017006, rtol=TOL)
