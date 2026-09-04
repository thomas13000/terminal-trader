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
# CONFIGURATION PAGE & STYLE BLOOMBERG
# ---------------------------------------------------------
st.set_page_config(
    page_title="TERMINAL TRADER PRO",
    page_icon="⚡",
    layout="wide"
)

st.markdown("""
<style>
    .block-container { padding-top: 4.5rem !important; padding-bottom: 0.8rem !important; }
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
    
    .cal-container {
        background-color: #12161c;
        border: 1px solid #2a2e39;
        border-radius: 6px;
        padding: 8px;
        max-height: 360px;
        overflow-y: auto;
    }
    .cal-day-header {
        background-color: #1f242d;
        color: #f0b90b;
        padding: 5px 10px;
        font-size: 0.78rem;
        font-weight: bold;
        border-radius: 4px;
        margin-top: 6px;
        margin-bottom: 4px;
        border-left: 3px solid #f0b90b;
    }
    .cal-row {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 5px 8px;
        border-bottom: 1px solid #1e222d;
        font-size: 0.75rem;
        background-color: rgba(255, 77, 77, 0.08);
        border-left: 4px solid #ff4d4d;
        margin-bottom: 3px;
        border-radius: 3px;
    }
    .cal-time { color: #00ff88; font-weight: bold; min-width: 48px; font-family: monospace; }
    .cal-currency {
        background-color: #ff4d4d; color: white; padding: 1px 5px; border-radius: 3px;
        font-weight: bold; font-size: 0.68rem; min-width: 38px; text-align: center; margin-right: 8px;
    }
    .cal-title { color: #ffffff; font-weight: 600; flex-grow: 1; white-space: nowrap; overflow: hidden; text-overflow: ellipsis; padding-right: 8px; }
    .cal-val-box { display: flex; gap: 10px; font-size: 0.7rem; color: #848e9c; min-width: 130px; justify-content: flex-end; }
    .cal-val { color: #d1d4dc; font-weight: 500; }
    
    /* STYLE FLUX NEWS YFINANCE */
    .news-container {
        background-color: #12161c;
        border: 1px solid #2a2e39;
        border-radius: 6px;
        padding: 8px;
        max-height: 280px;
        overflow-y: auto;
    }
    .news-card {
        background-color: #171b21;
        border-left: 3px solid #00ff88;
        padding: 6px 10px;
        margin-bottom: 6px;
        border-radius: 4px;
    }
    .news-title {
        color: #ffffff;
        font-weight: bold;
        text-decoration: none;
        font-size: 0.78rem;
        display: block;
    }
    .news-title:hover { color: #00ff88; }
    .news-source { color: #848e9c; font-size: 0.65rem; margin-top: 2px; }
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
# CALENDRIER ÉCONOMIQUE (FXSTREET API - SANS BLOCAGE)
# ---------------------------------------------------------
@st.cache_data(ttl=180)
def fetch_fxstreet_calendar():
    p_tz = zoneinfo.ZoneInfo("Europe/Paris")
    now_p = datetime.now(p_tz)
    
    start_date = now_p.strftime("%Y-%m-%d")
    end_date = (now_p + timedelta(days=7)).strftime("%Y-%m-%d")
    
    url = f"https://calendar-api.fxstreet.com/en/api/v1/eventDates?start={start_date}&end={end_date}&volatilities=HIGH"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)",
        "Accept": "application/json"
    }
    
    parsed = []
    try:
        res = requests.get(url, headers=headers, timeout=8)
        if res.status_code == 200:
            events = res.json()
            for item in events:
                date_str = item.get("dateUtc", "")
                if date_str:
                    dt_utc = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
                    dt_local = dt_utc.astimezone(p_tz)
                    
                    if dt_local >= now_p - timedelta(hours=2):
                        day_label = f"📅 {dt_local.strftime('%A %d/%m').upper()}"
                        if dt_local.date() == now_p.date():
                            day_label = f"📅 AUJOURD'HUI ({dt_local.strftime('%d/%m')})"
                        elif dt_local.date() == (now_p.date() + timedelta(days=1)):
                            day_label = f"📅 DEMAIN ({dt_local.strftime('%d/%m')})"

                        parsed.append({
                            "category": day_label,
                            "time_str": dt_local.strftime("%H:%M"),
                            "currency": item.get("currencyCode", "USD"),
                            "title": item.get("name", ""),
                            "forecast": str(item.get("consensus", "-")),
                            "previous": str(item.get("previous", "-")),
                            "dt": dt_local
                        })
    except Exception:
        pass

    parsed.sort(key=lambda x: x["dt"])
    return parsed

# ---------------------------------------------------------
# OPTION 3 : ACTUALITÉS VIA YFINANCE (AUCUN MODULE EN PLUS)
# ---------------------------------------------------------
@st.cache_data(ttl=300)
def fetch_yf_news():
    news_items = []
    try:
        sp = yf.Ticker("^GSPC")
        raw_news = sp.news
        if raw_news:
            for item in raw_news[:8]:
                # Ingestion selon la structure retournée par yfinance
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

cal_events = fetch_fxstreet_calendar()
news_feed = fetch_yf_news()

# Banner Alert
alert_text = f"PROCHAIN IMPACT : [{cal_events[0]['currency']}] {cal_events[0]['title']} à {cal_events[0]['time_str']}" if cal_events else "AUCUN ÉVÉNEMENT MAJEUR IMMINENT"
st.markdown(f"""
<div style="background-color: #2b0000; border: 1px solid #ff4d4d; border-radius: 4px; padding: 2px 8px; margin-bottom: 8px;">
    <marquee behavior="scroll" direction="left" scrollamount="7" style="color: #ff4d4d; font-weight: bold; font-size: 0.78rem;">
        🚨 CALENDRIER MACRO : {alert_text}
    </marquee>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# BANDEAU MARKET DATA
# ---------------------------------------------------------
@st.cache_data(ttl=60)
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
            col = "#00ff88" if c >= 0 else "#ff4d4d"
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-title">{k}</div>
                <div class="metric-value" style="color:{col};">{v:,.2f}</div>
                <div style="color:{col}; font-size:0.7rem;">{c:+.2f}%</div>
            </div>
            """, unsafe_allow_html=True)

st.divider()

def query_gemini(prompt):
    if "GEMINI_API_KEY" not in st.secrets:
        return "Clé API Gemini non configurée."
    try:
        client = genai.Client(api_key=st.secrets["GEMINI_API_KEY"])
        res = client.models.generate_content(model='gemini-2.5-flash', contents=prompt)
        return res.text
    except Exception as e:
        return f"Erreur IA : {e}"

# ---------------------------------------------------------
# LAYOUT PRINCIPAL (3 COLONNES)
# ---------------------------------------------------------
c_left, c_center, c_right = st.columns([1, 1.4, 1])

# --- COLONNE GAUCHE ---
with c_left:
    st.subheader("📈 SECTEURS S&P 500")
    @st.cache_data(ttl=300)
    def fetch_sectors():
        sectors = {"Tech": "XLK", "Fin": "XLF", "Nrg": "XLE", "Santé": "XLV", "Indus": "XLI", "Conso": "XLY"}
        res = []
        for name, tk in sectors.items():
            try:
                df = yf.Ticker(tk).history(period="2d")
                if len(df) >= 2:
                    c, p = df['Close'].iloc[-1], df['Close'].iloc[-2]
                    res.append({"Secteur": name, "Var %": round(((c - p) / p) * 100, 2)})
            except Exception:
                pass
        return pd.DataFrame(res)

    df_sec = fetch_sectors()
    if not df_sec.empty:
        fig = px.bar(df_sec, x="Var %", y="Secteur", orientation="h", color="Var %",
                     color_continuous_scale=["#ff4d4d", "#171b21", "#00ff88"], color_continuous_midpoint=0, text_auto=True)
        fig.update_layout(paper_bgcolor="#0c0f12", plot_bgcolor="#171b21", font=dict(color="#d1d4dc", size=10),
                          margin=dict(l=5, r=5, t=5, b=5), height=200, coloraxis_showscale=False)
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("🚀 Top Movers")
    st.dataframe(pd.DataFrame({
        "Ticker": ["NVDA", "TSLA", "AAPL", "AMD", "MSFT"],
        "Prix ($)": [130.2, 220.5, 225.1, 150.3, 448.2],
        "Chg (%)": ["+3.4%", "-2.1%", "+0.8%", "+4.1%", "-0.4%"]
    }), hide_index=True, use_container_width=True)

# --- COLONNE CENTRALE : CALENDRIER + NEWS YAHOO FINANCE ---
with c_center:
    st.subheader("🔴 CALENDRIER FXSTREET (HIGH IMPACT)")
    
    if cal_events:
        html_out = '<div class="cal-container">'
        curr_cat = ""
        for ev in cal_events:
            if ev['category'] != curr_cat:
                curr_cat = ev['category']
                html_out += f'<div class="cal-day-header">{curr_cat}</div>'
            html_out += (
                f'<div class="cal-row">'
                f'<span class="cal-time">{ev["time_str"]}</span>'
                f'<span class="cal-currency">{ev["currency"]}</span>'
                f'<span class="cal-title" title="{ev["title"]}">{ev["title"]}</span>'
                f'<div class="cal-val-box">'
                f'<span>Prév : <b class="cal-val">{ev["forecast"]}</b></span>'
                f'<span>Préc : <b class="cal-val">{ev["previous"]}</b></span>'
                f'</div></div>'
            )
        html_out += '</div>'
        st.markdown(html_out, unsafe_allow_html=True)
    else:
        st.info("Aucune annonce à fort impact planifiée.")

    # --- SECTION NEWS YAHOO FINANCE ---
    st.subheader("📰 FLUX ACTU MARCHÉS (YAHOO FINANCE / REUTERS)")
    if news_feed:
        news_html = '<div class="news-container">'
        for n in news_feed:
            news_html += f"""
            <div class="news-card">
                <a href="{n['link']}" target="_blank" class="news-title">{n['title']}</a>
                <div class="news-source">Source : {n['source']}</div>
            </div>
            """
        news_html += '</div>'
        st.markdown(news_html, unsafe_allow_html=True)
    else:
        st.info("Aucune actualité récente chargée.")

# --- COLONNE DROITE ---
with c_right:
    st.subheader("🌐 MACRO & TAUX")
    @st.cache_data(ttl=300)
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
            col = "#00ff88" if c >= 0 else "#ff4d4d"
            st.markdown(f"**{k}** : `{v:,.2f}` (<span style='color:{col}'>{c:+.2f}%</span>)", unsafe_allow_html=True)

    st.divider()
    st.subheader("💬 Prompt IA Macro")
    user_q = st.text_input("Question :", placeholder="Ex : Impact NFP ?", label_visibility="collapsed")
    if user_q:
        with st.spinner("Analyse..."):
            st.info(query_gemini(f"Expert macro trading, réponds très court : {user_q}"))
