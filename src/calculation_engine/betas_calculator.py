import logging
from functools import cached_property

import numpy as np
import pandas as pd

from ..legacy.helper import imply_smb_gmv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BetasCalculator:
    """
    A class that calculates the beta factors for a
    set of positions based on a set of factor prices.

    Attributes:
    position_prices (pd.DataFrame): A DataFrame of position prices.
    factor_prices (pd.DataFrame): A DataFrame of factor prices.

    Methods:
    factor_returns() -> pd.DataFrame:
        Calculates the factor returns from the factor prices.
    position_returns() -> pd.DataFrame:
        Calculates the position returns from the position prices.
    calculate_beta_factors() -> pd.DataFrame:
        Calculates the beta factors for each position.
    """

    def __init__(
        self,
        position_prices: pd.DataFrame,
        factor_prices: pd.DataFrame
    ) -> None:
        """
        Initialize a new instance of the BetasCalculator class.

        Args:
        position_prices: A DataFrame of position prices.
        factor_prices: A DataFrame of factor prices.
        """
        self._position_prices = position_prices
        self._factor_prices = factor_prices

    @cached_property
    def _position_prices_df(self) -> pd.DataFrame:
        """
        Private method that returns a DataFrame of position
        prices with a single column of position IDs.

        Returns:
        A DataFrame of position prices with a single column of position IDs.
        """
        return pd.DataFrame(
            self._position_prices.columns.values,
            index=np.repeat(
                self._factor_prices.index[-1],
                len(self._position_prices.columns)
            ),
        )

    @cached_property
    def factor_returns(self) -> pd.DataFrame:
        """
        Public method that calculates the factor
        returns from the factor prices.

        Returns:
        A DataFrame of factor returns.
        """
        factor_returns = (
            self._factor_prices.iloc[1:,]
            / self._factor_prices.iloc[1:,].shift(1)
        ) - 1
        factor_returns.index = self._factor_prices.index[1:]
        factor_returns = imply_smb_gmv(factor_returns)
        return factor_returns

    @cached_property
    def position_returns(self) -> pd.DataFrame:
        """
        Public method that calculates the position
        returns from the position prices.

        Returns:
        A DataFrame of position returns.
        """
        return (
            self._position_prices.iloc[1:,]
            / self._position_prices.iloc[1:,].shift(1)
        ) - 1

    @cached_property
    def _factor_rf_ret_mat(self) -> pd.DataFrame:
        """
        Private method that calculates the factor risk-free return matrix.

        Returns:
        A DataFrame of the factor risk-free return matrix.
        """
        factor_rf_ret_mat = pd.DataFrame(
            np.tile(
                self.factor_returns.iloc[:, 0].values[:, None],
                len(self.factor_returns.iloc[:, 0:].columns) - 1,
            ),
            index=self.factor_returns.index,
            columns=self.factor_returns.iloc[:, 1:].columns,
        )
        return factor_rf_ret_mat

    @cached_property
    def _factor_returns_rf(self) -> pd.DataFrame:
        """
        Private method that calculates the factor
        returns adjusted for the risk-free rate.

        Returns:
        A DataFrame of the factor returns adjusted for the risk-free rate.
        """
        return self.factor_returns.iloc[:, 1:] \
            - self._factor_rf_ret_mat.iloc[:, :]

    @cached_property
    def _factor_rf_ret_mat_for_pos(self) -> pd.DataFrame:
        """
        Private method that calculates the factor risk-free
        return matrix for position returns.

        Returns:
        A DataFrame of the factor risk-free
        return matrix for position returns.
        """
        factor_rf_ret_mat_for_pos = pd.DataFrame(
            np.tile(
                self.factor_returns.iloc[:, 0].values[:, None], len(
                    self.position_returns.columns)
            ),
            index=self.factor_returns.index,
            columns=self.position_returns.columns,
        )
        return factor_rf_ret_mat_for_pos

    @cached_property
    def position_returns_rf(self) -> pd.DataFrame:
        """
        Public method that calculates the position returns
        adjusted for the risk-free rate.

        Returns:
        A DataFrame of the position returns adjusted for the risk-free rate.
        """
        return self.position_returns - self._factor_rf_ret_mat_for_pos

    def calculate_beta_factors(self) -> pd.DataFrame:
        """
        Public method that calculates the
        beta factors for each position.

        Returns:
        A DataFrame of the beta factors for each position.
        """
        def calculate_beta_factors_for_factor(
            factor_returns_rf: pd.DataFrame
        ) -> pd.Series:
            positions_factors_rets_rf = pd.concat(
                [self.position_returns_rf, factor_returns_rf], axis=1
            )
            beta_factors = positions_factors_rets_rf.cov() / np.nanvar(
                factor_returns_rf
            )  # type: ignore
            return beta_factors.iloc[0, 1]

        factor_returns_rf = self._factor_returns_rf.iloc[:, 1:]
        beta_factors_df_list_by_factor = factor_returns_rf.apply(
            calculate_beta_factors_for_factor, axis=0
        )
        beta_factors_df_list_by_factor.name = "Beta"
        beta_factors_df_list_by_factor.index = factor_returns_rf.columns

        beta_factors_df_by_factor = pd.concat(
            [beta_factors_df_list_by_factor.index,
                beta_factors_df_list_by_factor], axis=1
        )
        beta_factors_df_by_factor.rename(columns={0: "ID"}, inplace=True)

        beta_factors_df_list_across_factors = beta_factors_df_list_by_factor.T
        beta_factors_df_list_across_factors.index = np.repeat(
            self._factor_prices.index[-1], len(
                beta_factors_df_list_across_factors)
        )
        logger.info("Done calculating beta factors.")
        return beta_factors_df_list_across_factors
