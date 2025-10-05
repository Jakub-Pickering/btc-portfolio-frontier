import numpy as np, pandas as pd, plotly.graph_objects as go, streamlit as st
from scipy.optimize import minimize
import yfinance as yf

st.set_page_config(layout="wide")
st.title("Efficient Frontier — BTC / SPX / GOLD")

# Sidebar controls
years = st.sidebar.slider("History length (years)", 2, 10, 5)
rf = st.sidebar.number_input("Risk-free rate (annual %)", 0.0, 10.0, 0.0, step=0.25) / 100.0
allow_short = st.sidebar.checkbox("Allow shorting?", value=False)
btc_cap = st.sidebar.slider("BTC max allocation", 0.0, 0.65, 0.65)
n_pts = st.sidebar.slider("Frontier resolution", 10, 120, 60)
st.sidebar.caption("Tip: Use the BTC cap to see how the frontier and Max-Sharpe shift.")

# Placeholder so main area is never blank
ph = st.empty()
ph.line_chart({"loading":[0,1,0]})

@st.cache_data(show_spinner=False)
def load_prices(years: int) -> pd.DataFrame:
    tickers = ["BTC-USD","^GSPC","GLD"]
    df = yf.download(tickers, period=f"{years}y", interval="1d", auto_adjust=True)["Close"]
    df = df.rename(columns={"BTC-USD":"BTC","^GSPC":"SPX","GLD":"GOLD"}).dropna()
    return df

try:
    prices = load_prices(years)
    rets = np.log(prices / prices.shift(1)).dropna()

    mu = rets.mean().values * 252
    cov = rets.cov().values * 252
    labels = rets.columns.to_list()
    idx = {a:i for i,a in enumerate(labels)}

    def port_stats(w):
        r = float(w @ mu)
        v = float((w @ cov @ w)**0.5)
        s = (r - rf)/v if v>0 else np.nan
        return r, v, s

    def neg_sharpe(w):  # minimize negative Sharpe
        r, v, _ = port_stats(w)
        return -(r - rf)/v if v>0 else 1e9

    bounds = [(0.0, 1.0) if not allow_short else (-1.0, 1.0) for _ in labels]
    # apply BTC cap by shrinking upper bound
    b_lo, b_hi = bounds[idx["BTC"]]
    bounds[idx["BTC"]] = (b_lo, min(b_hi, btc_cap))

    cons = [{"type":"eq","fun":lambda w: np.sum(w)-1.0}]

    # Sweep target returns between min/max asset means within cap
    t_min, t_max = mu.min(), mu.max()
    targets = np.linspace(t_min, t_max, n_pts)

    ef = []
    for t in targets:
        # minimize vol given target return
        cons_t = cons + [{"type":"eq","fun":lambda w, t=t: w @ mu - t}]
        w0 = np.repeat(1/len(labels), len(labels))
        try:
            res = minimize(lambda w: float((w @ cov @ w)**0.5),
                           w0, method="SLSQP", bounds=bounds, constraints=cons_t,
                           options={"maxiter": 10_000})
            if res.success and np.isfinite(res.fun):
                w = res.x
                r, v, s = port_stats(w)
                ef.append({"AnnVol": v*100, "AnnRet": r*100, "Sharpe": s,
                           **{labels[i]: w[i] for i in range(len(labels))}})
        except Exception as e:
            st.toast(f"Optimizer warning at target {t:.2%}: {e}", icon="⚠️")

    fig = go.Figure()
    fig.update_layout(template="plotly_white",
                      xaxis_title="Annualised Volatility (%)",
                      yaxis_title="Annualised Return (%)",
                      legend_title=None)

    # Always show assets scatter as baseline
    asset_vol = (rets.std().values * np.sqrt(252))*100
    asset_ret = (rets.mean().values * 252)*100
    for a, x, y in zip(labels, asset_vol, asset_ret):
        fig.add_scatter(x=[x], y=[y], mode="markers+text", name=a, text=[a],
                        textposition="top center")

    if ef:
        efdf = pd.DataFrame(ef).sort_values("AnnVol")
        fig.add_scatter(x=efdf["AnnVol"], y=efdf["AnnRet"],
                        mode="lines+markers", name="Efficient Frontier")
        # Max-Sharpe highlight
        best = efdf.loc[efdf["Sharpe"].idxmax()]
        fig.add_scatter(x=[best["AnnVol"]], y=[best["AnnRet"]],
                        mode="markers", name=f"Max-Sharpe (S={best['Sharpe']:.2f})",
                        marker=dict(size=12, symbol="star"))
        st.caption(
            f"Return: {best['AnnRet']:.2f}%,  Vol: {best['AnnVol']:.2f}%,  "
            f"Sharpe: {best['Sharpe']:.2f} | "
            f"Weights — BTC: {best['BTC']:.0%}, SPX: {best['SPX']:.0%}, GOLD: {best['GOLD']:.0%}"
        )
    else:
        st.warning("No feasible frontier points with the current constraints. "
                   "Try increasing history length, allowing shorting, or raising the BTC cap.")

    ph.plotly_chart(fig, use_container_width=True)

    with st.expander("Data sanity"):
        st.write("Rows:", len(rets))
        st.dataframe(prices.tail())

except Exception as e:
   
