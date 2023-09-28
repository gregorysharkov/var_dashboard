import pandas as pd
import numpy as np
import logging
from scipy.stats import expon, norm

logging.basicConfig(level=logging.INFO)
LOGGER = logging.getLogger(__name__)


def imply_SMB_GMV(factor_returns: pd.DataFrame) -> pd.DataFrame:
    # imply Small - Big, Growth - Value
    factor_returns["RIY less RTY"] = (
        factor_returns["RIY Index"] - factor_returns["RTY Index"]
    )
    factor_returns["RAG less RAV"] = (
        factor_returns["RAG Index"] - factor_returns["RAV Index"]
    )
    factor_returns = factor_returns[
        [
            "LD12TRUU Index",
            "SPX Index",
            "RIY less RTY",
            "RAG less RAV",
        ]
        + [
            col
            for col in factor_returns.columns
            if col
            not in [
                "LD12TRUU Index",
                "SPX Index",
                "RIY Index",
                "RTY Index",
                "RAG Index",
                "RAV Index",
                "RIY less RTY",
                "RAG less RAV",
            ]
        ]
    ]

    return factor_returns


def historical_series(risk_factors: pd.DataFrame, exposure: np.ndarray, name: str):
    ln = np.log(risk_factors.iloc[1:, :] / risk_factors.iloc[1:, :].shift(1))
    LOGGER.info(f"processing fund {name}")
    hist_ret = ln @ exposure
    hist_ret = pd.DataFrame(hist_ret, columns=["fund_pnl"])
    hist_ret.index = pd.to_datetime(hist_ret.index).strftime("%Y-%m-%d")

    return hist_ret


def option_price(
    S: pd.Series, X: pd.Series, T: pd.Series, Vol: pd.Series, rf: float, type: pd.Series
):
    price_list = []
    for ix in range(0, len(S)):
        d1 = (
            np.log(S.iloc[ix] / X.iloc[ix]) + (rf + Vol.iloc[ix] ** 2 / 2) * T.iloc[ix]
        ) / (Vol.iloc[ix] * np.sqrt(T.iloc[ix]))
        d2 = d1 - Vol.iloc[ix] * np.sqrt(T.iloc[ix])
        if (
            (type.iloc[ix] == "Call")
            or (type.iloc[ix] == "C")
            or (type.iloc[ix] == "c")
        ):
            price = S.iloc[ix] * norm.cdf(d1, 0, 1) - X.iloc[ix] * np.exp(
                -rf * T.iloc[ix]
            ) * norm.cdf(d2, 0, 1)
        elif (
            (type.iloc[ix] == "Put") or (type.iloc[ix] == "P") or (type.iloc[ix] == "p")
        ):
            price = X.iloc[ix] * np.exp(-rf * T.iloc[ix]) * norm.cdf(
                -d2, 0, 1
            ) - S.iloc[ix] * norm.cdf(-d1, 0, 1)

        price_list.append(price)

    return price_list
