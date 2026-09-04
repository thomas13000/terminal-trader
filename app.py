import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
import feedparser
from google import genai
import pandas as pd
import plotly.express as px
from datetime import datetime

# ---------------------------------------------------------
# CONFIGURATION & STYLE BLOOMBERG / FINANCIALJUICE
# ---------------------------------------------------------
st.set_page_config(
    page_title="Terminal Trader Pro",
    page_icon="⚡",
    layout="wide"
)

# Design compact & CSS FinancialJuice
st.markdown("""
<style>
    .block-container { padding-top: 0.8rem !important; padding-bottom: 0.8rem !important; }
    .stApp { background-color: #0c0f12; color: #d1d4dc; }
    
    h1 { font-size: 1.1rem !important; font-weight: 700 !important; color: #f0b90b !important; margin: 0 !important; }
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
    
    /* CSS FINANCIALJUICE LIVE FEED */
    .fj-container {
        background-color: #12161c;
        border: 1px solid #2a2e39;
        border-radius: 4px;
        padding: 4px;
        max-height: 520px;
        overflow-y: auto;
    }
    .fj-row {
        display: flex;
        align-items: center;
        padding: 5px 8px;
        border-bottom: 1px solid #1e222d;
        font-family: 'Courier New', Courier, monospace;
        font-size: 0.75rem;
    }
    .fj-row-alert {
        background-color: rgba(255, 77, 77, 0.22);
        border-left: 4px solid #ff4d4d;
    }
    .fj-row-normal {
        border-left: 4px solid #2962ff;
    }
    .fj-time {
        color: #848e9c;
        font-weight: bold;
        min-width: 50px;
    }
    .fj-badge {
        background-color: #2962ff;
        color: white;
        padding: 1px 5px;
        border-radius: 3px;
        font-size: 0.65rem;
        font-weight: bold;
        margin-right: 6px;
    }
    .fj-badge-red {
        background-color: #ff4d4d;
        color: white;
        padding: 1px 5px;
        border-radius: 3px;
        font-size: 0.65rem;
        font-weight: bold;
        margin-right: 6px;
    }
    .fj-text {
        color: #d1d4dc;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 1. EN-TÊTE & ALERTE ROUGE DEFILANTE
# ---------------------------------------------------------
st.markdown("<h1>⚡ TERMINAL TRADER PRO — FINANCIALJUICE EDITION</h1>", unsafe_allow_html=True)

@st.cache_data(ttl=90)
def fetch_breaking_news():
    urls = [
        "https://search.cnbc.com/rs/search/combinedrender?source=cnbcnews&titles=true&group=scenic&id=10000664&trending=true&output=rss",
        "https://feeds.content.dowjones.io/public/rss/mw_topstories"
    ]
    news = []
    for url in urls:
        try:
            feed = feedparser.parse(url)
            for entry in feed.entries[:5]:
                news.append(entry)
        except Exception:
            pass
    return news

all_news = fetch_breaking_news()
top_headline = all_news[0].title.upper() if all_news else "AUCUNE DEPECHE D'URGENCE"

st.markdown(f"""
<div style="background-color: #2b0000; border: 1px solid #ff4d4d; border-radius: 4px; padding: 2px 8px; margin-top: 4px; margin-bottom: 8px;">
    <marquee behavior="scroll" direction="left" scrollamount="7" style="color: #ff4d4d; font-weight: bold; font-size: 0.78rem;">
        🚨 SQUAWK FINANCIALJUICE : {top_headline} — 🚨 ALERTE MACRO ET MARCHÉS EN DIRECT
    </marquee>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 2. BANDEAU TICKEUR EN DIRECT
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
# 3. PANNEAUX PRINCIPAUX (3 COLONNES - FINANCIALJUICE AU CENTRE)
# ---------------------------------------------------------
col_left, col_center, col_right = st.columns([1, 1.4, 1])

# --- COLONNE GAUCHE : FINVIZ & TOP MOVERS ---
with col_left:
    st.subheader("📈 FINVIZ — HEATMAP SECTORIELLE")
    
    @st.cache_data(ttl=300)
    def fetch_sector_performance():
        sectors = {"Tech": "XLK", "Fin": "XLF", "Nrg": "XLE", "Santé": "XLV", "Indus": "XLI", "Conso": "XLY"}
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
            margin=dict(l=5, r=5, t=5, b=5), height=200, coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🚀 Top Movers S&P 500")
    movers_data = pd.DataFrame({
        "Ticker": ["NVDA", "TSLA", "AAPL", "AMD", "MSFT"],
        "Prix ($)": [130.2, 220.5, 225.1, 150.3, 448.2],
        "Chg (%)": ["+3.4%", "-2.1%", "+0.8%", "+4.1%", "-0.4%"]
    })
    st.dataframe(movers_data, hide_index=True, use_container_width=True)

# --- COLONNE CENTRALE : PURE FINANCIALJUICE SQUAWK & FEED ---
with col_center:
    st.subheader("🔴 FINANCIALJUICE — REAL-TIME SQUAWK & FEED")
    
    # Bouton Squawk Audio Vocale (JS Web Speech API)
    clean_speech_text = top_headline.replace("'", "\\'").replace('"', '\\"')
    squawk_js = f"""
    <div style="background-color:#171b21; padding:6px; border-radius:4px; border:1px solid #2a2e39; margin-bottom:8px; display:flex; align-items:center; justify-space-between;">
        <span style="color:#ff4d4d; font-weight:bold; font-size:0.75rem;">🎙️ AUDIO SQUAWK BOT :</span>
        <button onclick="playSquawk()" style="background-color:#ff4d4d; color:white; border:none; padding:4px 10px; border-radius:3px; font-weight:bold; cursor:pointer; font-size:0.7rem; margin-left:10px;">
            🔊 ÉCOUTER LA DERNIÈRE DEPECHE
        </button>
    </div>
    <script>
    function playSquawk() {{
        var msg = new SpeechSynthesisUtterance('{clean_speech_text}');
        msg.lang = 'en-US';
        msg.rate = 1.0;
        window.speechSynthesis.speak(msg);
    }}
    </script>
    """
    components.html(squawk_js, height=45)
    
    # Rendu du fil FinancialJuice ultra-dense
    if all_news:
        fj_html = '<div class="fj-container">'
        for idx, item in enumerate(all_news[:10]):
            title = item.title
            
            # Extraction heure
            time_str = datetime.now().strftime("%H:%M")
            if hasattr(item, 'published_parsed') and item.published_parsed:
                time_str = f"{item.published_parsed.tm_hour:02d}:{item.published_parsed.tm_min:02d}"
            
            # Mots-clés déclencheurs d'alerte rouge
            is_urgent = any(kw in title.upper() for kw in ["FED", "INFLATION", "CPI", "WAR", "BREAKING", "ALERT", "BIDEN", "TRUMP", "POWELL", "ECB", "RATE"])
            
            row_class = "fj-row-alert" if is_urgent else "fj-row-normal"
            badge_class = "fj-badge-red" if is_urgent else "fj-badge"
            badge_tag = "HIGH IMPACT" if is_urgent else "MACRO"
            
            fj_html += f"""
            <div class="fj-row {row_class}">
                <span class="fj-time">{time_str}</span>
                <span class="{badge_class}">{badge_tag}</span>
                <span class="fj-text" title="{title}">{title}</span>
            </div>
            """
        fj_html += '</div>'
        st.markdown(fj_html, unsafe_allow_html=True)
        
    st.divider()
    
    # Analyseur IA rapide de la dépêche sélectionnée
    st.subheader("⚡ Analyse Flash IA Gemini")
    if st.button("🔍 Analyser la dépêche en tête avec Gemini"):
        with st.spinner("Analyse par l'IA..."):
            prompt = f"Analyse cette dépêche financière : '{top_headline}'. Donne uniquement : 1. Impact Marché (HAUSSIER/BAISSIER/NEUTRE) 2. Actifs impactés (ex: S&P500, EURUSD, Or) 3. Explication en 10 mots max."
            analysis = query_gemini(prompt)
            st.info(analysis)

# --- COLONNE DROITE : BLOOMBERG MACRO & PROMPT ---
with col_right:
    st.subheader("🌐 BLOOMBERG — INDICATEURS MACRO")
    
    @st.cache_data(ttl=300)
    def fetch_macro():
        macro_tickers = {
            "Taux US 10 Ans": "^TNX",
            "Pétrole WTI": "CL=F",
            "EUR / USD": "EURUSD=X",
            "US Dollar Index": "DX-Y.NYB"
        }
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
    st.subheader("💬 Prompt IA Terminal")
    user_query = st.text_input("Question Macro :", placeholder="Ex: Impact hausse taux 10 ans sur la Tech...", label_visibility="collapsed")
    if user_query:
        with st.spinner("Analyse..."):
            st.info(query_gemini(f"En tant qu'expert macroéconomie de salle de marché, réponds très brièvement : {user_query}"))
            
