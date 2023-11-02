from datetime import datetime

import numpy as np
import pandas as pd

ANNUALIZATION_FACTOR = 252


def DD_Abs(X):
    r"""
    Calculate the Drawdown (DD) of a returns series
    using uncompounded cumulative returns.

    Parameters
    ----------
    X : 1d-array
        Returns series, must have Tx1 size.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    Returns
    -------
    value : float
        DD of an uncompounded cumulative returns.

    """

    a = np.array(X, ndmin=2)
    if a.shape[0] == 1 and a.shape[1] > 1:
        a = a.T
    if a.shape[0] > 1 and a.shape[1] > 1:
        raise ValueError("returns must have Tx1 size")

    prices = np.insert(np.array(a), 0, 1, axis=0)
    NAV = np.cumsum(np.array(prices), axis=0)
    peak = -99999
    n = 0
    DD_list = []
    for i in NAV:
        if i > peak:
            peak = i
        DD = peak - i
        if DD > 0:
            # value += DD
            DD_list.append(DD)
        n += 1
    if n == 0:
        # value = 0
        DD = 0
    # else:
    #     value = value
    current_drawdown = DD_list[-1:]

    # value = np.array(value).item()

    return current_drawdown


def MDD_Abs(X):
    r"""
    Calculate the Maximum Drawdown (MDD) of a returns series
    using uncompounded cumulative returns.

    Parameters
    ----------
    X : 1d-array
        Returns series, must have Tx1 size.

    Raises
    ------
    ValueError
        When the value cannot be calculated.

    Returns
    -------
    value : float
        MDD of an uncompounded cumulative returns.

    """

    a = np.array(X, ndmin=2)
    if a.shape[0] == 1 and a.shape[1] > 1:
        a = a.T
    if a.shape[0] > 1 and a.shape[1] > 1:
        raise ValueError("returns must have Tx1 size")

    prices = np.insert(np.array(a), 0, 1, axis=0)
    NAV = np.cumsum(np.array(prices), axis=0)
    value = 0
    peak = -99999
    for i in NAV:
        if i > peak:
            peak = i
        DD = peak - i
        if DD > value:
            value = DD

    value = np.array(value).item()

    return value


def clean_nav(aum: pd.DataFrame) -> pd.DataFrame:
    '''clean aum data and calculate returns'''

    clean_aum = convert_aum_columns(aum)
    daily_nav_agg = clean_aum\
        .groupby("PeriodEndDate")\
        .agg({"DailyBookPL": "sum", "EndBookNAV": "sum", "Fund": "count"})

    daily_nav_nav_filtered = daily_nav_agg[daily_nav_agg['Fund'] > 5]

    # calculate returns
    daily_nav_nav_filtered['ret'] = daily_nav_nav_filtered.DailyBookPL / \
        daily_nav_nav_filtered.EndBookNAV.shift(1)

    # keep only days, where abs or ret is lower than 1
    daily_nav_nav_filtered = daily_nav_nav_filtered.loc[
        abs(daily_nav_nav_filtered["ret"]) < 1
    ]

    return daily_nav_nav_filtered


def convert_aum_columns(aum: pd.DataFrame) -> pd.DataFrame:
    '''ensure right data types for aum columns'''

    aum["PeriodEndDate"] = pd.to_datetime(aum["PeriodEndDate"]).dt.date
    for col in aum.columns:
        if "BookPL" in col or "NAV" in col:
            aum[col].astype(float)
    return aum


def return_analysis(AUM: pd.DataFrame) -> pd.DataFrame:
    return_analysis_dict = {}
    # 1. last day ret
    last_day_return = AUM[["ret", "SPX Index"]].iloc[-1:, :]
    columns = last_day_return.columns
    index = last_day_return.index
    return_analysis_dict["Last Day Return"] = last_day_return
    # 2.mtd_return
    AUM["month"] = pd.to_datetime(AUM.index).strftime("%Y-%m")
    amon = pd.DatetimeIndex(AUM["month"]).month.tolist()
    ayear = pd.DatetimeIndex(AUM["month"]).year.tolist()
    bmon = [i for i, x in enumerate(amon) if ((x == datetime.now().month - 1))]
    byear = [i for i, x in enumerate(ayear) if ((x == datetime.now().year))]
    common = [i for i in bmon if i in byear]
    AUM_MTD = AUM.iloc[common][["ret", "SPX Index"]]
    MTD_return = pd.DataFrame(
        ((1 + AUM_MTD).cumprod() - 1).iloc[-1, :], index=columns, columns=index
    ).T
    return_analysis_dict["MTD Return"] = MTD_return
    # 3. ytd return
    AUM["year"] = pd.to_datetime(AUM.index).strftime("%Y")
    current_year = [i for i, x in enumerate(
        ayear) if ((x == datetime.now().year))]
    AUM_YTD = AUM.iloc[current_year][["ret", "SPX Index"]]
    YTD_return = pd.DataFrame(
        ((1 + AUM_YTD).cumprod() - 1).iloc[-1, :], index=columns, columns=index
    ).T
    return_analysis_dict["YTD Return"] = YTD_return
    # 4. cumul ret
    cumul_ret = pd.DataFrame(
        ((1 + AUM[["ret", "SPX Index"]]).cumprod() - 1).iloc[-1, :],
        index=columns,
        columns=index,
    ).T
    return_analysis_dict["Cumulative Return"] = cumul_ret
    # 5. annualized ret
    ann_ret = pd.DataFrame(
        (
            (1 + AUM[["ret", "SPX Index"]]).cumprod()
            ** (ANNUALIZATION_FACTOR / len(AUM))
            - 1
        ).iloc[-1, :],
        index=columns,
        columns=index,
    ).T
    return_analysis_dict["Annualized Return"] = ann_ret
    # 6. daily volatility
    daily_volatility = pd.DataFrame(
        np.std(AUM[["ret", "SPX Index"]]), index=columns, columns=index
    ).T
    return_analysis_dict["Daily Volatility"] = daily_volatility
    # 6. annualized volatility
    annualized_volatility = pd.DataFrame(
        np.std(AUM[["ret", "SPX Index"]]) * (np.sqrt(ANNUALIZATION_FACTOR)),
        index=columns,
        columns=index,
    ).T
    return_analysis_dict["Annualized Volatility"] = annualized_volatility
    # 7. sharpe ratio
    sharpe_ratio = ann_ret / annualized_volatility
    return_analysis_dict["Sharpe Ratio"] = sharpe_ratio
    # 8. downside volatility
    downside_volatility = pd.DataFrame(
        np.std(AUM[["ret", "SPX Index"]].loc[AUM["ret"] < 0]),
        index=columns,
        columns=index,
    ).T
    return_analysis_dict["Downside Deviation"] = downside_volatility
    # 9. annualized downside volatility
    annualized_downside_volatility_df_list = []
    for col in AUM[["ret", "SPX Index"]].columns:
        annualized_downside_volatility_df = pd.DataFrame(
            np.std(AUM[[col]].loc[AUM[col] < 0]) *
            (np.sqrt(ANNUALIZATION_FACTOR)),
            index=[col],
            columns=index,
        ).T
        annualized_downside_volatility_df_list.append(
            annualized_downside_volatility_df)
    annualized_downside_volatility = pd.concat(
        annualized_downside_volatility_df_list, axis=1
    )
    return_analysis_dict["Downside Deviation"] = downside_volatility
    # 10. sortino ratio
    sortino_ratio = ann_ret / annualized_downside_volatility
    return_analysis_dict["Sortino Ratio"] = sortino_ratio
    # 11. up_days
    up_days_df_list = []
    for col in AUM[["ret", "SPX Index"]].columns:
        up_days_df = pd.DataFrame(
            len(AUM[col].loc[AUM[col] > 0]), index=[col], columns=index
        ).T
        up_days_df_list.append(up_days_df)
    up_days = pd.concat(up_days_df_list, axis=1)
    return_analysis_dict["Up Days"] = up_days
    # 12. down_days
    down_days_df_list = []
    for col in AUM[["ret", "SPX Index"]].columns:
        down_days_df = pd.DataFrame(
            len(AUM[col].loc[AUM[col] < 0]), index=[col], columns=index
        ).T
        down_days_df_list.append(down_days_df)
    down_days = pd.concat(down_days_df_list, axis=1)
    return_analysis_dict["Down Days"] = down_days
    # 13. largest up day
    largest_up_day = pd.DataFrame(
        np.max(AUM[["ret", "SPX Index"]]), index=columns, columns=index
    ).T
    return_analysis_dict["Largest Up Day"] = largest_up_day
    # 14. largest down day
    largest_down_day = pd.DataFrame(
        np.min(AUM[["ret", "SPX Index"]]), index=columns, columns=index
    ).T
    return_analysis_dict["Largest Down Day"] = largest_down_day
    # 15. current drawdown
    current_drawdown_df_list = []
    for col in AUM[["ret", "SPX Index"]].columns:
        current_drawdown_df = pd.DataFrame(
            DD_Abs(AUM[col].values), index=[col], columns=index
        ).T
        current_drawdown_df_list.append(current_drawdown_df)
    current_drawdown = pd.concat(current_drawdown_df_list, axis=1)
    return_analysis_dict["Current Drawdown"] = current_drawdown
    # 16. max drawdown
    max_drawdown_df_list = []
    for col in AUM[["ret", "SPX Index"]].columns:
        max_drawdown_df = pd.DataFrame(
            MDD_Abs(AUM[col].values), index=[col], columns=index
        ).T
        max_drawdown_df_list.append(max_drawdown_df)
    max_drawdown = pd.concat(max_drawdown_df_list, axis=1)
    return_analysis_dict["Maximum Drawdown"] = max_drawdown
    # 17. CALMAR
    calmar = ann_ret / max_drawdown
    return_analysis_dict["Return over Drawdown (CALMAR)"] = calmar
    return_analysis_df = (
        pd.concat(return_analysis_dict, axis=0)
        .reset_index(level=0)
        .rename({"level_0": "Return Analysis"}, axis=1)
    )
    return_analysis_df.set_index(["Return Analysis"], inplace=True)

    return return_analysis_df


def comparative_statistics(AUM: pd.DataFrame, return_analysis_df: pd.DataFrame):
    comparative_statistics_dict = {}
    # 1. beta
    beta_df_list = []
    for col in AUM[["ret", "SPX Index"]].columns[1:]:
        beta_df = pd.DataFrame(
            (AUM[["ret", col]].cov() / np.nanvar(AUM[[col]])).iloc[1, 1],
            columns=[col],
            index=["Beta"],
        )
        beta_df.reset_index(inplace=True, drop=True)
        beta_df_list.append(beta_df)
    beta_df = pd.concat(beta_df_list, axis=1)
    comparative_statistics_dict["Beta"] = beta_df
    # 2. correlation
    correlation_df_list = []
    for col in AUM[["ret", "SPX Index"]].columns[1:]:
        correlation_df = pd.DataFrame(
            (
                beta_df.values[0, :]
                * (
                    return_analysis_df.loc[
                        return_analysis_df.index == "Annualized Volatility"
                    ][col]
                    / return_analysis_df.loc[
                        return_analysis_df.index == "Annualized Volatility"
                    ]["ret"]
                )
            ).values,
            columns=[col],
            index=["Correlation"],
        )
        correlation_df.reset_index(inplace=True, drop=True)
        correlation_df_list.append(correlation_df)
    correlation_df = pd.concat(correlation_df_list, axis=1)
    comparative_statistics_dict["Correlation"] = correlation_df
    # 3. up capture
    up_capture_df_list = []
    for col in AUM[["ret", "SPX Index"]].columns[1:]:
        up_capture_df = pd.DataFrame(
            (
                ((1 + AUM[["ret", col]].loc[AUM[col] > 0]["ret"]).cumprod() - 1).iloc[
                    -1:
                ]
                / ((1 + AUM[["ret", col]].loc[AUM[col] > 0][col]).cumprod() - 1).iloc[
                    -1:
                ]
            ).values,
            columns=[col],
            index=["Up Capture"],
        )
        up_capture_df_list.append(up_capture_df)
    up_capture = pd.concat(up_capture_df_list, axis=1)
    comparative_statistics_dict["Up Capture"] = up_capture
    # 4. down capture
    down_capture_df_list = []
    for col in AUM[["ret", "SPX Index"]].columns[1:]:
        down_capture_df = pd.DataFrame(
            (
                ((1 + AUM[["ret", col]].loc[AUM[col] < 0]["ret"]).cumprod() - 1).iloc[
                    -1:
                ]
                / ((1 + AUM[["ret", col]].loc[AUM[col] < 0][col]).cumprod() - 1).iloc[
                    -1:
                ]
            ).values,
            columns=[col],
            index=["Down Capture"],
        )
        down_capture_df_list.append(down_capture_df)
    down_capture = pd.concat(down_capture_df_list, axis=1)
    comparative_statistics_dict["Down Capture"] = down_capture
    comparative_statistics_df = (
        pd.concat(comparative_statistics_dict, axis=0)
        .reset_index(level=0)
        .rename({"level_0": "Comparative Statistics"}, axis=1)
    )
    comparative_statistics_df.set_index(
        ["Comparative Statistics"], inplace=True)

    return comparative_statistics_df
