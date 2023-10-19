# pylint: disable=missing-docstring
import pandas as pd

from ..calculation_engine.betas_calculator import BetasCalculator
from ..legacy.helper import imply_smb_gmv


def test_imply_smb_gmv():
    factor_returns = pd.DataFrame(
        {
            "RIY Index": [1, 2, 3, 4, 5],
            "RTY Index": [2, 3, 4, 5, 6],
            "RAG Index": [3, 4, 5, 6, 7],
            "RAV Index": [4, 5, 6, 7, 8],
        },
        index=range(5),
    )

    factor_returns["LD12TRUU Index"] = [None] * 5
    factor_returns["SPX Index"] = [None] * 5

    expected_factor_returns = pd.DataFrame(
        {
            "LD12TRUU Index": [None] * 5,
            "SPX Index": [None] * 5,
            "RIY less RTY": [-1, -1, -1, -1, -1],
            "RAG less RAV": [-1, -1, -1, -1, -1],
        },
        index=range(5),
    )

    factor_returns = imply_smb_gmv(factor_returns)

    pd.testing.assert_frame_equal(factor_returns, expected_factor_returns)


def test_calculate_beta_factors():
    position_prices_df = pd.DataFrame(
        {
            "Position 1": [100, 105, 110, 115, 120],
            "Position 2": [200, 205, 210, 215, 220],
            "Position 3": [300, 305, 310, 315, 320],
        },
        index=range(5),
    )
    factor_prices = pd.DataFrame(
        {
            "Factor 1": [100, 105, 110, 115, 120],
            "Factor 2": [200, 205, 210, 215, 220],
            "Factor 3": [300, 305, 310, 315, 320],
        },
        index=range(5),
    )
    factor_prices["RTY Index"] = [None] * len(factor_prices)
    factor_prices["RIY Index"] = [None] * len(factor_prices)
    factor_prices["RAG Index"] = [None] * len(factor_prices)
    factor_prices["RAV Index"] = [None] * len(factor_prices)
    factor_prices["LD12TRUU Index"] = [None] * len(factor_prices)
    factor_prices["SPX Index"] = [None] * len(factor_prices)
    betas_calculator = BetasCalculator(position_prices_df, factor_prices)

    expected_beta_factors = pd.DataFrame(
        {
            "ID": ["Position 1", "Position 2", "Position 3"],
            "Factor 1": [1.0, 1.0, 1.0],
            "Factor 2": [1.0, 1.0, 1.0],
            "Factor 3": [1.0, 1.0, 1.0],
        }
    )

    beta_factors = betas_calculator.calculate_beta_factors()
    pd.testing.assert_frame_equal(beta_factors, expected_beta_factors)
