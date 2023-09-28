# %%
import datetime

import numpy as np
import pandas as pd
from xlsxwriter.utility import xl_range


class obj_reportwriter:

    def __init__(self, writer):
        self.writer = writer
        self.workbook = writer.book

        self.datereport = datetime.datetime.today()  # to Modify (TODO)

        self.title_format = self.workbook.add_format({
            'bold': True,
            'bg_color': '#44546A',
            'font_color': 'white',
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': False  # Allow text wrapping for long titles
        })
        self.tbl_title_pct_format = self.workbook.add_format({
            'bold': True,
            'bg_color': '#44546A',
            'font_color': 'white',
            'font_size': 8,
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': False,  # Allow text wrapping for long titles
            'num_format': '#,##0%'
        })
        self.categ_format = self.workbook.add_format({
            'bold': False,
            'font_size': 8,
            'bg_color': 'white',
            'font_color': 'black',
            'align': 'left',
            'valign': 'vcenter',
            'border': 1,
            'border_color': '#D9D9D9',
            'text_wrap': True  # Allow text wrapping for long titles
        })
        self.money_format = self.workbook.add_format({
            'num_format': '$#,##0.00',
            'border': 1,
            'border_color': '#D9D9D9',
            'font_size': 8,
            'font_color': 'black'
        })
        self.percentage_format = self.workbook.add_format({
            'num_format': '#,##0.00%_);[Red](#,##0.00%)',
            'border': 1,
            'border_color': '#D9D9D9',
            'font_size': 8,
            'font_color': 'black'
        })

        self.maintitle_format = self.workbook.add_format(
            {'font_size': 24, 'font_color': 'black', 'align': 'right', 'bold': True})
        self.subtitle_format = self.workbook.add_format(
            {'font_size': 16, 'font_color': 'black', 'align': 'right'})
        self.subsubtitle_format = self.workbook.add_format(
            {'font_size': 11, 'font_color': 'black', 'align': 'left', 'bottom': 2})
        self.maindate_format = self.workbook.add_format(
            {'font_size': 16, 'font_color': 'black', 'align': 'right', 'bottom': 5})

        # self.bottom_border_format = self.workbook.add_format({'bottom': 4})

        self.dummy_format = self.workbook.add_format({'bg_color': 'red'})

    # generic Methods  ###################################################################################################################

    def close_writer(self):
        self.writer.close()

    def write_df(self, df, ws, sname, sr, sc, space_categ=0, format_inside=None, format_title=None, format_categ=None):
        sr -= 1
        sc -= 1
        # ws.set_column(xl_range(sr, sc+2,sr + len(df) , sc+5),None, self.percentage_format)
        # ws.set_column(sc+2, sc+5, None, self.dummy_format,  {'first_row': sr, 'last_row':sr+10, 'first_column': sc+2, 'last_column':sc+3})
        # ws.write('B2:D10',None, self.dummy_format)
        if format_inside is None:
            format_inside = self.percentage_format
        if format_title is None:
            format_title = self.title_format
        if format_categ is None:
            format_categ = self.categ_format

        for row_num, (index, row) in enumerate(df.iterrows()):
            for col_num, cell_value in enumerate(row):
                sp = space_categ if col_num > 0 else 0
                if row_num == 0:
                    if space_categ > 0 and col_num == 0:
                        ws.merge_range(xl_range(sr+row_num, sc + col_num, sr+row_num,
                                       sc + col_num + space_categ), df.columns[col_num], format_title)
                    else:
                        ws.write(sr+row_num, sc + col_num + sp,
                                 df.columns[col_num], format_title)
                if space_categ > 0 and col_num == 0:
                    ws.merge_range(xl_range(sr+row_num+1, sc + col_num, sr+row_num+1, sc + col_num +
                                   space_categ), cell_value, format_categ if col_num == 0 else format_inside)
                else:
                    ws.write(sr+1+row_num, sc+col_num+sp, cell_value if isinstance(cell_value,
                             (int, float, str)) else '', format_categ if col_num == 0 else format_inside)

    def write_chart(self, ws, sname, ch_type, tbl_sr, tbl_sc, tbl_er, tbl_series, ch_name,  ch_sr, ch_sc, ch_er, ch_ec):
        chart_width, chart_height = 0, 0
        # make the chart the width of columns between sc and ec
        for i in range(ch_sc-1, ch_ec-1):
            chart_width += ws._size_col(i)
        for i in range(ch_sr-1, ch_er-1):
            chart_height += ws._size_row(i)
        chart = self.workbook.add_chart({'type': ch_type})
        chart.set_title({'name': ch_name})
        chart.set_size({'width': chart_width, 'height': chart_height})
        clrs = ['#4472C4', '#ED7D31', 'black', 'red']
        clr = 0
        for i in tbl_series:
            chart.add_series(
                {
                    'categories': [sname, tbl_sr-1, tbl_sc-1, tbl_er-1, tbl_sc-1],
                    'values': [sname, tbl_sr, tbl_sc+i-1, tbl_er-1, tbl_sc+i-1],
                    'name': [sname, tbl_sr-1, tbl_sc+i-1],
                    'fill': {'color': clrs[clr]}
                }
            )
            clr += 1
        chart.set_legend({'position': 'bottom'})
        chart.set_x_axis({'num_font':  {'rotation': -45}})
        ws.insert_chart(ch_sr-1, ch_sc-1, chart)

    def write_page_title(self, ws, sr, sc, se, ttl1, ttl2, ttl3):
        sc -= 1
        sr -= 1
        ws.merge_range(xl_range(sr, sc, sr, se), ttl1, self.maintitle_format)
        sr += 1
        ws.merge_range(xl_range(sr, sc, sr, se), ttl2, self.subtitle_format)
        sr += 1
        ws.merge_range(xl_range(sr, sc, sr, se), ttl3, self.maindate_format)

    # Methods for detailes report building #############################################################################################

    def write_FactorCorrels(self, sname, matrix_correlation):
        ws = self.workbook.add_worksheet(name=sname)
        sr, sc = 1, 1
        self.write_df(matrix_correlation, ws, sname,  sr, sc)
        ws.conditional_format(xl_range(sr, sc, sr+len(matrix_correlation), sc+len(matrix_correlation.columns)), {
                              'type': '3_color_scale',  'min_value': -1, 'max_value': 1, 'max_type': 'max', 'min_color': 'red',  'mid_color': 'white',   'max_color': 'green',  'mid_type': 'num', 'mid_value': 0})

    def write_varReport(self,  sname, VaR_Top10, VaR_Bottom10, VaR_structured_strat, VaR_structured_sector, VaR_structured_industry, VaR_structured_country, VaR_structured_mcap):
        # ws = self.workbook.add_worksheet(name=sname)
        ws = self.workbook.add_worksheet(name=sname)
        sr, sc, se = 5, 2, 11
        ws.set_column(0, 0, 2)
        ws.set_column(1, 1, 40)
        ws.set_column(2, 10, 13)
        ws.hide_gridlines(2)

        self.write_page_title(ws, 1, 2, 9, "VaR Report", "Firm Level",
                              datetime.datetime.strftime(self.datereport, "%m/%d/%Y"))

        ch_height_incells = 15

        self.write_df(VaR_Top10, ws, sname,  sr, sc, 0)
        sc += len(VaR_Top10.columns)+1
        self.write_df(VaR_Bottom10, ws, sname,  sr, sc, 2)
        sc = 2
        sr += len(VaR_Bottom10)+2
        self.write_df(VaR_structured_strat, ws, sname,  sr, sc)
        hh = len(VaR_structured_strat)
        self.write_chart(ws, sname, 'column', sr, sc, sr + hh,
                         [1, 2], "Strategy VaR", sr + hh + 2, sc, sr + hh + 2 + ch_height_incells, se)
        sr += hh + 2 + ch_height_incells + 1

        self.write_df(VaR_structured_sector, ws, sname,  sr, sc)
        hh = len(VaR_structured_sector)
        self.write_chart(ws, sname, 'column', sr, sc, sr + hh,
                         [1, 2], "Sector VaR", sr + hh + 2, sc, sr + hh + 2 + ch_height_incells, se)
        sr += hh + 2 + ch_height_incells + 1

        self.write_df(VaR_structured_industry, ws, sname,  sr, sc)
        hh = len(VaR_structured_industry)
        self.write_chart(ws, sname, 'column', sr, sc, sr + hh,
                         [1, 2], "Industry VaR", sr + hh + 2, sc, sr + hh + 2 + ch_height_incells, se)
        sr += hh + 2 + ch_height_incells + 1

        self.write_df(VaR_structured_country, ws, sname,  sr, sc)
        hh = len(VaR_structured_country)
        self.write_chart(ws, sname, 'column', sr, sc, sr + hh,
                         [1, 2], "Country VaR", sr + hh + 2, sc, sr + hh + 2 + ch_height_incells, se)
        sr += hh + 2 + ch_height_incells + 1

        self.write_df(VaR_structured_mcap, ws, sname,  sr, sc)
        hh = len(VaR_structured_mcap)
        self.write_chart(ws, sname, 'column', sr, sc, sr + hh,
                         [1, 2], "Mcap VaR", sr + hh + 2, sc, sr + hh + 2 + ch_height_incells, se)
        sr += hh + 2 + ch_height_incells + 1

    def write_optionstress(self, sname, stress_test_beta_price_vol_results_df, stress_test_price_vol_results_df, stress_test_price_vol_exposure_results_df, options_delta_adj_exposure_calc, options_delta1_exposure_calc, greek_sensitivities_calc, options_premium_calc):
        # ws = self.workbook.add_worksheet(name=sname)
        ws = self.workbook.add_worksheet(name=sname)
        ws.set_column(1, 1, 3)
        ws.set_column(2, 2, 4)
        ws.set_column(3, 14, 15)
        ws.hide_gridlines(2)

        self.write_page_title(ws, 1, 2, 13, "Options Analysis & Stress Tests",
                              "Firm Level", datetime.datetime.strftime(self.datereport, "%m/%d/%Y"))

        sr, sc = 7, 2
        ws.merge_range(xl_range(sr-3, sc-1, sr-3, sc-2+13),
                       "Options Breakdown & Greek Sensitivities", self.subsubtitle_format)

        self.write_df(options_delta_adj_exposure_calc, ws,
                      sname,  sr, sc, 2, self.money_format)
        self.write_df(options_delta1_exposure_calc, ws,
                      sname,  sr, sc+8, 0, self.money_format)
        sr += len(options_delta1_exposure_calc)+2
        self.write_df(greek_sensitivities_calc, ws, sname,
                      sr, sc, 2, self.money_format)
        self.write_df(options_premium_calc, ws, sname,
                      sr, sc+8, 0, self.money_format)

        sr += 8 + len(options_premium_calc)
        ws.merge_range(xl_range(sr-5, sc-1, sr-4, sc-2+13),
                       "Stress Testing", self.subsubtitle_format)

        ws.write(xl_range(sr-3, sc-1, sr-3, sc-1+13),
                 "Price & Volatility Stress Test P&L")
        self.write_df(stress_test_beta_price_vol_results_df, ws, sname,  sr,
                      sc+1, 0, None, self.tbl_title_pct_format, self.tbl_title_pct_format)

        sr += len(stress_test_beta_price_vol_results_df)+4
        ws.write(xl_range(sr-3, sc-1, sr-3, sc-1+13),
                 "Beta & Volatility Stress Test P&L")
        self.write_df(stress_test_price_vol_results_df, ws, sname,  sr, sc+1,
                      0, None, self.tbl_title_pct_format, self.tbl_title_pct_format)

        sr += len(stress_test_price_vol_results_df)+4
        ws.write(xl_range(sr-3, sc-1, sr-3, sc-1+13),
                 "Price & Volatility Stress Test Net Exposure")
        self.write_df(stress_test_price_vol_exposure_results_df, ws, sname,  sr,
                      sc+1, 0, None, self.tbl_title_pct_format, self.tbl_title_pct_format)

    def write_ExpReport(self, sname, strat_exposure_df, sector_exposure_df, industry_exposure_df, country_exposure_df, mktcap_exposure_df,
                        strat_beta_adj_exposure_df, sector_beta_adj_exposure_df, industry_beta_adj_exposure_df, country_beta_adj_exposure_df, mktcap_beta_adj_exposure_df):
        # ws = self.workbook.add_worksheet(name=sname)
        ws = self.workbook.add_worksheet(name=sname)
        ws.set_column(0, 0, 2)
        ws.set_column(1, 1, 30)
        ws.set_column(7, 7, 30)

        ws.hide_gridlines(2)

        self.write_page_title(ws, 1, 2, 11, "Exposure report", "Firm Level",
                              datetime.datetime.strftime(self.datereport, "%m/%d/%Y"))

        ch_height_incells = 15

        sr, sc, se = 5, 2, 13
        self.write_df(strat_exposure_df, ws, sname,  sr, sc)
        hh = len(strat_exposure_df)
        self.write_chart(ws, sname, 'column', sr, sc, sr + hh, [
                         1, 2], "Strategy Exposure", sr + hh + 2, sc, sr + hh + 2 + ch_height_incells, se)
        self.write_df(strat_beta_adj_exposure_df, ws, sname,  sr, sc+6)

        sr += hh + 2 + ch_height_incells + 1
        self.write_df(sector_exposure_df, ws, sname,  sr, sc)
        hh = len(sector_exposure_df)
        self.write_chart(ws, sname, 'column', sr, sc, sr + hh, [
                         1, 2], "Sector Exposure", sr + hh + 2, sc, sr + hh + 2 + ch_height_incells, se)
        self.write_df(sector_beta_adj_exposure_df, ws, sname,  sr, sc+6)

        sr += hh + 2 + ch_height_incells + 1
        self.write_df(industry_exposure_df, ws, sname,  sr, sc)
        hh = len(industry_exposure_df)
        self.write_chart(ws, sname, 'column', sr, sc, sr + hh, [
                         1, 2], "Industry Exposure", sr + hh + 2, sc, sr + hh + 2 + ch_height_incells, se)
        self.write_df(industry_beta_adj_exposure_df, ws, sname,  sr, sc+6)

        sr += hh + 2 + ch_height_incells + 1
        self.write_df(country_exposure_df, ws, sname,  sr, sc)
        hh = len(country_exposure_df)
        self.write_chart(ws, sname, 'column', sr, sc, sr + hh, [
                         1, 2], "Country Exposure", sr + hh + 2, sc, sr + hh + 2 + ch_height_incells, se)
        self.write_df(country_beta_adj_exposure_df, ws, sname,  sr, sc+6)

        sr += hh + 2 + ch_height_incells + 1
        self.write_df(mktcap_exposure_df, ws, sname,  sr, sc)
        hh = len(mktcap_exposure_df)
        self.write_chart(ws, sname, 'column', sr, sc, sr + hh, [
                         1, 2], "Sector Exposure", sr + hh + 2, sc, sr + hh + 2 + ch_height_incells, se)
        self.write_df(mktcap_beta_adj_exposure_df, ws, sname,  sr, sc+6)

    def write_FactorExp(self, sname, macro_factor_decomp_df, sector_factor_decomp_df, risk_factor_exposure_top_N_list, risk_factor_exposure_bottom_N_list):
        ws = self.workbook.add_worksheet(name=sname)
        ws.set_column(0, 1, 5)
        ws.set_column(2, 2, 32)
        ws.set_column(6, 6, 32)
        ws.set_column(10, 10, 32)
        ws.set_column(14, 14, 32)
        ws.hide_gridlines(2)

        self.write_page_title(ws, 1, 2, 10, "Factor report", "Firm Level",
                              datetime.datetime.strftime(self.datereport, "%m/%d/%Y"))

        sr, sc = 5, 2
        self.write_df(macro_factor_decomp_df, ws, sname,  sr, sc)
        hh = len(macro_factor_decomp_df)
        ch_height_incells = hh + 1
        self.write_chart(ws, sname, 'column', sr, sc, sr + hh, [1], "Macro Sensitivities", sr, sc + len(
            macro_factor_decomp_df.columns)+1, sr + hh + 2 + ch_height_incells, sc+13)

        sr += hh + 2
        self.write_df(sector_factor_decomp_df, ws, sname,  sr, sc)
        hh = len(sector_factor_decomp_df)
        ch_height_incells = hh + 1
        self.write_chart(ws, sname, 'column', sr, sc, sr + hh, [1], "Sector Sensitivities", sr, sc + len(
            sector_factor_decomp_df.columns)+1, sr + hh + 2 + ch_height_incells, sc+13)

        sr += hh + 2
        for ix in range(0, len(risk_factor_exposure_top_N_list), 2):
            df = risk_factor_exposure_top_N_list[ix].reset_index()
            self.write_df(df, ws, sname,  sr + (6 * ix), sc)
            hh = len(df)

            df = risk_factor_exposure_bottom_N_list[ix].reset_index()
            self.write_df(df, ws, sname,  sr + (6 * ix), sc+3)
            hh = len(df)

            df = risk_factor_exposure_top_N_list[ix + 1].reset_index()
            self.write_df(df, ws, sname,  sr + (6 * ix), sc+7)
            hh = len(df)

            df = risk_factor_exposure_bottom_N_list[ix + 1].reset_index()
            self.write_df(df, ws, sname,  sr + (6 * ix), sc+11)
            hh = len(df)

    def write_heatmap(self, sname, factor_heat_map):
        ws = self.workbook.add_worksheet(name=sname)
        sr, sc = 1, 1
        self.write_df(factor_heat_map, ws, sname,  sr, sc)
        ws.conditional_format(xl_range(sr, sc, sr+len(factor_heat_map), sc+len(factor_heat_map.columns)), {
                              'type': '3_color_scale',  'min_type': 'min', 'max_type': 'max', 'min_color': 'red',  'mid_color': 'white',   'max_color': 'green',  'mid_type': 'num', 'mid_value': 0})

    def write_positionbd(self, sname, position_breakdown):
        ws = self.workbook.add_worksheet(name=sname)
        ws.set_column(1, 1, 27)
        ws.set_column(2, 2, 44)
        ws.set_column(3, 16, 9)
        ws.hide_gridlines(2)
        self.write_page_title(ws, 1, 2, 10, "Position report", "Firm Level",
                              datetime.datetime.strftime(self.datereport, "%m/%d/%Y"))

        sr, sc = 5, 2
        self.write_df(position_breakdown, ws, sname,  sr, sc)

    def write_positionsummary(self, sname,  position_summary):
        ws = self.workbook.add_worksheet(name=sname)
        ws.set_column(1, 1, 27)
        ws.set_column(2, 10, 10)
        ws.hide_gridlines(2)

        self.write_page_title(ws, 1, 2, 10, "Position summary", "Firm Level",
                              datetime.datetime.strftime(self.datereport, "%m/%d/%Y"))

        ws = self.workbook.add_worksheet(name=sname)
        sr, sc = 5, 2
        self.write_df(position_summary, ws, sname,  sr, sc)


################################ test ####################

# xlfw = pd.ExcelWriter(f"testxl.xlsx", engine="xlsxwriter")
# rw = obj_reportwriter(xlfw)
# data = {
#     'Month': ['January', 'February', 'March', 'April', 'May'],
#     'Revenue ($)': [5000, 6000, 5500, 7000, 7500],
#     'Profit ($)': [2000, 2500, 2300, 3000, 3200],
#     'Profit Margin (%)': [0.40, 0.42, 0.42, 0.43, 0.43],
# }
# df = pd.DataFrame(data)

# ws = xlfw.book.add_worksheet(name= "mysheet")
# sr,sc = 5, 2
# ws.set_column(0 , 0 , 2)
# ws.set_column(sc, sc , 40)
# ws.hide_gridlines(2)

# rw.write_df(df,ws,  "mysheet", sr, 2)
# rw.write_chart(ws, "mysheet", 'column', sr, sc, sr + len(df)+1, [1,2],'TOTO', sr + len(df)+2 , sc, sr + len(df)+2+18, sc+10)
# rw.write_chart(ws, "mysheet", 'column', sr, sc, sr + len(df)+1, [1,2],'TOTO', sr , sc+len(df.columns), sr +len(df), sc+10)

# #rw.write_df(df,ws,  "mysheet", sr, 2,0,True, "Var Report", 15,[1,10])

# rw.close_writer()

################################ END test ####################

################################ END test ####################
