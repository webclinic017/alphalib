from dataclasses import dataclass
from datetime import datetime

import pandas as pd
from yahooquery import Ticker

from alphalib.utils.convertutils import TypeConverter, dt_from_ts, join_dicts, strip
from alphalib.utils import dateutils

pd.set_option("display.max_rows", None)
pd.set_option("display.max_columns", None)
pd.set_option("display.width", None)
pd.set_option("display.max_colwidth", None)


@dataclass
class YahooQuery(TypeConverter):
    symbol: str = ""
    name: str = ""
    exchange: str = ""
    sector: str = ""
    beta: float = 0
    current_price: float | None = 0
    fifty_two_week_low: float | None = 0
    fifty_two_week_high: float | None = 0
    five_year_avg_dividend_yield: float | None = 0
    earnings_date: datetime = datetime.min
    ex_dividend_date: datetime = datetime.min
    dividend_date: datetime = datetime.min
    last_dividend_date: datetime = datetime.min
    forward_eps: float | None = 0
    forward_pe: float | None = 0
    trailing_eps: float | None = 0
    trailing_pe: float | None = 0
    peg_ratio: float | None = 0
    price_to_book: float | None = 0
    free_cash_flow: float | None = 0
    return_on_equity: float | None = 0
    debt_to_equity: float | None = 0
    price_to_sales_trailing_12_months: float | None = 0
    payout_ratio: float | None = 0
    dividend_yield: float | None = 0
    dividend_rate: float | None = 0
    trailing_annual_dividend_rate: float | None = 0
    trailing_annual_dividend_yield: float | None = 0
    dividend_history: pd.DataFrame | None = None


def get_stock_info(symbol: str) -> YahooQuery:
    assert symbol

    yq = YahooQuery()
    yq.symbol = symbol.upper()

    ticker = Ticker(symbol)
    ticker.history(period="10y")

    key_stats: dict = {}

    # Dividend history
    yq.dividend_history = ticker.dividend_history(start=dateutils.years_from_now(10))

    key_stats = join_dicts(key_stats, ticker.key_stats, yq.symbol)
    key_stats = join_dicts(key_stats, ticker.summary_profile, yq.symbol)
    key_stats = join_dicts(key_stats, ticker.summary_detail, yq.symbol)

    print(ticker.summary_detail)
    # print(key_stats)

    # key_stats = join_dicts(key_stats, stats, "defaultKeyStatistics")
    # key_stats = join_dicts(key_stats, stats, "defaultKeyStatistics")
    # key_stats = join_dicts(key_stats, stats, "financialData")
    # key_stats = join_dicts(key_stats, stats, "summaryDetail")
    # key_stats = join_dicts(key_stats, stats, "price")
    # key_stats = join_dicts(key_stats, stats, "summaryProfile")
    # key_stats = join_dicts(key_stats, stats, "calendarEvents")

    # yq.name = strip(key_stats.get("shortName"))
    # yq.exchange = strip(key_stats.get("exchange"))
    # yq.sector = strip(key_stats.get("sector"))
    # yq.beta = key_stats.get("beta")
    # yq.current_price = key_stats.get("currentPrice")
    # yq.fifty_two_week_low = key_stats.get("fiftyTwoWeekLow")
    # yq.fifty_two_week_high = key_stats.get("fiftyTwoWeekHigh")

    # earningDts: list = key_stats.get("earnings", {}).get("earningsDate", [])
    # if len(earningDts) > 0:
    #     yq.earnings_date = dt_from_ts(earningDts[0])

    # yq.ex_dividend_date = dt_from_ts(key_stats.get("exDividendDate"))
    # yq.dividend_date = dt_from_ts(key_stats.get("dividendDate"))
    # yq.five_year_avg_dividend_yield = key_stats.get(
    #     "fiveYearAvgDividendYield"
    # )
    # yq.last_dividend_date = dt_from_ts(key_stats.get("lastDividendDate"))
    # yq.forward_eps = key_stats.get("forwardEps")
    # yq.forward_pe = key_stats.get("forwardPE")
    # yq.trailing_eps = key_stats.get("trailingEps")
    # yq.trailing_pe = key_stats.get("trailingPE")

    # yq.peg_ratio = key_stats.get("pegRatio")
    # yq.price_to_book = key_stats.get("priceToBook")
    # yq.free_cash_flow = key_stats.get("freeCashflow")
    # yq.return_on_equity = key_stats.get("returnOnEquity")
    # yq.debt_to_equity = key_stats.get("debtToEquity")
    # yq.price_to_sales_trailing_12_months = key_stats.get(
    #     "priceToSalesTrailing12Months"
    # )
    # yq.payout_ratio = key_stats.get("payoutRatio")
    # yq.dividend_yield = key_stats.get("dividendYield")
    # yq.dividend_rate = key_stats.get("dividendRate")
    # yq.trailing_annual_dividend_rate = key_stats.get(
    #     "trailingAnnualDividendRate"
    # )
    # yq.trailing_annual_dividend_yield = key_stats.get(
    #     "trailingAnnualDividendYield"
    # )

    return yq