import json
import time
import numpy as np
import pandas_ta as ta

import streamlit as st
from streamlit_lightweight_charts import renderLightweightCharts

from settings import DEBUG, MODE, DUCKDB, BIGQUERY, START_DATE
from settings import SELECTED_TICKERS, ticker_sets

from load_duckdb import duckdb_connect, db_get_ticker_records
from load_bigquery import bigquery_connect, biqquery_get_ticker_records

COLOR_BULL = "rgba(38,166,154,0.9)"  # #26a69a
COLOR_BEAR = "rgba(239,83,80,0.9)"  # #ef5350

COLUMNS = ["open", "high", "low", "close", "volume", "ma_7", "ma_10", "ma_20", "ma_30", "ma_100", "macd", "rsi"] # "momentum", "volatility"


class DbConnector:
    def __init__(self, mode=MODE):
        self.mode = mode
        if self.mode == DUCKDB:
            con, tables = duckdb_connect()
            self.con = con
        elif self.mode == BIGQUERY:
            bq_client, dataset = bigquery_connect()
            self.bq_client = bq_client

    def get_ticker_records(self, table_name, ticker, start_date=START_DATE, end_date=None):
        if self.mode == DUCKDB:
            return db_get_ticker_records(self.con, table_name, ticker, start_date, end_date)
        elif self.mode == BIGQUERY:
            return biqquery_get_ticker_records(self.bq_client, table_name, ticker, start_date, end_date)


connection = DbConnector(MODE)


def print_log(message):
    print(message, flush=True)


def load_ticker_data(ticker):
    df = connection.get_ticker_records(table_name="tickers_data", ticker=ticker, start_date=START_DATE)
    print(list(df.columns))
    df.columns = ["time"] + COLUMNS # ! date should be the first column -> time
    print(df.head)
    # rename columns
    df["time"] = df["time"].dt.strftime("%Y-%m-%d")  # Date to string
    df["color"] = np.where(df["open"] > df["close"], COLOR_BEAR, COLOR_BULL)  # bull or bear
    df.ta.macd(close="close", fast=6, slow=12, signal=5, append=True)  # calculate macd
    return df


def chart_plotly(df1, df2, ticker1, ticker2, column):
    import plotly.express as px
    import plotly.graph_objs as go

    fig = go.Figure(
        [
            go.Scatter(
                name=ticker1,
                x=df1["time"],
                y=df1[column],
                # mode='markers',
                mode="lines",
                marker=dict(color="red"),
                line=dict(width=2),
                showlegend=True,
            ),
            go.Scatter(
                name=ticker2,
                x=df2["time"],
                y=df2[column],
                mode="lines",
                marker=dict(color="blue"),
                line=dict(width=2),
                showlegend=True,
            ),
        ]
    )
    fig.update_layout(yaxis_title=column, title=f"Comparison {ticker1} vs {ticker2}", hovermode="x")

    st.plotly_chart(fig)
    return


def chart_series_MACD(macd_fast, macd_slow, macd_hist):
    return [
        {"type": "Line", "data": macd_fast, "options": {"color": "blue", "lineWidth": 2}},
        {"type": "Line", "data": macd_slow, "options": {"color": "green", "lineWidth": 2}},
        {"type": "Histogram", "data": macd_hist, "options": {"color": "red", "lineWidth": 1}},
    ]


def chart_series_candlestick(ticker_data):
    return [
        {
            "type": "Candlestick",
            "data": ticker_data,
            "options": {
                "upColor": COLOR_BULL,
                "downColor": COLOR_BEAR,
                "borderVisible": False,
                "wickUpColor": COLOR_BULL,
                "wickDownColor": COLOR_BEAR,
            },
        }
    ]


def chart_options_MACD(ticker):
    return {
        "height": 200,
        "layout": {
            "background": {
                "type": "solid",
                "color": "#131722",
            },
            "textColor": "#d1d4dc",
        },
        "timeScale": {
            "visible": False,
        },
        "watermark": {
            "visible": True,
            "fontSize": 18,
            "horzAlign": "left",
            "vertAlign": "center",
            "color": "rgba(171, 71, 188, 0.7)",
            "text": f"MACD {ticker}",
        },
    }


def chart_options_candlestick(ticker):
    return {
        # "width": 800,
        "height": 300,
        "layout": {
            "background": {
                "type": "solid",
                "color": "#131722",
            },
            "textColor": "#d1d4dc",
        },
        "grid": {
            "vertLines": {"color": "rgba(197, 203, 206, 0.5)"},
            "horzLines": {"color": "rgba(197, 203, 206, 0.5)"},
        },
        "crosshair": {"mode": 0},
        "priceScale": {"borderColor": "rgba(197, 203, 206, 0.8)"},
        "timeScale": {"borderColor": "rgba(197, 203, 206, 0.8)", "barSpacing": 15},
        "watermark": {
            "visible": True,
            "fontSize": 48,
            "horzAlign": "center",
            "vertAlign": "center",
            "color": "rgba(171, 71, 188, 0.3)",
            "text": ticker,  # 'AAPL - D1',
        },
    }


def calculate_MACD(df):
    # export to JSON format
    candles = json.loads(df.to_json(orient="records"))
    macd_fast = json.loads(df.rename(columns={"MACD_6_12_5": "value"}).to_json(orient="records"))
    macd_slow = json.loads(df.rename(columns={"MACDs_6_12_5": "value"}).to_json(orient="records"))
    df["color"] = np.where(df["MACD_6_12_5"] > 0, COLOR_BULL, COLOR_BEAR)  # MACD histogram color
    macd_hist = json.loads(df.rename(columns={"MACDh_6_12_5": "value"}).to_json(orient="records"))
    return df, candles, macd_fast, macd_slow, macd_hist


def display_charts(ticker1, ticker2, column_choice):
    df1 = load_ticker_data(ticker1)
    df2 = load_ticker_data(ticker2)

    # Tile 1: simple comparison
    chart_plotly(df1, df2, ticker1, ticker2, column_choice)

    # Tile 2: advanced comparison
    df1, candles1, macd_fast1, macd_slow1, macd_hist1 = calculate_MACD(df1)
    df2, candles2, macd_fast2, macd_slow2, macd_hist2 = calculate_MACD(df2)

    renderLightweightCharts(
        [
            {
                "chart": chart_options_candlestick(ticker1),
                "series": chart_series_candlestick(candles1),
            },
            {
                "chart": chart_options_candlestick(ticker2),
                "series": chart_series_candlestick(candles2),
            },
            {"chart": chart_options_MACD(ticker1), "series": chart_series_MACD(macd_fast1, macd_slow1, macd_hist1)},
            {"chart": chart_options_MACD(ticker2), "series": chart_series_MACD(macd_fast2, macd_slow2, macd_hist2)},
        ],
        "multipane",
    )


def main():
    print_log("Starting the Stock market analysis application")
    st.set_page_config(
        page_title="Stock market data dashboard",
        page_icon="📊",  # 💹
        layout="wide",
        initial_sidebar_state="expanded",
        menu_items={
            "Get help": "https://github.com/dmytrovoytko/stock-market-data-engineering",
            "Report a bug": "https://github.com/dmytrovoytko/stock-market-data-engineering/issues",
            "About": "## Let's get insights from Stock market data!",
        },
    )
    st.title("📊 Stock market data dashboard")
    st.subheader("Let's get insights from Stock market data!", divider=True)

    col1, col2 = st.columns([3, 4])

    # Comparison column selection
    column_choice = col1.selectbox("Select column for comparison:", COLUMNS, index=min(4, len(COLUMNS) - 1))
    print_log(f"User selected column: {column_choice}")

    # User input
    user_input = col2.text_input("Choose 2 tickers to compare (space separated):", "AAPL MSFT")

    if st.button("⚖️ Analyze stocks"):
        print_log(f"User requested: {column_choice} '{user_input}'")
        with st.spinner("Processing..."):
            start_time = time.time()
            tickers = user_input.split()
            display_charts(tickers[0], tickers[1], column_choice)
            print_log(f"Building charts finished in {time.time() - start_time:.2f} seconds")
            st.success("Completed!")


print_log("Streamlit app loop completed")


if __name__ == "__main__":
    print_log("Stock market data analysis application started")
    main()
