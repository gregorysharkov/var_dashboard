'''
module contains functions required to generate
output tables for the final report
'''
import pandas as pd

COLUMN_MAPPING = {
    'isolated': 'Iso',
    'component': 'Comp',
    'incremental': 'Inc',
}

N_ROWS = 10


def generate_underlier_report(
    var_data: pd.DataFrame,
    ascending: bool = False,
) -> pd.DataFrame:
    '''
    funtion generates top or bottom var underlier contrinutions
    Args:
        positions: list of positions
        var_data: global dataset with calculated var values
        ascending: a bool flag indicating whether we want to get
            bottom or top rows. If ascending, the bottom rows will
            be returned
    '''

    selected_var_data = var_data.loc[
        (var_data.group == 'position') &
        (var_data.var_type.isin(COLUMN_MAPPING))
    ]

    return_data = _format_var_data(selected_var_data)
    return_data = _format_output_columns(return_data)
    return_data = return_data\
        .reset_index()\
        .sort_values('Comp95', ascending=ascending, axis=0)\
        .set_index('Positions')

    axis_name = 'Top10 VaR Diversifiers' \
        if ascending else 'Top10 VaR Contributors'

    return_data = return_data.rename_axis(axis_name)
    return return_data.head(N_ROWS)


def _format_var_data(
    selected_var_data: pd.DataFrame
) -> pd.DataFrame:
    '''wrapper function that pivots the var data and renames column names'''
    return_data = pd.pivot_table(
        selected_var_data,
        index='attribute',
        values='var',
        columns=['var_type', 'var_confidence'],
    )

    return_data = _flattern_column_names(return_data)\
        .reset_index()\
        .rename(columns={'attribute': 'Positions'})\
        .set_index('Positions')

    return return_data


def _format_output_columns(data: pd.DataFrame) -> pd.DataFrame:
    '''formats column_names'''
    # select columns in the right order
    return_data = data[[
        *[col for col in data.columns if 'Iso' in col],
        *[col for col in data.columns if 'Inc' in col],
        *[col for col in data.columns if 'Comp' in col],
    ]]

    # rename columns to give them the output values
    for key, value in COLUMN_MAPPING.items():
        return_data = return_data.rename(
            columns={col: col.replace(key, value)
                     for col in return_data.columns}
        )

    return return_data


def _flattern_column_names(data: pd.DataFrame) -> pd.DataFrame:
    '''function flatterns column names after pivoting'''
    return_columns = []
    for col in data.columns:
        combined_column_name = ''.join(col)
        if ('incremental' in combined_column_name) or \
           ('isolated' in combined_column_name):
            combined_column_name = combined_column_name[:3] + \
                combined_column_name[-2:]
            combined_column_name = combined_column_name.capitalize()
        elif 'component' in combined_column_name:
            combined_column_name = combined_column_name[:4] + \
                combined_column_name[-2:]
            combined_column_name = combined_column_name.capitalize()

        return_columns.append(combined_column_name)
    data.columns = return_columns
    return data


def generate_group_var_report(
    var_data: pd.DataFrame,
    group: str
) -> pd.DataFrame:
    '''generates a var report for a given group'''

    selected_var_data = var_data.loc[
        (var_data.group == group) &
        (var_data.var_type.isin(COLUMN_MAPPING))
    ]

    return_data = pd.pivot_table(
        selected_var_data,
        index='attribute',
        values='var',
        columns=['var_type', 'var_confidence'],
    )

    return_data = _flattern_column_names(return_data)\
        .reset_index()\
        .rename(columns={'attribute': group.capitalize()})\
        .set_index(group.capitalize())

    return_data = _format_output_columns(return_data)
    return return_data


def generate_group_var_reports(var_data: pd.DataFrame, groups: list[str]) -> dict[str, pd.DataFrame]:
    '''generates a var report for a given group'''

    return_data = {}
    for group in groups:
        return_data[group] = generate_group_var_report(var_data, group)

    return return_data
