import pandas as pd

from src.legacy.Factors import factor_betas


def test_factor_betas():
    # create sample data
    factor_prices = pd.DataFrame({
        'Factor 1': [10, 12, 15, 13],
        'Factor 2': [20, 18, 22, 25],
        'Factor 3': [30, 28, 26, 24]
    })
    position_prices = pd.DataFrame({
        'Position 1': [100, 110, 105, 95],
        'Position 2': [200, 190, 210, 205],
        'Position 3': [300, 310, 290, 295]
    })

    # expected output
    expected_output = pd.DataFrame({
        'ID': ['Position 1', 'Position 2', 'Position 3'],
        'Factor 1': [0.5, 0.5, 0.5],
        'Factor 2': [-1.0, -1.0, -1.0],
        'Factor 3': [0.0, 0.0, 0.0]
    }, index=[3, 3, 3])

    # test function output
    output = factor_betas(factor_prices, position_prices)
    pd.testing.assert_frame_equal(output, expected_output)
