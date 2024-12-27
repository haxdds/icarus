import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest, GetPortfolioHistoryRequest
from alpaca.trading.enums import OrderStatus, QueryOrderStatus

# 1. Set page config to wide layout
st.set_page_config(layout="wide")

# 2. Load environment variables from .env file
load_dotenv()

# 3. Apply custom page styling
st.markdown(
    """
    <style>
    /* Chart container to enforce ~80% vertical space */
    .chart-container {
        height: 5vh;
        overflow-y: scroll; /* In case the chart is taller than the container */
    }
    </style>
    """,
    unsafe_allow_html=True
)

# 4. Alpaca API credentials
API_KEYS = {
    'H1': {'key': os.getenv("H1_API_KEY"), 'secret': os.getenv("H1_API_SECRET")},
    'H2': {'key': os.getenv("H2_API_KEY"), 'secret': os.getenv("H2_API_SECRET")},
    'H3': {'key': os.getenv("H3_API_KEY"), 'secret': os.getenv("H3_API_SECRET")},
    'R1': {'key': os.getenv("R1_API_KEY"), 'secret': os.getenv("R1_API_SECRET")},
    'R2': {'key': os.getenv("R2_API_KEY"), 'secret': os.getenv("R2_API_SECRET")},
    'R3': {'key': os.getenv("R3_API_KEY"), 'secret': os.getenv("R3_API_SECRET")}
}
BASE_URL = "https://paper-api.alpaca.markets"  # Paper trading URL

# Initialize session state for trading clients if not exists
if 'trading_clients' not in st.session_state:
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

# Add account selector dropdown
selected_account = st.selectbox(
    "Select Account",
    options=list(API_KEYS.keys()),
    key='account_selector'
)

# Get current trading client
trading_client = st.session_state.trading_clients[selected_account]

# 6. Display Account ID
try:
    account = trading_client.get_account()
    st.caption(f"Account ID ({selected_account}): {account.id}")
except Exception as e:
    st.error(f"Error getting account info: {e}")
    st.stop()

# 7. Page Title
st.title("Alpaca Paper Trading Dashboard")

# ---------------------------
# Data-Fetching Functions
# ---------------------------

def get_account():
    try:
        account_info = trading_client.get_account()
        return account_info
    except Exception as e:
        st.error(f"Error fetching account information: {e}")
        return None

def get_order_history():
    request_params = GetOrdersRequest(
        status=QueryOrderStatus.ALL,
        limit=100,
        after=None,
        until=None
    )
    orders = trading_client.get_orders(filter=request_params)
    
    order_data = []
    for order in orders:
        order_data.append({
            "ID": order.id,
            "Symbol": order.symbol,
            "Type": order.order_type.value,
            "Side": order.side.value,
            "Qty": order.qty,
            "Filled": order.filled_qty,
            "Status": order.status.value,
            "Submitted At": order.submitted_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    
    df_orders = pd.DataFrame(order_data)
    return df_orders

def get_active_positions():
    try:
        positions = trading_client.get_all_positions()
        pos_data = []
        for pos in positions:
            pos_data.append({
                "Symbol": pos.symbol,
                "Qty": pos.qty,
                "Market Value": float(pos.market_value),
                "Cost Basis": float(pos.cost_basis),
                "Unrealized P/L": float(pos.unrealized_pl),
                "Change (%)": float(pos.unrealized_plpc) * 100
            })
        df_positions = pd.DataFrame(pos_data)
        return df_positions
    except Exception as e:
        st.error(f"Error fetching active positions: {e}")
        return pd.DataFrame()

def get_account_balance():
    account_info = get_account()
    if account_info:
        balance_data = {
            "Account ID": account_info.id,
            "Equity": float(account_info.equity),
            "Last Equity": float(account_info.last_equity),
            "Buying Power": float(account_info.buying_power),
            "Cash": float(account_info.cash)
        }
        df_balance = pd.DataFrame(list(balance_data.items()), columns=['Metric', 'Value'])
        return df_balance
    else:
        return pd.DataFrame()

def get_portfolio_history(period_start, period_end):
    """
    Fetches portfolio history with a fixed timeframe (1Min) & period (5D).
    Modify as needed for actual usage.
    """
    try:
        history_filter = GetPortfolioHistoryRequest(
            timeframe="1Min",
            period="5D"
        )
        portfolio_history = trading_client.get_portfolio_history(history_filter=history_filter)
        
        timestamps = portfolio_history.timestamp
        equity = portfolio_history.equity
    
        dates = [datetime.fromtimestamp(ts) for ts in timestamps]
        
        df_history = pd.DataFrame({
            'Date': dates,
            'Equity': equity,
        })
        return df_history
    except Exception as e:
        st.error(f"Error fetching portfolio history: {e}")
        return pd.DataFrame()

# ---------------------------
# Layout Configuration
# ---------------------------

# 8. Create a slider to control the relative width of the two columns
col_ratio = 40  # 40% left, 60% right by default
# col_ratio = st.slider(
#     "Adjust Column Width (%)",
#     min_value=10,
#     max_value=90,
#     value=default_ratio,
#     help="Adjust the width of the left column relative to the right column."
# )

# Convert ratio to floats for columns
left_col_width = col_ratio
right_col_width = 100 - col_ratio

# 9. Create two columns with dynamic width
left_col, right_col = st.columns([left_col_width, right_col_width], gap="small")

# ---------------------------
# Left Column (Account & Positions)
# ---------------------------
with left_col:
    st.subheader("Account Overview")
    df_balance = get_account_balance()
    if not df_balance.empty:
        # Display account metrics
        for _, row in df_balance.iterrows():
            metric_label = str(row['Metric'])
            metric_value = row['Value']
            # Format currency or ID
            if metric_label.lower() in ["equity", "last equity", "buying power", "cash"]:
                st.metric(label=metric_label, value=f"${metric_value:,.2f}")
            else:
                st.write(f"**{metric_label}:** {metric_value}")

    st.markdown("---")
    st.subheader("Active Positions")
    df_positions = get_active_positions()
    if not df_positions.empty:
        st.dataframe(df_positions)
    else:
        st.warning("No active positions available.")

# ---------------------------
# Right Column (Chart & Orders)
# ---------------------------
with right_col:
    st.subheader("Portfolio History (5 Days)")
    # Fetch 5-day history data
    end_date = datetime.now()
    start_date = end_date - timedelta(days=5)
    df_history = get_portfolio_history(period_start=start_date, period_end=end_date)

    if df_history.empty:
        st.warning("No portfolio history data available.")
    else:
        # 10. Make a container to enforce ~80% vertical space for the chart
        with st.container():
            st.markdown('<div class="chart-container">', unsafe_allow_html=True)
            
            # Plotly Chart
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
    df_orders = get_order_history()
    if not df_orders.empty:
        st.dataframe(df_orders)
    else:
        st.warning("No order history data available.")

# Footer
st.markdown("---")
st.markdown("Developed with ❤️ using Streamlit and Alpaca-py")