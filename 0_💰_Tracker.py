import numpy as np
import pandas as pd
import streamlit as st
from alphalib.tracker import load_portfolio, refresh_porfolio, save_portfolio
from streamlit.logger import get_logger

st.set_page_config(
    page_title="Stock Tracker",
    layout="wide",
    initial_sidebar_state="expanded",
    page_icon="💰",
)

LOGGER = get_logger(__name__)


def footer():
    hide_streamlit_style = """
                <style>
                #MainMenu {visibility: visible;}
                footer {visibility: hidden;}
                </style>
                """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True)


def sidebar():
    st.markdown(
        """
        <style>
            [data-testid="stSidebarNav"]::before {
                content: "Alphalib";
                margin-left: 20px;
                margin-top: 20px;
                font-size: 30px;
                position: relative;
                top: 10px;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )


def save():
    portfolio = st.session_state.portfolio
    portfolio.sort_values(by="symbol", inplace=True)
    portfolio.replace("{}", np.nan, inplace=True)
    save_portfolio(portfolio)
    st.success(f"Saved {len(portfolio)} records!")


def refresh():
    st.info("Refreshing portfolio...")
    refresh_porfolio(st.session_state.portfolio)
    st.rerun()


def content():
    st.title("Stock Tracker")
    portfolio = load_portfolio()
    with st.form("portfolio_form"):
        with st.container():
            col1, col2, _, _ = st.columns([2, 2, 1, 4])
            with col1:
                if st.form_submit_button("Refresh", use_container_width=True):
                    refresh()
            with col2:
                if st.form_submit_button("Save", use_container_width=True):
                    save()
    with st.container():
        data = st.data_editor(
            portfolio,
            num_rows="dynamic",
            use_container_width=True,
            column_config={
                "nasdaq_url": st.column_config.LinkColumn(),
                "yahoo_finance_url": st.column_config.LinkColumn(),
            },
            height=600,
            key="portfolio_editor",
        )
        st.session_state.portfolio = data


def app():
    sidebar()
    content()
    footer()


if __name__ == "__main__":
    app()
