# app.py — Streamlit dashboard หลัก
# รัน: streamlit run app.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

from config import WATCHLIST
from data import get_price_history
from fundamental import get_fundamentals
from technical import get_technicals
from scoring import score_total

st.set_page_config(page_title="Stock Analyzer", layout="wide")

# ---- Sidebar: watchlist ----
st.sidebar.title("Stock Analyzer")
custom = st.sidebar.text_area(
    "Watchlist (หนึ่ง ticker ต่อบรรทัด)",
    value="\n".join(WATCHLIST),
    height=200,
)
watchlist = [t.strip().upper() for t in custom.splitlines() if t.strip()]

page = st.sidebar.radio("หน้า", ["ดูทีละตัว", "Screener", "Scoring"])

# ==============================================================
# หน้า 1: ดูทีละตัว
# ==============================================================
if page == "ดูทีละตัว":
    ticker = st.sidebar.selectbox("เลือกหุ้น", watchlist)
    st.title(f"วิเคราะห์ {ticker}")

    with st.spinner("กำลังโหลดข้อมูล..."):
        fund = get_fundamentals(ticker)
        tech = get_technicals(ticker)
        scores = score_total(fund, tech)

    # ---- ข้อมูลทั่วไป ----
    st.subheader(fund.get("name", ticker))
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("ราคา", f"${fund.get('price', 'N/A')}")
    col2.metric("Market Cap", _fmt_mcap(fund.get("market_cap")))
    col3.metric("Sector", fund.get("sector", "N/A"))
    col4.metric("P/E (Trailing)", _fmt(fund.get("pe_trailing")))

    st.divider()

    # ---- คะแนน ----
    st.subheader("คะแนน")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Growth", f"{scores['growth']}/10")
    c2.metric("Technical", f"{scores['technical']}/10")
    c3.metric("Valuation", f"{scores['valuation']}/10")
    c4.metric("รวม", f"{scores['total']}/10")

    st.divider()

    # ---- Fundamentals ----
    st.subheader("Fundamentals")
    fc1, fc2 = st.columns(2)
    with fc1:
        st.markdown("**Growth**")
        st.write(f"Revenue Growth: {_pct(fund.get('revenue_growth'))}")
        st.write(f"EPS Growth: {_pct(fund.get('eps_growth'))}")
        st.write(f"PEG: {_fmt(fund.get('peg'))}")
    with fc2:
        st.markdown("**Margins & ROE**")
        st.write(f"Gross Margin: {_pct(fund.get('gross_margin'))}")
        st.write(f"Operating Margin: {_pct(fund.get('operating_margin'))}")
        st.write(f"Net Margin: {_pct(fund.get('net_margin'))}")
        st.write(f"ROE: {_pct(fund.get('roe'))}")

    st.divider()

    # ---- กราฟราคา + MA ----
    st.subheader("กราฟราคา + Moving Averages")
    df = tech.get("df_price", pd.DataFrame())
    if not df.empty:
        fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                            row_heights=[0.7, 0.3],
                            subplot_titles=("Price + MA", "MACD"))

        close = df["Close"].squeeze()
        fig.add_trace(go.Scatter(x=df.index, y=close, name="Price", line=dict(color="#1f77b4")), row=1, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MA50"], name="MA50", line=dict(dash="dot", color="orange")), row=1, col=1)
        if df["MA200"].notna().any():
            fig.add_trace(go.Scatter(x=df.index, y=df["MA200"], name="MA200", line=dict(dash="dot", color="red")), row=1, col=1)

        # MACD
        colors = ["green" if v >= 0 else "red" for v in df["Histogram"]]
        fig.add_trace(go.Bar(x=df.index, y=df["Histogram"], name="Histogram", marker_color=colors), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["MACD"], name="MACD", line=dict(color="#1f77b4")), row=2, col=1)
        fig.add_trace(go.Scatter(x=df.index, y=df["Signal"], name="Signal", line=dict(color="orange")), row=2, col=1)

        fig.update_layout(height=600, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

    # ---- Technical summary ----
    st.subheader("Technical")
    tc1, tc2, tc3 = st.columns(3)
    tc1.metric("Price vs MA50", _pct(tech.get("price_vs_ma50")))
    tc2.metric("Price vs MA200", _pct(tech.get("price_vs_ma200")))
    tc3.metric("MACD Signal", "Bullish" if tech.get("macd_bullish") else "Bearish")


# ==============================================================
# หน้า 2: Screener
# ==============================================================
elif page == "Screener":
    st.title("Screener")
    st.info("กรองหุ้นตาม criteria ที่กำหนด")

    # Filter controls
    min_rev_growth = st.slider("Revenue Growth ขั้นต่ำ (%)", -50, 100, 10)
    max_peg = st.slider("PEG สูงสุด", 0.0, 5.0, 2.5, 0.1)
    only_macd_bullish = st.checkbox("MACD Bullish เท่านั้น", value=False)

    if st.button("Run Screener"):
        rows = []
        progress = st.progress(0)
        for i, t in enumerate(watchlist):
            try:
                fund = get_fundamentals(t)
                tech = get_technicals(t)
                rows.append({
                    "Ticker": t,
                    "Name": fund.get("name", t)[:30],
                    "Price": fund.get("price"),
                    "Rev Growth %": fund.get("revenue_growth"),
                    "EPS Growth %": fund.get("eps_growth"),
                    "PEG": fund.get("peg"),
                    "Net Margin %": fund.get("net_margin"),
                    "MACD Bullish": tech.get("macd_bullish"),
                    "vs MA50 %": tech.get("price_vs_ma50"),
                })
            except Exception as e:
                st.warning(f"{t}: {e}")
            progress.progress((i + 1) / len(watchlist))

        df = pd.DataFrame(rows)

        # Apply filters
        if "Rev Growth %" in df.columns:
            df = df[df["Rev Growth %"].fillna(-999) >= min_rev_growth]
        if "PEG" in df.columns:
            df = df[df["PEG"].fillna(999) <= max_peg]
        if only_macd_bullish:
            df = df[df["MACD Bullish"] == True]

        st.dataframe(df.reset_index(drop=True), use_container_width=True)


# ==============================================================
# หน้า 3: Scoring
# ==============================================================
elif page == "Scoring":
    st.title("Scoring — ภาพรวม Watchlist")

    if st.button("คำนวณคะแนนทั้งหมด"):
        rows = []
        progress = st.progress(0)
        for i, t in enumerate(watchlist):
            try:
                fund = get_fundamentals(t)
                tech = get_technicals(t)
                s = score_total(fund, tech)
                rows.append({
                    "Ticker": t,
                    "Name": fund.get("name", t)[:25],
                    "Growth": s["growth"],
                    "Technical": s["technical"],
                    "Valuation": s["valuation"],
                    "Total": s["total"],
                })
            except Exception as e:
                st.warning(f"{t}: {e}")
            progress.progress((i + 1) / len(watchlist))

        df = pd.DataFrame(rows).sort_values("Total", ascending=False).reset_index(drop=True)
        st.dataframe(
            df.style.background_gradient(subset=["Total", "Growth", "Technical", "Valuation"], cmap="RdYlGn"),
            use_container_width=True,
        )

        # Bar chart top 10
        top = df.head(10)
        fig = go.Figure()
        fig.add_bar(name="Growth", x=top["Ticker"], y=top["Growth"])
        fig.add_bar(name="Technical", x=top["Ticker"], y=top["Technical"])
        fig.add_bar(name="Valuation", x=top["Ticker"], y=top["Valuation"])
        fig.update_layout(barmode="group", title="Top 10 — คะแนนแยกด้าน", yaxis_range=[0, 10])
        st.plotly_chart(fig, use_container_width=True)


# ---- Helper formatters ----
def _fmt(val, decimals=2) -> str:
    if val is None:
        return "N/A"
    return f"{val:.{decimals}f}"


def _pct(val) -> str:
    if val is None:
        return "N/A"
    return f"{val:+.2f}%"


def _fmt_mcap(val) -> str:
    if val is None:
        return "N/A"
    if val >= 1e12:
        return f"${val/1e12:.1f}T"
    if val >= 1e9:
        return f"${val/1e9:.1f}B"
    return f"${val/1e6:.1f}M"
