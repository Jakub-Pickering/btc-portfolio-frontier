An applied quantitative finance project analyzing how Bitcoin affects the efficiency of a traditional S&P 500 and Gold portfolio — using Python, portfolio theory, and visualization.

# btc-portfolio-frontier
Quant Project exploring Bitcoins impact on portfolio efficiency - risk, volatility, and diversification vs Gold and S&amp;P500.
#  Quant Project: Bitcoin, Risk, and Portfolio Diversification

This notebook explores how **Bitcoin (BTC)** affects the risk and return profile of a traditional portfolio consisting of the **S&P 500 (SPX)** and **Gold (GLD)**.

##  Key Sections
-  Data download using **Yahoo Finance** and **CCXT (Binance)**  
-  Log returns and rolling volatility  
-  Normalised price comparisons  
-  **Efficient frontier**: SPX+GOLD vs SPX+GOLD+BTC  
-  **Tangency (max-Sharpe)** portfolios & Capital Market Line  
-  **Monthly rebalancing** simulation (10bps transaction cost)  
-  **Intraday BTC volatility** patterns  
-  Rolling Sharpe ratios and correlation heatmaps  

##  Tech Stack
- Python, Pandas, NumPy, Matplotlib  
- SciPy (for portfolio optimisation)  
- Yahoo Finance & Binance (via CCXT)
 ## Demo
Try the interactive dashboard here: [Streamlit App](https://your-streamlit-link.streamlit.app)

Use the sliders to adjust BTC allocation, toggle shorting, and instantly see how the Efficient Frontier and Max Sharpe point shift.
## Insights
- Adding BTC improved the portfolio’s Sharpe ratio by ~15% in this sample.
- BTC’s low correlation with SPX/Gold provides diversification benefits.
- Higher BTC weights increase volatility — but also raise potential returns.



##  To Run
1. Clone the repo or download the notebook.  
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
