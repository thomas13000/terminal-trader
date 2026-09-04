import streamlit as st
import streamlit.components.v1 as components
from google import genai
import yfinance as yf
import pandas as pd

# ---------------------------------------------------------
# CONFIGURATION PAGE & STYLE BASE
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
# BANDEAU DÉFILANT D'ALERTE MACRO (ROUGE BLOOMBERG)
# ---------------------------------------------------------
texte_alerte = "🚨 ALERTE MACRO : Publication NFP & Taux de chômage US à 14:30 — Risque de volatilité extrême sur USD, Or et S&P 500 !"

st.markdown(f"""
<div style="background-color: rgba(255, 59, 48, 0.15); border: 1px solid #ff3b30; border-radius: 4px; padding: 4px 8px; margin-bottom: 12px;">
    <marquee behavior="scroll" direction="left" scrollamount="7" style="color: #ffffff; font-weight: bold; font-size: 0.82rem; display: flex; align-items: center;">
        <span style="background-color: #ff3b30; color: #ffffff; padding: 2px 6px; border-radius: 3px; margin-right: 10px; font-size: 0.68rem; font-weight: 900;">HIGH IMPACT</span>
        {texte_alerte}
    </marquee>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GEMINI IA (gemini-3.6-flash)
# ---------------------------------------------------------
def query_gemini(prompt):
    if "GEMINI_API_KEY" not in st.secrets:
        return "Clé API Gemini non configurée."
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        res = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
        return res.text
    except Exception as e:
        return f"Erreur IA : {e}"

# ---------------------------------------------------------
# LAYOUT PRINCIPAL (STRUCTURE 2 COLONNES)
# ---------------------------------------------------------
col_main, col_side = st.columns([2.2, 1])

# --- COLONNE PRINCIPALE : FINVIZ HEATMAP ---
with col_main:
    st.subheader("🔥 FINVIZ S&P 500 MAP")
    
    # Intégration directe de la Heatmap Finviz
    finviz_url = "https://finviz.com/map.ashx?t=sec"
    components.iframe(finviz_url, height=650, scrolling=True)

# --- COLONNE SECONDAIRE : MACRO, CALENDRIER & IA ---
with col_side:
    st.subheader("🔴 CALENDRIER ÉCONOMIQUE")
    tv_widget = """
    <div class="tradingview-widget-container" style="width: 100%; height: 320px;">
      <div class="tradingview-widget-container__widget" style="width: 100%; height: 320px;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
      {
      "colorTheme": "dark",
      "isTransparent": true,
      "width": "100%",
      "height": "320",
      "locale": "fr",
      "importanceFilter": "0,1",
      "currencyFilter": "USD,EUR,GBP"
    }
      </script>
    </div>
    """
    components.html(tv_widget, height=325)

    st.divider()

    st.subheader("💬 PROMPT IA MACRO")
    user_q = st.text_input("Question :", placeholder="Ex : Impact NFP ?", label_visibility="collapsed")
    if user_q:
        with st.spinner("Analyse..."):
            st.info(query_gemini(f"Expert macro trading, réponds très court : {user_q}"))
