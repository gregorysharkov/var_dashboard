# pylint: disable=E501,W0621,C0114,C0301
import logging
from itertools import product
from typing import Dict

import numpy as np
import pandas as pd
from tqdm import tqdm

from src.legacy.helper import option_price

pd.set_option("mode.chained_assignment", None)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RISK_FREE_RATE = 5.5e-2  # as of Aug 2023

AGGREGATIONS = {
    "TradeDate": "first",
    "Strat": "first",
    "UnderlierName": "first",
    "VaRTicker": "first",
    "MarketValue": "sum",
    "Exposure": "sum",
}

GROUP_AGGREGATIONS = {"VaRTicker": "first", "Exposure": "sum"}

QUANTILES = {
    '95': 1.644854,
    '99': 2.326348,
}


SECURITY_TYPES = [
    "fixed", "future", "public", "prefer",
    "common", "reit", "fund", "mlp", "adr",
]


def filter_stress_test_price_vol(
    filter_dict: Dict,
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    price_vol_shock_range: Dict,
):
    '''add docstring'''
    price_shock_list = price_vol_shock_range["price_shock"]
    vol_shock_list = price_vol_shock_range["vol_shock"]
    shock_params_list = []
    for a, b in product(
        price_shock_list,
        vol_shock_list,
    ):
        params = {"price_shock": a, "vol_shock": b}
        shock_params_list.append(params)
    filter_list = list(filter_dict.keys())
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
                        "|".join(SECURITY_TYPES),
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
    '''docstring goes here'''
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
        position_grouped = position.groupby(filter.get(filter_item))
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
                        "|".join(SECURITY_TYPES),
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
    stress_test_df: pd.DataFrame,
    position: pd.DataFrame,
    price_vol_shock_range: Dict
):
    '''dosctring goes here...'''
    position_grouped = position.groupby(["Strat"])
    fund_list = list(position_grouped.groups.keys())
    # agg positions by exposure across fund strats
    position_agg_exposure = (
        position.groupby('RFID')
        .agg(AGGREGATIONS)
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

    some_dict = {}
    for shock in shock_params_list:
        price_shock = shock["price_shock"]
        vol_shock = shock["vol_shock"]
        combined_shock_string = f"{price_shock}_{vol_shock}"
        stress_shock_filter = stress_test_df.loc[
            stress_test_df.index.str.contains(combined_shock_string)
        ]
        stress_shock_filter = stress_shock_filter[
            stress_shock_filter.index.str.contains(
                "|".join(fund_list))  # type: ignore
        ]
        some_dict[combined_shock_string] = stress_shock_filter.sum()
    stress_test_arr = np.array(list(some_dict.values()))
    stress_test_arr = np.reshape(
        stress_test_arr,
        (
            int(np.sqrt(len(some_dict))),  # type: ignore
            int(np.sqrt(len(some_dict)))  # type: ignore
        )
    ).T
    logger.info("convert results into summary tbl")
    stress_test_results_df = pd.DataFrame(
        stress_test_arr,
        index=list(reversed(vol_shock_list)),
        columns=price_shock_list
    )

    return stress_test_results_df
