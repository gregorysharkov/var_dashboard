'''module contains portfolio var calculator'''

from dataclasses import dataclass
from functools import cached_property
from typing import Any

import numpy as np
import pandas as pd

QUANTILES = {
    '95': 1.644854,
    '99': 2.326348,
}


@dataclass
class PortfolioVarCalculator:
    '''
    class is responsible for calculation of different types
    of vars of elements that constiture the portfolio
    It has the following public methods:
        portfolio_var: returns portfolio var for given quantile
        isolated_var: returns isolated var for given quantile
        component_var: returns component var for given quantile
        incremental_var: returns all incremental vars for each asset

    Class attributes:
        prices_table: a dataframe that contains prices of all positions
        positions_table: a dataframe containing all
            positions of a given portfolio
    '''
    prices_table: pd.DataFrame
    positions_table: pd.DataFrame

    def __post_init__(self):
        # make sure that prices table consits only of factors
        # that are relevant for the given positions table
        var_tickers = self.positions_table['VaRTicker'].unique()
        self.prices_table = self.prices_table.loc[:, var_tickers]

    def portfolio_var(self, quantile: float) -> float:
        '''returns portfolio var for given quantile'''
        return self._portfolio_std * quantile

    def isolated_var(self, quantile: float) -> pd.Series:
        '''returns isolated var for given quantile'''
        return self._position_std * quantile

    def component_var(self, quantile: float) -> pd.Series:
        '''returns component var for given quantile'''
        return self._position_weights * self.portfolio_var(quantile)

    def incremental_var(self, quantile: float) -> pd.Series:
        '''returns all incremental vars for each asset'''

        return pd.Series(
            {
                ticker: self._ticker_incremental_var(ticker, quantile)
                for ticker in self._var_tickers
            }
        )

    @cached_property
    def _positions(self) -> pd.DataFrame:
        '''aggregated position exposure for each varTicker'''
        return self.positions_table\
            .groupby('VaRTicker')\
            .agg({'Exposure': 'sum'})

    @cached_property
    def _position_weights(self) -> pd.Series:
        '''returns position weights in the portfolio'''
        return self._positions.Exposure / self._positions.Exposure.sum()

    @cached_property
    def _position_returns(self) -> pd.DataFrame:
        '''returns daily returns of the portfolio'''
        return (
            (self.prices_table.shift(1) - self.prices_table)
            / self.prices_table.shift(1)
        )\
            .dropna()

    @cached_property
    def _return_covariance(self) -> pd.DataFrame:
        '''returns covariance matrix of the portfolio'''
        return self._position_returns.cov()

    @cached_property
    def _portfolio_std(self) -> float:
        '''returns standard deviation of the portfolio'''
        return np.sqrt(
            self._position_weights.T
            @ self._return_covariance
            @ self._position_weights
        )  # type: ignore

    @property
    def _var_tickers(self) -> pd.Series:
        '''returns var tickers'''
        return self._positions.index.to_series()

    @cached_property
    def _position_std(self) -> pd.Series:
        '''returns standard deviation of the portfolio positions'''
        return self._position_returns.std()

    @cached_property
    def _isolated_calculators(self) -> dict[str, Any]:
        '''returns isolated var calculators for each ticker'''

        return_dict = {}
        for ticker in self._var_tickers:
            incremental_positions = self.positions_table.loc[
                self.positions_table.VaRTicker != ticker, :
            ]
            return_dict[ticker] = PortfolioVarCalculator(
                prices_table=self.prices_table,
                positions_table=incremental_positions,
            )

        return return_dict

    def _ticker_incremental_var(
        self,
        ticker: str,
        quantile: float
    ) -> pd.Series:
        '''returns incremental var for a given ticker for given quantile'''

        return self.portfolio_var(quantile) \
            - self._isolated_calculators[ticker].portfolio_var(quantile)
