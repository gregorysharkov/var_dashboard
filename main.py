# pylint: disable=E501,W0621,C0114,C0301
import logging
import warnings
from argparse import ArgumentParser
from datetime import datetime
from typing import List

import pandas as pd
import pandas_market_calendars as mcal
import xlsxwriter

import src.legacy.Exposures as Exposures
import src.legacy.Factors as fac
import src.legacy.pnl_stats as pnl_stats
import src.legacy.VaR as var
import src.legacy.var_utils as var_utils
import src.report_sheets as rsh
from src.calculation_engine.constants import GROUP_LEVELS
from src.calculation_engine.var_calculator import calculate_vars
from src.legacy.helper import calculate_returns, imply_smb_gmv
from src.reporting_engine.var_reports import (
    generate_group_var_reports,
    generate_underlier_report,
)

# Filter out the FutureWarning
warnings.filterwarnings(
    'ignore',
    message="The default dtype for empty Series will be 'object' instead"
    " of 'float64' in a future version."
)


formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
handler = logging.StreamHandler()
handler.setFormatter(formatter)

logger = logging.getLogger(__name__)
logger.addHandler(handler)
logger.setLevel(logging.INFO)
logging.getLogger().handlers.clear()

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


def parse_arguments():
    """Parse command line arguments."""
    parser = ArgumentParser(description="")
    parser.add_argument(
        "--price_vol_shock_range",
        type=str,
        default="""
            {
                'price_shock': [-.2, -.1, -.05, -.02, -.01, .0, .01, .02, .05, .1, .2],
                'vol_shock': [-.5, -.4, -.3, -.2, -.1, .0, .1, .2, .3, .4, .5],
            }
            """,
        help="range across which price shocks are expressed for stress testing",
    )
    parser.add_argument(
        "--holdings_date",
        type=str,
        default="2023-10-09",
        help="holdings date of postions across investment advisor",
    )
    parsed_args = parser.parse_args()
    return parsed_args


def parse_price_vol_shock_range():
    '''parses a price volatility from args'''

    # price_vol_shock_range = args.price_vol_shock_range
    # price_vol_shock_range = price_vol_shock_range.replace("'", '"')
    # """Note: read-in quasi_opt_AM_sort_list via json"""
    # price_vol_shock_range = json.loads(price_vol_shock_range)
    return {
        'price_shock': [-.2, -.1, -.05, -.02, -.01, .0, .01, .02, .05, .1, .2],
        'vol_shock': [-.5, -.4, -.3, -.2, -.1, .0, .1, .2, .3, .4, .5],
    }


def parse_holdings_date(args):
    '''Parse holdings date from command line arguments.'''
    holdings_date = datetime.strptime(args.holdings_date, '%Y-%m-%d').date()
    return holdings_date


def calculate_global_returns(price: pd. DataFrame) -> pd.DataFrame:
    '''
    function calculates global returns from a given price dataframe
    Returns are generated in the long format with each row representing a
    single date and having a var ticker and its return for that day
    '''

    global_returns = calculate_returns(price)
    global_returns.reset_index(inplace=True)
    global_returns.date = pd.to_datetime(
        global_returns.date,
        format=r'%Y-%m-%d',
    ).dt.date
    global_returns.rename(columns={'date': 'TradeDate'}, inplace=True)

    global_returns_long = global_returns\
        .melt(
            id_vars='TradeDate',
            value_name='return',
            var_name='VaRTicker',
        )

    return global_returns_long


if __name__ == "__main__":
    args = parse_arguments()
    price_vol_shock_range = parse_price_vol_shock_range()
    holdings_date = parse_holdings_date(args)

    # 1. Read in factors, prices, positions, AUM
    factor = pd.read_csv("data/factors.csv", sep=';')
    price = pd.read_csv("data/prices.csv")
    # TODO: date column may come as date or as Date
    price.rename({'Date': 'date'}, axis=1, inplace=True)
    price.date = pd.to_datetime(
        price.date,
        format=r'%m/%d/%Y',
    ).dt.date

    price.set_index(["date"], inplace=True)

    # read and process raw positions
    # RAW_POSITION_COLS = [
    #     'Expiry', 'FundName',
    #     'PutCall', 'Delta', 'Quantity', 'MarketPrice',
    #     'PX_POS_MULT_FACTOR', 'UndlPrice', 'Strike',
    #     'Gamma$', 'Vega', 'Theta', 'MtyYears', 'IVOL_TM',
    #     'FXRate', 'Description'
    # ]
    # raw_positions = read_xlsx(
    #     'data/Master_varFactor_Engine_2.xlsm',
    #     'RawPositions',
    #     RAW_POSITION_COLS,
    # )
    # raw_positions['Expiry'] = pd.to_datetime(raw_positions['Expiry'])

    # # read and process positions
    # position = pd.read_csv("data/positions.csv")
    position = pd.read_excel("data/positions.xlsx")
    # position["MarketValue"] = position["MarketValue"].astype(float)
    # for col in RAW_POSITION_COLS:
    #     position[col] = raw_positions[col]
    # TODO: Sometimes Exposure, sometimes varExposure, converge to the first
    # TODO: Sometimes MarketCap.1, sometimes MarketCap, converge to the first
    # TODO: VarTicker -> VarTicker
    # TODO: UnderlierSymbol -> UnderlierName
    position.rename(
        {
            'VaRExposure': 'Exposure',
            # 'MarketCap': 'MarketCap.1',
            'VarTicker': 'VaRTicker',
            # 'UnderlierSymbol': 'UnderlierName',
            'ProdType': 'SECURITY_TYP',
        },
        axis=1,
        inplace=True
    )

    aum = pd.read_excel("data/Historical Pnl and Nav.xlsx")
    # AUM = pd.read_csv("data/Historical Pnl and Nav.csv",
    #                   sep=';', decimal='.',)
    aum_clean = pnl_stats.clean_nav(aum)  # model NAVs
    firm_nav = aum_clean.loc[aum_clean.index == holdings_date]["EndBookNAV"]

    price_date_index = pd.to_datetime(price.index)
    price_date_min = price_date_index.min()
    price_date_max = price_date_index.max()
    date_list = pd.date_range(price_date_min, price_date_max, freq="D")
    market_trading_days_range = get_market_trading_days(
        price_date_min, price_date_max)
    market_trading_days_range = market_trading_days_range.index.strftime(
        "%Y-%m-%d")

    # for now need to process positions and force a
    # distinct RFID for each distinct symbol
    logger.info(
        "process positions and force a distinct RFID for each distinct symbol")
    cols = position.columns[~position.columns.isin(["RFID"])]
    position = position[cols]
    position_group = position.groupby("VaRTicker")
    position["RFID"] = position_group.cumcount() + 1
    position["Exposure"] = position["Exposure"].astype(float)
    position.TradeDate = pd.to_datetime(
        position.TradeDate,
        format=r'%Y-%m-%d',  # r'%m/%d/%Y'
    ).dt.date

    # structure positions, factor, price data for subsequent
    # estimation of Factor
    # betas, vars, Exposures, and Stress Tests
    # price.index = pd.to_datetime(price.index).strftime("%Y-%m-%d")
    # TODO: MAKE IT PARAMETRISABLE
    # position = position.loc[(position["RFID"] > 0) & (position["RFID"] < 10)]
    factor_names = list(factor["Factor Names"])
    factor_names = [name for name in factor_names if str(name) != "nan"]
    complete_factor_ids = list(factor["FactorID"])
    factors_to_remove = ["RIY less RTY", "RAG less RAV"]
    factor_ids = [
        item for item in complete_factor_ids if item not in factors_to_remove]
    factor_prices = price[factor_ids]

    factor_ids = complete_factor_ids
    factors_to_remove = ["RIY Index", "RTY Index", "RAG Index", "RAV Index"]
    factor_ids = [item for item in factor_ids if item not in factors_to_remove]
    factor = factor.loc[factor["FactorID"].isin(factor_ids)]

    position_ids = list(position["VaRTicker"].unique())
    position_prices = price[position_ids]

    strat_filters = position["Strat"].unique()
    sector_filters = position["Sector"].unique()
    industry_filters = position["Industry"].unique()
    country_filters = position["Country"].unique()
    mcap_filters = position["MarketCap"].unique()
    filters_dict = {
        "Strat": strat_filters,
        "Sector": sector_filters,
        "Industry": industry_filters,
        "Country": country_filters,
        "MarketCap": mcap_filters,
    }

    # logger.info("review input data")

    # 1.a. estimate factor betas, factor vols
    logger.info('Calculating factor betas')
    factor_returns = calculate_returns(factor_prices)
    factor_returns = imply_smb_gmv(factor_returns)
    position_returns = calculate_returns(position_prices)
    logger.info('Done with position returns estimation')

    factor_betas = fac.calculate_position_betas(
        factor_returns, position_returns)
    logger.info('Done with factor betas estimation')

    # 1.b. var functions
    # Create a Pandas Excel writer using XlsxWriter as the engine.
    # pd.ExcelWriter
    writer_options = {'constant_memory': False, 'nan_inf_to_errors': True}
    file_name = f"output/risk_report_{now}.xlsx"
    writer = xlsxwriter.Workbook(file_name, writer_options)
    writer.set_tab_ratio(75)
    # Excel equivalent ["FactorCorrels"]
    matrix_correlation = var_utils.correlation_matrix(factor_prices, factor)
    matrix_cov = var_utils.covariance_matrix(factor_returns)
    decay_cov = var_utils.decay_covariance_matrix(factor_returns)

    var_data = calculate_vars(prices=price, positions=position)
    var_data.to_excel('output/var_data.xlsx')

    top_var_contributors = generate_underlier_report(
        var_data, ascending=False
    )
    top_var_diversifiers = generate_underlier_report(
        var_data, ascending=True
    )

    group_var_reports = generate_group_var_reports(
        var_data, list(GROUP_LEVELS.keys())
    )

    # Excel equivalent ["varReport; "Strat var", "Sector var", "Industry var",
    # "Country var", "Market Cap var" tbls]
    var_structured_strat = group_var_reports.get('fund')
    var_structured_sector = group_var_reports.get('sector')
    var_structured_industry = group_var_reports.get('industry')
    var_structured_country = group_var_reports.get('country')
    var_structured_mcap = group_var_reports.get('mktcap')

    # # 1.c Stress Test functions
    # Excel equivalent ["Options&Stress;
    # "Beta & Volatility Stress Test P&L tbl"]
    filter_items = {
        # 'position': 'VaRTicker',
        'fund': 'Strat',
        'sector': 'Sector',
        'industry': 'Industry',
        'country': 'Country',
        'mktcap': 'MarketCap',
    }
    # stress_test_beta_price_vol_calc = var.filter_stress_test_beta_price_vol(
    #     filter_items, factor_prices, position,
    #     factor_betas, price_vol_shock_range
    # )
    # stress_test_beta_price_vol_results_df = var.stress_test_structuring(
    #     stress_test_beta_price_vol_calc,
    #     position, price_vol_shock_range
    # )
    # Excel equivalent ["Options&Stress;
    # "Price & Volatility Stress Test P&L tbl"]
    # (
    #     stress_test_price_vol_calc,
    #     stress_test_price_vol_exposure_calc,
    # ) = var.filter_stress_test_price_vol(
    #     filters_dict, factor_prices, position, price_vol_shock_range
    # )
    # Excel equivalent ["Options&Stress;
    # "Price & Volatility Stress Test Net Exposure tbl"]
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
    options_delta_adj_exposure_calc = Exposures\
        .filter_options_delta_adj_exposure(
            position
        )
    # Excel equivalent ["Options&Stress"; "Option Notional" tbl]
    options_delta1_exposure_calc = Exposures\
        .filter_options_delta_unadj_exposure(
            position
        )
    # Excel equivalent ["Options&Stress"; "Premium" tbl]
    options_premium_calc = Exposures.filter_options_premium(position)
    # Excel equivalent ["Options&Stress"; "Greek Sensitivity" tbl]
    greek_sensitivities_calc = Exposures.greek_sensitivities(position)
    # Excel equivalent ["FactorExposures"; "Macro Factor Sensitivity" tbl
    # & "Sector Sensitivities" tbl]
    macro_factor_decomp_df, sector_factor_decomp_df = Exposures\
        .factor_decomp_filtered(
            position, factor_betas, factor_prices,
            factor, matrix_cov, firm_nav
        )
    # Excel equivalent ["FactorExposures"; "Top10" tbls & "Bottom10"
    # tbls by Factor, Exposure by Position]
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
    # , left_index=True, right_index=True
    aum_clean = aum_clean.join(factor_rets["SPX Index"])
    # Excel equivalents ["PNLReport"]
    return_analysis_stats = pnl_stats.return_analysis(aum_clean)
    comparative_analysis_stats = pnl_stats.comparative_statistics(
        aum_clean, return_analysis_stats
    )

    # 1.f. dashboard
    # Excel equivalents
    # ["Dashboard; "Fund Exposure %" tbl; "Fund Exposures $" tbl]
    # fund exposure % tbl
    position_agg_exposure = (
        position
        .groupby("RFID")
        .agg({
            "TradeDate": "first",
            "Strat": "first",
            "UnderlierName": "first",
            "VaRTicker": "first",
            "MarketValue": "sum",
            "Exposure": "sum",
        })
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
                sector_exposure_df["Long"].sum(),  # type: ignore
                sector_beta_adj_exposure_df["Long"].sum(),  # type: ignore
                long_mkt_value_pct,
            ],
            "Short": [
                sector_exposure_df["Short"].sum(),  # type: ignore
                sector_beta_adj_exposure_df["Short"].sum(),  # type: ignore
                short_mkt_value_pct,
            ],
            "Gross": [
                sector_exposure_df["Gross"].sum(),  # type: ignore
                sector_beta_adj_exposure_df["Gross"].sum(),  # type: ignore
                gross_mkt_value_pct,
            ],
            "Net": [
                sector_exposure_df["Net"].sum(),  # type: ignore
                sector_beta_adj_exposure_df["Net"].sum(),  # type: ignore
                net_mkt_value_pct,
            ],
        }
    )
    nav_value = firm_nav.values[0]
    fund_exp_usd_dashboard = pd.DataFrame(
        {
            "Fund Exposures $": [
                "Delta Adjusted Exposure",
                "Beta Adjusted Exposure",
                "Market Value",
            ],
            "Long": [
                sector_exposure_df["Long"].sum() * nav_value,  # type: ignore
                sector_beta_adj_exposure_df["Long"].sum(  # type: ignore
                ) * nav_value,  # type: ignore
                long_mkt_value,
            ],
            "Short": [
                sector_exposure_df["Short"].sum() * nav_value,  # type: ignore
                sector_beta_adj_exposure_df["Short"].sum(  # type: ignore
                ) * nav_value,  # type: ignore
                short_mkt_value,
            ],
            "Gross": [
                sector_exposure_df["Gross"].sum() * nav_value,  # type: ignore
                sector_beta_adj_exposure_df["Gross"].sum(  # type: ignore
                ) * nav_value,  # type: ignore
                gross_mkt_value,
            ],
            "Net": [
                sector_exposure_df["Net"].sum() * nav_value,  # type: ignore
                sector_beta_adj_exposure_df["Net"].sum(  # type: ignore
                ) * nav_value,  # type: ignore
                net_mkt_value,
            ],
        }
    )

    rsh.generate_dashboard_sheet(
        writer,
        data={
            'var_structured_position_top10': top_var_contributors,
            'var_structured_position_bottom10': top_var_diversifiers,
            'sector_exposure_df': sector_exposure_df,
            'options_premium_calc': options_premium_calc,
            'greek_sensitivities_calc': greek_sensitivities_calc.sort_index(),
            'macro_factor_decomp_df': macro_factor_decomp_df.sort_index(),  # type: ignore
            'sector_factor_decomp_df': sector_factor_decomp_df,
            'fund_exp_pct_dashboard': fund_exp_pct_dashboard,
            'fund_exp_usd_dashboard': fund_exp_usd_dashboard,
        }
    )

    # 1.g., build rest of workbook beyond dashboard
    rsh.generate_pnldata_sheet(
        writer,
        data_dict={
            'aum_clean': aum_clean.dropna(),
        }
    )

    rsh.generate_pnlreport_sheet(
        writer,
        data_dict={
            'comparative_analysis_stats': comparative_analysis_stats,
            'return_analysis_stats': return_analysis_stats,
        }
    )
    rsh.generate_factor_heatmap_sheet(
        writer,
        data_dict={
            'factor_heatmap': factor_heat_map.
            sort_values('Exposure', ascending=False),
        }
    )
    rsh.generate_factor_exposures_sheet(
        writer,
        data={
            'macro_factor_decomp_df': macro_factor_decomp_df,
            'sector_factor_decomp_df': sector_factor_decomp_df,
            'risk_factor_exposure_top_n_list': risk_factor_exposure_top_N_list,
            'risk_factor_exposure_bottom_n_list': risk_factor_exposure_bottom_N_list,
        }
    )

    rsh.generate_exp_report_sheet(
        writer,
        data=[
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
    )
    # mktcap_exposure_df.to_csv(r'data/mktcap_exposure_df.csv', sep=';')
    rsh.generate_var_report_sheet(
        writer,
        data=[
            {
                'var_top10': top_var_contributors,
                'var_bottom10': top_var_diversifiers,
            },
            {
                'Strat var': var_structured_strat.fillna(0),
                'Sector var': var_structured_sector.fillna(0),
                'Industry var': var_structured_industry.fillna(0),
                'Country var': var_structured_country.fillna(0),
                'MarketCap var': var_structured_mcap.fillna(0),
            },
        ]
    )

    # rsh.generate_options_stress_sheet(
    #     writer,
    #     data=[
    #         {
    #             'options_delta_adj_exposure_calc': options_delta_adj_exposure_calc,
    #             'options_delta1_exposure_calc': options_delta1_exposure_calc,
    #             # .set_index('Greek Sensitivity'),
    #             'greek_sensitivities_calc': greek_sensitivities_calc,
    #             'options_premium_calc': options_premium_calc.set_index('Premium'),
    #         },
    #         {
    #             'stress_test_beta_price_vol_results_df': stress_test_beta_price_vol_results_df,
    #             'stress_test_price_vol_results_df': stress_test_price_vol_results_df,
    #             'stress_test_price_vol_exposure_results_df': stress_test_price_vol_exposure_results_df,
    #         },
    #         stress_test_price_vol_exposure_results_df,
    #     ]
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
    logger.info("assess & interpret")
