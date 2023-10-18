'''refactored version of the IBIS var engine'''

import logging
import warnings

import numpy as np
import pandas as pd
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

CONTROL_GROUPS = ["FundName", "Sector", "Country",]
#   "MarketCap", "Industry", 'UnderlierName',]  # "Positions"]
VAR_MULTIPLIERS = {"95VaR": 1.644854, "99VaR": 2.326348}
VAR_DATA_COLUMNS = [
    "TradeDate", "Client", "Strat", "VaRType",
    "VaRSubType", "AttributeType", "AttributeValue", "VaRValue"
]

QUANTILES = {
    95: 1.644854,
    99: 2.326348,
}


def calculate_vars(
    positions: pd.DataFrame,
    prices: pd.DataFrame,
) -> pd.DataFrame:
    '''
    Function generates a VarData table that contains all
    valculated values at risk
    Basically we calculate the firm level var and then
    for every control group we calculate
        * 3 different var types: isolated, component and incremental
        * multiple confidence levels, described in QUANTILES

    Control groups are described in CONTROL_GROUPS

    Args:
        positions (pd.DataFrame): positions table
        prices (pd.DataFrame): prices table

    Returns:
        pd.DataFrame: VarData table that has
            columns described in VAR_DATA_COLUMNS
    '''
    var_tickers = positions.VaRTicker.unique()
    prices = prices[var_tickers]  # type: ignore
    trade_date = positions.TradeDate[0]
    client = str(positions.iloc[0, 1])
    # exposure = positions.groupby('VaRTicker').sum('Exposure').values
    exposure = positions.groupby('VaRTicker').agg({'Exposure': 'sum'})
    # exposure = positions.loc[:, "Exposure"].values

    # PositionCovarianceMatrix
    log_returns = np.log(prices / prices.shift(1))  # type: ignore
    control_position_covariance = log_returns.cov()  # type: ignore

    var_data = pd.DataFrame(columns=VAR_DATA_COLUMNS)

    # FirmLevelTotals
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", message="invalid value encountered in sqrt")
        stdev = np.sqrt(
            exposure.T @ (control_position_covariance @ exposure)
        )  # type: ignore

    var_data.loc[0] = [
        trade_date, client, "FirmLevel", "StDev",
        "Total", "Total", "Fund", stdev.iloc[0, 0],  # type: ignore
    ]

    var_data = add_vars_to_var_data(
        var_data=var_data,
        stdev=stdev.iloc[0, 0],  # type: ignore
        trade_date=trade_date,  # type: ignore
        client=client,
        control_group="Total",
        control_group_item="Total",
        quantiles=list(QUANTILES.keys()),
        var_type='Fund',
    )

    # CompVaR
    mvar = control_position_covariance @ exposure
    compvar = np.nan_to_num(
        mvar / stdev.iloc[0, 0] * exposure,  # type: ignore
        nan=0.0
    )

    # FirmLevel
    var_data = add_firm_level_vars(
        var_data,
        positions,
        trade_date,
        client,
        log_returns,
        control_position_covariance,
        compvar
    )

    return var_data


def add_firm_level_vars(
    var_data: pd.DataFrame,
    positions: pd.DataFrame,
    tradedate: str,
    client: str,
    log_returns: pd.DataFrame,
    control_position_covariance: pd.DataFrame,
    compvar: str
) -> pd.DataFrame:
    '''
    calculates firm level VaRs for every group
    '''
    for control_group in CONTROL_GROUPS:
        filter_items = extract_group_items(positions, control_group)
        for control_group_item in tqdm(
            filter_items,
            desc=f"Calculating firm level VaRs for {control_group}",
        ):
            # Isolated
            filtered_positions = positions.query(
                f"{control_group} == @control_group_item"
            )
            group_exposure = filtered_positions\
                .groupby('VaRTicker')\
                .agg({'Exposure': 'sum'})
            control_position_covariance = log_returns[group_exposure.index].\
                cov()

            var_data = add_control_group_isolated_var(
                tradedate, client, control_position_covariance,
                control_group, control_group_item, group_exposure,
                var_data
            )

            # Component
            var_data = add_control_group_component_var(
                positions, tradedate, client,
                compvar, control_group, control_group_item,
                var_data
            )

            # Incremental
            var_data = add_control_group_incremental_var(
                positions, tradedate, client, log_returns,
                control_group, control_group_item, var_data
            )

    return var_data


def add_control_group_incremental_var(
    positions: pd. DataFrame,
    tradedate,
    client,
    log_returns,
    control_group,
    control_group_item,
    var_data,
) -> pd.DataFrame:
    '''calculates incremental var for a given quantiles'''
    incremental_component_stdev = calculate_incremental_stdev(
        positions,
        log_returns,
        control_group,
        control_group_item,
    )  # type: ignore

    var_data = add_vars_to_var_data(
        var_data=var_data,
        stdev=incremental_component_stdev,
        trade_date=tradedate,
        client=client,
        control_group=control_group,
        control_group_item=control_group_item,
        quantiles=list(QUANTILES.keys()),
        var_type="Incremental",
    )

    return var_data


def add_control_group_component_var(
    positions,
    tradedate,
    client,
    compvar,
    control_group,
    control_group_item,
    var_data
) -> pd.DataFrame:
    '''calculates component var for a given quantiles'''
    exposure = positions\
        .groupby('VaRTicker')\
        .agg({'Exposure': 'sum'})

    component_stdev = np.nan_to_num(
        (exposure * compvar).sum(),
        nan=0,
    )[0]

    var_data = add_vars_to_var_data(
        var_data=var_data,
        stdev=component_stdev,
        trade_date=tradedate,
        client=client,
        control_group=control_group,
        control_group_item=control_group_item,
        quantiles=list(QUANTILES.keys()),
        var_type="Component",
    )

    return var_data


def add_control_group_isolated_var(
        tradedate,
        client,
        control_position_covariance: pd.DataFrame,
        control_group: str,
        control_group_item: str,
        group_exposure: pd.DataFrame,
        var_data: pd.DataFrame,
) -> pd.DataFrame:
    '''calculates isolated components for a given quantiles'''
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore",
            message="invalid value encountered in sqrt",
        )
        group_strdev = np.sqrt(
            np.nan_to_num(
                group_exposure.T @ (
                    control_position_covariance @
                    group_exposure
                ),
                nan=0,
            )
        )[0, 0]  # type: ignore

    var_data = add_vars_to_var_data(
        trade_date=tradedate,
        client=client,
        var_data=var_data,  # type: ignore
        control_group=control_group,
        control_group_item=control_group_item,
        stdev=group_strdev,  # type: ignore
        quantiles=list(QUANTILES.keys()),
        var_type="Isolated",
    )  # type: ignore

    return var_data


def calculate_incremental_stdev(
    positions: pd.DataFrame,
    log_returns: pd.DataFrame,
    control_group: str,
    control_group_item: str,
) -> pd.DataFrame:
    '''calculates stdv when excluding control group item'''
    exclude_condition = positions[control_group] != control_group_item
    positions_without_group_item = positions.loc[exclude_condition, :]
    isolated_exposure = positions_without_group_item\
        .groupby('VaRTicker')\
        .agg({'Exposure': 'sum'})\

    control_position_covariance = log_returns[isolated_exposure.index].cov()
    with warnings.catch_warnings():
        warnings.filterwarnings(
            "ignore", message="invalid value encountered in sqrt")
        component_stdev = np.sqrt(
            isolated_exposure.T @ (control_position_covariance @
                                   isolated_exposure)
        )  # type: ignore
    return np.nan_to_num(component_stdev, nan=0)[0, 0]


def add_vars_to_var_data(
    var_data: pd.DataFrame,
    stdev: pd.DataFrame,
    trade_date: str,
    client: str,
    control_group: str,
    control_group_item: str,
    quantiles: list[int],
    var_type: str,
) -> pd.DataFrame:
    '''adds isolated components for a given quantiles to var_data'''
    for quantile in quantiles:
        var_row = calculate_isolated_group_var(
            var_data=var_data,
            stdev=stdev,
            tradedate=trade_date,
            client=client,
            control_group=control_group,
            control_group_item=control_group_item,
            quantile=quantile,
            var_type=var_type,
        )
        var_data = pd.concat([var_data, var_row], ignore_index=True)
        # var_data.append(var_row)  # type: ignore
    return var_data


def calculate_isolated_group_var(
    tradedate: str,
    client: str,
    var_data: pd.DataFrame,
    control_group: str,
    control_group_item: str,
    stdev: pd.DataFrame,
    quantile: int,
    var_type: str,
) -> pd.DataFrame:
    '''Calculates the group var for a given quantile'''

    group_var = stdev * QUANTILES[quantile]  # type: ignore
    var_row = pd.DataFrame(
        [[
            tradedate, client, "FirmLevel", f"{quantile}VaR", var_type,
            control_group, control_group_item, group_var,
        ]],
        columns=var_data.columns
    )

    return var_row


def extract_group_items(positions, control_group):
    '''returns a list of unique not empty control group items'''

    return positions\
        .loc[positions[control_group].notnull(), control_group]\
        .unique()\
        # .reshape(-1, 1)

    # # StratLevel
    # strats = pd.DataFrame(
    #     positions.loc[:, "Strat"].unique(), columns=["Strat"])
    # control = control[1:]

    # for s in strats["Strat"]:
    #     stratPos = positions.loc[positions["Strat"] == s, :]
    #     rfid = stratPos.loc[:, "RFID"].values
    #     exposure = stratPos.loc[:, "VaRExposure"].values
    #     control_position_covariance = log_returns[rfid[:, None], rfid] # type: ignore

    #     # StratLevelTotals
    #     stdev = np.sqrt(exposure.T @ (control_position_covariance @ exposure))
    #     var_data = var_data.append(pd.DataFrame(
    #         [[tradedate, client, s, "StDev", "Total", "Total", "Strat", stdev[0, 0]]], columns=var_data.columns))
    #     var95 = stdev * 1.644854
    #     var_data = var_data.append(pd.DataFrame(
    #         [[tradedate, client, s, "95VaR", "Total", "Total", "Strat", var95[0, 0]]], columns=var_data.columns))
    #     var99 = stdev * 2.326348
    #     var_data = var_data.append(pd.DataFrame(
    #         [[tradedate, client, s, "99VaR", "Total", "Total", "Strat", var99[0, 0]]], columns=var_data.columns))

    #     # CompVaR
    #     mvar = control_position_covariance @ exposure
    #     compvar = mvar / stdev[0, 0] * exposure

    #     for control_group in control:
    #         filter_items = pd.DataFrame(
    #             stratPos.loc[stratPos[control_group].notnull(), control_group].unique(), columns=[control_group])
    #         for control_group_item in filter_items[control_group]:
    #             # Isolated
    #             filter_pos = stratPos.loc[stratPos[control_group]
    #                                       == control_group_item, :]
    #             rfid = filter_pos.loc[:, "RFID"].values
    #             exposure = filter_pos.loc[:, "VaRExposure"].values
    #             control_position_covariance = return_matrix[rfid[:, None], rfid]
    #             component_stdev = np.sqrt(
    #                 exposure.T @ (control_position_covariance @ exposure))
    #             component_stdev[np.isnan(component_stdev)] = 0
    #             component_var = component_stdev * 1.644854
    #             var_data = var_data.append(pd.DataFrame(
    #                 [[tradedate, client, s, "95VaR", "Isolated", control_group, control_group_item, component_var[0, 0]]], columns=var_data.columns))
    #             component_var = component_stdev * 2.326348
    #             var_data = var_data.append(pd.DataFrame(
    #                 [[tradedate, client, s, "99VaR", "Isolated", control_group, control_group_item, component_var[0, 0]]], columns=var_data.columns))

    #             # Component
    #             component_stdev = ((stratPos[control_group] ==
    #                                 control_group_item) * compvar).sum()
    #             component_stdev[np.isnan(component_stdev)] = 0
    #             component_var = component_stdev * 1.644854
    #             var_data = var_data.append(pd.DataFrame(
    #                 [[tradedate, client, s, "95VaR", "Component", control_group, control_group_item, component_var[0, 0]]], columns=var_data.columns))
    #             component_var = component_stdev * 2.326348
    #             var_data = var_data.append(pd.DataFrame(
    #                 [[tradedate, client, s, "99VaR", "Component", control_group, control_group_item, component_var[0, 0]]], columns=var_data.columns))

    #             # Incremental
    #             filter_pos = stratPos.loc[stratPos[control_group]
    #                                       != control_group_item, :]
    #             rfid = filter_pos.loc[:, "RFID"].values
    #             exposure = filter_pos.loc[:, "VaRExposure"].values
    #             control_position_covariance = return_matrix[rfid[:, None], rfid]
    #             component_stdev = np.sqrt(
    #                 exposure.T @ (control_position_covariance @ exposure))
    #             component_stdev[np.isnan(component_stdev)] = 0
    #             component_var = (stdev - component_stdev) * 1.644854
    #             var_data = var_data.append(pd.DataFrame(
    #                 [[tradedate, client, s, "95VaR", "Incremental", control_group, control_group_item, component_var[0, 0]]], columns=var_data.columns))
    #             component_var = (stdev - component_stdev) * 2.326348
    #             var_data = var_data.append(pd.DataFrame(
    #                 [[tradedate, client, s, "99VaR", "Incremental", control_group, control_group_item, component_var[0, 0]]], columns=var_data.columns))
    #     del control_group, control_group_item, component_stdev, component_var, filter_pos, rfid, exposure, control_position_covariance, filter_items
    # del s, stratPos, rfid, exposure, control_position_covariance, strats
