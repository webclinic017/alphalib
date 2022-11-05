import plotly.graph_objects as go
import plotly.io as pio
import yfinance as yf
from plotly.subplots import make_subplots

from alphalib.analysis.ta import momentum_rsi, volatility_atr


def plot_rsi(symbol: str, period: str = "1y"):
    assert symbol

    df = yf.download(symbol, period=period)
    df["RSI"] = momentum_rsi(df["Close"])

    pio.templates.default = "plotly_dark"
    fig = make_subplots(
        rows=2,
        cols=1,
        shared_xaxes=True,
        subplot_titles=("Price", "RSI"),
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["Close"],
            name="Price",
            line_color="rgb(0,204,0)",
        ),
        row=1,
        col=1,
    )

    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df["RSI"],
            name="RSI",
            line_color="rgb(204,0,0)",
        ),
        row=2,
        col=1,
    )

    fig.update_layout(title_text=f"Momentum Indicator - RSI for {symbol.upper()}")
    fig.update_xaxes(title="Date", rangeslider_visible=True, row=2, col=1)
    fig.update_yaxes(title="Price", row=1, col=1)
    fig.update_yaxes(title="RSI", row=2, col=1)
    fig.show()
