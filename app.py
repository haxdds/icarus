import streamlit as st
import plotly.graph_objects as go
import os
from datetime import datetime, timedelta

# 1) Import your configuration (APIs, environment)
from config import API_KEYS, BASE_URL

# 2) Import the data-fetching methods
import data

# 3) Alpaca Client
from alpaca.trading.client import TradingClient

# -------------- Page Setup --------------

st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    /* Chart container to enforce ~80% vertical space */
    .chart-container {
        height: 5vh;
        overflow-y: scroll;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# -------------- Initialize Trading Clients in Session State --------------

if "trading_clients" not in st.session_state:
    st.session_state.trading_clients = {}
    for name, creds in API_KEYS.items():
        try:
            st.session_state.trading_clients[name] = TradingClient(
                api_key=creds['key'], 
                secret_key=creds['secret'], 
                paper=True
            )
        except Exception as e:
            st.error(f"Error initializing Alpaca Trading Client for {name}: {e}")

# -------------- Account Selector --------------

selected_account = st.selectbox(
    "Select Account",
    options=list(API_KEYS.keys()),
    key='account_selector'
)

trading_client = st.session_state.trading_clients[selected_account]

# -------------- Verify Account Info --------------

try:
    account = trading_client.get_account()
    st.caption(f"Account ID ({selected_account}): {account.id}")
except Exception as e:
    st.error(f"Error getting account info: {e}")
    st.stop()

# -------------- Title --------------

st.title("Alpaca Paper Trading Dashboard")

# ============== Layout Configuration ==============

col_ratio = 40
left_col, right_col = st.columns([col_ratio, 100 - col_ratio], gap="small")

# ============== Left Column (Account & Positions) ==============

with left_col:
    st.subheader("Account Overview")
    df_balance = data.get_account_balance(trading_client)
    if not df_balance.empty:
        for _, row in df_balance.iterrows():
            metric_label = str(row['Metric'])
            metric_value = row['Value']
            if metric_label.lower() in ["equity", "last equity", "buying power", "cash"]:
                st.metric(label=metric_label, value=f"${metric_value:,.2f}")
            else:
                st.write(f"**{metric_label}:** {metric_value}")
    else:
        st.warning("No balance data available.")
    
    st.markdown("---")
    st.subheader("Active Positions")
    df_positions = data.get_active_positions(trading_client)
    if not df_positions.empty:
        st.dataframe(df_positions)
    else:
        st.warning("No active positions available.")

# ============== Right Column (Chart & Orders) ==============

with right_col:
    st.subheader("Portfolio History (5 Days)")
    df_history = data.get_portfolio_history(trading_client, period_days=5)

    if df_history.empty:
        st.warning("No portfolio history data available.")
    else:
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=df_history['Date'],
                y=df_history['Equity'],
                mode='lines',
                name='Equity',
                line=dict(color='blue', width=2)
            ))
            fig.update_layout(
                title=f"Portfolio Equity Over Time (Past 5 Days) - {selected_account}",
                xaxis_title="Date",
                yaxis_title="Equity ($)",
                hovermode="x unified",
                xaxis_rangeslider_visible=True
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("---")
    st.subheader("Order History")
    df_orders = data.get_order_history(trading_client)
    if not df_orders.empty:
        st.dataframe(df_orders)
    else:
        st.warning("No order history data available.")

st.markdown("---")
st.markdown("Developed with ❤️ using Streamlit and Alpaca-py")