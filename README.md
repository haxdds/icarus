# Icarus - Alpaca Paper Trading Dashboard

A Streamlit-based dashboard for monitoring and managing multiple Alpaca paper trading accounts. Built with Python, this application provides real-time portfolio tracking, order management, and performance visualization.

[https://icarus-zv9z2tuk8uwdxfq2mwab8b.streamlit.app/](https://icarus-zv9z2tuk8uwdxfq2mwab8b.streamlit.app/)
```

## Features

- Multi-account support with easy account switching
- Real-time account balance and portfolio metrics
- Active positions monitoring
- 5-day portfolio history visualization using Plotly
- Comprehensive order history tracking
- Clean, responsive interface built with Streamlit

## Setup

1. Clone this repository
2. Install requirements:
   ```bash
   pip install streamlit pandas plotly alpaca-py python-dotenv
   ```
3. Create a `.env` file with your Alpaca API credentials:
   ```
   H1_API_KEY=your_key_here
   H1_API_SECRET=your_secret_here
   # Add additional account credentials as needed
   ```
4. Run the dashboard:
   ```bash
   streamlit run dashboard.py
   ```

## Environment Variables

The application expects Alpaca API credentials for multiple accounts (H1, H2, H3, R1, R2, R3) to be set in the `.env` file.

## Contributing

Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.
# Alpaca Trading Dashboard
