import logging
from typing import Dict

import numpy as np
import pandas as pd

from legacy.helper import option_price

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

RISK_FREE_RATE = 5.5e-2  # as of Aug 2023


def filter_exposure_calc(
    filter: Dict,
    position: pd.DataFrame,
    firm_NAV: float,
) -> pd.DataFrame:
    # agg positions by exposure across fund strats
    position_agg_exposure = (
        position.groupby(
            [
                "RFID",
            ]
        )
        .agg(
            {
                "TradeDate": "first",
                "FundName": "first",
                "UnderlierName": "first",
                "VaRTicker": "first",
                "MarketValue": "sum",
                "Exposure": "sum",
            }
        )
        .reset_index()
    )
    filter_list = list(filter.keys())
    exposure_calc_dict = {}
    for filter_item in filter_list:
        position_grouped = position.groupby([filter_item])
        for name, group in position_grouped:
            if isinstance(name, tuple):
                name = name[0]
            long_exposure = group.loc[group["Exposure"] > 0]
            short_exposure = group.loc[group["Exposure"] < 0]
            long_exposure_calc = long_exposure["Exposure"].sum()
            short_exposure_calc = short_exposure["Exposure"].sum()
            gross_exposure_calc = long_exposure_calc + abs(short_exposure_calc)
            net_exposure_calc = long_exposure_calc + short_exposure_calc
            exposure_calc_dict[f"{filter_item}_{name}_exposure"] = [
                long_exposure_calc / firm_NAV.values[0],
                short_exposure_calc / firm_NAV.values[0],
                gross_exposure_calc / firm_NAV.values[0],
                net_exposure_calc / firm_NAV.values[0],
            ]
    exposure_calc_df = pd.DataFrame(
        exposure_calc_dict,
        index=[
            "Long",
            "Short",
            "Gross",
            "Net",
        ],
    ).T
    exposure_calc_df = pd.concat([exposure_calc_df], axis=1)
    # strat
    strat_df = exposure_calc_df.loc[exposure_calc_df.index.str.contains(
        "Fund")]
    strat_df.reset_index(inplace=True)
    strat_df.rename(columns={"index": "Strategy Exposure"}, inplace=True)
    strat_df["Strategy Exposure"].replace(
        {"FundName_": ""}, regex=True, inplace=True)
    strat_df.set_index(["Strategy Exposure"], inplace=True)
    # sector
    sector_df = exposure_calc_df.loc[exposure_calc_df.index.str.contains(
        "Sector")]
    sector_df.reset_index(inplace=True)
    sector_df.rename(columns={"index": "Sector Exposure"}, inplace=True)
    sector_df["Sector Exposure"].replace(
        {"Sector_": ""}, regex=True, inplace=True)
    sector_df.set_index(["Sector Exposure"], inplace=True)
    # industry
    industry_df = exposure_calc_df.loc[exposure_calc_df.index.str.contains(
        "Industry")]
    industry_df.reset_index(inplace=True)
    industry_df.rename(columns={"index": "Industry Exposure"}, inplace=True)
    industry_df["Industry Exposure"].replace(
        {"Industry_": ""}, regex=True, inplace=True
    )
    industry_df.set_index(["Industry Exposure"], inplace=True)
    # country
    country_df = exposure_calc_df.loc[exposure_calc_df.index.str.contains(
        "Country")]
    country_df.reset_index(inplace=True)
    country_df.rename(columns={"index": "Country Exposure"}, inplace=True)
    country_df["Country Exposure"].replace(
        {"Country_": ""}, regex=True, inplace=True)
    country_df.set_index(["Country Exposure"], inplace=True)
    # market cap
    mktcap_df = exposure_calc_df.loc[exposure_calc_df.index.str.contains(
        "MarketCap")]
    mktcap_df.reset_index(inplace=True)
    mktcap_df.rename(columns={"index": "Market Cap Exposure"}, inplace=True)
    mktcap_df["Market Cap Exposure"].replace(
        {"MarketCap.1_": ""}, regex=True, inplace=True
    )
    mktcap_df.set_index(["Market Cap Exposure"], inplace=True)

    return strat_df, sector_df, industry_df, country_df, mktcap_df


def filter_beta_adj_exposure_calc(
    filter: Dict, position: pd.DataFrame, factor_betas: pd.DataFrame, firm_NAV: float
) -> pd.DataFrame:
    # agg positions by exposure across fund strats
    position_agg_exposure = (
        position.groupby(
            [
                "RFID",
            ]
        )
        .agg(
            {
                "TradeDate": "first",
                "FundName": "first",
                "UnderlierName": "first",
                "VaRTicker": "first",
                "MarketValue": "sum",
                "Exposure": "sum",
            }
        )
        .reset_index()
    )
    equity_mkt_beta = factor_betas[["ID", "SPX Index"]]
    filter_list = list(filter.keys())
    exposure_calc_dict = {}
    for filter_item in filter_list:
        position_grouped = position.groupby([filter_item])
        for name, group in position_grouped:
            if isinstance(name, tuple):
                name = name[0]
            long_exposure = group.loc[group["Exposure"] > 0]
            short_exposure = group.loc[group["Exposure"] < 0]
            # aggregate long exposures with same RFID;
            long_exposure_tmp = (
                long_exposure.groupby(
                    [
                        "RFID",
                    ]
                )
                .agg(
                    {
                        "TradeDate": "first",
                        "FundName": "first",
                        "VaRTicker": "first",
                        "Exposure": "sum",
                    }
                )
                .reset_index()
            )
            # aggregate short exposures withsame RFID
            short_exposure_tmp = (
                short_exposure.groupby(
                    [
                        "RFID",
                    ]
                )
                .agg(
                    {
                        "TradeDate": "first",
                        "FundName": "first",
                        "VaRTicker": "first",
                        "Exposure": "sum",
                    }
                )
                .reset_index()
            )
            if not long_exposure_tmp.empty:
                equity_mkt_beta_group = equity_mkt_beta.loc[
                    equity_mkt_beta["ID"].isin(
                        list(long_exposure_tmp["VaRTicker"].unique())
                    )
                ]
                equity_mkt_beta_group = equity_mkt_beta_group["SPX Index"]
                long_exposure_tmp["beta_adj_exposure"] = (
                    equity_mkt_beta_group.values *
                    long_exposure_tmp["Exposure"]
                )
                long_exposure_calc = long_exposure_tmp["beta_adj_exposure"].sum(
                )
            else:
                long_exposure_calc = 0
            if not short_exposure_tmp.empty:
                equity_mkt_beta_group = equity_mkt_beta.loc[
                    equity_mkt_beta["ID"].isin(
                        list(short_exposure_tmp["VaRTicker"].unique())
                    )
                ]
                equity_mkt_beta_group = equity_mkt_beta_group["SPX Index"]
                short_exposure_tmp["beta_adj_exposure"] = (
                    equity_mkt_beta_group.values *
                    short_exposure_tmp["Exposure"]
                )
                short_exposure_calc = short_exposure_tmp["beta_adj_exposure"].sum(
                )
            else:
                short_exposure_calc = 0
            gross_exposure_calc = long_exposure_calc + abs(short_exposure_calc)
            net_exposure_calc = long_exposure_calc + short_exposure_calc
            exposure_calc_dict[f"{filter_item}_{name}"] = [
                long_exposure_calc / firm_NAV.values[0],
                short_exposure_calc / firm_NAV.values[0],
                gross_exposure_calc / firm_NAV.values[0],
                net_exposure_calc / firm_NAV.values[0],
            ]
    beta_adj_exposure_calc_df = pd.DataFrame(
        exposure_calc_dict,
        index=[
            "Long",
            "Short",
            "Gross",
            "Net",
        ],
    ).T
    beta_adj_exposure_calc_df = pd.concat([beta_adj_exposure_calc_df], axis=1)
    # strat
    strat_df = beta_adj_exposure_calc_df.loc[
        beta_adj_exposure_calc_df.index.str.contains("Fund")
    ]
    strat_df.reset_index(inplace=True)
    strat_df.rename(columns={"index": "Strategy Beta Exposure"}, inplace=True)
    strat_df["Strategy Beta Exposure"].replace(
        {"FundName_": ""}, regex=True, inplace=True
    )
    strat_df.set_index(["Strategy Beta Exposure"], inplace=True)
    # sector
    sector_df = beta_adj_exposure_calc_df.loc[
        beta_adj_exposure_calc_df.index.str.contains("Sector")
    ]
    sector_df.reset_index(inplace=True)
    sector_df.rename(columns={"index": "Sector Beta Exposure"}, inplace=True)
    sector_df["Sector Beta Exposure"].replace(
        {"Sector_": ""}, regex=True, inplace=True)
    sector_df.set_index(["Sector Beta Exposure"], inplace=True)
    # industry
    industry_df = beta_adj_exposure_calc_df.loc[
        beta_adj_exposure_calc_df.index.str.contains("Industry")
    ]
    industry_df.reset_index(inplace=True)
    industry_df.rename(
        columns={"index": "Industry Beta Exposure"}, inplace=True)
    industry_df["Industry Beta Exposure"].replace(
        {"Industry_": ""}, regex=True, inplace=True
    )
    industry_df.set_index(["Industry Beta Exposure"], inplace=True)
    # country
    country_df = beta_adj_exposure_calc_df.loc[
        beta_adj_exposure_calc_df.index.str.contains("Country")
    ]
    country_df.reset_index(inplace=True)
    country_df.rename(columns={"index": "Country Beta Exposure"}, inplace=True)
    country_df["Country Beta Exposure"].replace(
        {"Country_": ""}, regex=True, inplace=True
    )
    country_df.set_index(["Country Beta Exposure"], inplace=True)
    # market cap
    mktcap_df = beta_adj_exposure_calc_df.loc[
        beta_adj_exposure_calc_df.index.str.contains("MarketCap")
    ]
    mktcap_df.reset_index(inplace=True)
    mktcap_df.rename(
        columns={"index": "Market Cap Beta Exposure"}, inplace=True)
    mktcap_df["Market Cap Beta Exposure"].replace(
        {"MarketCap.1_": ""}, regex=True, inplace=True
    )
    mktcap_df.set_index(["Market Cap Beta Exposure"], inplace=True)

    return strat_df, sector_df, industry_df, country_df, mktcap_df


def filter_options_delta_adj_exposure(position: pd.DataFrame) -> pd.DataFrame:
    options_exposure_calc_dict = {}
    position_grouped = position.groupby("FundName")
    for strat_name, strat_group in position_grouped:
        expiry_grouped = strat_group.groupby(["Expiry"])
        for expiry_date, expiry_group in expiry_grouped:
            if isinstance(expiry_date, tuple):
                expiry_date = expiry_date[0]
            position_option = expiry_group.loc[
                expiry_group["SECURITY_TYP"].str.contains(
                    "|".join(["call", "option", "put"]),
                    na=False,
                    case=False,
                )
            ]
            if not position_option.empty:
                long_call_exposure = expiry_group.loc[
                    (expiry_group["Exposure"] > 0)
                    & (
                        expiry_group["PutCall"].str.contains(
                            "call", na=False, case=False
                        )
                    )
                ]
                short_call_exposure = expiry_group.loc[
                    (expiry_group["Exposure"] < 0)
                    & (
                        expiry_group["PutCall"].str.contains(
                            "call", na=False, case=False
                        )
                    )
                ]
                long_put_exposure = expiry_group.loc[
                    (expiry_group["Exposure"] > 0)
                    & (
                        expiry_group["PutCall"].str.contains(
                            "put", na=False, case=False
                        )
                    )
                ]
                short_put_exposure = expiry_group.loc[
                    (expiry_group["Exposure"] < 0)
                    & (
                        expiry_group["PutCall"].str.contains(
                            "put", na=False, case=False
                        )
                    )
                ]
            long_call_exposure_calc = long_call_exposure["Exposure"].sum()
            short_call_exposure_calc = short_call_exposure["Exposure"].sum()
            long_put_exposure_calc = long_put_exposure["Exposure"].sum()
            short_put_exposure_calc = short_put_exposure["Exposure"].sum()
            options_exposure_calc_dict[
                f"{strat_name}_{expiry_date}_options_exposure"
            ] = [
                expiry_date,
                long_call_exposure_calc,
                short_call_exposure_calc,
                long_put_exposure_calc,
                short_put_exposure_calc,
            ]
    options_exposure_calc_df = pd.DataFrame(
        options_exposure_calc_dict,
        index=[
            "Option Exposure",
            "Long Calls",
            "Short Calls",
            "long Puts",
            "Short Puts",
        ],
    ).T
    options_exposure_calc_df["Option Exposure"] = pd.to_datetime(
        options_exposure_calc_df["Option Exposure"]
    ).dt.strftime("%Y-%m-%d")
    options_exposure_calc_df.reset_index(inplace=True, drop=True)
    options_exposure_calc_df.set_index(["Option Exposure"], inplace=True)

    return options_exposure_calc_df


def filter_options_delta_unadj_exposure(position: pd.DataFrame) -> pd.DataFrame:
    options_exposure_delta1_calc_dict = {}
    position["delta_1_exposure"] = (
        1 / abs(position["Delta"])) * position["Exposure"]
    position_grouped = position.groupby("FundName")
    for strat_name, strat_group in position_grouped:
        expiry_grouped = strat_group.groupby(["Expiry"])
        for expiry_date, expiry_group in expiry_grouped:
            if isinstance(expiry_date, tuple):
                expiry_date = expiry_date[0]
            position_option = expiry_group.loc[
                expiry_group["SECURITY_TYP"].str.contains(
                    "|".join(["call", "option", "put"]),
                    na=False,
                    case=False,
                )
            ]
            if not position_option.empty:
                long_call_exposure = expiry_group.loc[
                    (expiry_group["Exposure"] > 0)
                    & (
                        expiry_group["PutCall"].str.contains(
                            "call", na=False, case=False
                        )
                    )
                ]
                short_call_exposure = expiry_group.loc[
                    (expiry_group["Exposure"] < 0)
                    & (
                        expiry_group["PutCall"].str.contains(
                            "call", na=False, case=False
                        )
                    )
                ]
                long_put_exposure = expiry_group.loc[
                    (expiry_group["Exposure"] > 0)
                    & (
                        expiry_group["PutCall"].str.contains(
                            "put", na=False, case=False
                        )
                    )
                ]
                short_put_exposure = expiry_group.loc[
                    (expiry_group["Exposure"] < 0)
                    & (
                        expiry_group["PutCall"].str.contains(
                            "put", na=False, case=False
                        )
                    )
                ]
            long_call_exposure_calc = long_call_exposure["delta_1_exposure"].sum(
            )
            short_call_exposure_calc = short_call_exposure["delta_1_exposure"].sum(
            )
            long_put_exposure_calc = long_put_exposure["delta_1_exposure"].sum(
            )
            short_put_exposure_calc = short_put_exposure["delta_1_exposure"].sum(
            )
            options_exposure_delta1_calc_dict[
                f"{strat_name}_{expiry_date}_delta1_options_exposure"
            ] = [
                expiry_date,
                long_call_exposure_calc,
                short_call_exposure_calc,
                long_put_exposure_calc,
                short_put_exposure_calc,
            ]
    options_exposure_delta1_calc_df = pd.DataFrame(
        options_exposure_delta1_calc_dict,
        index=[
            "Option Notional",
            "Long Calls",
            "Short Calls",
            "long Puts",
            "Short Puts",
        ],
    ).T
    options_exposure_delta1_calc_df["Option Notional"] = pd.to_datetime(
        options_exposure_delta1_calc_df["Option Notional"]
    ).dt.strftime("%Y-%m-%d")
    options_exposure_delta1_calc_df.reset_index(inplace=True, drop=True)
    options_exposure_delta1_calc_df.set_index(
        ["Option Notional"], inplace=True)

    return options_exposure_delta1_calc_df


def filter_options_premium(position: pd.DataFrame) -> pd.DataFrame:
    options_premium_dict = {}
    position["premium"] = (
        position["Quantity"].astype(float)
        * position["MarketPrice"]
        * position["PX_POS_MULT_FACTOR"]
    )
    position_grouped = position.groupby("FundName")
    for strat_name, strat_group in position_grouped:
        expiry_grouped = strat_group.groupby(["Expiry"])
        for expiry_date, expiry_group in expiry_grouped:
            if isinstance(expiry_date, tuple):
                expiry_date = expiry_date[0]
            position_option = expiry_group.loc[
                expiry_group["SECURITY_TYP"].str.contains(
                    "|".join(["call", "option", "put"]),
                    na=False,
                    case=False,
                )
            ]
            if not position_option.empty:
                call_exposure = expiry_group.loc[
                    (expiry_group["PutCall"].str.contains(
                        "call", na=False, case=False))
                ]
                call_exposure["intrinsic_value"] = np.where(
                    call_exposure["UndlPrice"].values -
                    call_exposure["Strike"].values
                    < 0,
                    0,
                    call_exposure["UndlPrice"].values -
                    call_exposure["Strike"].values,
                )
                put_exposure = expiry_group.loc[
                    (expiry_group["PutCall"].str.contains(
                        "put", na=False, case=False))
                ]
                put_exposure["intrinsic_value"] = np.where(
                    put_exposure["Strike"].values -
                    put_exposure["UndlPrice"].values
                    < 0,
                    0,
                    put_exposure["Strike"].values -
                    put_exposure["UndlPrice"].values,
                )
            call_premium_calc = call_exposure["premium"].sum()
            call_intrinsic_calc = call_exposure["intrinsic_value"].sum()
            put_premium_calc = put_exposure["premium"].sum()
            put_intrinsic_calc = put_exposure["intrinsic_value"].sum()
            options_premium_dict[f"{strat_name}_{expiry_date}_options_premium"] = [
                expiry_date,
                call_premium_calc,
                call_intrinsic_calc,
                put_premium_calc,
                put_intrinsic_calc,
            ]
    options_premium_df = pd.DataFrame(
        options_premium_dict,
        index=[
            "Premium",
            "Call_Premium",
            "Call_Intrinsic",
            "Put_Premium",
            "Put_Intrinsic",
        ],
    ).T
    options_premium_df["Premium"] = pd.to_datetime(
        options_premium_df["Premium"]
    ).dt.strftime("%Y-%m-%d")
    options_premium_df.reset_index(inplace=True, drop=True)
    options_premium_df.set_index(["Premium"], inplace=True)

    return options_premium_df


def greek_sensitivities(position: pd.DataFrame) -> pd.DataFrame:
    greek_sensitivities_dict = {}
    position_grouped = position.groupby("FundName")
    for strat_name, strat_group in position_grouped:
        expiry_grouped = strat_group.groupby(["Expiry"])
        for expiry_date, expiry_group in expiry_grouped:
            if isinstance(expiry_date, tuple):
                expiry_date = expiry_date[0]
            position_option = expiry_group.loc[
                expiry_group["SECURITY_TYP"].str.contains(
                    "|".join(["call", "option", "put"]),
                    na=False,
                    case=False,
                )
            ]
            if not position_option.empty:
                position_option["Dollar Gamma 1%"] = (
                    position_option["Gamma$"].astype(float)
                    * position_option["Exposure"]
                )
                position_option["Dollar Vega 1%"] = (
                    position_option["Vega"] * position_option["Exposure"]
                )
                position_option["Dollar Theta 1D"] = (
                    position_option["Theta"] * position_option["Exposure"]
                )
            delta_exposure_calc = position_option["Exposure"].sum()
            gamma_exposure_calc = position_option["Dollar Gamma 1%"].sum()
            vega_exposure_calc = position_option["Dollar Vega 1%"].sum()
            theta_exposure_calc = position_option["Dollar Theta 1D"].sum()
            greek_sensitivities_dict[
                f"{strat_name}_{expiry_date}_greek_sensitivities"
            ] = [
                expiry_date,
                delta_exposure_calc,
                gamma_exposure_calc,
                vega_exposure_calc,
                theta_exposure_calc,
            ]
    greek_sensitivities_df = pd.DataFrame(
        greek_sensitivities_dict,
        index=[
            "Greek Sensitivity",
            "Delta_Exposure",
            "Dollar_Gamma_1%",
            "Dollar_Vega_1%",
            "Dollar_Theta_1D",
        ],
    ).T
    greek_sensitivities_df["Greek Sensitivity"] = pd.to_datetime(
        greek_sensitivities_df["Greek Sensitivity"]
    ).dt.strftime("%Y-%m-%d")
    greek_sensitivities_df.reset_index(inplace=True, drop=True)
    greek_sensitivities_df.set_index(["Greek Sensitivity"], inplace=True)

    return greek_sensitivities_df


def factor_decomp_filtered(
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
    factor_prices: pd.DataFrame,
    factor: pd.DataFrame,
    matrix_cov: pd.DataFrame,
    firm_NAV: float,
) -> pd.DataFrame:
    # agg positions by exposure across fund strats
    position_agg_exposure = (
        position.groupby(
            [
                "RFID",
            ]
        )
        .agg(
            {
                "TradeDate": "first",
                "FundName": "first",
                "UnderlierName": "first",
                "VaRTicker": "first",
                "MarketValue": "sum",
                "Exposure": "sum",
            }
        )
        .reset_index()
    )
    factor_vol = np.sqrt(
        pd.Series(np.diag(matrix_cov.iloc[1:, 1:]),
                  index=factor_betas.columns[1:])
    )
    macro_factor_df = factor.loc[factor["factor_group"]
                                 == "macro"][["Factor Names"]]
    sector_factor_df = factor.loc[factor["factor_group"]
                                  == "sector"][["Factor Names"]]
    date = factor_prices.index[-1]
    factor_decomp_dict = {}
    position_grouped = position.groupby("FundName")
    factor_vol_df = pd.DataFrame(
        factor_vol.values, index=factor_vol.index, columns=["FactorVol"]
    )
    for strat_name, strat_group in position_grouped:
        if isinstance(strat_name, tuple):
            strat_name = strat_name[0]
        tmp = (
            strat_group.groupby(
                [
                    "RFID",
                ]
            )
            .agg({"VaRTicker": "first", "Exposure": "sum"})
            .reset_index()
        )
        exposure = tmp["Exposure"].values
        fund_positions = tmp["VaRTicker"]
        factor_betas_fund = factor_betas.loc[factor_betas["ID"].isin(
            fund_positions)]
        strat_factor_exp = exposure[:,
                                    None].T @ factor_betas_fund.values[:, 1:]
        factor_decomp_dict[f"{strat_name}"] = strat_factor_exp[0, :]
    factor_decomp_df = pd.DataFrame(factor_decomp_dict, index=factor_vol.index)
    date_vector = pd.DataFrame(
        np.repeat(date, len(factor_decomp_df)),
        index=factor_decomp_df.index,
        columns=["date"],
    )
    factor_decomp_df = pd.concat(
        [date_vector, factor_decomp_df, factor_vol_df], axis=1)
    factor_decomp_df["FactorExp"] = (
        factor_decomp_df.iloc[:, 1:-1].sum(axis=1) / firm_NAV.values[0]
    )
    factor_decomp_df.reset_index(inplace=True)
    factor_decomp_df.rename(columns={"index": "FactorID"}, inplace=True)
    factor_decomp_df = pd.merge(
        factor_decomp_df,
        factor[["Factor Names"]],
        on=["FactorID"],
        how="left",
    )
    factor_decomp_df.set_index(["Factor Names"], inplace=True)
    LOGGER.info(f"factor_decomp generated for strat {strat_name}")
    macro_factor_decomp_df = factor_decomp_df.loc[
        factor_decomp_df.index.isin(macro_factor_df["Factor Names"])
    ]
    macro_factor_decomp_df = macro_factor_decomp_df[["FactorExp", "FactorVol"]]
    macro_factor_decomp_df.reset_index(inplace=True)
    macro_factor_decomp_df.rename(
        columns={"Factor Names": "Macro Factor Sensitivity"}, inplace=True
    )
    macro_factor_decomp_df.set_index(
        ["Macro Factor Sensitivity"], inplace=True)
    sector_factor_decomp_df = factor_decomp_df.loc[
        factor_decomp_df.index.isin(sector_factor_df["Factor Names"])
    ]
    sector_factor_decomp_df = sector_factor_decomp_df[[
        "FactorExp", "FactorVol"]]
    sector_factor_decomp_df.reset_index(inplace=True)
    sector_factor_decomp_df.rename(
        columns={"Factor Names": "Sector Sensitivities"}, inplace=True
    )
    sector_factor_decomp_df.set_index(["Sector Sensitivities"], inplace=True)

    return macro_factor_decomp_df, sector_factor_decomp_df


def factor_decomp_by_factor_position(
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
    factor: pd.DataFrame,
    firm_NAV: float,
) -> pd.DataFrame:
    factor = factor.reindex(index=factor_betas.columns[1:])
    factor.reset_index(inplace=True)
    factor.rename(columns={"index": "FactorID"}, inplace=True)
    factor.set_index(["Factor Names"], inplace=True)
    factor_betas.columns = [factor_betas.columns[0]] + list(factor.index)
    # agg positions by exposure across fund strats
    position_agg_exposure = (
        position.groupby(
            [
                "RFID",
            ]
        )
        .agg(
            {
                "TradeDate": "first",
                "FundName": "first",
                "UnderlierName": "first",
                "VaRTicker": "first",
                "MarketValue": "sum",
                "Exposure": "sum",
            }
        )
        .reset_index()
    )
    position_agg_exposure.rename(columns={"VaRTicker": "ID"}, inplace=True)
    factor_beta_exposure = pd.merge(
        factor_betas, position_agg_exposure, on=["ID"], how="inner"
    )
    # loop through column by column
    risk_factor_exposure_top_N_list = []
    risk_factor_exposure_bottom_N_list = []
    for col in factor_beta_exposure.columns[1: len(factor_betas.columns)]:
        risk_factor_exposure = pd.DataFrame(
            np.concatenate(
                (
                    factor_beta_exposure["UnderlierName"].values[:, None],
                    (
                        factor_beta_exposure[col] *
                        factor_beta_exposure["Exposure"]
                    ).values[:, None]
                    / firm_NAV.values[:, None],
                    factor_beta_exposure["Exposure"].values[:, None]
                    / firm_NAV.values[:, None],
                ),
                axis=1,
            ),
            columns=[f"{col} - Top 10", "Exposure", "FactorExp"],
            index=factor_betas.index,
        )
        risk_factor_exposure_sorted = risk_factor_exposure.sort_values(
            ["Exposure"], ascending=[False]
        )
        risk_factor_exposure_sorted_top_10 = risk_factor_exposure_sorted.iloc[:10, :]
        risk_factor_exposure_sorted_top_10.reset_index(inplace=True, drop=True)
        risk_factor_exposure_sorted_top_10.set_index(
            [f"{col} - Top 10"], inplace=True)
        risk_factor_exposure_top_N_list.append(
            risk_factor_exposure_sorted_top_10)
        risk_factor_exposure_sorted = risk_factor_exposure.sort_values(
            ["Exposure"], ascending=[True]
        )
        risk_factor_exposure_sorted_bottom_10 = risk_factor_exposure_sorted.iloc[:10, :]
        risk_factor_exposure_sorted_bottom_10.reset_index(
            inplace=True, drop=True)
        risk_factor_exposure_sorted_bottom_10.rename(
            columns={f"{col} - Top 10": f"{col} - Bottom 10"}, inplace=True
        )
        risk_factor_exposure_sorted_bottom_10.set_index(
            [f"{col} - Bottom 10"], inplace=True
        )
        risk_factor_exposure_bottom_N_list.append(
            risk_factor_exposure_sorted_bottom_10)
    LOGGER.info(
        "apply position agg data against factor betas to build the factor by "
        "factor top N risk contributors by position"
    )

    return risk_factor_exposure_top_N_list, risk_factor_exposure_bottom_N_list


def factor_heat_map(
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
    factor: pd.DataFrame,
    firm_NAV: float,
) -> pd.DataFrame:
    factor.reset_index(inplace=True)
    factor.set_index(["Factor Names"], inplace=True)
    factor = factor.reindex(index=factor_betas.columns[1:])
    factor_betas.columns = [factor_betas.columns[0]] + list(factor.index)
    # agg positions by exposure across fund strats
    position_agg_exposure = (
        position.groupby(
            [
                "RFID",
            ]
        )
        .agg(
            {
                "TradeDate": "first",
                "FundName": "first",
                "UnderlierName": "first",
                "VaRTicker": "first",
                "MarketValue": "sum",
                "Exposure": "sum",
            }
        )
        .reset_index()
    )
    position_agg_exposure.rename(columns={"VaRTicker": "ID"}, inplace=True)
    factor_beta_exposure = pd.merge(
        factor_betas, position_agg_exposure, on=["ID"], how="inner"
    )
    # loop through column by column
    risk_factor_exposure_df_list = []
    for col in factor_beta_exposure.columns[1: len(factor_betas.columns)]:
        risk_factor_exposure = pd.DataFrame(
            np.concatenate(
                (
                    factor_beta_exposure["UnderlierName"].values[:, None],
                    (
                        factor_beta_exposure[col] *
                        factor_beta_exposure["Exposure"]
                    ).values[:, None]
                    / firm_NAV.values[:, None],
                    factor_beta_exposure["Exposure"].values[:, None]
                    / firm_NAV.values[:, None],
                ),
                axis=1,
            ),
            columns=["Position", f"{col}", "Exposure"],
            index=factor_betas.index,
        )
        risk_factor_exposure_df_list.append(risk_factor_exposure)
    LOGGER.info(
        "apply position agg data against factor betas to build the factor by "
        "factor top N risk contributors by position"
    )
    risk_factor_exposure_df = pd.concat(risk_factor_exposure_df_list, axis=1)
    risk_factor_exposure_df = risk_factor_exposure_df.loc[
        :, ~risk_factor_exposure_df.columns.duplicated()
    ]
    risk_factor_exposure_df.rename(columns={"Equity": "Beta"}, inplace=True)
    risk_factor_exposure_df.reset_index(inplace=True, drop=True)
    risk_factor_exposure_df.set_index(["Position"], inplace=True)

    return risk_factor_exposure_df


def stress_test_beta_price_vol_exposure_by_position(
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
    matrix_cov: pd.DataFrame,
    position_returns: pd.DataFrame,
    factor: pd.DataFrame,
    firm_NAV: float,
) -> pd.DataFrame:
    factor = factor.reindex(index=factor_betas.columns[1:])
    factor.reset_index(inplace=True)
    factor.rename(columns={"index": "Factor Names"}, inplace=True)
    factor.set_index(["Factor Names"], inplace=True)
    factor_betas.columns = [factor_betas.columns[0]] + list(factor.index)
    # agg positions by exposure across fund strats
    price_shock_list = [-0.01, -0.1]

    position_non_option = position.loc[
        position["SECURITY_TYP"].str.contains(
            "|".join(
                [
                    "fixed",
                    "future",
                    "public",
                    "prefer",
                    "common",
                    "reit",
                    "fund",
                    "mlp",
                    "adr",
                ]
            ),
            na=False,
            case=False,
        )
    ]
    position_option = position.loc[
        position["SECURITY_TYP"].str.contains(
            "|".join(["call", "option", "put"]),
            na=False,
            case=False,
        )
    ]
    price_shock_df_list = []
    for price_shock in price_shock_list:
        if not position_non_option.empty:
            position_non_option[f"{100*abs(price_shock):.0f}$ shock value"] = (
                position_non_option["Quantity"].astype(float)
                * position_non_option["FXRate"]
                * position_non_option["MarketPrice"]
                * position_non_option["PX_POS_MULT_FACTOR"]
                * (1 + price_shock)
            )
            position_non_option[f"{100*abs(price_shock):.0f}% Shock $"] = (
                position_non_option[f"{100*abs(price_shock):.0f}$ shock value"]
            ) - (
                position_non_option["Quantity"].astype(float)
                * position_non_option["FXRate"]
                * position_non_option["MarketPrice"]
                * position_non_option["PX_POS_MULT_FACTOR"]
            )
            position_non_option[
                f"{100*abs(price_shock):.0f}% Shock %"
            ] = position_non_option[f"{100*abs(price_shock):.0f}% Shock $"].divide(
                firm_NAV.values[0]
            )
            position_non_option_brief = position_non_option[
                [
                    "UnderlierName",
                    "Description",
                    "VaRTicker",
                    "RFID",
                    "Quantity",
                    "MarketValue",
                    "Exposure",
                    f"{100*abs(price_shock):.0f}% Shock $",
                    f"{100*abs(price_shock):.0f}% Shock %",
                ]
            ]
        if not position_option.empty:
            position_option["shock_underlying_price"] = position_option["UndlPrice"] * (
                1 + price_shock
            )
            position_option["shock_option_price"] = option_price(
                S=position_option["shock_underlying_price"],
                X=position_option["Strike"],
                T=position_option["MtyYears"],
                Vol=position_option["IVOL_TM"].astype(float),
                rf=RISK_FREE_RATE,
                type=position_option["PutCall"],
            )
            position_option[f"{100*abs(price_shock):.0f}$ shock value"] = (
                position_option["shock_option_price"]
                * position_option["PX_POS_MULT_FACTOR"]
                * position_option["Quantity"].astype(float)
                * position_option["FXRate"]
            )
            position_option[f"{100*abs(price_shock):.0f}% Shock $"] = (
                position_option[f"{100*abs(price_shock):.0f}$ shock value"]
            ) - (
                position_option["MarketPrice"]
                * position_option["PX_POS_MULT_FACTOR"]
                * position_option["Quantity"].astype(float)
                * position_option["FXRate"]
            )
            position_option[f"{100*abs(price_shock):.0f}% Shock %"] = position_option[
                f"{100*abs(price_shock):.0f}% Shock $"
            ].divide(firm_NAV.values[0])
            position_option["Dollar Delta"] = position_option["Exposure"]
            position_option["Dollar Gamma 1%"] = (
                position_option["Gamma$"].astype(
                    float) * position_option["Exposure"]
            )
            position_option["Dollar Vega 1%"] = (
                position_option["Vega"] * position_option["Exposure"]
            )
            position_option["Dollar Theta 1D"] = (
                position_option["Theta"] * position_option["Exposure"]
            )
            position_option_brief = position_option[
                [
                    "UnderlierName",
                    "Description",
                    "VaRTicker",
                    "RFID",
                    "Quantity",
                    "Dollar Delta",
                    "Dollar Gamma 1%",
                    "Dollar Vega 1%",
                    "Dollar Theta 1D",
                    "MarketValue",
                    "Exposure",
                    f"{100*abs(price_shock):.0f}% Shock $",
                    f"{100*abs(price_shock):.0f}% Shock %",
                ]
            ]
        price_shock_df_list.append(
            pd.concat([position_non_option_brief,
                      position_option_brief], axis=0)
        )
    price_shock_df = pd.concat(price_shock_df_list, axis=1)
    price_shock_df = price_shock_df.loc[:,
                                        ~price_shock_df.columns.duplicated()]
    LOGGER.info("estimate RFID vol")
    position_cov = position_returns.cov()
    position_vols = pd.DataFrame(
        np.sqrt(pd.Series(np.diag(position_cov))).values,
        index=position_cov.index,
        columns=["stdev"],
    )
    position_vols.reset_index(inplace=True)
    position_vols.rename(columns={"index": "ID"}, inplace=True)
    price_shock_df.rename(columns={"VaRTicker": "ID"}, inplace=True)
    beta_spx = factor_betas[["ID", "Equity"]]
    price_shock_df = pd.merge(price_shock_df, beta_spx, on=["ID"], how="left")
    price_shock_df = pd.merge(
        price_shock_df, position_vols, on=["ID"], how="left")
    spx_vol = np.sqrt(
        matrix_cov.loc[matrix_cov.index == "SPX Index"]["SPX Index"])
    price_shock_df["Correl"] = (
        price_shock_df["Equity"].values * spx_vol.values
    ) / price_shock_df["stdev"].values
    price_shock_df.rename(
        columns={
            "UnderlierName": "Underlier",
            "Description": "Position",
            "Quantity": "Shares/Contracts",
            "Equity": "Beta",
            "stdev": "Volatility",
        },
        inplace=True,
    )
    price_shock_df["Exposure"] = price_shock_df["Exposure"] / \
        firm_NAV.values[0]
    price_shock_df = price_shock_df[
        [
            "Underlier",
            "Position",
            "Shares/Contracts",
            "Exposure",
            "Beta",
            "Correl",
            "Volatility",
        ]
        + [
            col
            for col in price_shock_df.columns
            if col
            not in [
                "Underlier",
                "Position",
                "Shares/Contracts",
                "Exposure",
                "Beta",
                "Correl",
                "Volatility",
                "ID",
                "RFID",
            ]
        ]
    ]
    position_breakdown = price_shock_df
    position_breakdown.reset_index(inplace=True, drop=True)
    position_breakdown.set_index(["Underlier"], inplace=True)
    position_breakdown = position_breakdown.sort_values(
        ["Exposure"], ascending=False)
    cols = [
        col
        for col in position_breakdown.columns
        if col
        not in [
            "UnderlierName",
            "Dollar Delta",
            "Dollar Gamma 1%",
            "Dollar Vega 1%",
            "Dollar Theta 1D",
        ]
    ]
    position_breakdown.reset_index(inplace=True)
    position_breakdown_agg = (
        position_breakdown.groupby(
            [
                "Position",
            ]
        )
        .agg(
            {
                "Underlier": "sum",
                "Shares/Contracts": "sum",
                "Exposure": "sum",
                "Beta": "first",
                "Correl": "first",
                "Volatility": "first",
                "MarketValue": "sum",
                "1% Shock $": "sum",
                "1% Shock %": "sum",
                "Dollar Delta": "sum",
                "Dollar Gamma 1%": "sum",
                "Dollar Vega 1%": "sum",
                "Dollar Theta 1D": "sum",
                "10% Shock $": "sum",
                "10% Shock %": "sum",
            }
        )
    )
    position_breakdown = position_breakdown_agg.copy()
    position_breakdown.reset_index(inplace=True)
    position_breakdown.set_index(["Underlier"], inplace=True)
    position_summary = position_breakdown[cols]
    position_summary.reset_index(inplace=True, drop=True)
    position_summary.set_index(["Position"], inplace=True)
    position_summary = position_summary.sort_values(
        ["Exposure"], ascending=False)

    return position_breakdown, position_summary
