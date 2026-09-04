import streamlit as st
import yfinance as yf
import pandas as pd

# ---------------------------------------------------------
# CONFIGURATION ET STYLE BLOOMBERG DARK MODE
# ---------------------------------------------------------
st.set_page_config(
    page_title="Terminal Trader Pro",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Style CSS personnalisé (Bloomberg Dark / Neon Green & Red)
st.markdown("""
<style>
    .stApp {
        background-color: #0c0f12;
        color: #d1d4dc;
    }
    .metric-card {
        background-color: #171b21;
        border-radius: 6px;
        padding: 12px;
        border: 1px solid #2a2e39;
        text-align: center;
    }
    .metric-title {
        color: #848e9c;
        font-size: 0.85rem;
        font-weight: 600;
        margin-bottom: 4px;
    }
    .metric-value {
        font-size: 1.3rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# EN-TÊTE DU TERMINAL
# ---------------------------------------------------------
st.title("⚡ TERMINAL TRADER PRO — AI POWERS")

# ---------------------------------------------------------
# 1. BANDEAU TICKEUR EN DIRECT (S&P 500, Nasdaq, DXY, Or, VIX)
# ---------------------------------------------------------
st.subheader("📊 Marché en Direct")

@st.cache_data(ttl=60)
def fetch_market_data():
    tickers = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "US Dollar (DXY)": "DX-Y.NYB",
        "Or (Gold)": "GC=F",
        "VIX Volatilité": "^VIX"
    }
    data = {}
    for name, ticker in tickers.items():
        try:
            df = yf.Ticker(ticker).history(period="2d")
            if len(df) >= 2:
                current = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                change = ((current - prev) / prev) * 100
                data[name] = (current, change)
            elif len(df) == 1:
                data[name] = (df['Close'].iloc[-1], 0.0)
        except Exception:
            pass
    return data

market_data = fetch_market_data()

if market_data:
    cols = st.columns(len(market_data))
    for i, (name, (val, chg)) in enumerate(market_data.items()):
        with cols[i]:
            color = "#00ff88" if chg >= 0 else "#ff4d4d"
            sign = "+" if chg >= 0 else ""
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{name}</div>
                <div class="metric-value" style="color: {color};">{val:,.2f}</div>
                <div style="color: {color}; font-size: 0.8rem; margin-top: 2px;">{sign}{chg:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# 2. DISPOSITION EN COLONNES DES MODULES
# ---------------------------------------------------------
col_left, col_center, col_right = st.columns([1, 1.2, 1])

with col_left:
    st.subheader("📈 Heatmap & Screener (Finviz)")
    st.info("⚙️ Module Finviz en cours de préparation...")

with col_center:
    st.subheader("📰 Actualités Live & IA (FinancialJuice)")
    st.info("⚙️ Module IA & Flux d'actualités en cours de préparation...")

with col_right:
    st.subheader("🌐 Macro & Calendrier Éco (Bloomberg)")
    st.info("⚙️ Module Macro en cours de préparation...")
