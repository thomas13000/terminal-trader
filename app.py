import streamlit as st
import streamlit.components.v1 as components
from google import genai
import pandas as pd

# ---------------------------------------------------------
# CONFIGURATION PAGE & STYLE BLOOMBERG
# ---------------------------------------------------------
st.set_page_config(
    page_title="TERMINAL TRADER PRO",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .block-container { padding-top: 4rem !important; padding-bottom: 0.8rem !important; }
    .stApp { background-color: #0c0f12; color: #d1d4dc; }
    h2, h3 { font-size: 0.85rem !important; font-weight: 600 !important; margin-top: 4px !important; margin-bottom: 4px !important; color: #848e9c !important; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# HORLOGES TEMPS RÉEL (JS)
# ---------------------------------------------------------
header_html = """
<style>
    body { margin: 0; padding: 2px; background-color: transparent; font-family: system-ui, sans-serif; overflow: hidden; }
    .header-box { display: flex; justify-content: space-between; align-items: center; background-color: #12161c; padding: 8px 16px; border: 1px solid #2a2e39; border-radius: 6px; }
    .header-title { font-size: 1.4rem; font-weight: 900; color: #f0b90b; margin: 0; }
    .clock-card { text-align: center; background-color: #171b21; padding: 4px 12px; border-radius: 4px; border: 1px solid #2a2e39; min-width: 95px; }
    .clock-label { font-size: 0.65rem; color: #848e9c; font-weight: bold; }
    .clock-time { font-size: 1.1rem; color: #00ff88; font-weight: bold; font-family: monospace; }
</style>

<div class="header-box">
    <div class="header-title">⚡ TERMINAL TRADER PRO</div>
    <div style="display: flex; gap: 12px;">
        <div class="clock-card">
            <div class="clock-label">PARIS</div>
            <div id="clock-paris" class="clock-time">--:--:--</div>
        </div>
        <div class="clock-card">
            <div class="clock-label">NEW YORK</div>
            <div id="clock-ny" class="clock-time">--:--:--</div>
        </div>
    </div>
</div>

<script>
    function updateClocks() {
        const now = new Date();
        document.getElementById('clock-paris').textContent = new Intl.DateTimeFormat('fr-FR', { timeZone: 'Europe/Paris', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }).format(now);
        document.getElementById('clock-ny').textContent = new Intl.DateTimeFormat('en-US', { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }).format(now);
    }
    setInterval(updateClocks, 1000);
    updateClocks();
</script>
"""
components.html(header_html, height=75)

# ---------------------------------------------------------
# BANDEAU DÉFILANT D'ALERTE MACRO
# ---------------------------------------------------------
texte_alerte = "🚨 ALERTE MACRO : Publication NFP & Taux de chômage US à 14:30 — Risque de volatilité extrême sur USD, Or et S&P 500 !"

st.markdown(f"""
<div style="background-color: rgba(255, 59, 48, 0.15); border: 1px solid #ff3b30; border-radius: 4px; padding: 4px 8px; margin-bottom: 8px;">
    <marquee behavior="scroll" direction="left" scrollamount="7" style="color: #ffffff; font-weight: bold; font-size: 0.82rem; display: flex; align-items: center;">
        <span style="background-color: #ff3b30; color: #ffffff; padding: 2px 6px; border-radius: 3px; margin-right: 10px; font-size: 0.68rem; font-weight: 900;">HIGH IMPACT</span>
        {texte_alerte}
    </marquee>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# MARKET DATA STREAMING TEMPS RÉEL (TRADINGVIEW TICKER TAPE)
# ---------------------------------------------------------
ticker_tape_html = """
<div class="tradingview-widget-container">
  <div class="tradingview-widget-container__widget"></div>
  <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-ticker-tape.js" async>
  {
  "symbols": [
    { "proName": "FOREXCOM:SPXUSD", "title": "S&P 500" },
    { "proName": "FOREXCOM:NSXUSD", "title": "US 100" },
    { "proName": "FX_IDC:EURUSD", "title": "EUR/USD" },
    { "proName": "BITSTAMP:BTCUSD", "title": "Bitcoin" },
    { "proName": "OANDA:XAUUSD", "title": "Gold" },
    { "proName": "TVC:US10Y", "title": "US 10Y" },
    { "proName": "TVC:VIX", "title": "VIX" }
  ],
  "showSymbolLogo": true,
  "isTransparent": true,
  "displayMode": "adaptive",
  "colorTheme": "dark",
  "locale": "fr"
}
  </script>
</div>
"""
components.html(ticker_tape_html, height=50)

st.divider()

# ---------------------------------------------------------
# LAYOUT PRINCIPAL (3 COLONNES)
# ---------------------------------------------------------
c_left, c_center, c_right = st.columns([1.1, 1.3, 1.1])

# --- COLONNE GAUCHE : WATCHLIST TRADINGVIEW LIVE ---
with c_left:
    st.subheader("📊 MARCHÉS & ACTIONS LIVE")
    market_overview_html = """
    <div class="tradingview-widget-container" style="height: 520px;">
      <div class="tradingview-widget-container__widget" style="height: 520px;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-market-overview.js" async>
      {
      "colorTheme": "dark",
      "dateRange": "1D",
      "showChart": false,
      "locale": "fr",
      "largeChartUrl": "",
      "isTransparent": true,
      "showSymbolLogo": true,
      "width": "100%",
      "height": "520",
      "tabs": [
        {
          "title": "Top Tech",
          "symbols": [
            {"s": "NASDAQ:NVDA", "d": "NVIDIA"},
            {"s": "NASDAQ:AAPL", "d": "Apple"},
            {"s": "NASDAQ:MSFT", "d": "Microsoft"},
            {"s": "NASDAQ:TSLA", "d": "Tesla"},
            {"s": "NASDAQ:AMD", "d": "AMD"}
          ]
        },
        {
          "title": "Indices",
          "symbols": [
            {"s": "FOREXCOM:SPXUSD", "d": "S&P 500"},
            {"s": "FOREXCOM:NSXUSD", "d": "Nasdaq 100"},
            {"s": "INDEX:BTCUSD", "d": "Bitcoin"}
          ]
        }
      ]
    }
      </script>
    </div>
    """
    components.html(market_overview_html, height=525)

# --- COLONNE CENTRALE : CALENDRIER TRADINGVIEW ---
with c_center:
    st.subheader("🔴 CALENDRIER ÉCONOMIQUE")
    tv_widget = """
    <div class="tradingview-widget-container" style="width: 100%; height: 520px;">
      <div class="tradingview-widget-container__widget" style="width: 100%; height: 520px;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
      {
      "colorTheme": "dark",
      "isTransparent": true,
      "width": "100%",
      "height": "520",
      "locale": "fr",
      "importanceFilter": "0,1",
      "currencyFilter": "USD,EUR,GBP,JPY,CAD,AUD,CHF"
    }
      </script>
    </div>
    """
    components.html(tv_widget, height=525)

# --- COLONNE DROITE : IA & MACRO ---
with c_right:
    st.subheader("🌐 MACRO & FOREX LIVE")
    forex_cross_html = """
    <div class="tradingview-widget-container" style="height: 300px;">
      <div class="tradingview-widget-container__widget" style="height: 300px;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-forex-cross-rates.js" async>
      {
      "width": "100%",
      "height": "300",
      "currencies": ["EUR", "USD", "JPY", "GBP", "CHF"],
      "isTransparent": true,
      "colorTheme": "dark",
      "locale": "fr"
    }
      </script>
    </div>
    """
    components.html(forex_cross_html, height=305)

    st.subheader("💬 Prompt IA Macro")
    def query_gemini(prompt):
        if "GEMINI_API_KEY" not in st.secrets:
            return "Clé API Gemini non configurée."
        try:
            client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
            res = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
            return res.text
        except Exception as e:
            return f"Erreur IA : {e}"

    user_q = st.text_input("Question :", placeholder="Ex : Impact NFP ?", label_visibility="collapsed")
    if user_q:
        with st.spinner("Analyse..."):
            st.info(query_gemini(f"Expert macro trading, réponds très court : {user_q}"))
