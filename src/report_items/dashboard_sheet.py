import excel_utils as eu


def generate_dashboard_sheet(
    writer,
    VaR_structured_position_top10,
    VaR_structured_position_bottom10,
    sector_exposure_df,
    options_premium_calc,
    greek_sensitivities_calc,
    macro_factor_decomp_df,
    sector_factor_decomp_df,
    fund_exp_pct_dashboard,
    fund_exp_usd_dashboard,
) -> None:
    eu.format_table(
        data=VaR_structured_position_top10,
        writer=writer,
        sheet_name='Dashboard',
        start_col=1,
        start_row=4,
        table_name='VaR_structured_position_top10'.lower()
    )
    eu.format_table(
        data=VaR_structured_position_bottom10,
        writer=writer,
        sheet_name="Dashboard",
        start_col=9,
        start_row=4,
        table_name='VaR_structured_position_bottom10'.lower(),
    )
    # VaR_structured_position_top10.to_excel(
    #     writer, sheet_name="Dashboard", startcol=1, startrow=4
    # )
    # VaR_structured_position_bottom10.to_excel(
    #     writer, sheet_name="Dashboard", startcol=9, startrow=4
    # )
    # Excel equivalents ["Dashboard; "Fund Exposure %" and "Fund Exposure $" tbl]
    fund_exp_pct_dashboard.set_index(["Fund Exposures %"], inplace=True)
    eu.format_table(fund_exp_pct_dashboard, writer,
                    'Dashboard', 1, 16, 'fund_exp_pct_dashboard')
    # fund_exp_pct_dashboard.to_excel(
    #     writer, sheet_name="Dashboard", startcol=1, startrow=16
    # )
    fund_exp_usd_dashboard.set_index(["Fund Exposures $"], inplace=True)
    fund_exp_usd_dashboard.to_excel(
        writer, sheet_name="Dashboard", startcol=9, startrow=16
    )
    # Excel equivalents ["Dashboard; "Sector Exposure" tbl]
    sector_exposure_df.to_excel(
        writer,
        sheet_name="Dashboard",
        startcol=1,
        startrow=16 + len(fund_exp_pct_dashboard) + 2,
    )
    # Excel equivalents ["Dashboard; "Macro Factor Sensitivity" tbl]
    macro_factor_decomp_df.to_excel(
        writer,
        sheet_name="Dashboard",
        startcol=1,
        startrow=16 + len(fund_exp_pct_dashboard) +
        len(sector_exposure_df) + (2 * 2),
    )
    # Excel equivalents ["Dashboard; "Sector Sensitivity" tbl]
    sector_factor_decomp_df.to_excel(
        writer,
        sheet_name="Dashboard",
        startcol=1,
        startrow=16
        + len(fund_exp_pct_dashboard)
        + len(sector_exposure_df)
        + len(macro_factor_decomp_df)
        + (3 * 2),
    )
    # Excel equivalent ["Dashboard"; "Greek Sensitivity" tbl]
    greek_sensitivities_calc.to_excel(
        writer,
        sheet_name="Dashboard",
        startcol=1,
        startrow=16
        + len(fund_exp_pct_dashboard)
        + len(sector_exposure_df)
        + len(macro_factor_decomp_df)
        + len(sector_factor_decomp_df)
        + (4 * 2),
    )
    # Excel equivalent ["Dashboard"; "Option Premium" tbl]
    options_premium_calc.to_excel(
        writer,
        sheet_name="Dashboard",
        startcol=9,
        startrow=16
        + len(fund_exp_pct_dashboard)
        + len(sector_exposure_df)
        + len(macro_factor_decomp_df)
        + len(sector_factor_decomp_df)
        + (4 * 2),
    )
