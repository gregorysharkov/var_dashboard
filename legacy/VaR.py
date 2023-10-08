import logging
from functools import reduce
from itertools import product
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from tqdm import tqdm

import legacy.Factors as fac
import legacy.var_utils as var_utils
from legacy.helper import option_price

pd.set_option("mode.chained_assignment", None)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

RISK_FREE_RATE = 5.5e-2  # as of Aug 2023

COLUMN_TO_GROUP_MAPPING = {
    'position': 'VaRTicker',
    'fund': 'FundName',
    'sector': 'Sector',
    'industry': 'Industry',
    'country': 'Country',
    'mktcap': 'MarketCap',
}

AGGREGATIONS = {
    "TradeDate": "first",
    "FundName": "first",
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


def group_var_report_data_by_type(
    data_group: List[pd.DataFrame],
    groupped_data: Dict,
) -> Dict[str, List[pd.DataFrame]]:
    '''groups VaR data by position, fund, sector, industry, country, mktcap'''

    for data in data_group:
        for group_name, keyword in COLUMN_TO_GROUP_MAPPING.items():
            if data.columns.str.contains(keyword):
                groupped_data[group_name].append(data)

    return groupped_data


# def generate_factor_returns(factor_prices: pd.DataFrame) -> pd.DataFrame:
#     '''
#     generates factor returns from factor prices
#     it is a logarithm of ratio between todays and tomorrow's prices
#     when we do a shift, the first line is NaN, so we need to remove it
#     '''

#     factor_returns = np.log(
#         factor_prices / factor_prices.shift(1))  # type: ignore
#     return factor_returns.iloc[1:, :]  # type: ignore

def filter_var_ticker_group(
    position_returns: pd.DataFrame,
    factor_returns: pd.DataFrame,
    matrix_cov: pd.DataFrame,
    firm_nav: float,
    quantiles: List[str],
    filter_items: Dict[str, str],
) -> Dict[str, pd.DataFrame]:
    '''
    wraper for filter_var
    calculates var for a given group and returns
    a list of dataframes containing var for each group
    and each quantiles

    Args:
        position: pd.DataFrame. Contains positions
        factor_betas: pd.DataFrame, contains factor betas
        matrix_cov: pd.DataFrame, contains covariance matrix
        firm_nav: float, Net Asset Value for a given firm
        quantiles: List[str], list of quantiles to be calculated
        filter_items: Dict[str, str], a dictionary that maps a group
            to a name of the column in the positions dataframe

    Returns:
        dictionary of dataframes:
            key: string name of the grouping
            value: dataframe with calculated vars
    '''

    return_dict = {}
    for group_name, column_name in filter_items.items():
        logger.info('Calculating VaR for %s', group_name)
        group_var = filter_var(
            factor_returns=factor_returns,
            position_returns=position_returns,
            matrix_cov=matrix_cov,
            firm_nav=firm_nav,
            quantiles=quantiles,
            filter_item=column_name,
        )
        return_dict[group_name] = group_var
        logger.info('Done calculating VaR for %s', group_name)
    return return_dict


def filter_var(
    factor_returns: pd.DataFrame,
    position_returns: pd.DataFrame,
    matrix_cov: pd.DataFrame,
    firm_nav: float,
    quantiles: List[str],
    filter_item: str = "VaRTicker",
) -> pd.DataFrame:
    '''
    calculates var exposure per position given a list of quantities

    Args:
        factor_returns: contains returns per market symbol
        position_returns: contains returns per position
        matrix_cov: contains covariance matrix
        firm_nav: float, Net Asset Value for a given firm
        quantiles: List[str], list of quantiles to be calculated
        filter_item: string, name of the column in the positions dataframe

    Returns:
        combined dataframe where given quantiles of var are calculated
        per each group (filter_item)
    '''

    alfa_quantiles = [QUANTILES.get(quantile) for quantile in quantiles]

    group_exposure = calculate_group_exposure(
        factor_returns, position_returns, matrix_cov, filter_item
    )

    var_exposures = []
    for alfa, quantile, in zip(alfa_quantiles, quantiles):
        var_exposure = calculate_exposure(
            firm_nav=firm_nav,
            filter_item=filter_item,
            group_exposure=group_exposure,
            alfa=alfa,  # type: ignore
            quantile=quantile
        )
        var_exposures.append(var_exposure)

    combined_exposures = reduce(lambda x, y: x.join(y), var_exposures)
    return combined_exposures


def calculate_group_exposure(
    factor_returns: pd.DataFrame,
    position_returns: pd.DataFrame,
    matrix_cov: pd.DataFrame,
    group_column: str,
) -> pd.DataFrame:
    '''
    function calculates exposure for a given group

    Args:
        factor_returns. Returns calculated asset wise.
            For each market symbol. Wide format
        position_returns: Returns calculated position-wise.
            Per each position at trading date
        matrix_cov: Covariance matrix of factor returns between them
            n x n matrix. each column is a market symbol

    Returns:
        a var exposure adjusted by betas and covariance matrix for each group
    '''

    group_returns = position_returns\
        .groupby(['TradeDate', group_column])\
        .agg({
            'return': 'sum',
        })\
        .unstack(level=1)\
        .reset_index()\
        .rename(columns={'TradeDate': 'date'})\
        .set_index('date')

    group_exposure = position_returns\
        .groupby(group_column)\
        .agg({"Exposure": "sum"})

    group_betas = fac.calculate_position_betas(group_returns, factor_returns)

    exposure = var_utils.multiply_matrices(
        matrix_cov=matrix_cov,
        exposure=group_exposure,
        factor_betas=group_betas,
    )

    return exposure


def calculate_exposure(
    firm_nav: float,
    filter_item: str,
    group_exposure: pd.DataFrame,
    alfa: float,
    quantile: str,
) -> pd.DataFrame:
    '''calculates var exposure for given filter item and the given quantile'''

    var_exposure = group_exposure * alfa / firm_nav
    var_exposure.reset_index(inplace=True)
    var_exposure.rename(
        columns={
            'Exposure': f'position_VaR{quantile}',
            'position': 'UnderlierName'
            if filter_item == 'VaRTicker' else filter_item,
        },
        inplace=True
    )
    var_exposure.set_index('UnderlierName', inplace=True)
    return var_exposure


def filter_var95_iso(
    filter: Dict,
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
    matrix_cov: pd.DataFrame,
    firm_NAV: float,
) -> pd.DataFrame:
    print(filter)
    # agg positions by exposure across fund strats
    filter_VaR95_iso_df_list = []  # contains all compuuted results across all filters
    filter_list = ["VaRTicker"] + list(filter.keys())
    for filter_item in filter_list:
        position_grouped = position.groupby([filter_item])
        dict = {}
        for name, group in tqdm(position_grouped, 'filter_VaR95_iso'):
            if isinstance(name, tuple):
                name = name[0]
            tmp = aggregate_by_rfid(group)
            exposure = tmp["Exposure"].values
            fund_positions = tmp["VaRTicker"]
            factor_betas_fund = factor_betas.loc[
                factor_betas["ID"].isin(fund_positions)
            ]
            VaR95_iso = multiply_matrices(
                matrix_cov, exposure, factor_betas_fund)
            dict[name] = (VaR95_iso[:, 0] * 1.644854) / firm_NAV
        VaR95_iso_df = pd.DataFrame(dict).T
        VaR95_iso_df = pd.DataFrame(
            VaR95_iso_df.values,
            columns=[f"{filter_item}_Iso95"],
            index=VaR95_iso_df.index,
        )
        filter_VaR95_iso_df_list.append(VaR95_iso_df)

    return filter_VaR95_iso_df_list


def filter_var99_iso(
    filter: Dict,
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
    matrix_cov: pd.DataFrame,
    firm_NAV: float,
) -> pd.DataFrame:
    filter_VaR99_iso_df_list = []  # contains all compuuted results across all filters
    filter_list = list(filter.keys())
    filter_list = ["VaRTicker"] + list(filter.keys())
    for filter_item in filter_list:
        position_grouped = position.groupby([filter_item])
        dict = {}
        for name, group in tqdm(position_grouped, 'filter_VaR99_iso'):
            if isinstance(name, tuple):
                name = name[0]
            tmp = aggregate_by_rfid(group)
            exposure = tmp["Exposure"].values
            fund_positions = tmp["VaRTicker"]
            factor_betas_fund = factor_betas.loc[
                factor_betas["ID"].isin(fund_positions)
            ]
            VaR99_iso = multiply_matrices(
                matrix_cov, exposure, factor_betas_fund)
            dict[name] = (VaR99_iso[:, 0] * 2.326348) / firm_NAV
        VaR99_iso_df = pd.DataFrame(dict).T
        VaR99_iso_df = pd.DataFrame(
            VaR99_iso_df.values,
            columns=[f"{filter_item}_Iso99"],
            index=VaR99_iso_df.index,
        )
        filter_VaR99_iso_df_list.append(VaR99_iso_df)

    return filter_VaR99_iso_df_list


def filter_var95_inc(
    filter: Dict,
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
    matrix_cov: pd.DataFrame,
    firm_NAV: float,
) -> pd.DataFrame:
    # agg positions by exposure across fund strats
    position_agg_exposure = (
        position.groupby('RFID')
        .agg(AGGREGATIONS)
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
    for filter_item in filter_list:
        position_grouped = position.groupby([filter_item])
        dict = {}
        for name, group in tqdm(position_grouped, 'filter_VaR95_inc'):
            if isinstance(name, tuple):
                name = name[0]
            tmp = position.loc[position[filter_item] != name]
            # TODO: ATTENTION this is different compared to previous
            tmp = aggregate_by_rfid(tmp)
            exposure = tmp["Exposure"].values
            fund_positions = tmp["VaRTicker"]
            factor_betas_fund = factor_betas.loc[
                factor_betas["ID"].isin(fund_positions)
            ]
            VaR95_inc = multiply_matrices(
                matrix_cov, exposure, factor_betas_fund)
            dict[name] = (
                (VaR95_total - (VaR95_inc[:, 0] *
                 1.644854)) / firm_NAV.values[:, None]
            )[0, :]
        VaR95_inc_df = pd.DataFrame(dict).T
        VaR95_inc_df = pd.DataFrame(
            VaR95_inc_df.values,
            columns=[f"{filter_item}_Inc95"],
            index=VaR95_inc_df.index,
        )
        filter_VaR95_inc_df_list.append(VaR95_inc_df)

    return filter_VaR95_inc_df_list


def filter_var99_inc(
    filter: Dict,
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
    matrix_cov: pd.DataFrame,
    firm_NAV: float,
) -> pd.DataFrame:
    # agg positions by exposure across fund strats
    position_agg_exposure = (
        position.groupby('RFID')
        .agg(AGGREGATIONS)
        .reset_index()
    )
    total_exposure = position_agg_exposure["Exposure"].values
    VaR99_total = multiply_matrices(
        matrix_cov, total_exposure, factor_betas) * 2.326348
    filter_VaR99_inc_df_list = []  # contains all computed results across all filters
    filter_list = list(filter.keys())
    filter_list = ["VaRTicker"] + list(filter.keys())
    for filter_item in filter_list:
        position_grouped = position.groupby([filter_item])
        dict = {}
        for name, group in tqdm(position_grouped, 'filter_VaR99_inc'):
            if isinstance(name, tuple):
                name = name[0]
            tmp = position.loc[position[filter_item] != name]
            tmp = aggregate_by_rfid(tmp)
            exposure = tmp["Exposure"].values
            fund_positions = tmp["VaRTicker"]
            factor_betas_fund = factor_betas.loc[
                factor_betas["ID"].isin(fund_positions)
            ]
            VaR99_inc = multiply_matrices(
                matrix_cov, exposure, factor_betas_fund)
            dict[name] = (
                (VaR99_total - (VaR99_inc[:, 0] *
                 2.326348)) / firm_NAV.values[:, None]
            )[0, :]
        VaR99_inc_df = pd.DataFrame(dict).T
        VaR99_inc_df = pd.DataFrame(
            VaR99_inc_df.values,
            columns=[f"{filter_item}_Inc99"],
            index=VaR99_inc_df.index,
        )
        filter_VaR99_inc_df_list.append(VaR99_inc_df)

    return filter_VaR99_inc_df_list


def filter_var95_comp(
    filter: Dict,
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
    matrix_cov: pd.DataFrame,
    firm_NAV: float,
) -> List:
    filter_list = list(filter.keys())
    filter_list = ["VaRTicker"] + list(filter.keys())
    filter_VaR95_comp_df_list = []
    for filter_item in filter_list:
        position_grouped = position.groupby([filter_item])
        dict = {}
        for name, group in tqdm(position_grouped, 'filter_Var95_comp'):
            if isinstance(name, tuple):
                name = name[0]
            tmp = group_by_rf_id(group)
            exposure = tmp["Exposure"].values
            fund_positions = tmp["VaRTicker"]
            factor_betas_fund = factor_betas.loc[
                factor_betas["ID"].isin(fund_positions)
            ]
            filter_mvar_95 = calculate_mvar(
                matrix_cov, exposure, factor_betas_fund)
            dict[name] = filter_mvar_95 / firm_NAV

        VaR95_comp_df = pd.DataFrame(dict).T
        VaR95_comp_df = pd.DataFrame(
            VaR95_comp_df.values,
            columns=[f"{filter_item}_Comp95"],
            index=VaR95_comp_df.index,
        )
        filter_VaR95_comp_df_list.append(VaR95_comp_df)

    return filter_VaR95_comp_df_list


def filter_var99_comp(
    filter: Dict,
    factor_prices: pd.DataFrame,
    position: pd.DataFrame,
    factor_betas: pd.DataFrame,
    matrix_cov: pd.DataFrame,
    firm_NAV: float,
) -> List:
    # agg positions by exposure across fund strats
    position_agg_exposure = (
        position.groupby('RFID')
        .agg(AGGREGATIONS)
        .reset_index()
    )
    filter_list = list(filter.keys())
    filter_list = ["VaRTicker"] + list(filter.keys())
    filter_VaR99_comp_df_list = []
    for filter_item in filter_list:
        position_grouped = position.groupby([filter_item])
        dict = {}
        for name, group in tqdm(position_grouped, 'filter_Var99_comp'):
            if isinstance(name, tuple):
                name = name[0]
            tmp = group_by_rf_id(group)
            exposure = tmp["Exposure"].values
            fund_positions = tmp["VaRTicker"]
            factor_betas_fund = factor_betas.loc[
                factor_betas["ID"].isin(fund_positions)
            ]
            filter_mvar_99 = calculate_mvar(
                matrix_cov, exposure, factor_betas_fund)
            dict[name] = filter_mvar_99 / firm_NAV

        VaR99_comp_df = pd.DataFrame(dict).T
        VaR99_comp_df = pd.DataFrame(
            VaR99_comp_df.values,
            columns=[f"{filter_item}_Comp99"],
            index=VaR99_comp_df.index,
        )
        filter_VaR99_comp_df_list.append(VaR99_comp_df)

    return filter_VaR99_comp_df_list


def calculate_mvar(matrix_cov, exposure, factor_betas_fund):
    '''calculates marginal VaR'''

    return (
        matrix_cov.values[1:, 1:]
        @ factor_betas_fund.values[:, 1:].T
        @ exposure[:, None]
    ).sum()


def generate_var_reports(
    var_reports: List[List[pd.DataFrame]],
    # position: pd.DataFrame,
) -> Tuple[
    pd.DataFrame, pd.DataFrame, pd.DataFrame,
    pd.DataFrame, pd.DataFrame, pd.DataFrame,
    pd.DataFrame
]:

    # go through all Lists and pull out the FundVaR stats, SectorVaR stats,
    # IndustryVaR stats,CountryVaR stats, MktCap VaR stats into their
    # respective places
    groupped_data = {
        'position': [],  # List[pd.DataFrame],
        'fund': [],  # List[pd.DataFrame],
        'sector': [],  # List[pd.DataFrame],
        'industry': [],  # List[pd.DataFrame],
        'country': [],  # List[pd.DataFrame],
        'mktcap': [],  # List[pd.DataFrame],
    }

    assert len(var_reports) == len(groupped_data.keys())
    # for each dataframe group defined in var_reports iterate through each group
    # collect columns that correspond to positions, funds, sectors, industries,
    # countries, mktcaps inside each dataframe in this group
    for var_report in var_reports:
        groupped_data = group_var_report_data_by_type(
            data_group=var_report,
            groupped_data=groupped_data
        )

    # inside each group prepare a dataframe that contains output information
    for key, value in groupped_data.items():
        groupped_data[key] = pd.concat(value, axis=1)
        groupped_data[key].reset_index(inplace=True)
        groupped_data[key].rename(
            columns={"index": f'{key}_name'}, inplace=True)

        # this part is only for position_list
        # selected_position_data = position[["VaRTicker", "UnderlierName"]]
        # groupped_data[key] = pd.merge(
        #     groupped_data[key],
        #     selected_position_data,
        #     on='VaRTicker',
        #     how="inner",
        # )
        groupped_data[key] = groupped_data[key].drop_duplicates(keep="first")
        # sort values by VaR95
        # groupped_data[key] = groupped_data[key].sort_values(
        #     ["VaRTicker_Iso95"], ascending=False
        # )
        # just keep iso95, iso99, inc95, inc99 etc.
        # groupped_data[key].columns = groupped_data[key].columns.str.replace(
        #     f"VaRTicker_", ""
        # )
        groupped_data[key].set_index([f'{key}_name'], inplace=True)

    # TODO: this has to go to the formatting section
    var_top_10 = groupped_data['position'].iloc[:10]  # type: ignore
    var_top_10.rename(
        columns={"UnderlierName": "Top10 VaR Contributors"}, inplace=True
    )
    # var_top_10.set_index(["Top10 VaR Contributors"], inplace=True)

    var_bottom_10 = groupped_data['position'].iloc[-10:]  # type: ignore
    var_bottom_10.rename(
        columns={"UnderlierName": "Top10 VaR Diversifiers"}, inplace=True
    )
    # var_bottom_10.set_index(["Top10 VaR Diversifiers"], inplace=True)

    var_fund = groupped_data['fund']
    var_sector = groupped_data['sector']
    var_industry = groupped_data['industry']
    var_country = groupped_data['country']
    var_mktcap = groupped_data['mktcap']

    return (
        var_top_10,
        var_bottom_10,
        var_fund,
        var_sector,
        var_industry,
        var_country,
        var_mktcap,
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
    logger.info("convert results into summary tbl")
    stress_test_results_df = pd.DataFrame(
        stress_test_arr, index=list(reversed(vol_shock_list)), columns=price_shock_list
    )

    return stress_test_results_df
