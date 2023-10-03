import json
import logging
from argparse import ArgumentParser
from datetime import datetime
from typing import List

import pandas as pd
import pandas_market_calendars as mcal
import xlsxwriter

import legacy.Exposures as Exposures
import legacy.Factors as Factors
import legacy.pnl_stats as pnl_stats
import legacy.VaR as var
import src.report_sheets as rsh

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)

now = datetime.utcnow().strftime("%Y%m%d")


def get_market_trading_days(start_date: str, end_date: str) -> pd.DataFrame:
    '''generate market calendar for NYSE'''
    nyse = mcal.get_calendar("NYSE")
    market_trading_days_range = nyse.schedule(
        start_date=start_date, end_date=end_date)

    return market_trading_days_range


def read_xlsx(
    xlsx_path: str,
    sheet_name: str,
    cols: List[str]
) -> pd.DataFrame:
    '''read xlsx file and return specified columns of a specified sheet'''

    df = pd.read_excel(xlsx_path, sheet_name=sheet_name, header=0)
    return df[cols]


if __name__ == "__main__":
    parser = ArgumentParser(description="")
    parser.add_argument(
        "--price_vol_shock_range",
        type=str,
        default="{'price_shock': [-0.2,-0.1,-0.05,-0.02,-0.01,0.0,0.01,0.02,0.05,0.1,"
        "0.2],\
                'vol_shock': [-0.5,-0.4,-0.3,-0.2,-0.1,0.0,0.1,0.2,0.3,0.4,0.5]}",
        help="range across which price shocks are expressed for stress testing",
    )
    parser.add_argument(
        "--holdings_date",
        type=str,
        default="2023-08-10",
        help="holdings date of postions across investment advisor",
    )
    args = parser.parse_args()

    # open the price_shock_range command line argument
    price_vol_shock_range = args.price_vol_shock_range
    price_vol_shock_range = price_vol_shock_range.replace("'", '"')
    """Note: read-in quasi_opt_AM_sort_list via json"""
    price_vol_shock_range = json.loads(price_vol_shock_range)

    # open the holdings_date command line argument
    holdings_date = args.holdings_date

    # 1. Read in factors, prices, positions, AUM
    factor = pd.read_csv("data/factors.csv")
    price = pd.read_csv("data/prices.csv")
    # TODO: date column may come as date or as Date
    price.rename({'Date': 'date'}, axis=1, inplace=True)
    price.set_index(["date"], inplace=True)

    # read and process raw positions
    RAW_POSITION_COLS = [
        'Expiry', 'FundName',
        'PutCall', 'Delta', 'Quantity', 'MarketPrice',
        'PX_POS_MULT_FACTOR', 'UndlPrice', 'Strike',
        'Gamma$', 'Vega', 'Theta', 'MtyYears', 'IVOL_TM',
        'FXRate', 'Description'
    ]
    raw_positions = read_xlsx(
        'data/Master_VaRFactor_Engine_2.xlsm',
        'RawPositions',
        RAW_POSITION_COLS,
    )
    raw_positions['Expiry'] = pd.to_datetime(raw_positions['Expiry'])

    # read and process positions
    position = pd.read_csv("data/positions.csv")
    position["MarketValue"] = position["MarketValue"].astype(float)
    for col in RAW_POSITION_COLS:
        position[col] = raw_positions[col]
    # TODO: Sometimes Exposure, sometimes VaRExposure, converge to the first
    # TODO: Sometimes MarketCap.1, sometimes MarketCap, converge to the first
    # TODO: VarTicker -> VaRTicker
    # TODO: UnderlierSymbol -> UnderlierName
    position.rename(
        {
            'VaRExposure': 'Exposure',
            'MarketCap': 'MarketCap.1',
            'VarTicker': 'VaRTicker',
            'UnderlierSymbol': 'UnderlierName',
            'ProdType': 'SECURITY_TYP',
        },
        axis=1,
        inplace=True
    )
    AUM = pd.read_excel("data/Historical Pnl and Nav.xlsx")
    # AUM = pd.read_csv("data/Historical Pnl and Nav.csv",
    #                   sep=';', decimal='.',)
    AUM_clean = pnl_stats.NAV_clean(AUM)  # model NAVs
    firm_nav = AUM_clean.loc[AUM_clean.index == holdings_date]["EndBookNAV"]

    price_date_index = pd.to_datetime(price.index)
    price_date_min = price_date_index.min()
    price_date_max = price_date_index.max()
    date_list = pd.date_range(price_date_min, price_date_max, freq="D")
    market_trading_days_range = get_market_trading_days(
        price_date_min, price_date_max)
    market_trading_days_range = market_trading_days_range.index\
        .strftime("%Y-%m-%d")

    # for now need to process positions and
    # force a distinct RFID for each distinct symbol
    LOGGER.info(
        "process positions and force a distinct RFID for each distinct symbol")
    cols = position.columns[~position.columns.isin(["RFID"])]
    position = position[cols]
    position_group = position.groupby("VaRTicker")
    count = 0
    position_group_df_list = []
    for name, group in position_group:
        count += 1
        group["RFID"] = count
        position_group_df_list.append(group)
    position = pd.concat(position_group_df_list, axis=0)
    position["Exposure"] = position["Exposure"].astype(float)

    # structure positions, factor, price data for subsequent estimation of Factor
    # betas, VaRs, Exposures, and Stress Tests
    price.index = pd.to_datetime(price.index).strftime("%Y-%m-%d")
    # TODO: MAKE IT PARAMETRISABLE
    price.index = pd.to_datetime(price.index).strftime("%Y-%m-%d")
    position = position.loc[(position["RFID"] > 0) & (position["RFID"] < 25)]
    factor_names = list(factor["Factor Names"])
    factor_names = [name for name in factor_names if str(name) != "nan"]
    factor_ids_full = list(factor["FactorID"])
    factors_to_remove = ["RIY less RTY", "RAG less RAV"]
    factor_ids = [
        item for item in factor_ids_full if item not in factors_to_remove]
    factor_prices = price[factor_ids]
    factor_ids = factor_ids_full
    factors_to_remove = ["RIY Index", "RTY Index", "RAG Index", "RAV Index"]
    factor_ids = [item for item in factor_ids if item not in factors_to_remove]
    factor = factor.loc[factor["FactorID"].isin(factor_ids)]
    position_ids = list(position["VaRTicker"].unique())
    position_prices = price[position_ids]
    strat_filters = position["FundName"].unique()
    sector_filters = position["Sector"].unique()
    industry_filters = position["Industry"].unique()
    country_filters = position["Country"].unique()
    mcap_filters = position["MarketCap.1"].unique()
    filters_dict = {
        "FundName": strat_filters,
        "Sector": sector_filters,
        "Industry": industry_filters,
        "Country": country_filters,
        "MarketCap.1": mcap_filters,
    }

    LOGGER.info("review input data")

    # 1.a. estimate factor betas, factor vols
    factor_betas = Factors.FactorBetas(factor_prices, position_prices)
    position_returns = Factors.position_returns(position_prices)

    # 1.b. VaR functions
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    # pd.ExcelWriter
    writer_options = {'constant_memory': False, 'nan_inf_to_errors': True}
    file_name = f"output/risk_report_{now}.xlsx"
    writer = xlsxwriter.Workbook(file_name, writer_options)
    writer.set_tab_ratio(75)
    # Excel equivalent ["FactorCorrels"]
    matrix_correlation = var.matrix_correlation(factor_prices, factor)
    matrix_cov = var.matrix_cov(factor_prices)
    decay_cov = var.decay_cov(factor_prices)
    var95_top_10, var95_bottom_10 = var.filter_VaR95(
        factor_prices, position, factor_betas, matrix_cov, firm_nav
    )
    var99_top_10, var99_bottom_10 = var.filter_VaR99(
        factor_prices, position, factor_betas, matrix_cov, firm_nav
    )
    var95_filtered_iso = var.filter_VaR95_iso(
        filters_dict, factor_prices, position, factor_betas, matrix_cov, firm_nav
    )
    var_top10 = pd.merge(var95_top_10, var99_top_10,
                         left_index=True, right_index=True)
    var_bottom10 = pd.merge(
        var95_bottom_10, var99_bottom_10, left_index=True, right_index=True
    )
    var99_filtered_iso = var.filter_VaR99_iso(
        filters_dict, factor_prices, position,
        factor_betas, matrix_cov, firm_nav
    )
    var95_filtered_inc = var.filter_VaR95_inc(
        filters_dict, factor_prices, position,
        factor_betas, matrix_cov, firm_nav
    )
    var99_filtered_inc = var.filter_VaR99_inc(
        filters_dict, factor_prices, position,
        factor_betas, matrix_cov, firm_nav
    )
    var95_filtered_comp = var.filter_Var95_comp(
        filters_dict, factor_prices, position,
        factor_betas, matrix_cov, firm_nav
    )
    var99_filtered_comp = var.filter_Var99_comp(
        filters_dict, factor_prices, position,
        factor_betas, matrix_cov, firm_nav
    )
    var_reports = [
        var95_filtered_iso,
        var99_filtered_iso,
        var95_filtered_inc,
        var99_filtered_inc,
        var95_filtered_comp,
        var99_filtered_comp,
    ]
    # Excel equivalent ["VaRReport; "Strat VaR", "Sector VaR", "Industry VaR",
    # "Country VaR", "Market Cap VaR" tbls]
    (
        var_structured_position_top10,
        var_structured_position_bottom10,
        var_structured_strat,
        var_structured_sector,
        var_structured_industry,
        var_structured_country,
        var_structured_mcap,
    ) = var.generate_var_reports(
        var_reports,
        position,
    )

    # # 1.c Stress Test functions
    # Excel equivalent ["Options&Stress; "Beta & Volatility Stress Test P&L tbl"]
    # stress_test_beta_price_vol_calc = var.filter_stress_test_beta_price_vol(
    #     filters_dict, factor_prices, position, factor_betas, price_vol_shock_range
    # )
    # stress_test_beta_price_vol_results_df = var.stress_test_structuring(
    #     stress_test_beta_price_vol_calc, position, price_vol_shock_range
    # )
    # # Excel equivalent ["Options&Stress; "Price & Volatility Stress Test P&L tbl"]
    # (
    #     stress_test_price_vol_calc,
    #     stress_test_price_vol_exposure_calc,
    # ) = var.filter_stress_test_price_vol(
    #     filters_dict, factor_prices, position, price_vol_shock_range
    # )
    # # Excel equivalent ["Options&Stress; "Price & Volatility Stress Test Net Exposure tbl"]
    # stress_test_price_vol_results_df = var.stress_test_structuring(
    #     stress_test_price_vol_calc, position, price_vol_shock_range
    # )
    # stress_test_price_vol_exposure_results_df = var.stress_test_structuring(
    #     stress_test_price_vol_exposure_calc, position, price_vol_shock_range
    # )

    # 1.d Exposure functions
    # Excel equivalent ["ExpReport"]
    (
        strat_exposure_df,
        sector_exposure_df,
        industry_exposure_df,
        country_exposure_df,
        mktcap_exposure_df,
    ) = Exposures.filter_exposure_calc(filters_dict, position, firm_nav)
    # Excel equivalent ["ExpReport"]
    (
        strat_beta_adj_exposure_df,
        sector_beta_adj_exposure_df,
        industry_beta_adj_exposure_df,
        country_beta_adj_exposure_df,
        mktcap_beta_adj_exposure_df,
    ) = Exposures.filter_beta_adj_exposure_calc(
        filters_dict, position, factor_betas, firm_nav
    )
    # Excel equivalent ["Options&Stress"; "Option Exposure" tbl]
    options_delta_adj_exposure_calc = Exposures.filter_options_delta_adj_exposure(
        position
    )
    # Excel equivalent ["Options&Stress"; "Option Notional" tbl]
    options_delta1_exposure_calc = Exposures.filter_options_delta_unadj_exposure(
        position
    )
    # Excel equivalent ["Options&Stress"; "Premium" tbl]
    options_premium_calc = Exposures.filter_options_premium(position)
    # Excel equivalent ["Options&Stress"; "Greek Sensitivity" tbl]
    greek_sensitivities_calc = Exposures.greek_sensitivities(position)
    # Excel equivalent ["FactorExposures"; "Macro Factor Sensitivity" tbl & "Sector
    # Sensitivities" tbl]
    macro_factor_decomp_df, sector_factor_decomp_df = Exposures.factor_decomp_filtered(
        position, factor_betas, factor_prices, factor, matrix_cov, firm_nav
    )
    # Excel equivalent ["FactorExposures"; "Top10" tbls & "Bottom10" tbls by Factor
    # Exposure by Position]
    (
        risk_factor_exposure_top_N_list,
        risk_factor_exposure_bottom_N_list,
    ) = Exposures.factor_decomp_by_factor_position(
        position, factor_betas, factor, firm_nav
    )
    # Excel equivalents ["FactorHeatMap"]
    factor_heat_map = Exposures.factor_heat_map(
        position, factor_betas, factor, firm_nav
    )
    # Excel equivalents ["PositionsBreakdown"]; ["PositionsSummary"];
    (
        position_breakdown,
        position_summary,
    ) = Exposures.stress_test_beta_price_vol_exposure_by_position(
        position, factor_betas, matrix_cov, position_returns, factor, firm_nav
    )

    # 1.e. pnl estimation
    factor_rets = pd.DataFrame(
        factor_prices["SPX Index"] / factor_prices["SPX Index"].shift(1) - 1,
        columns=["SPX Index"],
        index=factor_prices.index,
    )
    AUM_clean = pd.merge(
        AUM_clean, factor_rets["SPX Index"], left_index=True, right_index=True
    )
    # Excel equivalents ["PNLReport"]
    return_analysis_stats = pnl_stats.return_analysis(AUM_clean)
    comparative_analysis_stats = pnl_stats.comparative_statistics(
        AUM_clean, return_analysis_stats
    )

    # 1.f. dashboard
    # Excel equivalents ["Dashboard; "Fund Exposure %" tbl; "Fund Exposures $" tbl]
    # fund exposure % tbl
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
    long_mkt_value_pct = tmp = (
        position.loc[position["MarketValue"] > 0]["MarketValue"].sum()
        / firm_nav.values[0]
    )
    short_mkt_value_pct = tmp = (
        position.loc[position["MarketValue"] < 0]["MarketValue"].sum()
        / firm_nav.values[0]
    )
    gross_mkt_value_pct = abs(
        position["MarketValue"]).sum() / firm_nav.values[0]
    net_mkt_value_pct = position["MarketValue"].sum() / firm_nav.values[0]
    long_mkt_value = position.loc[position["MarketValue"]
                                  > 0]["MarketValue"].sum()
    short_mkt_value = position.loc[position["MarketValue"]
                                   < 0]["MarketValue"].sum()
    gross_mkt_value = abs(position["MarketValue"]).sum()
    net_mkt_value = position["MarketValue"].sum()
    fund_exp_pct_dashboard = pd.DataFrame(
        {
            "Fund Exposures %": [
                "Delta Adjusted Exposure",
                "Beta Adjusted " "Exposure",
                "Market Value",
            ],
            "Long": [
                sector_exposure_df["Long"].sum(),
                sector_beta_adj_exposure_df["Long"].sum(),
                long_mkt_value_pct,
            ],
            "Short": [
                sector_exposure_df["Short"].sum(),
                sector_beta_adj_exposure_df["Short"].sum(),
                short_mkt_value_pct,
            ],
            "Gross": [
                sector_exposure_df["Gross"].sum(),
                sector_beta_adj_exposure_df["Gross"].sum(),
                gross_mkt_value_pct,
            ],
            "Net": [
                sector_exposure_df["Net"].sum(),
                sector_beta_adj_exposure_df["Net"].sum(),
                net_mkt_value_pct,
            ],
        }
    )
    fund_exp_usd_dashboard = pd.DataFrame(
        {
            "Fund Exposures $": [
                "Delta Adjusted Exposure",
                "Beta Adjusted Exposure",
                "Market Value",
            ],
            "Long": [
                sector_exposure_df["Long"].sum() * firm_nav.values[0],
                sector_beta_adj_exposure_df["Long"].sum() * firm_nav.values[0],
                long_mkt_value,
            ],
            "Short": [
                sector_exposure_df["Short"].sum() * firm_nav.values[0],
                sector_beta_adj_exposure_df["Short"].sum(
                ) * firm_nav.values[0],
                short_mkt_value,
            ],
            "Gross": [
                sector_exposure_df["Gross"].sum() * firm_nav.values[0],
                sector_beta_adj_exposure_df["Gross"].sum(
                ) * firm_nav.values[0],
                gross_mkt_value,
            ],
            "Net": [
                sector_exposure_df["Net"].sum() * firm_nav.values[0],
                sector_beta_adj_exposure_df["Net"].sum() * firm_nav.values[0],
                net_mkt_value,
            ],
        }
    )

    dashboard_data = {
        'var_structured_position_top10': var_structured_position_top10.fillna(0),
        'var_structured_position_bottom10': var_structured_position_bottom10.fillna(0),
        'sector_exposure_df': sector_exposure_df,
        'options_premium_calc': options_premium_calc,
        'greek_sensitivities_calc': greek_sensitivities_calc.sort_index(),
        'macro_factor_decomp_df': macro_factor_decomp_df.sort_index(),
        'sector_factor_decomp_df': sector_factor_decomp_df,
        'fund_exp_pct_dashboard': fund_exp_pct_dashboard,
        'fund_exp_usd_dashboard': fund_exp_usd_dashboard,
    }

    rsh.generate_dashboard_sheet(
        writer,
        data=dashboard_data
    )

    # 1.g., build rest of workbook beyond dashboard
    pnldata_report_data = {
        'aum_clean': AUM_clean,
    }

    rsh.generate_pnldata_sheet(
        writer,
        data_dict=pnldata_report_data
    )

    pnl_report_data = {
        'comparative_analysis_stats': comparative_analysis_stats,
        'return_analysis_stats': return_analysis_stats,
    }

    rsh.generate_pnlreport_sheet(
        writer,
        data_dict=pnl_report_data
    )

    factor_heatmap_data = {
        'factor_heatmap': factor_heat_map.
        sort_values('Exposure', ascending=False),
    }

    rsh.generate_factor_heatmap_sheet(
        writer,
        data_dict=factor_heatmap_data
    )

    factor_exposure_report_data = {
        'macro_factor_decomp_df': macro_factor_decomp_df,
        'sector_factor_decomp_df': sector_factor_decomp_df,
        'risk_factor_exposure_top_n_list': risk_factor_exposure_top_N_list,
        'risk_factor_exposure_bottom_n_list': risk_factor_exposure_bottom_N_list,
    }

    rsh.generate_factor_exposures_sheet(
        writer,
        data=factor_exposure_report_data
    )

    exp_report_data = [
        {
            'Strategy exposure': strat_exposure_df,
            'Strategy Beta Exposure': strat_beta_adj_exposure_df,
        },
        {
            'Sector Exposure': sector_exposure_df.set_index('Sector Exposure'),
            'Sector Beta Exposure': sector_beta_adj_exposure_df,
        },
        {
            'Industry Exposure': industry_exposure_df,
            'Industry Beta Exposure': industry_beta_adj_exposure_df,
        },
        {
            'Country Exposure': country_exposure_df,
            'Country Beta Exposure': country_beta_adj_exposure_df,
        },
        {
            'Market Cap Exposure': mktcap_exposure_df,
            'Market Cap Beta Exposure': mktcap_beta_adj_exposure_df,
        },
    ]

    rsh.generate_exp_report_sheet(
        writer,
        data=exp_report_data
    )
    # mktcap_exposure_df.to_csv(r'data/mktcap_exposure_df.csv', sep=';')
    var_report_data = [
        {
            'var_top10': var_top10,
            'var_bottom10': var_bottom10,
        },
        {
            'Strat VaR': var_structured_strat.fillna(0),
            'Sector VaR': var_structured_sector.fillna(0),
            'Industry VaR': var_structured_industry.fillna(0),
            'Country VaR': var_structured_country.fillna(0),
            'MarketCap VaR': var_structured_mcap.fillna(0),
        },
    ]

    rsh.generate_var_report_sheet(
        writer,
        data=var_report_data
    )

    # stress_test_report_data = [
    #     {
    #         'options_delta_adj_exposure_calc': options_delta_adj_exposure_calc,
    #         'options_delta1_exposure_calc': options_delta1_exposure_calc,
    #         # .set_index('Greek Sensitivity'),
    #         'greek_sensitivities_calc': greek_sensitivities_calc,
    #         'options_premium_calc': options_premium_calc.set_index('Premium'),
    #     },
    #     {
    #         'stress_test_beta_price_vol_results_df': stress_test_beta_price_vol_results_df,
    #         'stress_test_price_vol_results_df': stress_test_price_vol_results_df,
    #         'stress_test_price_vol_exposure_results_df': stress_test_price_vol_exposure_results_df,
    #     },
    #     stress_test_price_vol_exposure_results_df,
    # ]

    # rsh.generate_options_stress_sheet(
    #     writer,
    #     data=stress_test_report_data
    # )

    rsh.generate_positions_summary_sheet(
        writer,
        position_summary,  # type: ignore
    )

    rsh.generate_positions_breakdown_sheet(
        writer,
        position_breakdown.fillna(0),  # type: ignore
    )

    rsh.generate_factor_correlations_sheet(
        writer,
        matrix_correlation,
    )

    writer.close()
    LOGGER.info("assess & interpret")
