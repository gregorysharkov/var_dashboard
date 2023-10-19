# pylint: disable=missing-docstring
'''testing var engine on a sample portfolio'''

import pandas as pd

from src.calculation_engine.portfolio_var_calculator import \
    PortfolioVarCalculator


def main():
    prices_data = pd.DataFrame(
        {
            "Asset 1": [100, 106, 116, 123, 125, 133, 133, 124, 126, 121],
            "Asset 2": [200, 200, 200, 201, 199, 199, 196, 195, 195, 196],
            "Asset 3": [300, 310, 304, 311, 318, 315, 307, 315, 308, 311],
        },
        index=range(10),
    )

    portfolio_data = pd.DataFrame(
        {
            'VaRTicker': ['Asset 1', 'Asset 2', 'Asset 3'],
            'Exposure': [-300, 500, 400],
        }
    )

    var_engine = PortfolioVarCalculator(
        prices_table=prices_data,
        positions_table=portfolio_data,
    )

    # print(var_engine)
    print(f'{var_engine.portfolio_var(quantile=1.64)=:.4f}')
    print(f'Isolated_var:\n{var_engine.isolated_var(quantile=1.64)}')
    print(f'Component var:\n{var_engine.component_var(quantile=1.64)}')
    print(f'Incremental var:\n{var_engine.incremental_var(quantile=1.64)}')


if __name__ == '__main__':
    main()
