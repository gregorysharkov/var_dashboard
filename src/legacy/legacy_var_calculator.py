'''
Calculates VarExposure of a potfolio that
consists of multiple positions
'''

import warnings
from dataclasses import dataclass
from functools import cache, cached_property
from typing import Dict

import numpy as np
import pandas as pd

QUANTILES = {
    '95': 1.644854,
    '99': 2.326348,
}


@dataclass
class PortfolioVarCalculator:
    '''
    this class calculates the isolated and component VaR
    for given quantiles, positions and prices

    It has two public properties:
        isolated_varIsolated var is the var without taking into
            account the correlation between assets
        component_var: Component var is the var taking into account
            the correlation between assets

    Prices that do not have a corresponding position are ignored
    '''
    prices_table: pd.DataFrame
    positions_table: pd.DataFrame
    quantiles = QUANTILES

    @cached_property
    def isolated_var(self) -> Dict[str, float]:
        '''function calculates multiple vars for a given quantile'''
        return_dict = {}
        for quantile_name, quantile_value in self.quantiles.items():
            return_dict[f'{quantile_name}VaR_iso'] = self._isolated_var * \
                quantile_value

        return return_dict

    @cached_property
    def component_var(self) -> Dict[str, float]:
        '''function calculates multiple component vars for a given quantile'''
        return_dict = {}
        for quantile_name, quantile_value in self.quantiles.items():
            return_dict[f'{quantile_name}VaR_comp'] = self._component_var * \
                quantile_value

        return return_dict

    @cached_property
    def _prices(self) -> pd.DataFrame:
        '''returns prices corresponding to VaRTickers of the positions table'''
        var_tickers = self.positions_table.VaRTicker.unique()
        return self.prices_table[var_tickers]  # type: ignore

    @cached_property
    def _ticker_exposure(self) -> pd.DataFrame:
        '''returns total exposure by tickets'''
        return self.positions_table\
            .groupby('VaRTicker')\
            .agg({'Exposure': 'sum'})

    @cached_property
    def _daily_returns(self) -> pd.DataFrame:
        '''calculates daily returns of a position table'''
        return np.log(self._prices / self._prices.shift(1))  # type: ignore

    @cached_property
    def _return_covariance(self) -> pd.DataFrame:
        return self._daily_returns.cov()

    @cached_property
    def _portfolio_var(self) -> float:
        with warnings.catch_warnings():
            warnings.simplefilter('ignore')
            stdev = np.sqrt(
                self._ticker_exposure.T
                    .dot(self._return_covariance)
                    .dot(self._ticker_exposure)
            )  # type: ignore

        return stdev.iloc[0, 0]  # type: ignore

    @cached_property
    def _mvar(self) -> pd.DataFrame:
        return self._return_covariance.dot(self._ticker_exposure)

    @cached_property
    def _isolated_var(self) -> pd.DataFrame:
        return np.nan_to_num(
            self._mvar / self._portfolio_var * self._ticker_exposure
        )[0, 0]

    @cached_property
    def _component_var(self) -> float:
        return np.nan_to_num(
            (self._ticker_exposure * self._isolated_var).sum(),
            nan=0.0
        )[0]


@dataclass
class AlternativeVarCalculator:
    '''
    alternative calculation of portfolio var

    The logic is the following:
    1. calculate daily returns of each asset
    2. calculate standard deviation of daily returns per each asset
    3. Estimate portfolio standard deviation as a weighted sum of portfolio returns
        portfolio returns is a weighted sum of daily returns of each asset
    4. Calculate portfolio var
    5. Calculate each asset's isolated var
    6. calculate 
    '''
    prices_table: pd.DataFrame
    positions_table: pd.DataFrame
    quantiles = QUANTILES

    @cached_property
    def daily_returns(self) -> pd.DataFrame:
        '''returns table with assets in columns and dates in rows'''
        returns = (self.prices_table - self.prices_table.shift(1)) \
            / self.prices_table
        return returns.dropna()

    @cached_property
    def asset_stdev(self) -> pd.Series:
        '''returns standard deviation of daily returns per each asset'''
        return self.daily_returns.std().to_series()

    @cached_property
    def position_counts(self) -> pd.Series:
        '''returns counts of assets in portfolio'''
        return self.positions_table\
            .groupby('VaRTicker')\
            .agg({'Counts': 'sum'})\
            .Counts

    @cached_property
    def portfolio_stdev(self) -> float:
        '''returns standard deviation of portfolio returns'''
        return self.portfolio_returns.sum(axis=1).std()

    @cached_property
    def weights(self) -> pd.DataFrame:
        '''returns weights of assets in portfolio'''
        return self.positions_table\
            .groupby('VaRTicker')\
            .agg({'Exposure': 'sum'})\
            .apply(lambda x: 100 * x / float(x.sum()))\
            .rename(columns={'Exposure': 'weight'})

    @cached_property
    def portfolio_returns(self) -> pd.DataFrame:
        '''returns weighted returns of assets in portfolio'''
        return self.daily_returns\
            .multiply(self.position_counts, axis=1)

        # return self.daily_returns\
        #     .apply(lambda x: x * self.weights, axis=1)

    def portfolio_var(self, quantile: float) -> float:
        '''returns portfolio var for given quantile'''
        return self.portfolio_stdev * quantile

    def _calculate_isolated_var(self, quantile: float) -> pd.Series:
        '''returns isolated var for given quantile'''
        return self.asset_stdev * quantile

    def isolated_var(self) -> dict[str, pd.Series]:
        '''returns isolated var for given quantile'''

        return {
            key: self._calculate_isolated_var(quantile)
            for key, quantile in self.quantiles.items()
        }

    def component_var(self) -> Dict[str, pd.Series]:
        '''returns component var for given quantile'''
        return {
            key: self._calculate_isolated_var(quantile) * self.weights.weight
            for key, quantile in self.quantiles.items()
        }

    def incremental_var(self) -> Dict[str, pd.Series]:
        '''returns incremental var for given quantile'''
        return_dict = {
            key: pd.Series() for key in self.quantiles
        }
        for item in self.weights.index:
            isolated_prices = self.prices_table.drop(item, axis=1)
            isolated_positions = self.positions_table.loc[
                self.positions_table.VaRTicker != item,
                :,
            ]
            isolated_var_calculator = AlternativeVarCalculator(
                prices_table=isolated_prices,
                positions_table=isolated_positions,
            )

            for key, quantile in self.quantiles.items():
                isolated_portfolio_var = isolated_var_calculator\
                    .portfolio_var(quantile)
                incremental_var = self.portfolio_var(
                    quantile) - isolated_portfolio_var
                return_dict[key][item] = incremental_var

        return return_dict
