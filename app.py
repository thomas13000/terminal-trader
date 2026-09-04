import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
from google import genai
import pandas as pd
import plotly.express as px

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
    
    .metric-card {
        background-color: #171b21;
        border-radius: 4px;
        padding: 6px;
        border: 1px solid #2a2e39;
        text-align: center;
    }
    .metric-title { color: #848e9c; font-size: 0.7rem; font-weight: 600; }
    .metric-value { font-size: 1rem; font-weight: bold; }
    
    .news-container {
        background-color: #12161c;
        border: 1px solid #2a2e39;
        border-radius: 6px;
        padding: 8px;
        max-height: 280px;
        overflow-y: auto;
    }
</style>
""", unsafe_allow_html=True)

# Auto-rafraîchissement automatique du navigateur toutes les 15 minutes (900 000 ms)
components.html("<script>setTimeout(function(){ window.location.reload(); }, 900000);</script>", height=0)

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
# BANDEAU DÉFILANT D'ALERTE MACRO (BLOOMBERG RED)
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
# BANDEAU MARKET DATA (RAFRAÎCHISSEMENT 15 MIN)
# ---------------------------------------------------------
@st.cache_data(ttl=900)
def fetch_market_data():
    tickers = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "DXY": "DX-Y.NYB", "GOLD": "GC=F", "VIX": "^VIX"}
    data = {}
    for name, ticker in tickers.items():
        try:
            df = yf.Ticker(ticker).history(period="2d")
            if len(df) >= 2:
                curr, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
                data[name] = (curr, ((curr - prev) / prev) * 100)
        except Exception:
            pass
    return data

mkt = fetch_market_data()
if mkt:
    cols = st.columns(len(mkt))
    for i, (k, (v, c)) in enumerate(mkt.items()):
        with cols[i]:
            col = "#00ff88" if c >= 0 else "#ff3b30"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{k}</div>
                <div class="metric-value" style="color:{col};">{v:,.2f}</div>
                <div style="color:{col}; font-size:0.7rem;">{c:+.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# FONCTION GEMINI IA (gemini-3.6-flash)
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
# RECUPERATION DES NEWS YFINANCE (RAFRAÎCHISSEMENT 15 MIN)
# ---------------------------------------------------------
@st.cache_data(ttl=900)
def fetch_yf_news():
    news_items = []
    try:
        sp = yf.Ticker("^GSPC")
        raw_news = sp.news
        if raw_news:
            for item in raw_news[:8]:
                title = item.get("title") or item.get("content", {}).get("title", "")
                link = item.get("link") or item.get("content", {}).get("clickThroughUrl", {}).get("url", "#")
                provider = item.get("publisher") or item.get("content", {}).get("provider", {}).get("displayName", "Yahoo Finance")
                
                if title:
                    news_items.append({
                        "title": title,
                        "link": link,
                        "source": provider
                    })
    except Exception:
        pass
    return news_items

news_feed = fetch_yf_news()

# ---------------------------------------------------------
# LAYOUT PRINCIPAL (3 COLONNES AVEC FINVIZ HEATMAP)
# ---------------------------------------------------------
c_left, c_center, c_right = st.columns([1.5, 1.2, 1])

# --- COLONNE GAUCHE : FINVIZ HEATMAP S&P 500 ---
with c_left:
    st.subheader("🔥 FINVIZ HEATMAP (MIS À JOUR / 15 MIN)")
    finviz_map_url = "https://finviz.com/map.ashx?t=sec"
    components.iframe(finviz_map_url, height=580, scrolling=True)

# --- COLONNE CENTRALE : CALENDRIER TRADINGVIEW + NEWS ---
with c_center:
    st.subheader("🔴 CALENDRIER ÉCONOMIQUE")
    
    tv_widget = """
    <div class="tradingview-widget-container" style="width: 100%; height: 280px;">
      <div class="tradingview-widget-container__widget" style="width: 100%; height: 280px;"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
      {
      "colorTheme": "dark",
      "isTransparent": true,
      "width": "100%",
      "height": "280",
      "locale": "fr",
      "importanceFilter": "0,1",
      "currencyFilter": "USD,EUR,GBP,JPY,CAD,AUD,CHF"
    }
      </script>
    </div>
    """
    components.html(tv_widget, height=285)

    st.subheader("📰 FLUX ACTU MARCHÉS")
    
    BLOOMBERG_RED = "#ff3b30"
    RED_BG = "rgba(255, 59, 48, 0.12)"
    STANDARD_GREEN = "#00ff88"

    if news_feed:
        cards_list = []
        for i, n in enumerate(news_feed):
            is_high_impact = i < 2
            border_col = BLOOMBERG_RED if is_high_impact else STANDARD_GREEN
            bg_col = RED_BG if is_high_impact else "#171b21"
            badge_html = f'<span style="background-color: {BLOOMBERG_RED}; color: #ffffff; font-size: 0.55rem; font-weight: 900; padding: 2px 5px; border-radius: 3px; margin-right: 6px;">HIGH IMPACT</span>' if is_high_impact else ''
            
            cards_list.append(
                f'<div style="background-color: {bg_col}; border-left: 4px solid {border_col}; padding: 8px 10px; margin-bottom: 6px; border-radius: 4px;">'
                f'<div style="display: flex; align-items: center; margin-bottom: 2px;">{badge_html}<span style="color: #848e9c; font-size: 0.65rem;">Source : {n["source"]}</span></div>'
                f'<a href="{n["link"]}" target="_blank" style="color: #ffffff; font-weight: bold; text-decoration: none; font-size: 0.78rem; display: block;">{n["title"]}</a>'
                f'</div>'
            )
            
        cards_html = "".join(cards_list)
        st.markdown(f'<div class="news-container">{cards_html}</div>', unsafe_allow_html=True)
    else:
        st.info("Aucune actualité chargée.")

# --- COLONNE DROITE : MACRO & IA ---
with c_right:
    st.subheader("🌐 MACRO & TAUX")
    @st.cache_data(ttl=900)
    def fetch_macro():
        tickers = {"Taux US 10Y": "^TNX", "Pétrole WTI": "CL=F", "EUR / USD": "EURUSD=X", "US Dollar Index": "DX-Y.NYB"}
        res = {}
        for name, tk in tickers.items():
            try:
                df = yf.Ticker(tk).history(period="2d")
                if len(df) >= 2:
                    c, p = df['Close'].iloc[-1], df['Close'].iloc[-2]
                    res[name] = (c, ((c - p) / p) * 100)
            except Exception:
                pass
        return res

    macro_data = fetch_macro()
    if macro_data:
        for k, (v, c) in macro_data.items():
            col = "#00ff88" if c >= 0 else BLOOMBERG_RED
            st.markdown(f"**{k}** : `{v:,.2f}` (<span style='color:{col}'>{c:+.2f}%</span>)", unsafe_allow_html=True)

    st.divider()
    st.subheader("💬 Prompt IA Macro")
    user_q = st.text_input("Question :", placeholder="Ex : Impact NFP ?", label_visibility="collapsed")
    if user_q:
        with st.spinner("Analyse..."):
            st.info(query_gemini(f"Expert macro trading, réponds très court : {user_q}"))
