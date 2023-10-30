'''ectention of PortfolioVarCalculator allowing to group positions'''

from dataclasses import dataclass
from functools import cache, cached_property
from typing import Any

import pandas as pd

from src.calculation_engine.portfolio_var_calculator import \
    PortfolioVarCalculator


@dataclass
class GroupVarCalculator:
    '''
    class is wraps PortfolioVarCalculator allowing to
    group positions and calculate group vars
    first, we calculate portfolio var based on individual assets
    '''
    group_column: str
    prices_table: pd.DataFrame
    positions_table: pd.DataFrame

    def __post_init__(self):
        # make sure that prices table consits only of factors
        # that are relevant for the given positions table
        var_tickers = self.positions_table['VaRTicker'].unique()
        self.prices_table = self.prices_table.loc[:, var_tickers]
        # we will also need a standard PortfolioVarCalculator to estimate
        # overall portfolio var from given positions
        self.portfolio_var_calculator = PortfolioVarCalculator(
            prices_table=self.prices_table,
            positions_table=self.positions_table,
        )

    @cached_property
    def _group_positions(self) -> pd.DataFrame:
        '''
        aggregated position exposure for each varTicker
        Output should be something like this
        Fund    VaRTicker   Exposure
        Fund 1  Asset 1     -300
                Asset 2      500
        Fund 2  Asset 1      400
                Asset 3     -200
        Name: Weight, dtype: float64
        '''
        return self.positions_table\
            .groupby([self.group_column, 'VaRTicker'])\
            .agg({'Exposure': 'sum'})

    @cached_property
    def _group_weights(self) -> pd.Series:
        '''
        returns position weights in the portfolio
        Output should be something like this
        Fund    VaRTicker   Weight
        Fund 1  Asset 1     -0.75
                Asset 2      1.25
        Fund 2  Asset 1     -0.50
                Asset 3      1.00
        Name: Weight, dtype: float64
        '''
        return self._group_positions.Exposure \
            / self._group_positions.Exposure.sum()

    @cached_property
    def _iso_fund_stds(self) -> pd.Series:
        '''
        returns isolated fund stds
        Output should be something like this
        Fund      IsolatedVar
        Fund 1    0.037940
        Fund 2    0.038505
        '''
        groups = self._group_weights.index.levels[0]  # type: ignore
        group_stds = pd.Series()
        for group in groups:
            group_exposure = self._group_weights.loc[group]
            group_positions = list(group_exposure.index)
            group_return_covariance = self.portfolio_var_calculator\
                .return_covariance\
                .loc[group_positions, group_positions]

            fund_std = (
                group_exposure.T
                @ group_return_covariance
                @ group_exposure
            ) ** .5
            group_stds[group] = fund_std

        group_stds.index.name = self.group_column
        return group_stds

    def portfolio_var(self, quantile: float) -> float:
        '''returns the overal portfolio variable'''
        return self.portfolio_var_calculator.portfolio_var(quantile)

    def isolated_var(self, quantile) -> pd.Series:
        '''
        returns isolated var for given quantile
        Output should be something like this
        Fund      IsolatedVar
        Fund 1    0.062222
        Fund 2    0.063148
        '''
        return self._iso_fund_stds.apply(lambda x: x * quantile)

    def component_var(self, quantile) -> pd.Series:
        '''
        returns component var for given quantile
        Output should be something like this
        Fund      ComponentVar
        Fund 1    0.060499
        Fund 2    0.060499
        because combined weight of each fund is .5
        '''
        fund_weights = self._group_weights.groupby(level=0).sum()
        return self.portfolio_var(quantile) \
            * fund_weights

    def incremental_var(self, quantile) -> pd.Series:
        '''
        returns incremental var for given quantile
        Output should be something like this
        Fund      IncrementalVar
        Fund 1    0.001723
        Fund 2    0.001723
        '''
        incremental_var = pd.Series()
        groups = self._group_weights.index.levels[0]  # type: ignore
        for group in groups:
            incremental_var[group] = self._group_incremental_var(
                group=group,
                quantile=quantile,
            )
        incremental_var.index.name = self.group_column
        return incremental_var

    @cached_property
    def _isolated_group_calculators(self) -> dict[str, Any]:
        '''returns isolated var calculators for each ticker'''

        return_dict = {}

        groups = self._group_weights.index.levels[0]  # type: ignore
        for group in groups:
            group_positions = self._group_positions.loc[group].index.values
            # remove group positions from the positions table
            match_condition = (
                (self.positions_table[self.group_column] == group)
                & (self.positions_table['VaRTicker'].isin(group_positions))
            )
            incremental_positions = self.positions_table.loc[
                ~match_condition, :
            ]
            # calculator of the portfolio var for the remaining positions
            return_dict[group] = PortfolioVarCalculator(
                prices_table=self.prices_table,
                positions_table=incremental_positions,
            )

        return return_dict

    def _group_incremental_var(self, group, quantile) -> pd.Series:
        '''returns incremental var for given quantile'''
        return self.portfolio_var(quantile) \
            - self._isolated_group_calculators[group].portfolio_var(quantile)
