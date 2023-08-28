from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal, Tuple

import pandas as pd
from yahooquery import Ticker

from alphalib.data_sources.nasdaq import Nasdaq, get_dividend_info
from alphalib.utils.logging import logger


IntervalType = Literal["Monthly", "Quarterly", "Annually"]


@dataclass(kw_only=True)
class DividendAnalysis(Nasdaq):
    interval: IntervalType = "Quarterly"
    result: pd.DataFrame = None


def derive_dividend_interval(interval: float) -> IntervalType:
    if interval <= 45:
        return "Monthly"
    if interval <= 110:
        return "Quarterly"
    return "Annually"


def calculate_dividend_interval(
    dividend_history: pd.DataFrame,
) -> Tuple[pd.DataFrame, float]:
    dividend_history["interval"] = abs(dividend_history["exOrEffDate"].diff().dt.days)
    intervals = dividend_history.groupby(
        by=["exOrEffDate"], as_index=False, sort=False
    )["interval"].max()
    return intervals, intervals.head(5)["interval"].mean()


def cleanse_and_transform(dividend_history: pd.DataFrame):
    dividend_history["exOrEffDate"] = pd.to_datetime(
        dividend_history["exOrEffDate"], format="%m/%d/%Y", errors="coerce"
    )


def get_historical_prices(
    symbol: str, start_date: datetime, end_date: datetime
) -> pd.DataFrame:
    ticker = Ticker(symbol)
    try:
        hist_prices = ticker.history(start=start_date, end=end_date)
        if hist_prices.empty:
            logger.error(f"Unable to retrieve historical prices for {symbol}")
            return pd.DataFrame()
        hist_prices.reset_index(inplace=True)
        hist_prices["date"] = pd.to_datetime(
            hist_prices["date"], format="%Y-%m-%d", utc=True
        )
        return hist_prices
    except Exception:
        return pd.DataFrame()
    finally:
        ticker.session.close()


def analyze_prices_over_dividend_periods(
    dividend_dates: list[datetime], hist_prices: pd.DataFrame
) -> pd.DataFrame:
    date_intervals = [
        dividend_dates[i : i + 2] for i in range(0, len(dividend_dates), 1)
    ]
    results = []
    for interval in date_intervals:
        if len(interval) == 2:
            end_date = pd.to_datetime(interval[0] - timedelta(days=1), utc=True)
            start_date = pd.to_datetime(interval[1], utc=True)
            prices_between_dividend_dates = hist_prices[
                hist_prices["date"].between(start_date, end_date)
            ]
            dividend_analysis = {}
            if not prices_between_dividend_dates.empty:
                dividend_analysis["from"] = start_date.date()
                dividend_analysis["to"] = end_date.date()
                dividend_analysis["symbol"] = prices_between_dividend_dates[
                    "symbol"
                ].values[0]
                dividend_analysis["min_date"] = prices_between_dividend_dates.loc[
                    prices_between_dividend_dates["close"].idxmin(), "date"
                ].date()
                dividend_analysis["min"] = (
                    prices_between_dividend_dates["close"].min().round(4)
                )
                dividend_analysis["max_date"] = prices_between_dividend_dates.loc[
                    prices_between_dividend_dates["close"].idxmax(), "date"
                ].date()
                dividend_analysis["max"] = (
                    prices_between_dividend_dates["close"].max().round(4)
                )
                dividend_analysis["mean"] = (
                    prices_between_dividend_dates["close"].mean().round(4)
                )
                results.append(dividend_analysis)

    return pd.DataFrame(results)


def analyze_historical_prices(symbol: str, intervals: pd.DataFrame) -> pd.DataFrame:
    # Get historical dates for the first 12 rows
    dividend_dates = intervals["exOrEffDate"].head(12).to_list()
    start_date = dividend_dates[-1]
    end_date = dividend_dates[0]
    if end_date < datetime.now():
        dividend_dates.insert(0, pd.Timestamp.now().normalize())
        end_date = dividend_dates[0]

    hist_prices = get_historical_prices(symbol, start_date, end_date)

    # Analyze prices over the dividend periods
    return analyze_prices_over_dividend_periods(dividend_dates, hist_prices)


def dividend_analysis(symbol: str) -> DividendAnalysis:
    # Get dividend history
    stock_dividend_info: Nasdaq = get_dividend_info(symbol)

    # Create analysis
    analysis: DividendAnalysis = DividendAnalysis(**vars(stock_dividend_info))

    if analysis.dividend_history.empty:
        return analysis

    # Transform the dividend history
    cleanse_and_transform(analysis.dividend_history)

    # Calclucate the dividend intervals
    intervals, mean_interval = calculate_dividend_interval(analysis.dividend_history)

    # Derive the interval
    analysis.interval = derive_dividend_interval(mean_interval)

    # Analyze the dividend history
    analysis.result = analyze_historical_prices(symbol, intervals)

    return analysis