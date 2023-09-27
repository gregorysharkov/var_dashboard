import logging

import numpy as np
import pandas as pd
from tqdm import tqdm

from helper import imply_SMB_GMV

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


# HistSeries function
hist_series = """
HistSeries <- function ( riskfactors, rfid, exposure, data.in.columns=TRUE){ 
  count <- nrow(riskfactors);
  ln <- log(riskfactors[2:count,]/riskfactors[1:count-1,]);
  count <- nrow(ln);
  Hist_Rtn_Mtx <- ln[,c(rfid)];
  Hist_Rtn <- Hist_Rtn_Mtx %*% exposure;
  x <- Hist_Rtn;
  return( x );
}
"""


def FactorBetas(factor_prices: pd.DataFrame, position_prices: pd.DataFrame):
    # Inputs:
    # Factor prices
    # Position-level prices

    # Outputs:
    # Position level beta to each factor
    position_prices_df = pd.DataFrame(
        position_prices.columns.values,
        index=np.repeat(factor_prices.index[-1], len(position_prices.columns)),
    )
    factor_returns = (
        factor_prices.iloc[1:,] / factor_prices.iloc[1:,].shift(1)) - 1
    factor_returns.index = factor_prices.index[1:]
    factor_returns = imply_SMB_GMV(factor_returns)
    position_returns = (
        position_prices.iloc[1:,] / position_prices.iloc[1:,].shift(1)
    ) - 1
    # contains returns of the STerm Treas in every column
    # used when estimating risk factor returns in excess of cash equivalents
    factor_rf_ret_mat = pd.DataFrame(
        np.tile(
            factor_returns.iloc[:, 0].values[:, None],
            len(factor_returns.iloc[:, 0:].columns) - 1,
        ),
        index=factor_returns.index,
        columns=factor_returns.iloc[:, 1:].columns,
    )
    factor_returns_rf = factor_returns.iloc[:,
                                            1:] - factor_rf_ret_mat.iloc[:, :]
    factor_rf_ret_mat_for_pos = pd.DataFrame(
        np.tile(
            factor_returns.iloc[:, 0].values[:, None], len(
                position_returns.columns)
        ),
        index=factor_returns.index,
        columns=position_returns.columns,
    )
    position_returns_rf = position_returns - factor_rf_ret_mat_for_pos
    beta_factors_df_list_across_factors = []
    for i in tqdm(range(0, len(factor_returns_rf.columns)), 'Betas'):
        beta_factors_df_list_by_factor = []
        for n in range(0, len(position_returns_rf.columns)):
            positions_factors_rets_rf = pd.concat(
                [position_returns_rf.iloc[:, n],
                    factor_returns_rf.iloc[:, i]], axis=1
            )
            beta_factors = positions_factors_rets_rf.cov() / np.nanvar(
                factor_returns_rf.iloc[:, i]
            )
            beta_factors_df_list_by_factor.append(beta_factors.iloc[0, 1])
        beta_factors_df_by_factor = pd.DataFrame(beta_factors_df_list_by_factor,
                                                 columns=[
                                                     factor_returns_rf.columns[i]],
                                                 index=np.repeat(factor_prices.index[-1], len(position_prices.columns)))
        beta_factors_df_by_factor = pd.concat(
            [position_prices_df, beta_factors_df_by_factor], axis=1)
        beta_factors_df_by_factor.rename(columns={0: "ID"}, inplace=True)
        beta_factors_df_list_across_factors.append(beta_factors_df_by_factor)
    beta_factors_df_list_across_factors = pd.concat(
        beta_factors_df_list_across_factors, axis=1)
    beta_factors_df_list_across_factors = beta_factors_df_list_across_factors.loc[
        :, ~beta_factors_df_list_across_factors.columns.duplicated()]

    return beta_factors_df_list_across_factors


def position_returns(position_prices: pd.DataFrame):
    position_returns = (
        position_prices.iloc[1:,] / position_prices.iloc[1:,].shift(1)
    ) - 1

    return position_returns
