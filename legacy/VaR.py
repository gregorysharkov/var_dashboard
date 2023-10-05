import logging
from itertools import product
from typing import Dict, List

import numpy as np
import pandas as pd
from tqdm import tqdm

from legacy.helper import imply_smb_gmv, option_price

pd.set_option("mode.chained_assignment", None)


logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

RISK_FREE_RATE = 5.5e-2  # as of Aug 2023


def filter_var_grouping(
    df: pd.DataFrame,
    position_list: List,
    fund_list: List,
    sector_list: List,
    industry_list: List,
    country_list: List,
    mktcap_list: List,
):
    if df.columns.str.contains("VaRTicker"):
        position_list.append(df)
    elif df.columns.str.contains("FundName"):
        fund_list.append(df)
    elif df.columns.str.contains("Sector"):
        sector_list.append(df)
    elif df.columns.str.contains("Industry"):
        industry_list.append(df)
    elif df.columns.str.contains("Country"):
        country_list.append(df)
    elif df.columns.str.contains("MarketCap"):
        mktcap_list.append(df)

    return (
        position_list,
        fund_list,
        sector_list,
        industry_list,
        country_list,
        mktcap_list,
    )


def generate_factor_returns(factor_prices: pd.DataFrame) -> pd.DataFrame:
    '''generates factor returns from factor prices'''

    return np.log(
        factor_prices.iloc[1:, :] / factor_prices.iloc[1:, :].shift(1)
    )  # type: ignore


def matrix_correlation(
    factor_prices: pd.DataFrame,
    factor: pd.DataFrame,
) -> pd.DataFrame:
    '''calculates factor correlation matrix'''
    factor_returns = generate_factor_returns(factor_prices)
    factor_returns = imply_smb_gmv(factor_returns)  # type: ignore
    factor_correl = factor_returns.corr()
    factor.set_index(["FactorID"], inplace=True)
    factor_correl = pd.merge(
        factor_correl, factor["Factor Names"],
        left_index=True,
        right_index=True,
    )
    factor_correl.reset_index(inplace=True, drop=True)
    factor_correl.set_index(["Factor Names"], inplace=True)
    factor_correl.columns = factor_correl.index

    return factor_correl


def decay_cov(factor_prices: pd.DataFrame) -> pd.DataFrame:
    factor_returns = generate_factor_returns(factor_prices)
    factor_returns = imply_smb_gmv(factor_returns)
    nn = np.linspace(start=1, stop=len(
        factor_returns), num=len(factor_returns))
    df = ((1 - 0.94) * 0.94 ** (nn - 1)) ** (0.5)
    df_tmp = np.repeat(df, len(factor_returns.columns))
    df_tmp = df_tmp.reshape(len(df), len(factor_returns.columns))
    factor_returns_decay = factor_returns * df_tmp
    factor_covar_decay = factor_returns_decay.cov()

    return factor_covar_decay


def matrix_cov(factor_prices: pd.DataFrame) -> pd.DataFrame:
    factor_returns = generate_factor_returns(factor_prices)
    factor_returns = imply_smb_gmv(factor_returns)  # type: ignore
    factor_cov = factor_returns.cov()

    return factor_cov


def filter_VaR95(
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
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
    dict = {}
    date = factor_prices.index[-1]
    filter_item = "VaRTicker"
    position_grouped = position.groupby([filter_item])
    for name, group in tqdm(position_grouped, 'filter_VaR95'):
        if isinstance(name, tuple):
            name = name[0]
        tmp = (
            group.groupby(
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
        VaR95 = (
            exposure[:, None].T
            @ factor_betas_fund.values[:, 1:]
            @ matrix_cov.values[1:, 1:]
            @ factor_betas_fund.values[:, 1:].T
            @ exposure[:, None]
        ) ** (0.5)
        dict[name] = (VaR95[:, 0] * 1.644854) / firm_NAV
        # LOGGER.info(
        #     f"estimating  port VaR 95 of {name} as of date {date} within"
        #     f"filter {filter_item}"
        # )
    VaR95_df = pd.DataFrame(dict).T
    VaR95_df = pd.DataFrame(
        VaR95_df.values,
        columns=[f"{filter_item}_VaR95"],
        index=position_agg_exposure["UnderlierName"],
    )
    VaR95_top10 = VaR95_df.sort_values([f"{filter_item}_VaR95"], ascending=False).iloc[
        :10
    ]
    VaR95_top10.reset_index(inplace=True)
    VaR95_top10.rename(
        columns={
            "UnderlierName": "Top10 VaR Contributors",
            f"{filter_item}_VaR95": "VaR95",
        },
        inplace=True,
    )
    VaR95_top10.set_index(["Top10 VaR Contributors"], inplace=True)
    VaR95_bottom10 = VaR95_df.sort_values(
        [f"{filter_item}_VaR95"], ascending=True
    ).iloc[:10]
    VaR95_bottom10.reset_index(inplace=True)
    VaR95_bottom10.rename(
        columns={
            "UnderlierName": "Top10 VaR Diversifiers",
            f"{filter_item}_VaR95": "VaR95",
        },
        inplace=True,
    )
    VaR95_bottom10.set_index(["Top10 VaR Diversifiers"], inplace=True)

    return VaR95_top10, VaR95_bottom10


def filter_VaR99(
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
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
    dict = {}
    date = factor_prices.index[-1]
    filter_item = "VaRTicker"
    position_grouped = position.groupby([filter_item])
    for name, group in tqdm(position_grouped, 'filter_VaR99'):
        if isinstance(name, tuple):
            name = name[0]
        tmp = (
            group.groupby(
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
        VaR99 = (
            exposure[:, None].T
            @ factor_betas_fund.values[:, 1:]
            @ matrix_cov.values[1:, 1:]
            @ factor_betas_fund.values[:, 1:].T
            @ exposure[:, None]
        ) ** (0.5)
        dict[name] = (VaR99[:, 0] * 2.326348) / firm_NAV
        # LOGGER.info(
        #     f"estimating  port VaR 99 of {name} as of date {date} within"
        #     f"filter {filter_item}"
        # )
    VaR99_df = pd.DataFrame(dict).T
    VaR99_df = pd.DataFrame(
        VaR99_df.values,
        columns=[f"{filter_item}_VaR99"],
        index=position_agg_exposure["UnderlierName"],
    )
    VaR99_top10 = VaR99_df.sort_values([f"{filter_item}_VaR99"], ascending=False).iloc[
        :10
    ]
    VaR99_top10.reset_index(inplace=True)
    VaR99_top10.rename(
        columns={
            "UnderlierName": "Top10 VaR Contributors",
            f"{filter_item}_VaR99": "VaR99",
        },
        inplace=True,
    )
    VaR99_top10.set_index(["Top10 VaR Contributors"], inplace=True)
    VaR99_bottom10 = VaR99_df.sort_values(
        [f"{filter_item}_VaR99"], ascending=True
    ).iloc[:10]
    VaR99_bottom10.reset_index(inplace=True)
    VaR99_bottom10.rename(
        columns={
            "UnderlierName": "Top10 VaR Diversifiers",
            f"{filter_item}_VaR99": "VaR99",
        },
        inplace=True,
    )
    VaR99_bottom10.set_index(["Top10 VaR Diversifiers"], inplace=True)

    return VaR99_top10, VaR99_bottom10


def filter_VaR95_iso(
    filter: Dict,
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
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
    filter_VaR95_iso_df_list = []  # contains all compuuted results across all filters
    filter_list = ["VaRTicker"] + list(filter.keys())
    date = factor_prices.index[-1]
    for filter_item in filter_list:
        position_grouped = position.groupby([filter_item])
        dict = {}
        for name, group in tqdm(position_grouped, 'filter_VaR95_iso'):
            if isinstance(name, tuple):
                name = name[0]
            tmp = (
                group.groupby(
                    [
                        "RFID",
                    ]
                )
                .agg({"VaRTicker": "first", "Exposure": "sum"})
                .reset_index()
            )
            exposure = tmp["Exposure"].values
            fund_positions = tmp["VaRTicker"]
            factor_betas_fund = factor_betas.loc[
                factor_betas["ID"].isin(fund_positions)
            ]
            VaR95_iso = (
                exposure[:, None].T
                @ factor_betas_fund.values[:, 1:]
                @ matrix_cov.values[1:, 1:]
                @ factor_betas_fund.values[:, 1:].T
                @ exposure[:, None]
            ) ** (0.5)
            dict[name] = (VaR95_iso[:, 0] * 1.644854) / firm_NAV
            # LOGGER.info(
            #     f"estimating  port VaR 95 of {name} as of date {date} within"
            #     f"filter {filter_item}"
            # )
        VaR95_iso_df = pd.DataFrame(dict).T
        VaR95_iso_df = pd.DataFrame(
            VaR95_iso_df.values,
            columns=[f"{filter_item}_Iso95"],
            index=VaR95_iso_df.index,
        )
        filter_VaR95_iso_df_list.append(VaR95_iso_df)

    return filter_VaR95_iso_df_list


def filter_VaR99_iso(
    filter: Dict,
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
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
    filter_VaR99_iso_df_list = []  # contains all compuuted results across all filters
    filter_list = list(filter.keys())
    filter_list = ["VaRTicker"] + list(filter.keys())
    date = factor_prices.index[-1]
    for filter_item in filter_list:
        position_grouped = position.groupby([filter_item])
        dict = {}
        for name, group in tqdm(position_grouped, 'filter_VaR99_iso'):
            if isinstance(name, tuple):
                name = name[0]
            tmp = (
                group.groupby(
                    [
                        "RFID",
                    ]
                )
                .agg({"VaRTicker": "first", "Exposure": "sum"})
                .reset_index()
            )
            exposure = tmp["Exposure"].values
            fund_positions = tmp["VaRTicker"]
            factor_betas_fund = factor_betas.loc[
                factor_betas["ID"].isin(fund_positions)
            ]
            VaR99_iso = (
                exposure[:, None].T
                @ factor_betas_fund.values[:, 1:]
                @ matrix_cov.values[1:, 1:]
                @ factor_betas_fund.values[:, 1:].T
                @ exposure[:, None]
            ) ** (0.5)
            dict[name] = (VaR99_iso[:, 0] * 2.326348) / firm_NAV
            # LOGGER.info(
            #     f"estimating  port VaR 99 of {name} as of date {date} within"
            #     f"filter {filter_item}"
            # )
        VaR99_iso_df = pd.DataFrame(dict).T
        VaR99_iso_df = pd.DataFrame(
            VaR99_iso_df.values,
            columns=[f"{filter_item}_Iso99"],
            index=VaR99_iso_df.index,
        )
        filter_VaR99_iso_df_list.append(VaR99_iso_df)

    return filter_VaR99_iso_df_list


def filter_VaR95_inc(
    filter: Dict,
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
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
    total_exposure = position_agg_exposure["Exposure"].values
    VaR95_total = (
        total_exposure[:, None].T
        @ factor_betas.drop('ID', axis=1).values
        @ matrix_cov.values[1:, 1:]
        @ factor_betas.drop('ID', axis=1).values.T
        @ total_exposure[:, None]
    ) ** (0.5) * 1.644854
    filter_VaR95_inc_df_list = []  # contains all computed results across all filters
    filter_list = list(filter.keys())
    filter_list = ["VaRTicker"] + list(filter.keys())
    date = factor_prices.index[-1]
    for filter_item in filter_list:
        position_grouped = position.groupby([filter_item])
        dict = {}
        for name, group in tqdm(position_grouped, 'filter_VaR95_inc'):
            if isinstance(name, tuple):
                name = name[0]
            tmp = position.loc[position[filter_item] != name]
            tmp = (
                tmp.groupby(
                    [
                        "RFID",
                    ]
                )
                .agg({"VaRTicker": "first", "Exposure": "sum"})
                .reset_index()
            )
            exposure = tmp["Exposure"].values
            fund_positions = tmp["VaRTicker"]
            factor_betas_fund = factor_betas.loc[
                factor_betas["ID"].isin(fund_positions)
            ]
            VaR95_inc = (
                exposure[:, None].T
                @ factor_betas_fund.values[:, 1:]
                @ matrix_cov.values[1:, 1:]
                @ factor_betas_fund.values[:, 1:].T
                @ exposure[:, None]
            ) ** (0.5)
            dict[name] = (
                (VaR95_total - (VaR95_inc[:, 0] *
                 1.644854)) / firm_NAV.values[:, None]
            )[0, :]
            # LOGGER.info(
            #     f"estimating  port VaR 95 of {name} as of date {date} within"
            #     f"filter {filter_item}"
            # )
        VaR95_inc_df = pd.DataFrame(dict).T
        VaR95_inc_df = pd.DataFrame(
            VaR95_inc_df.values,
            columns=[f"{filter_item}_Inc95"],
            index=VaR95_inc_df.index,
        )
        filter_VaR95_inc_df_list.append(VaR95_inc_df)

    return filter_VaR95_inc_df_list


def filter_VaR99_inc(
    filter: Dict,
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
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
    total_exposure = position_agg_exposure["Exposure"].values
    VaR99_total = (
        total_exposure[:, None].T
        @ factor_betas.values[:, 1:]
        @ matrix_cov.values[1:, 1:]
        @ factor_betas.values[:, 1:].T
        @ total_exposure[:, None]
    ) ** (0.5) * 2.326348
    filter_VaR99_inc_df_list = []  # contains all computed results across all filters
    filter_list = list(filter.keys())
    filter_list = ["VaRTicker"] + list(filter.keys())
    date = factor_prices.index[-1]
    for filter_item in filter_list:
        position_grouped = position.groupby([filter_item])
        dict = {}
        for name, group in tqdm(position_grouped, 'filter_VaR99_inc'):
            if isinstance(name, tuple):
                name = name[0]
            tmp = position.loc[position[filter_item] != name]
            tmp = (
                tmp.groupby(
                    [
                        "RFID",
                    ]
                )
                .agg({"VaRTicker": "first", "Exposure": "sum"})
                .reset_index()
            )
            exposure = tmp["Exposure"].values
            fund_positions = tmp["VaRTicker"]
            factor_betas_fund = factor_betas.loc[
                factor_betas["ID"].isin(fund_positions)
            ]
            VaR99_inc = (
                exposure[:, None].T
                @ factor_betas_fund.values[:, 1:]
                @ matrix_cov.values[1:, 1:]
                @ factor_betas_fund.values[:, 1:].T
                @ exposure[:, None]
            ) ** (0.5)
            dict[name] = (
                (VaR99_total - (VaR99_inc[:, 0] *
                 2.326348)) / firm_NAV.values[:, None]
            )[0, :]
            # LOGGER.info(
            #     f"estimating  port VaR 99 of {name} as of date {date} within"
            #     f"filter {filter_item}"
            # )
        VaR99_inc_df = pd.DataFrame(dict).T
        VaR99_inc_df = pd.DataFrame(
            VaR99_inc_df.values,
            columns=[f"{filter_item}_Inc99"],
            index=VaR99_inc_df.index,
        )
        filter_VaR99_inc_df_list.append(VaR99_inc_df)

    return filter_VaR99_inc_df_list


def filter_Var95_comp(
    filter: Dict,
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
    matrix_cov: pd.DataFrame,
    firm_NAV: float,
) -> List:
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
    filter_list = ["VaRTicker"] + list(filter.keys())
    date = factor_prices.index[-1]
    filter_VaR95_comp_df_list = []
    for filter_item in filter_list:
        position_grouped = position.groupby([filter_item])
        dict = {}
        for name, group in tqdm(position_grouped, 'filter_Var95_comp'):
            if isinstance(name, tuple):
                name = name[0]
            tmp = (
                group.groupby(
                    [
                        "RFID",
                    ]
                )
                .agg({"VaRTicker": "first", "Exposure": "sum"})
                .reset_index()
            )
            exposure = tmp["Exposure"].values
            fund_positions = tmp["VaRTicker"]
            factor_betas_fund = factor_betas.loc[
                factor_betas["ID"].isin(fund_positions)
            ]
            filter_mvar_95 = (
                matrix_cov.values[1:, 1:]
                @ factor_betas_fund.values[:, 1:].T
                @ exposure[:, None]
            ).sum()
            dict[name] = filter_mvar_95 / firm_NAV
            # LOGGER.info(
            #     f"estimating VaR 95 comp of {name} as of date {date} within"
            #     f"filter {filter_item}"
            # )

        VaR95_comp_df = pd.DataFrame(dict).T
        VaR95_comp_df = pd.DataFrame(
            VaR95_comp_df.values,
            columns=[f"{filter_item}_Comp95"],
            index=VaR95_comp_df.index,
        )
        filter_VaR95_comp_df_list.append(VaR95_comp_df)

    return filter_VaR95_comp_df_list


def filter_Var99_comp(
    filter: Dict,
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
    matrix_cov: pd.DataFrame,
    firm_NAV: float,
) -> List:
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
    filter_list = ["VaRTicker"] + list(filter.keys())
    date = factor_prices.index[-1]
    filter_VaR99_comp_df_list = []
    for filter_item in filter_list:
        position_grouped = position.groupby([filter_item])
        dict = {}
        for name, group in tqdm(position_grouped, 'filter_Var99_comp'):
            if isinstance(name, tuple):
                name = name[0]
            tmp = (
                group.groupby(
                    [
                        "RFID",
                    ]
                )
                .agg({"VaRTicker": "first", "Exposure": "sum"})
                .reset_index()
            )
            exposure = tmp["Exposure"].values
            fund_positions = tmp["VaRTicker"]
            factor_betas_fund = factor_betas.loc[
                factor_betas["ID"].isin(fund_positions)
            ]
            filter_mvar_99 = (
                matrix_cov.values[1:, 1:]
                @ factor_betas_fund.values[:, 1:].T
                @ exposure[:, None]
            ).sum()
            dict[name] = filter_mvar_99 / firm_NAV
            # LOGGER.info(
            #     f"estimating VaR 99 comp of {name} as of date {date} within"
            #     f"filter {filter_item}"
            # )

        VaR99_comp_df = pd.DataFrame(dict).T
        VaR99_comp_df = pd.DataFrame(
            VaR99_comp_df.values,
            columns=[f"{filter_item}_Comp99"],
            index=VaR99_comp_df.index,
        )
        filter_VaR99_comp_df_list.append(VaR99_comp_df)

    return filter_VaR99_comp_df_list


def var_structuring(
    var95_filtered_iso: List,
    VaR99_filtered_iso: List,
    var95_filtered_inc: List,
    VaR99_filtered_inc: List,
    VaR95_filtered_comp: List,
    VaR99_filtered_comp: List,
    position: pd.DataFrame,
) -> pd.DataFrame:
    # go through all Lists and pull out the FundVaR stats, SectorVaR stats,
    # IndustryVaR stats,CountryVaR stats, MktCap VaR stats into their respective places
    position_list = []
    fund_list = []
    sector_list = []
    industry_list = []
    country_list = []
    mktcap_list = []
    for ix in range(0, len(var95_filtered_iso)):
        df = var95_filtered_iso[ix]
        (
            position_list,
            fund_list,
            sector_list,
            industry_list,
            country_list,
            mktcap_list,
        ) = filter_var_grouping(
            df,
            position_list,
            fund_list,
            sector_list,
            industry_list,
            country_list,
            mktcap_list,
        )
    for ix in range(0, len(VaR99_filtered_iso)):
        df = VaR99_filtered_iso[ix]
        (
            position_list,
            fund_list,
            sector_list,
            industry_list,
            country_list,
            mktcap_list,
        ) = filter_var_grouping(
            df,
            position_list,
            fund_list,
            sector_list,
            industry_list,
            country_list,
            mktcap_list,
        )
    for ix in range(0, len(var95_filtered_inc)):
        df = var95_filtered_inc[ix]
        (
            position_list,
            fund_list,
            sector_list,
            industry_list,
            country_list,
            mktcap_list,
        ) = filter_var_grouping(
            df,
            position_list,
            fund_list,
            sector_list,
            industry_list,
            country_list,
            mktcap_list,
        )
    for ix in range(0, len(VaR99_filtered_inc)):
        df = VaR99_filtered_inc[ix]
        (
            position_list,
            fund_list,
            sector_list,
            industry_list,
            country_list,
            mktcap_list,
        ) = filter_var_grouping(
            df,
            position_list,
            fund_list,
            sector_list,
            industry_list,
            country_list,
            mktcap_list,
        )
    for ix in range(0, len(VaR95_filtered_comp)):
        df = VaR95_filtered_comp[ix]
        (
            position_list,
            fund_list,
            sector_list,
            industry_list,
            country_list,
            mktcap_list,
        ) = filter_var_grouping(
            df,
            position_list,
            fund_list,
            sector_list,
            industry_list,
            country_list,
            mktcap_list,
        )
    for ix in range(0, len(VaR99_filtered_comp)):
        df = VaR99_filtered_comp[ix]
        (
            position_list,
            fund_list,
            sector_list,
            industry_list,
            country_list,
            mktcap_list,
        ) = filter_var_grouping(
            df,
            position_list,
            fund_list,
            sector_list,
            industry_list,
            country_list,
            mktcap_list,
        )

    VaR_position_df = pd.concat(position_list, axis=1)
    VaR_position_df.reset_index(inplace=True)
    VaR_position_df.rename(columns={"index": "VaRTicker"}, inplace=True)
    VaR_position_df = pd.merge(
        VaR_position_df,
        position[["VaRTicker", "UnderlierName"]],
        on=["VaRTicker"],
        how="inner",
    )
    VaR_position_df = VaR_position_df.drop_duplicates(keep="first")
    cols = [col for col in VaR_position_df.columns if col != "VaRTicker"]
    VaR_position_df = VaR_position_df[cols]
    VaR_position_df = VaR_position_df.sort_values(
        ["VaRTicker_Iso95"], ascending=False)
    VaR_position_df.columns = VaR_position_df.columns.str.replace(
        "VaRTicker_", "")
    VaR_position_top10 = VaR_position_df.iloc[:10]
    VaR_position_bottom10 = VaR_position_df.iloc[-10:]
    VaR_position_top10.rename(
        columns={"UnderlierName": "Top10 VaR Contributors"}, inplace=True
    )
    VaR_position_top10.set_index(["Top10 VaR Contributors"], inplace=True)
    VaR_position_bottom10.rename(
        columns={"UnderlierName": "Top10 VaR Diversifiers"}, inplace=True
    )
    VaR_position_bottom10.set_index(["Top10 VaR Diversifiers"], inplace=True)
    VaR_fund_df = pd.concat(fund_list, axis=1)
    VaR_fund_df.reset_index(inplace=True)
    VaR_fund_df.rename(columns={"index": "Strat VaR"}, inplace=True)
    VaR_fund_df.set_index(["Strat VaR"], inplace=True)
    VaR_fund_df.columns = VaR_fund_df.columns.str.replace("FundName_", "")
    VaR_sector_df = pd.concat(sector_list, axis=1)
    VaR_sector_df.reset_index(inplace=True)
    VaR_sector_df.rename(columns={"index": "Sector VaR"}, inplace=True)
    VaR_sector_df.set_index(["Sector VaR"], inplace=True)
    VaR_sector_df.columns = VaR_sector_df.columns.str.replace("Sector_", "")
    VaR_industry_df = pd.concat(industry_list, axis=1)
    VaR_industry_df.reset_index(inplace=True)
    VaR_industry_df.rename(columns={"index": "Industry VaR"}, inplace=True)
    VaR_industry_df.set_index(["Industry VaR"], inplace=True)
    VaR_industry_df.columns = VaR_industry_df.columns.str.replace(
        "Industry_", "")
    VaR_country_df = pd.concat(country_list, axis=1)
    VaR_country_df.reset_index(inplace=True)
    VaR_country_df.rename(columns={"index": "Country VaR"}, inplace=True)
    VaR_country_df.set_index(["Country VaR"], inplace=True)
    VaR_country_df.columns = VaR_country_df.columns.str.replace("Country_", "")
    VaR_mktcap_df = pd.concat(mktcap_list, axis=1)
    VaR_mktcap_df.reset_index(inplace=True)
    VaR_mktcap_df.rename(columns={"index": "MarketCap VaR"}, inplace=True)
    VaR_mktcap_df.set_index(["MarketCap VaR"], inplace=True)
    VaR_mktcap_df.columns = VaR_mktcap_df.columns.str.replace(
        "MarketCap.1_", "")

    return (
        VaR_position_top10,
        VaR_position_bottom10,
        VaR_fund_df,
        VaR_sector_df,
        VaR_industry_df,
        VaR_country_df,
        VaR_mktcap_df,
    )


def filter_stress_test_price_vol(
    filter: Dict,
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    price_vol_shock_range: Dict,
):
    price_shock_list = price_vol_shock_range["price_shock"]
    vol_shock_list = price_vol_shock_range["vol_shock"]
    shock_params_list = []
    for a, b in product(
        price_shock_list,
        vol_shock_list,
    ):
        params = {"price_shock": a, "vol_shock": b}
        shock_params_list.append(params)
    filter_list = list(filter.keys())
    stress_test_price_vol_dict = {}
    stress_test_price_vol_exposure_dict = {}
    for filter_item in filter_list:
        position_grouped = position.groupby([filter_item])
        for filter_name, filter_group in tqdm(
            position_grouped,
            f'Stress test price for group: {filter_item}',
        ):
            if isinstance(filter_name, tuple):
                filter_name = filter_name[0]
            for shock in shock_params_list:
                shock_pnl = 0
                price_shock = shock["price_shock"]
                vol_shock = shock["vol_shock"]
                position_non_option = filter_group.loc[
                    filter_group["SECURITY_TYP"].str.contains(
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
                if not position_non_option.empty:
                    position_non_option["shock_value"] = (
                        position_non_option["Quantity"].astype(float)
                        * position_non_option["FXRate"]
                        * position_non_option["MarketPrice"]
                        * position_non_option["PX_POS_MULT_FACTOR"]
                        * (1 + price_shock)
                    )
                    position_non_option["shock_pnl"] = (
                        position_non_option["shock_value"]
                    ) - (
                        position_non_option["Quantity"].astype(float)
                        * position_non_option["FXRate"]
                        * position_non_option["MarketPrice"]
                        * position_non_option["PX_POS_MULT_FACTOR"]
                    )
                    position_non_option["shock_exposure"] = (
                        position_non_option["shock_value"]
                        - position_non_option["Exposure"]
                    )
                    shock_pnl += position_non_option["shock_pnl"].sum()
                    shock_exposure = position_non_option["shock_exposure"].sum(
                    )
                position_option = filter_group.loc[
                    filter_group["SECURITY_TYP"].str.contains(
                        "|".join(["call", "option", "put"]),
                        na=False,
                        case=False,
                    )
                ]
                if not position_option.empty:
                    position_option["shock_underlying_price"] = position_option[
                        "UndlPrice"
                    ] * (1 + price_shock)
                    position_option["shock_implied_vol"] = position_option[
                        "IVOL_TM"
                    ].astype(float) * (1 + vol_shock)
                    position_option["shock_option_price"] = option_price(
                        S=position_option["shock_underlying_price"],
                        X=position_option["Strike"],
                        T=position_option["MtyYears"],
                        Vol=position_option["shock_implied_vol"].astype(float),
                        rf=RISK_FREE_RATE,
                        type=position_option["PutCall"],
                    )
                    position_option["shock_value"] = (
                        position_option["shock_option_price"]
                        * position_option["PX_POS_MULT_FACTOR"]
                        * position_option["Quantity"].astype(float)
                        * position_option["FXRate"]
                    )
                    position_option["shock_exposure"] = (
                        position_option["shock_value"] -
                        position_option["Exposure"]
                    )
                    position_option["shock_pnl"] = (position_option["shock_value"]) - (
                        position_option["MarketPrice"]
                        * position_option["PX_POS_MULT_FACTOR"]
                        * position_option["Quantity"].astype(float)
                        * position_option["FXRate"]
                    )
                    shock_pnl += position_option["shock_pnl"].sum()
                    shock_exposure = position_option["shock_exposure"].sum()
                stress_test_price_vol_dict[
                    f"{filter_name}_price_shock_{price_shock}_vol_shock_{vol_shock}"
                ] = shock_pnl
                stress_test_price_vol_exposure_dict[
                    f"{filter_name}_price_shock_{price_shock}_vol_shock_{vol_shock}"
                ] = shock_exposure
        # LOGGER.info(
        #     f"stress test results for price shock for group {filter_name} ")

        stress_test_price_vol_df = pd.DataFrame(
            stress_test_price_vol_dict, index=["stress_pnl & vol shock"]
        ).T
        date_vector = pd.DataFrame(
            np.repeat(factor_prices.index[-1], len(stress_test_price_vol_df)),
            index=stress_test_price_vol_df.index,
        )
        stress_test_price_vol_df = pd.concat(
            [date_vector, stress_test_price_vol_df], axis=1
        )
        stress_test_price_vol_exposure_df = pd.DataFrame(
            stress_test_price_vol_exposure_dict, index=[
                "stress_exposure & vol shock"]
        ).T
        date_vector = pd.DataFrame(
            np.repeat(factor_prices.index[-1],
                      len(stress_test_price_vol_exposure_df)),
            index=stress_test_price_vol_exposure_df.index,
            columns=[factor_prices.index[-1]],
        )
        stress_test_price_vol_exposure_df = pd.concat(
            [date_vector, stress_test_price_vol_exposure_df], axis=1
        )

    return stress_test_price_vol_df, stress_test_price_vol_exposure_df


def filter_stress_test_beta_price_vol(
    filter: Dict,
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
    price_vol_shock_range: Dict,
):
    equity_mkt_beta = factor_betas[["ID", "SPX Index"]]
    equity_mkt_beta.rename(columns={"ID": "VaRTicker"}, inplace=True)
    price_shock_list = price_vol_shock_range["price_shock"]
    vol_shock_list = price_vol_shock_range["vol_shock"]
    shock_params_list = []
    for a, b in product(
        price_shock_list,
        vol_shock_list,
    ):
        params = {"price_shock": a, "vol_shock": b}
        shock_params_list.append(params)
    filter_list = list(filter.keys())
    stress_test_beta_price_vol_dict = {}
    for filter_item in filter_list:
        position_grouped = position.groupby([filter_item])
        for filter_name, filter_group in tqdm(
            position_grouped,
            f'Stress test beta for group: {filter_item}'
        ):
            if isinstance(filter_name, tuple):
                filter_name = filter_name[0]
            for shock in shock_params_list:
                shock_pnl = 0
                price_shock = shock["price_shock"]
                vol_shock = shock["vol_shock"]
                position_non_option = filter_group.loc[
                    filter_group["SECURITY_TYP"].str.contains(
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
                position_non_option["TradeDate"] = pd.to_datetime(
                    position_non_option["TradeDate"]
                )
                position_non_option.set_index(["TradeDate"], inplace=True)
                if not position_non_option.empty:
                    equity_mkt_beta_group = pd.merge(
                        position_non_option[["VaRTicker"]],
                        equity_mkt_beta,
                        on=["VaRTicker"],
                        how="left",
                    )
                    equity_mkt_beta_group = equity_mkt_beta_group["SPX Index"]
                    beta_price_shock = equity_mkt_beta_group.values * price_shock
                    position_non_option["shock_value"] = (
                        position_non_option["Quantity"].astype(float)
                        * position_non_option["FXRate"]
                        * position_non_option["MarketPrice"]
                        * position_non_option["PX_POS_MULT_FACTOR"]
                        * (1 + beta_price_shock)
                    )
                    position_non_option["shock_pnl"] = (
                        position_non_option["shock_value"]
                    ) - (
                        position_non_option["Quantity"].astype(float)
                        * position_non_option["FXRate"]
                        * position_non_option["MarketPrice"]
                        * position_non_option["PX_POS_MULT_FACTOR"]
                    )
                    shock_pnl += position_non_option["shock_pnl"].sum()
                position_option = filter_group.loc[
                    filter_group["SECURITY_TYP"].str.contains(
                        "|".join(["call", "option", "put"]),
                        na=False,
                        case=False,
                    )
                ]
                position_option["TradeDate"] = pd.to_datetime(
                    position_option["TradeDate"]
                )
                position_option.set_index(["TradeDate"], inplace=True)
                if not position_option.empty:
                    equity_mkt_beta_group = pd.merge(
                        position_option[["VaRTicker"]],
                        equity_mkt_beta,
                        on=["VaRTicker"],
                        how="left",
                    )
                    equity_mkt_beta_group = equity_mkt_beta_group["SPX Index"]
                    beta_price_shock = equity_mkt_beta_group.values * price_shock
                    position_option["shock_underlying_price"] = position_option[
                        "UndlPrice"
                    ] * (1 + beta_price_shock)
                    position_option["shock_implied_vol"] = position_option[
                        "IVOL_TM"
                    ].astype(float) * (1 + vol_shock)
                    position_option["shock_option_price"] = option_price(
                        S=position_option["shock_underlying_price"],
                        X=position_option["Strike"],
                        T=position_option["MtyYears"],
                        Vol=position_option["shock_implied_vol"].astype(float),
                        rf=RISK_FREE_RATE,
                        type=position_option["PutCall"],
                    )
                    position_option["shock_value"] = (
                        position_option["shock_option_price"]
                        * position_option["PX_POS_MULT_FACTOR"]
                        * position_option["Quantity"].astype(float)
                        * position_option["FXRate"]
                    )
                    position_option["shock_pnl"] = (position_option["shock_value"]) - (
                        position_option["MarketPrice"]
                        * position_option["PX_POS_MULT_FACTOR"]
                        * position_option["Quantity"].astype(float)
                        * position_option["FXRate"]
                    )
                    shock_pnl += position_option["shock_pnl"].sum()
                stress_test_beta_price_vol_dict[
                    f"{filter_name}_price_shock_" f"{price_shock}_vol_shock_{vol_shock}"
                ] = shock_pnl
            # LOGGER.info(
            #     f"stress test results for beta * price shock for group {filter_name} "
            # )

        stress_test_beta_price_vol_df = pd.DataFrame(
            stress_test_beta_price_vol_dict, index=[
                "stress_pnl_beta*price & vol shock"]
        ).T
        date_vector = pd.DataFrame(
            np.repeat(factor_prices.index[-1],
                      len(stress_test_beta_price_vol_df)),
            index=stress_test_beta_price_vol_df.index,
            columns=[factor_prices.index[-1]],
        )
        stress_test_beta_price_vol_df = pd.concat(
            [date_vector, stress_test_beta_price_vol_df], axis=1
        )

    return stress_test_beta_price_vol_df


def stress_test_structuring(
    stress_test_df: pd.DataFrame, position: pd.DataFrame, price_vol_shock_range: Dict
):
    position_grouped = position.groupby(["FundName"])
    fund_list = list(position_grouped.groups.keys())
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
    # convert stress_test_df to % from $ space
    col = stress_test_df.filter(like="stress_").columns
    stress_test_df = stress_test_df[col] / \
        position_agg_exposure["MarketValue"].sum()
    price_shock_list = price_vol_shock_range["price_shock"]
    vol_shock_list = price_vol_shock_range["vol_shock"]
    shock_params_list = []
    for a, b in product(
        price_shock_list,
        vol_shock_list,
    ):
        params = {"price_shock": f"price_shock_{a}",
                  "vol_shock": f"vol_shock_{b}"}
        shock_params_list.append(params)

    dict = {}
    for shock in shock_params_list:
        price_shock = shock["price_shock"]
        vol_shock = shock["vol_shock"]
        combined_shock_string = f"{price_shock}_{vol_shock}"
        stress_shock_filter = stress_test_df.loc[
            stress_test_df.index.str.contains(combined_shock_string)
        ]
        stress_shock_filter = stress_shock_filter[
            stress_shock_filter.index.str.contains("|".join(fund_list))
        ]
        dict[combined_shock_string] = stress_shock_filter.sum()
    stress_test_arr = np.array(list(dict.values()))
    stress_test_arr = np.reshape(
        stress_test_arr, (int(np.sqrt(len(dict))), int(np.sqrt(len(dict))))
    ).T
    LOGGER.info("convert results into summary tbl")
    stress_test_results_df = pd.DataFrame(
        stress_test_arr, index=list(reversed(vol_shock_list)), columns=price_shock_list
    )

    return stress_test_results_df
