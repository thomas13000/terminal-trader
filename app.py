import streamlit as st
import yfinance as yf
import feedparser
from google import genai
import pandas as pd

# ---------------------------------------------------------
# CONFIGURATION ET STYLE BLOOMBERG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Terminal Trader Pro",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #0c0f12; color: #d1d4dc; }
    .metric-card {
        background-color: #171b21;
        border-radius: 6px;
        padding: 10px;
        border: 1px solid #2a2e39;
        text-align: center;
    }
    .metric-title { color: #848e9c; font-size: 0.8rem; font-weight: 600; }
    .metric-value { font-size: 1.2rem; font-weight: bold; }
    .news-card {
        background-color: #171b21;
        border-left: 4px solid #2962ff;
        padding: 10px;
        margin-bottom: 8px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ TERMINAL TRADER PRO — AI POWERS")

# ---------------------------------------------------------
# 1. BANDEAU TICKEUR EN DIRECT
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
                <div style="color:{color}; font-size:0.8rem;">{sign}{chg:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# FONCTION IA GEMINI POUR L'ANALYSE D'ACTU
# ---------------------------------------------------------
def analyze_news_with_gemini(headline):
    if "GEMINI_API_KEY" not in st.secrets:
        return headline, "⚪ NEUTRE", "Clé API non configurée"
    
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        prompt = f"""
        Tu es un analyste financier senior de Wall Street.
        Analyse ce titre d'actualité : "{headline}"
        
        Réponds strictement sous ce format (3 lignes maxi) :
        IMPACT: [HAUSSIER ou BAISSIER ou NEUTRE]
        RESUME: [Résumé en 8 mots maximum en français]
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Erreur IA : {str(e)}"

# ---------------------------------------------------------
# 2. DISPOSITION EN COLONNES
# ---------------------------------------------------------
col_left, col_center, col_right = st.columns([1, 1.2, 1])

with col_left:
    st.subheader("📈 Heatmap & Screener")
    st.info("⚙️ Prochaine étape : Heatmap Finviz")

with col_center:
    st.subheader("📰 Actualités Live & IA")
    if st.button("🔄 Rafraîchir les actualités"):
        st.cache_data.clear()

    # Flux RSS Économique gratuit
    rss_url = "https://search.cnbc.com/rs/search/combinedrender?source=cnbcnews&titles=true&group=scenic&id=10000664&trending=true&output=rss"
    feed = feedparser.parse(rss_url)
    
    if feed.entries:
        for entry in feed.entries[:5]: # Prend les 5 dernières actus
            headline = entry.title
            
            with st.expander(f"📌 {headline[:60]}..."):
                st.write(f"**Titre brut :** {headline}")
                st.write(f"**Heure :** {entry.get('published', 'Récente')}")
                
                # Analyse IA
                with st.spinner("Analyse Gemini en cours..."):
                    ai_analysis = analyze_news_with_gemini(headline)
                    st.markdown(f"```text\n{ai_analysis}\n```")

with col_right:
    st.subheader("🌐 Macro & Calendrier Éco")
    st.info("⚙️ Prochaine étape : Taux US & Calendrier")import streamlit as st
import yfinance as yf
import feedparser
from google import genai
import pandas as pd

# ---------------------------------------------------------
# CONFIGURATION ET STYLE BLOOMBERG
# ---------------------------------------------------------
st.set_page_config(
    page_title="Terminal Trader Pro",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .stApp { background-color: #0c0f12; color: #d1d4dc; }
    .metric-card {
        background-color: #171b21;
        border-radius: 6px;
        padding: 10px;
        border: 1px solid #2a2e39;
        text-align: center;
    }
    .metric-title { color: #848e9c; font-size: 0.8rem; font-weight: 600; }
    .metric-value { font-size: 1.2rem; font-weight: bold; }
    .news-card {
        background-color: #171b21;
        border-left: 4px solid #2962ff;
        padding: 10px;
        margin-bottom: 8px;
        border-radius: 4px;
    }
</style>
""", unsafe_allow_html=True)

st.title("⚡ TERMINAL TRADER PRO — AI POWERS")

# ---------------------------------------------------------
# 1. BANDEAU TICKEUR EN DIRECT
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
                <div style="color:{color}; font-size:0.8rem;">{sign}{chg:.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

st.divider()

# ---------------------------------------------------------
# FONCTION IA GEMINI POUR L'ANALYSE D'ACTU
# ---------------------------------------------------------
def analyze_news_with_gemini(headline):
    if "GEMINI_API_KEY" not in st.secrets:
        return headline, "⚪ NEUTRE", "Clé API non configurée"
    
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        prompt = f"""
        Tu es un analyste financier senior de Wall Street.
        Analyse ce titre d'actualité : "{headline}"
        
        Réponds strictement sous ce format (3 lignes maxi) :
        IMPACT: [HAUSSIER ou BAISSIER ou NEUTRE]
        RESUME: [Résumé en 8 mots maximum en français]
        """
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        return response.text
    except Exception as e:
        return f"Erreur IA : {str(e)}"

# ---------------------------------------------------------
# 2. DISPOSITION EN COLONNES
# ---------------------------------------------------------
col_left, col_center, col_right = st.columns([1, 1.2, 1])

with col_left:
    st.subheader("📈 Heatmap & Screener")
    st.info("⚙️ Prochaine étape : Heatmap Finviz")

with col_center:
    st.subheader("📰 Actualités Live & IA")
    if st.button("🔄 Rafraîchir les actualités"):
        st.cache_data.clear()

    # Flux RSS Économique gratuit
    rss_url = "https://search.cnbc.com/rs/search/combinedrender?source=cnbcnews&titles=true&group=scenic&id=10000664&trending=true&output=rss"
    feed = feedparser.parse(rss_url)
    
    if feed.entries:
        for entry in feed.entries[:5]: # Prend les 5 dernières actus
            headline = entry.title
            
            with st.expander(f"📌 {headline[:60]}..."):
                st.write(f"**Titre brut :** {headline}")
                st.write(f"**Heure :** {entry.get('published', 'Récente')}")
                
                # Analyse IA
                with st.spinner("Analyse Gemini en cours..."):
                    ai_analysis = analyze_news_with_gemini(headline)
                    st.markdown(f"```text\n{ai_analysis}\n```")

with col_right:
    st.subheader("🌐 Macro & Calendrier Éco")
    st.info("⚙️ Prochaine étape : Taux US & Calendrier")
