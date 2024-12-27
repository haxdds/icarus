import pandas as pd
from datetime import datetime
from alpaca.trading.requests import (
    GetOrdersRequest,
    GetPortfolioHistoryRequest
)
from alpaca.trading.enums import (
    QueryOrderStatus
)
import streamlit as st  # In case you need st.warning or st.error

def get_account(trading_client):
    """Fetch account information from Alpaca."""
    try:
        account_info = trading_client.get_account()
        return account_info
    except Exception as e:
        st.error(f"Error fetching account information: {e}")
        return None

def get_order_history(trading_client):
    """Fetch and return a DataFrame of recent orders."""
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
                if order.submitted_at else "N/A"
        })
    
    return pd.DataFrame(order_data)

def get_active_positions(trading_client):
    """Fetch and return a DataFrame of open positions."""
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
        return pd.DataFrame(pos_data)
    except Exception as e:
        st.error(f"Error fetching active positions: {e}")
        return pd.DataFrame()

def get_account_balance(trading_client):
    """Build and return a DataFrame with key account metrics."""
    account_info = get_account(trading_client)
    if account_info:
        balance_data = {
            "Account ID": account_info.id,
            "Equity": float(account_info.equity),
            "Last Equity": float(account_info.last_equity),
            "Buying Power": float(account_info.buying_power),
            "Cash": float(account_info.cash)
        }
        df_balance = pd.DataFrame(
            list(balance_data.items()), 
            columns=['Metric', 'Value']
        )
        return df_balance
    else:
        return pd.DataFrame()

def get_portfolio_history(trading_client, period_days=5):
    """Fetch and return a DataFrame with portfolio history over given days."""
    from datetime import datetime
    try:
        history_filter = GetPortfolioHistoryRequest(
            timeframe="1Min",
            period=f"{period_days}D"  
        )
        portfolio_history = trading_client.get_portfolio_history(
            history_filter=history_filter
        )
        timestamps = portfolio_history.timestamp
        equity = portfolio_history.equity
        dates = [datetime.fromtimestamp(ts) for ts in timestamps]
        
        return pd.DataFrame({
            'Date': dates,
            'Equity': equity,
        })
    except Exception as e:
        st.error(f"Error fetching portfolio history: {e}")
        return pd.DataFrame()