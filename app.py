import streamlit as st
import yfinance as yf
import feedparser
from google import genai
import pandas as pd
import plotly.express as px

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
# FONCTION IA GEMINI
# ---------------------------------------------------------
def query_gemini(prompt_text):
    if "GEMINI_API_KEY" not in st.secrets:
        return "Clé API Gemini introuvable dans les secrets Streamlit."
    
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
# 2. DISPOSITION EN COLONNES
# ---------------------------------------------------------
col_left, col_center, col_right = st.columns([1.1, 1.2, 1])

# --- COLONNE GAUCHE : HEATMAP FINVIZ ---
with col_left:
    st.subheader("📈 Heatmap Sectorielle (Style Finviz)")
    
    @st.cache_data(ttl=300)
    def fetch_sector_performance():
        sectors = {
            "Tech": "XLK",
            "Finance": "XLF",
            "Énergie": "XLE",
            "Santé": "XLV",
            "Conso Disc.": "XLY",
            "Industrie": "XLI",
            "Immobilier": "XLRE"
        }
        results = []
        for name, ticker in sectors.items():
            try:
                df = yf.Ticker(ticker).history(period="2d")
                if len(df) >= 2:
                    curr, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
                    chg = ((curr - prev) / prev) * 100
                    results.append({"Secteur": name, "Variation (%)": round(chg, 2)})
            except Exception:
                pass
        return pd.DataFrame(results)

    df_sectors = fetch_sector_performance()
    
    if not df_sectors.empty:
        fig = px.bar(
            df_sectors,
            x="Variation (%)",
            y="Secteur",
            orientation="h",
            color="Variation (%)",
            color_continuous_scale=["#ff4d4d", "#171b21", "#00ff88"],
            color_continuous_midpoint=0,
            text_auto=True
        )
        
        fig.update_layout(
            paper_bgcolor="#0c0f12",
            plot_bgcolor="#171b21",
            font=dict(color="#d1d4dc"),
            margin=dict(l=10, r=10, t=10, b=10),
            height=320,
            coloraxis_showscale=False
        )
        st.plotly_chart(fig, use_container_width=True)

# --- COLONNE CENTRALE : FINANCIALJUICE + IA ---
with col_center:
    st.subheader("📰 Actualités Live & IA")
    
    rss_url = "https://search.cnbc.com/rs/search/combinedrender?source=cnbcnews&titles=true&group=scenic&id=10000664&trending=true&output=rss"
    feed = feedparser.parse(rss_url)
    
    if feed.entries:
        for entry in feed.entries[:4]:
            headline = entry.title
            with st.expander(f"📌 {headline[:55]}..."):
                st.write(f"**Titre :** {headline}")
                with st.spinner("Analyse Gemini..."):
                    prompt = f"""
                    Tu es un analyste financier senior.
                    Analyse ce titre : "{headline}"
                    Format strict (3 lignes maxi) :
                    IMPACT: [HAUSSIER ou BAISSIER ou NEUTRE]
                    RESUME: [Résumé en 8 mots maxi en français]
                    """
                    ai_analysis = query_gemini(prompt)
                    st.markdown(f"```text\n{ai_analysis}\n```")

# --- COLONNE DROITE : MACRO & PROMPT IA ---
with col_right:
    st.subheader("🌐 Macro & Taux US")
    
    @st.cache_data(ttl=300)
    def fetch_macro_indicators():
        macro_tickers = {
            "US 10Y Yield": "^TNX",
            "Pétrole WTI": "CL=F",
            "EUR / USD": "EURUSD=X"
        }
        data = {}
        for name, ticker in macro_tickers.items():
            try:
                df = yf.Ticker(ticker).history(period="2d")
                if len(df) >= 2:
                    curr, prev = df['Close'].iloc[-1], df['Close'].iloc[-2]
                    chg = ((curr - prev) / prev) * 100
                    data[name] = (curr, chg)
            except Exception:
                pass
        return data

    macro_data = fetch_macro_indicators()
    if macro_data:
        m_cols = st.columns(len(macro_data))
        for i, (name, (val, chg)) in enumerate(macro_data.items()):
            with m_cols[i]:
                color = "#00ff88" if chg >= 0 else "#ff4d4d"
                st.markdown(f"""
                <div class="metric-card">
                    <div class="metric-title">{name}</div>
                    <div class="metric-value">{val:,.2f}</div>
                    <div style="color:{color}; font-size:0.75rem;">{chg:+.2f}%</div>
                </div>
                """, unsafe_allow_html=True)
                
    st.divider()
    
    # Ligne de commande IA
    st.subheader("💬 Prompt IA Terminal")
    user_query = st.text_input("Pose une question macro à Gemini :", placeholder="Ex: Impact taux 10 ans sur la tech...")
    if user_query:
        with st.spinner("Analyse en cours..."):
            response = query_gemini(f"En tant qu'expert en macroéconomie, réponds de façon synthétique : {user_query}")
            st.info(response)
