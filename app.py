import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
from google import genai
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import requests
import zoneinfo

# ---------------------------------------------------------
# CONFIGURATION & STYLE BLOOMBERG / FOREX FACTORY
# ---------------------------------------------------------
st.set_page_config(
    page_title="TERMINAL TRADER PRO",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    /* Marge haute augmentée pour éviter le chevauchement avec la barre Streamlit */
    .block-container { padding-top: 2.5rem !important; padding-bottom: 0.8rem !important; }
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
    
    /* STYLE FOREX FACTORY CALENDAR */
    .ff-container {
        background-color: #12161c;
        border: 1px solid #2a2e39;
        border-radius: 6px;
        padding: 8px;
        max-height: 560px;
        overflow-y: auto;
    }
    .ff-day-header {
        background-color: #1f242d;
        color: #f0b90b;
        padding: 6px 10px;
        font-size: 0.8rem;
        font-weight: bold;
        border-radius: 4px;
        margin-top: 8px;
        margin-bottom: 6px;
        border-left: 3px solid #f0b90b;
    }
    .ff-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 6px 8px;
        border-bottom: 1px solid #1e222d;
        font-size: 0.78rem;
        background-color: rgba(255, 77, 77, 0.08);
        border-left: 4px solid #ff4d4d;
        margin-bottom: 4px;
        border-radius: 3px;
    }
    .ff-time {
        color: #00ff88;
        font-weight: bold;
        min-width: 50px;
        font-family: 'Courier New', Courier, monospace;
    }
    .ff-currency {
        background-color: #ff4d4d;
        color: white;
        padding: 2px 6px;
        border-radius: 3px;
        font-weight: bold;
        font-size: 0.7rem;
        min-width: 42px;
        text-align: center;
        margin-right: 8px;
    }
    .ff-title {
        color: #ffffff;
        font-weight: 600;
        flex-grow: 1;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
        padding-right: 10px;
    }
    .ff-val-box {
        display: flex;
        gap: 12px;
        font-size: 0.72rem;
        color: #848e9c;
        min-width: 140px;
        justify-content: flex-end;
    }
    .ff-val {
        color: #d1d4dc;
        font-weight: 500;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# EN-TÊTE : TITRE + HORLOGES TEMPS RÉEL (JS FLUIDE)
# ---------------------------------------------------------
header_html = """
<style>
    body { margin: 0; padding: 2px; background-color: transparent; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; overflow: hidden; }
    .header-box {
        display: flex;
        justify-content: space-between;
        align-items: center;
        background-color: #12161c;
        padding: 8px 16px;
        border: 1px solid #2a2e39;
        border-radius: 6px;
        box-sizing: border-box;
    }
    .header-title {
        font-size: 1.5rem;
        font-weight: 900;
        color: #f0b90b;
        margin: 0;
        letter-spacing: 0.5px;
    }
    .clock-card {
        text-align: center;
        background-color: #171b21;
        padding: 4px 12px;
        border-radius: 4px;
        border: 1px solid #2a2e39;
        min-width: 95px;
    }
    .clock-label {
        font-size: 0.65rem;
        color: #848e9c;
        font-weight: bold;
        letter-spacing: 0.5px;
    }
    .clock-time {
        font-size: 1.1rem;
        color: #00ff88;
        font-weight: bold;
        font-family: 'Courier New', monospace;
    }
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
        const parisOptions = { timeZone: 'Europe/Paris', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
        const nyOptions = { timeZone: 'America/New_York', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false };
        
        document.getElementById('clock-paris').textContent = new Intl.DateTimeFormat('fr-FR', parisOptions).format(now);
        document.getElementById('clock-ny').textContent = new Intl.DateTimeFormat('en-US', nyOptions).format(now);
    }
    setInterval(updateClocks, 1000);
    updateClocks();
</script>
"""

components.html(header_html, height=80)

# ---------------------------------------------------------
# RÉCUPÉRATION DU FLUX JSON OFFICIEL FOREX FACTORY
# ---------------------------------------------------------
@st.cache_data(ttl=120)
def fetch_forex_factory_red_folder():
    url = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            events = response.json()
            
            try:
                p_tz = zoneinfo.ZoneInfo("Europe/Paris")
                now_p = datetime.now(p_tz)
            except Exception:
                p_tz = None
                now_p = datetime.now()
                
            today_date = now_p.date()
            tomorrow_date = today_date + timedelta(days=1)
            
            parsed_events = []
            for item in events:
                if item.get("impact") == "High":
                    date_str = item.get("date", "")
                    if date_str:
                        dt = datetime.fromisoformat(date_str)
                        if p_tz:
                            dt_local = dt.astimezone(p_tz)
                        else:
                            dt_local = dt
                            
                        ev_date = dt_local.date()
                        
                        if ev_date == today_date:
                            day_cat = f"📅 AUJOURD'HUI ({dt_local.strftime('%d/%m')})"
                        elif ev_date == tomorrow_date:
                            day_cat = f"📅 DEMAIN ({dt_local.strftime('%d/%m')})"
                        else:
                            continue
                            
                        parsed_events.append({
                            "category": day_cat,
                            "time_str": dt_local.strftime("%H:%M"),
                            "currency": item.get("country", "USD"),
                            "title": item.get("title", ""),
                            "forecast": item.get("forecast", "-"),
                            "previous": item.get("previous", "-")
                        })
            return parsed_events
    except Exception as e:
        st.error(f"Erreur de connexion avec Forex Factory : {e}")
    return []

ff_events = fetch_forex_factory_red_folder()

top_alert = "AUCUNE ANNONCE ROUGE RESTANTE AUJOURD'HUI OU DEMAIN"
if ff_events:
    top_alert = f"PROCHAIN IMPACT ROUGE : [{ff_events[0]['currency']}] {ff_events[0]['title']} à {ff_events[0]['time_str']} — Prévision : {ff_events[0]['forecast']}"

st.markdown(f"""
<div style="background-color: #2b0000; border: 1px solid #ff4d4d; border-radius: 4px; padding: 2px 8px; margin-top: 2px; margin-bottom: 8px;">
    <marquee behavior="scroll" direction="left" scrollamount="7" style="color: #ff4d4d; font-weight: bold; font-size: 0.78rem;">
        🚨 FOREX FACTORY RED ALERT : {top_alert}
    </marquee>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# BANDEAU DE COURS
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
# DÉFINITION DES COLONNES DE LAYOUT
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

# --- COLONNE CENTRALE : EXCLUSIF FOREX FACTORY RED NEWS ---
with col_center:
    col_hdr1, col_hdr2 = st.columns([3, 1])
    with col_hdr1:
        st.subheader("🔴 FOREX FACTORY — HIGH IMPACT ONLY")
    with col_hdr2:
        if st.button("🔄 Rafraîchir", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

    if ff_events:
        html_out = '<div class="ff-container">'
        current_cat = ""
        
        for ev in ff_events:
            if ev['category'] != current_cat:
                current_cat = ev['category']
                html_out += f'<div class="ff-day-header">{current_cat}</div>'
                
            html_out += (
                f'<div class="ff-row">'
                f'<span class="ff-time">{ev["time_str"]}</span>'
                f'<span class="ff-currency">{ev["currency"]}</span>'
                f'<span class="ff-title" title="{ev["title"]}">{ev["title"]}</span>'
                f'<div class="ff-val-box">'
                f'<span>Prév : <b class="ff-val">{ev["forecast"]}</b></span>'
                f'<span>Préc : <b class="ff-val">{ev["previous"]}</b></span>'
                f'</div>'
                f'</div>'
            )
            
        html_out += '</div>'
        st.markdown(html_out, unsafe_allow_html=True)
    else:
        st.info("Aucune annonce économique majeure à fort impact (Dossier Rouge) prévue pour Aujourd'hui ou Demain.")

    st.divider()
    
    st.subheader("⚡ Analyse du Prochain Événement")
    if st.button("🔍 Analyser le risque du prochain événement rouge"):
        if ff_events:
            nxt = ff_events[0]
            with st.spinner("Analyse en cours..."):
                prompt = f"L'événement économique '{nxt['title']}' sur la devise {nxt['currency']} a lieu à {nxt['time_str']}. Prévision : {nxt['forecast']}, Précédent : {nxt['previous']}. En 2 phrases, explique l'impact attendu si la donnée dépasse la prévision."
                st.info(query_gemini(prompt))
        else:
            st.write("Aucune annonce rouge à analyser.")

# --- COLONNE DROITE : BLOOMBERG MACRO & PROMPT ---
with col_right:
    st.subheader("🌐 BLOOMBERG — MACRO & TAUX")
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
    st.subheader("💬 Prompt Terminal")
    user_query = st.text_input("Question Macro :", placeholder="Ex : Impact NFP supérieur aux attentes...", label_visibility="collapsed")
    if user_query:
        with st.spinner("Analyse..."):
            st.info(query_gemini(f"Expert macro trading, réponds très court : {user_query}"))
