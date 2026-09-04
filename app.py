import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
from google import genai
import pandas as pd

# ---------------------------------------------------------
# CONFIGURATION PAGE & STYLES HAUT DE GAMME
# ---------------------------------------------------------
st.set_page_config(
    page_title="TERMINAL TRADER PRO",
    page_icon="⚡",
    layout="wide"
)

# Injection des Google Fonts + Style CSS complet
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600;700&display=swap');

    /* Reset & Fond Général */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }
    
    .stApp {
        background-color: #090a0f;
        color: #e1e3ea;
    }
    
    .block-container {
        padding-top: 2.2rem !important;
        padding-bottom: 1rem !important;
        max-width: 98% !important;
    }

    /* Scrollbars ultra-discrètes */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: #090a0f; }
    ::-webkit-scrollbar-thumb { background: #1e2430; border-radius: 4px; }
    ::-webkit-scrollbar-thumb:hover { background: #f0b90b; }

    /* Titres de sections */
    .section-header {
        font-size: 0.78rem;
        font-weight: 700;
        letter-spacing: 0.8px;
        text-transform: uppercase;
        color: #787b86;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Cartes Métriques du Haut */
    .metric-card-v2 {
        background: linear-gradient(145deg, #131722 0%, #0d1017 100%);
        border: 1px solid #1e222d;
        border-radius: 8px;
        padding: 8px 12px;
        transition: all 0.2s ease-in-out;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
    }
    .metric-card-v2:hover {
        border-color: rgba(240, 185, 11, 0.3);
        transform: translateY(-1px);
    }
    .metric-label {
        font-size: 0.68rem;
        font-weight: 600;
        color: #787b86;
        letter-spacing: 0.5px;
    }
    .metric-price {
        font-family: 'JetBrains Mono', monospace;
        font-size: 1.15rem;
        font-weight: 700;
        color: #f0f3fa;
        margin: 2px 0;
    }
    .metric-badge {
        font-family: 'JetBrains Mono', monospace;
        font-size: 0.68rem;
        font-weight: 600;
        padding: 2px 6px;
        border-radius: 4px;
        display: inline-block;
    }
    .badge-bull { background: rgba(8, 153, 129, 0.15); color: #089981; }
    .badge-bear { background: rgba(242, 54, 69, 0.15); color: #f23645; }

    /* =========================================================
       ONGLETS PREMIUM (GLASSMORPHIC & GLOW)
       ========================================================= */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: #131722;
        padding: 6px;
        border-radius: 10px;
        border: 1px solid #1e222d;
        margin-bottom: 16px;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent !important;
        border: none !important;
        border-radius: 6px !important;
        color: #787b86 !important;
        font-weight: 600 !important;
        font-size: 0.82rem !important;
        padding: 8px 22px !important;
        transition: all 0.25s ease-in-out !important;
    }

    .stTabs [data-baseweb="tab"]:hover {
        color: #f0f3fa !important;
        background: rgba(255, 255, 255, 0.04) !important;
    }

    .stTabs [aria-selected="true"] {
        color: #f0b90b !important;
        background: rgba(240, 185, 11, 0.1) !important;
        box-shadow: inset 0 0 0 1px rgba(240, 185, 11, 0.3), 0 4px 15px rgba(240, 185, 11, 0.12) !important;
    }

    .stTabs [data-baseweb="tab-highlight-title"],
    .stTabs [data-baseweb="tab-border-selected"] {
        background-color: transparent !important;
    }

    /* Container de News */
    .news-wrapper {
        background: #131722;
        border: 1px solid #1e222d;
        border-radius: 8px;
        padding: 10px;
        max-height: 295px;
        overflow-y: auto;
    }
    .news-card {
        background: #181c27;
        border-left: 3px solid #f0b90b;
        border-radius: 0 6px 6px 0;
        padding: 8px 10px;
        margin-bottom: 8px;
        transition: transform 0.15s ease;
    }
    .news-card:hover {
        transform: translateX(3px);
        background: #1e2430;
    }
    .news-title {
        color: #f0f3fa;
        font-size: 0.78rem;
        font-weight: 600;
        text-decoration: none;
        line-height: 1.3;
        display: block;
    }
    .news-meta {
        font-size: 0.63rem;
        color: #787b86;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
        gap: 6px;
    }

    /* Input IA Personnalisé */
    .stTextInput input {
        background-color: #131722 !important;
        border: 1px solid #1e222d !important;
        color: #f0f3fa !important;
        border-radius: 6px !important;
        font-size: 0.8rem !important;
    }
    .stTextInput input:focus {
        border-color: #f0b90b !important;
        box-shadow: 0 0 0 1px #f0b90b !important;
    }

    /* Animation LED clignotante pour alerte */
    @keyframes pulse-red {
        0% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(242, 54, 69, 0.7); }
        70% { transform: scale(1); box-shadow: 0 0 0 6px rgba(242, 54, 69, 0); }
        100% { transform: scale(0.95); box-shadow: 0 0 0 0 rgba(242, 54, 69, 0); }
    }
    .led-red {
        width: 8px; height: 8px; background-color: #f23645; border-radius: 50%;
        display: inline-block; animation: pulse-red 2s infinite; margin-right: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Auto-rafraîchissement automatique du navigateur toutes les 15 minutes
components.html("<script>setTimeout(function(){ window.location.reload(); }, 900000);</script>", height=0)

# ---------------------------------------------------------
# HORLOGES TEMPS RÉEL (JS) - DESIGN NATIVE
# ---------------------------------------------------------
header_html = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@800&family=JetBrains+Mono:wght@600&display=swap');
    body { margin: 0; padding: 0; background: transparent; font-family: 'Inter', sans-serif; overflow: hidden; }
    .header-box { 
        display: flex; justify-content: space-between; align-items: center; 
        background: #131722; padding: 8px 16px; border: 1px solid #1e222d; border-radius: 8px; 
    }
    .header-title { font-size: 1.15rem; font-weight: 900; color: #f0b90b; letter-spacing: 0.5px; display: flex; align-items: center; gap: 8px; }
    .clocks-wrap { display: flex; gap: 10px; }
    .clock-card { 
        background: #181c27; padding: 4px 12px; border-radius: 6px; border: 1px solid #2a2e39; text-align: center; min-width: 90px; 
    }
    .clock-label { font-size: 0.6rem; color: #787b86; font-weight: 700; letter-spacing: 0.5px; }
    .clock-time { font-family: 'JetBrains Mono', monospace; font-size: 0.95rem; color: #089981; font-weight: 600; }
</style>

<div class="header-box">
    <div class="header-title">⚡ TERMINAL TRADER PRO</div>
    <div class="clocks-wrap">
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
components.html(header_html, height=52)

# ---------------------------------------------------------
# BANDEAU D'ALERTE MACRO MODERNE
# ---------------------------------------------------------
texte_alerte = "Publication NFP & Taux de chômage US à 14:30 — Volatilité extrême attendue sur USD, Or et Indices US !"

st.markdown(f"""
<div style="background: rgba(242, 54, 69, 0.08); border: 1px solid rgba(242, 54, 69, 0.3); border-radius: 6px; padding: 6px 12px; margin-top: 4px; margin-bottom: 12px; display: flex; align-items: center; overflow: hidden;">
    <div style="display: flex; align-items: center; white-space: nowrap; margin-right: 12px;">
        <span class="led-red"></span>
        <span style="color: #f23645; font-size: 0.68rem; font-weight: 800; letter-spacing: 0.5px; text-transform: uppercase;">HIGH IMPACT</span>
    </div>
    <div style="color: #f0f3fa; font-size: 0.78rem; font-weight: 500; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
        {texte_alerte}
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# GENERATION SPARKLINE HD AVEC DÉGRADÉ
# ---------------------------------------------------------
def generate_sparkline(series, width=130, height=34, color="#089981"):
    values = series.dropna().tolist()
    if len(values) < 2:
        return ""
    
    if len(values) > 120:
        step = len(values) // 120
        values = values[::step]
        
    min_val, max_val = min(values), max(values)
    val_range = max_val - min_val if max_val != min_val else 1
    
    points = []
    n = len(values)
    for i, val in enumerate(values):
        x = (i / (n - 1)) * width
        y = height - ((val - min_val) / val_range) * (height - 8) - 4
        points.append(f"{x:.1f},{y:.1f}")
    
    polyline = " ".join(points)
    fill_points = f"0,{height} " + polyline + f" {width},{height}"
    
    grad_id = f"grad_{abs(hash(polyline))}"
    
    return f'''<svg width="100%" height="{height}" viewBox="0 0 {width} {height}" preserveAspectRatio="none" style="margin-top: 4px;">
        <defs>
            <linearGradient id="{grad_id}" x1="0" y1="0" x2="0" y2="1">
                <stop offset="0%" stop-color="{color}" stop-opacity="0.25"/>
                <stop offset="100%" stop-color="{color}" stop-opacity="0.0"/>
            </linearGradient>
        </defs>
        <polygon fill="url(#{grad_id})" points="{fill_points}"/>
        <polyline fill="none" stroke="{color}" stroke-width="1.8" stroke-linecap="round" points="{polyline}"/>
    </svg>'''

# ---------------------------------------------------------
# BANDEAU MARKET DATA 1M
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def fetch_market_data():
    tickers = {"S&P 500": "^GSPC", "NASDAQ": "^IXIC", "DXY": "DX-Y.NYB", "GOLD": "GC=F", "VIX": "^VIX"}
    data = {}
    for name, ticker in tickers.items():
        try:
            df = yf.Ticker(ticker).history(period="1d", interval="1m")
            if not df.empty and len(df) >= 2:
                curr = df['Close'].iloc[-1]
                first = df['Close'].iloc[0]
                pct = ((curr - first) / first) * 100
                data[name] = (curr, pct, df['Close'])
        except Exception:
            pass
    return data

mkt = fetch_market_data()
if mkt:
    cols = st.columns(len(mkt))
    for i, (k, (v, c, series)) in enumerate(mkt.items()):
        with cols[i]:
            is_bull = c >= 0
            col = "#089981" if is_bull else "#f23645"
            badge_class = "badge-bull" if is_bull else "badge-bear"
            sparkline = generate_sparkline(series, color=col)
            
            st.markdown(f"""
            <div class="metric-card-v2">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="metric-label">{k}</span>
                    <span class="metric-badge {badge_class}">{c:+.2f}%</span>
                </div>
                <div class="metric-price">{v:,.2f}</div>
                {sparkline}
            </div>
            """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# FONCTIONS IA & NEWS
# ---------------------------------------------------------
def query_gemini(prompt):
    if "GEMINI_API_KEY" not in st.secrets:
        return "Clé API Gemini non configurée dans st.secrets."
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        res = client.models.generate_content(model='gemini-3.6-flash', contents=prompt)
        return res.text
    except Exception as e:
        return f"Erreur IA : {e}"

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
# SYSTEME D'ONGLETS REDESSINÉ
# ---------------------------------------------------------
tab_main, tab_1, tab_2, tab_3 = st.tabs([
    "⚡ Vue Marchés & IA", 
    "📈 Analyse Technique", 
    "📊 Portefeuille", 
    "⚙️ Configuration"
])

# =========================================================
# ONGLET PRINCIPAL
# =========================================================
with tab_main:
    c_left, c_center, c_right = st.columns([1.5, 1.2, 1])

    # --- COLONNE GAUCHE : HEATMAP NASDAQ ---
    with c_left:
        st.markdown('<div class="section-header">🔥 Heatmap Nasdaq 100</div>', unsafe_allow_html=True)
        
        heatmap_html = """
        <div class="tradingview-widget-container" style="height: 560px; width: 100%;">
          <div class="tradingview-widget-container__widget" style="height: 560px; width: 100%;"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js" async>
          {
            "exchanges": [],
            "dataSource": "NASDAQ100",
            "grouping": "sector",
            "blockSize": "market_cap_basic",
            "blockColor": "change",
            "locale": "fr",
            "symbolUrl": "",
            "colorTheme": "dark",
            "hasTopBar": false,
            "isDataSetEnabled": false,
            "isZoomEnabled": true,
            "hasSymbolTooltip": true,
            "width": "100%",
            "height": "560"
          }
          </script>
        </div>
        """
        components.html(heatmap_html, height=565)

    # --- COLONNE CENTRALE : CALENDRIER + NEWS ---
    with c_center:
        st.markdown('<div class="section-header">📅 Calendrier Économique</div>', unsafe_allow_html=True)
        
        tv_widget = """
        <div class="tradingview-widget-container" style="width: 100%; height: 260px;">
          <div class="tradingview-widget-container__widget" style="width: 100%; height: 260px;"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
          {
          "colorTheme": "dark",
          "isTransparent": true,
          "width": "100%",
          "height": "260",
          "locale": "fr",
          "importanceFilter": "0,1",
          "currencyFilter": "USD,EUR,GBP,JPY,CAD,AUD,CHF"
        }
          </script>
        </div>
        """
        components.html(tv_widget, height=265)

        st.markdown('<div class="section-header">📰 Fil d\'Actualités En Direct</div>', unsafe_allow_html=True)

        if news_feed:
            cards_list = []
            for i, n in enumerate(news_feed):
                is_urgent = i < 2
                border_style = "border-left: 3px solid #f23645;" if is_urgent else "border-left: 3px solid #089981;"
                badge_urgent = '<span style="background: rgba(242,54,69,0.2); color:#f23645; font-size:0.55rem; font-weight:800; padding:1px 4px; border-radius:3px;">URGENT</span>' if is_urgent else ''
                
                cards_list.append(
                    f'<div class="news-card" style="{border_style}">'
                    f'<div class="news-meta">{badge_urgent}<span>{n["source"]}</span></div>'
                    f'<a href="{n["link"]}" target="_blank" class="news-title">{n["title"]}</a>'
                    f'</div>'
                )
                
            cards_html = "".join(cards_list)
            st.markdown(f'<div class="news-wrapper">{cards_html}</div>', unsafe_allow_html=True)
        else:
            st.info("Aucune actualité disponible.")

    # --- COLONNE DROITE : MACRO & IA ---
    with c_right:
        st.markdown('<div class="section-header">🌐 Variables Macro</div>', unsafe_allow_html=True)
        
        @st.cache_data(ttl=900)
        def fetch_macro():
            tickers = {"Taux US 10Y": "^TNX", "Pétrole WTI": "CL=F", "EUR / USD": "EURUSD=X", "Dollar Index": "DX-Y.NYB"}
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
                col = "#089981" if c >= 0 else "#f23645"
                st.markdown(
                    f"""
                    <div style="display:flex; justify-content:space-between; align-items:center; background:#131722; border:1px solid #1e222d; padding:6px 10px; border-radius:6px; margin-bottom:6px;">
                        <span style="font-size:0.75rem; color:#787b86; font-weight:600;">{k}</span>
                        <span style="font-family:'JetBrains Mono'; font-size:0.82rem; font-weight:600; color:#f0f3fa;">{v:,.2f} <span style="color:{col}; font-size:0.72rem;">({c:+.2f}%)</span></span>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

        st.markdown('<div class="section-header" style="margin-top:16px;">🤖 Assistant IA Macro</div>', unsafe_allow_html=True)
        user_q = st.text_input("Question IA", placeholder="Ex : Quel impact si le NFP dépasse 200k ?", label_visibility="collapsed")
        
        if user_q:
            with st.spinner("Analyse du marché..."):
                ans = query_gemini(f"Tu es un analyste macro senior sur un terminal Bloomberg. Réponds de façon concise et synthétique à : {user_q}")
                st.markdown(
                    f"""
                    <div style="background:#131722; border:1px solid #f0b90b; border-radius:6px; padding:10px; font-size:0.78rem; color:#e1e3ea; line-height:1.4;">
                        <span style="color:#f0b90b; font-weight:700;">💡 ANALYSE IA :</span><br>{ans}
                    </div>
                    """, 
                    unsafe_allow_html=True
                )

# =========================================================
# ONGLETS SECONDAIRES
# =========================================================
with tab_1:
    st.markdown('<div class="section-header">📈 Analyse Technique Pro</div>', unsafe_allow_html=True)
    st.info("Espace prêt pour ajouter un graphique TradingView dynamique ou tes indicateurs personnalisés.")

with tab_2:
    st.markdown('<div class="section-header">📊 Suivi de Portefeuille</div>', unsafe_allow_html=True)
    st.info("Espace prêt pour ajouter la gestion de tes positions, PnL et risque.")

with tab_3:
    st.markdown('<div class="section-header">⚙️ Configuration du Terminal</div>', unsafe_allow_html=True)
    st.info("Espace prêt pour personnaliser tes tickers, alertes et paramètres API.")
