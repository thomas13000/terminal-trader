import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import feedparser
from google import genai
import pandas as pd
import plotly.express as px

# ---------------------------------------------------------
# CONFIGURATION & STYLE BLOOMBERG COMPACT
# ---------------------------------------------------------
st.set_page_config(
    page_title="Terminal Trader Pro",
    page_icon="⚡",
    layout="wide"
)

# Réduction drastique des tailles de police et des espacements
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; }
    .stApp { background-color: #0c0f12; color: #d1d4dc; }
    
    h1 { font-size: 1.1rem !important; font-weight: 700 !important; color: #f0b90b !important; margin: 0 !important; }
    h2, h3 { font-size: 0.85rem !important; font-weight: 600 !important; margin-top: 5px !important; margin-bottom: 5px !important; color: #848e9c !important; }
    
    .metric-card {
        background-color: #171b21;
        border-radius: 4px;
        padding: 6px;
        border: 1px solid #2a2e39;
        text-align: center;
    }
    .metric-title { color: #848e9c; font-size: 0.7rem; font-weight: 600; }
    .metric-value { font-size: 1rem; font-weight: bold; }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. BANDEAU DECOUPE / BANNER DEFILANT ALERTE (ROUGE)
# ---------------------------------------------------------
st.markdown("<h1>⚡ TERMINAL TRADER PRO</h1>", unsafe_allow_html=True)

# Récupération de la dernière actu pour le bandeau défilant
@st.cache_data(ttl=120)
def get_latest_breaking_news():
    rss_url = "https://search.cnbc.com/rs/search/combinedrender?source=cnbcnews&titles=true&group=scenic&id=10000664&trending=true&output=rss"
    feed = feedparser.parse(rss_url)
    if feed.entries:
        return feed.entries[0].title.upper()
    return "AUCUNE ALERTE MAJEURE POUR LE MOMENT"

breaking_news = get_latest_breaking_news()

st.markdown(f"""
<div style="background-color: #2b0000; border: 1px solid #ff4d4d; border-radius: 4px; padding: 2px 8px; margin-top: 5px; margin-bottom: 10px;">
    <marquee behavior="scroll" direction="left" scrollamount="6" style="color: #ff4d4d; font-weight: bold; font-size: 0.8rem;">
        🚨 URGENT FINANCIALJUICE : {breaking_news} — 🚨 ALERTE MARCHÉ EN DIRECT — 
    </marquee>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. TICKEUR DES COURS PRINCIPAUX
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def fetch_market_data():
    tickers = {
        "S&P 500": "^GSPC",
        "NASDAQ": "^IXIC",
        "DXY": "DX-Y.NYB",
        "GOLD": "GC=F",
        "VIX": "^VIX"
    }
    data = {}
    for name, ticker in tickers.items():
        try:
            df = yf.Ticker(ticker).history(period="2d")
            if len(df) >= 2:
                curr, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
                chg = ((curr - prev) / prev) * 100
                data[name] = (curr, chg)
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
                <div class="metric-value" style="color:{color};">{val:,.2f}</div>
                <div style="color:{color}; font-size:0.7rem;">{sign}{chg:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# FONCTION IA GEMINI
# ---------------------------------------------------------
def query_gemini(prompt_text):
    if "GEMINI_API_KEY" not in st.secrets:
        return "Clé API Gemini non configurée."
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt_text
        )
        return response.text
    except Exception as e:
        return f"Erreur IA : {str(e)}"

# ---------------------------------------------------------
# 3. PANNEAUX PRINCIPAUX (3 COLONNES DENSES)
# ---------------------------------------------------------
col_left, col_center, col_right = st.columns([1, 1.1, 1])

# --- COLONNE GAUCHE : FINVIZ & TOP MOVERS ---
with col_left:
    st.subheader("📈 FINVIZ — HEATMAP & MOVERS")
    
    # Heatmap sectorielle compacte
    @st.cache_data(ttl=300)
    def fetch_sector_performance():
        sectors = {"Tech": "XLK", "Fin": "XLF", "Nrg": "XLE", "Sante": "XLV", "Indus": "XLI"}
        results = []
        for name, ticker in sectors.items():
            try:
                df = yf.Ticker(ticker).history(period="2d")
                if len(df) >= 2:
                    curr, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
                    results.append({"Secteur": name, "Var %": round(((curr - prev) / prev) * 100, 2)})
            except Exception:
                pass
        return pd.DataFrame(results)

    df_sectors = fetch_sector_performance()
    if not df_sectors.empty:
        fig = px.bar(
            df_sectors, x="Var %", y="Secteur", orientation="h",
            color="Var %", color_continuous_scale=["#ff4d4d", "#171b21", "#00ff88"],
            color_continuous_midpoint=0, text_auto=True
        )
        fig.update_layout(
            paper_bgcolor="#0c0f12", plot_bgcolor="#171b21",
            font=dict(color="#d1d4dc", size=10),
            margin=dict(l=5, r=5, t=5, b=5), height=180, coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🚀 Top Movers (S&P 500 Leaders)")
    # Tableau compact des movers
    movers_data = pd.DataFrame({
        "Ticker": ["NVDA", "TSLA", "AAPL", "AMD"],
        "Prix ($)": [130.2, 220.5, 225.1, 150.3],
        "Chg (%)": ["+3.4%", "-2.1%", "+0.8%", "+4.1%"]
    })
    st.dataframe(movers_data, hide_index=True, use_container_width=True)

# --- COLONNE CENTRALE : FINANCIALJUICE & TRADINGVIEW ---
with col_center:
    st.subheader("📰 FINANCIALJUICE — FEED IA")
    
    rss_url = "https://search.cnbc.com/rs/search/combinedrender?source=cnbcnews&titles=true&group=scenic&id=10000664&trending=true&output=rss"
    feed = feedparser.parse(rss_url)
    if feed.entries:
        for entry in feed.entries[:3]:
            headline = entry.title
            with st.expander(f"📌 {headline[:45]}...", expanded=False):
                st.caption(headline)
                with st.spinner("Analyse..."):
                    prompt = f"Analyse ce titre: '{headline}'. Reponds sur 2 lignes max: 1. IMPACT: [HAUSSIER/BAISSIER/NEUTRE] 2. RESUME (6 mots max)."
                    st.code(query_gemini(prompt), language="text")

    st.subheader("📊 Jauge Technique TradingView")
    # Widget Jauge Technique TradingView
    tv_gauge = """
    <div class="tradingview-widget-container">
      <div class="tradingview-widget-container__widget"></div>
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
      {
      "interval": "15m",
      "width": "100%",
      "isTransparent": true,
      "height": "220",
      "symbol": "FOREXCOM:SPXUSD",
      "showIntervalTabs": false,
      "displayMode": "single",
      "locale": "fr",
      "colorTheme": "dark"
    }
      </script>
    </div>
    """
    components.html(tv_gauge, height=230)

# --- COLONNE DROITE : BLOOMBERG MACRO & PROMPT ---
with col_right:
    st.subheader("🌐 BLOOMBERG — MACRO & TAUX")
    
    @st.cache_data(ttl=300)
    def fetch_macro():
        macro_tickers = {"US 10Y Yield": "^TNX", "WTI Crude": "CL=F", "EUR/USD": "EURUSD=X"}
        data = {}
        for name, ticker in macro_tickers.items():
            try:
                df = yf.Ticker(ticker).history(period="2d")
                if len(df) >= 2:
                    curr, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
                    data[name] = (curr, ((curr - prev) / prev) * 100)
            except Exception:
                pass
        return data

    macro = fetch_macro()
    if macro:
        for name, (val, chg) in macro.items():
            col_c = "#00ff88" if chg >= 0 else "#ff4d4d"
            st.markdown(f"**{name}** : `{val:,.2f}` (<span style='color:{col_c}'>{chg:+.2f}%</span>)", unsafe_allow_html=True)

    st.divider()
    st.subheader("💬 Prompt Terminal IA")
    user_query = st.text_input("Question Macro :", placeholder="Ex: Impact DXY sur l'Or...", label_visibility="collapsed")
    if user_query:
        with st.spinner("Analyse..."):
            st.info(query_gemini(f"Expert macro, reponds court : {user_query}"))
            
