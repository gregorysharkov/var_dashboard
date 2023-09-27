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
        @ factor_betas.values[:, 1:]
        @ matrix_cov.values[1:, 1:]
        @ factor_betas.values[:, 1:].T
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
