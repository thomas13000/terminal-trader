import base64
import datetime
import json
import os
import time
import numpy as np
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. CONFIGURATION STREAMLIT & THEME SOMBRE PRO TRADER
# ---------------------------------------------------------
st.set_page_config(
    page_title="TERMINAL TRADER PRO",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS pour look Pro Trader / Binance Dark
st.markdown(
    """
<style>
    /* Style global */
    .stApp {
        background-color: #0b0e11;
        color: #eaecef;
        font-family: 'Inter', sans-serif;
    }
    
    /* En-tête personnalisé */
    .header-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        background: #181a20;
        padding: 15px 25px;
        border-radius: 12px;
        border: 1px solid #2b313a;
        margin-bottom: 20px;
        box-shadow: 0 4px 20px rgba(0,0,0,0.5);
    }
    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        background: rgba(14, 203, 129, 0.12);
        color: #0ecb81;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
        border: 1px solid rgba(14, 203, 129, 0.3);
    }
    .pulse-dot {
        width: 8px;
        height: 8px;
        background-color: #0ecb81;
        border-radius: 50%;
        box-shadow: 0 0 10px #0ecb81;
        animation: pulse-animation 1.5s infinite;
    }
    @keyframes pulse-animation {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.2); opacity: 1; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }
    
    /* Cartes & Métriques */
    .metric-card {
        background: #1e2329;
        border: 1px solid #2b313a;
        border-radius: 10px;
        padding: 16px;
        text-align: center;
        transition: border-color 0.2s;
    }
    .metric-card:hover {
        border-color: #f0b90b;
    }
    .metric-title { font-size: 0.75rem; color: #848e9c; font-weight: 600; text-transform: uppercase; }
    .metric-val { font-size: 1.5rem; font-weight: 800; color: #ffffff; margin: 4px 0; }
    .val-up { color: #0ecb81; font-weight: 700; font-size: 0.85rem; }
    .val-down { color: #f6465d; font-weight: 700; font-size: 0.85rem; }

    /* Onglets surmesure */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #181a20;
        padding: 8px;
        border-radius: 10px;
        border: 1px solid #2b313a;
    }
    .stTabs [data-baseweb="tab"] {
        height: 42px;
        white-space: pre-wrap;
        background-color: transparent;
        border-radius: 6px;
        color: #848e9c;
        font-weight: 700;
        font-size: 0.85rem;
    }
    .stTabs [aria-selected="true"] {
        background-color: #f0b90b !important;
        color: #0b0e11 !important;
    }
</style>
""",
    unsafe_allow_html=True,
)

# ---------------------------------------------------------
# 2. INITIALISATION SESSION STATE (Alertes & Portfolio)
# ---------------------------------------------------------
if "alerts" not in st.session_state:
    st.session_state.alerts = [
        {
            "id": 1,
            "symbol": "BTCUSDT",
            "target": 98500.0,
            "type": "Franchissement Haussier",
            "status": "Active",
            "created": "14:30:00",
        },
        {
            "id": 2,
            "symbol": "US100",
            "target": 21200.0,
            "type": "Franchissement Baissier",
            "status": "Active",
            "created": "10:15:00",
        },
    ]

if "capital" not in st.session_state:
    st.session_state.capital = 25000.0


# ---------------------------------------------------------
# 3. CHARGEMENT AUDIO BASE64 (acdc.mp3)
# ---------------------------------------------------------
def load_audio_b64(filename="acdc.mp3"):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


audio_b64 = load_audio_b64("acdc.mp3")


# ---------------------------------------------------------
# 4. OVERLAY 3D WELCOME SCREEN + GESTION AUDIO (10s -> 35s)
# ---------------------------------------------------------
def render_welcome_screen(audio_data):
    audio_src = f"data:audio/mp3;base64,{audio_data}" if audio_data else ""

    html_code = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=JetBrains+Mono:wght@500;700;800&display=swap">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; user-select: none; }}
            body, html {{ width: 100%; height: 100%; overflow: hidden; font-family: 'Inter', sans-serif; background: transparent; }}
            
            #welcome-screen-root {{
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background: radial-gradient(circle at center, #0e131f 0%, #030406 100%);
                z-index: 999999; display: flex; align-items: center; justify-content: space-between;
                padding: 0 4vw; cursor: pointer; transition: opacity 0.6s ease;
            }}
            #canvas-3d {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }}
            
            .left-panel {{
                position: relative; z-index: 2; text-align: center;
                background: rgba(13, 17, 26, 0.85); border: 1px solid rgba(240, 185, 11, 0.35);
                padding: 35px; border-radius: 20px; backdrop-filter: blur(18px);
                box-shadow: 0 0 70px rgba(0, 0, 0, 0.9); width: 380px;
            }}
            .badge-live {{
                display: inline-flex; align-items: center; gap: 8px;
                font-family: 'JetBrains Mono', monospace; color: #f0b90b;
                font-size: 0.68rem; font-weight: 700; letter-spacing: 2px;
                background: rgba(240, 185, 11, 0.1); padding: 4px 12px; border-radius: 20px;
                border: 1px solid rgba(240, 185, 11, 0.25); margin-bottom: 10px;
            }}
            .dot-pulse {{ width: 8px; height: 8px; background-color: #089981; border-radius: 50%; box-shadow: 0 0 8px #089981; animation: pulse 1.5s infinite; }}
            @keyframes pulse {{ 0% {{ transform: scale(0.95); opacity: 0.8; }} 50% {{ transform: scale(1.2); opacity: 1; }} 100% {{ transform: scale(0.95); opacity: 0.8; }} }}
            
            .clock-main {{ font-family: 'JetBrains Mono', monospace; font-size: 3.8rem; font-weight: 800; color: #fff; margin: 6px 0; line-height: 1; }}
            .clock-sub {{ font-size: 0.65rem; color: #787b86; letter-spacing: 1.5px; margin-bottom: 20px; }}
            
            .btn-enter {{
                background: linear-gradient(135deg, #f0b90b 0%, #d4a007 100%); color: #090a0f;
                border: none; padding: 14px 24px; font-size: 0.85rem; font-weight: 800;
                letter-spacing: 1.5px; border-radius: 8px; cursor: pointer; width: 100%;
                box-shadow: 0 4px 20px rgba(240, 185, 11, 0.35); transition: transform 0.2s;
            }}
            .btn-enter:hover {{ transform: scale(1.02); }}
            
            .side-panel {{ position: relative; z-index: 2; display: flex; flex-direction: column; gap: 10px; width: 290px; }}
            .side-panel-header {{
                font-family: 'JetBrains Mono', monospace; font-size: 0.7rem; font-weight: 700;
                color: #f0b90b; letter-spacing: 1.5px; background: rgba(19, 23, 34, 0.75);
                padding: 6px 12px; border-radius: 6px; border: 1px solid rgba(240, 185, 11, 0.2);
            }}
            .tv-card-wrapper {{
                background: rgba(13, 17, 26, 0.82); border: 1px solid rgba(255, 255, 255, 0.1);
                border-left: 3px solid #f0b90b; border-radius: 8px; padding: 4px 8px; backdrop-filter: blur(12px);
            }}
            .hint-bottom {{ margin-top: 10px; font-size: 0.62rem; color: #5d606b; text-align: center; }}
        </style>
    </head>
    <body>
    <div id="welcome-screen-root" onclick="enterTerminalWithAudio()">
        <canvas id="canvas-3d"></canvas>

        <div class="left-panel" onclick="event.stopPropagation()">
            <div class="badge-live"><span class="dot-pulse"></span> TERMINAL LIVE SESSION</div>
            <div class="clock-main" id="clock-display">00:00:00</div>
            <div class="clock-sub">HEURE DE PARIS — MARKET STANDBY</div>
            <button class="btn-enter" onclick="enterTerminalWithAudio()">ENTRER DANS LE TERMINAL ➔</button>
            <div class="hint-bottom">Cliquez n'importe où pour activer la session</div>
        </div>

        <div class="side-panel" onclick="event.stopPropagation()">
            <div class="side-panel-header">⚡ MARCHÉS TEMPS RÉEL</div>
            <div class="tv-card-wrapper">
                <div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-single-quote.js" async>
                {{ "symbol": "CAPITALCOM:US100", "width": "100%", "colorTheme": "dark", "isTransparent": true, "locale": "fr" }}
                </script></div>
            </div>
            <div class="tv-card-wrapper">
                <div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-single-quote.js" async>
                {{ "symbol": "CAPITALCOM:US500", "width": "100%", "colorTheme": "dark", "isTransparent": true, "locale": "fr" }}
                </script></div>
            </div>
            <div class="tv-card-wrapper">
                <div class="tradingview-widget-container"><div class="tradingview-widget-container__widget"></div>
                <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-single-quote.js" async>
                {{ "symbol": "CAPITALCOM:DXY", "width": "100%", "colorTheme": "dark", "isTransparent": true, "locale": "fr" }}
                </script></div>
            </div>
        </div>
    </div>

    <script>
        const audioDataUri = "{audio_src}";
        
        // --- TIMING MUSICAL (10s -> 35s) ---
        const startSecond = 10;
        const endSecond   = 35;
        const fadeSec     = 2.5;

        let audioObj = null;

        function enterTerminalWithAudio() {{
            if (audioDataUri && audioDataUri.length > 50) {{
                try {{
                    audioObj = new Audio(audioDataUri);
                    audioObj.volume = 0.85;
                    audioObj.currentTime = startSecond;

                    const playPromise = audioObj.play();
                    if (playPromise !== undefined) {{
                        playPromise.then(() => {{
                            const totalPlayMs = (endSecond - startSecond) * 1000;
                            const fadeStartMs = Math.max(0, totalPlayMs - (fadeSec * 1000));

                            setTimeout(() => {{
                                const intervalMs = 50;
                                const steps = (fadeSec * 1000) / intervalMs;
                                const volStep = audioObj.volume / steps;

                                const fadeInterval = setInterval(() => {{
                                    if (audioObj && audioObj.volume > volStep) {{
                                        audioObj.volume -= volStep;
                                    }} else {{
                                        if (audioObj) {{
                                            audioObj.volume = 0;
                                            audioObj.pause();
                                        }}
                                        clearInterval(fadeInterval);
                                    }}
                                }}, intervalMs);
                            }}, fadeStartMs);
                        }}).catch(e => console.log("Audio notice:", e));
                    }}
                }} catch(e) {{
                    console.log("Audio init error:", e);
                }}
            }}
            dismissOverlay();
        }}

        function dismissOverlay() {{
            const root = document.getElementById('welcome-screen-root');
            if (root) {{
                root.style.opacity = '0';
                root.style.pointerEvents = 'none';
                setTimeout(() => {{ root.style.display = 'none'; }}, 700);
            }}
            try {{
                if (window.parent && window.parent.document) {{
                    const iframes = window.parent.document.querySelectorAll('iframe');
                    iframes.forEach(iframe => {{
                        try {{
                            if (iframe.contentWindow === window) {{
                                iframe.style.pointerEvents = 'none';
                            }}
                        }} catch(e) {{}}
                    }});
                }}
            }} catch(e) {{}}
        }}

        function expandIframeToFullscreen() {{
            try {{
                if (window.parent && window.parent.document) {{
                    const iframes = window.parent.document.querySelectorAll('iframe');
                    iframes.forEach(iframe => {{
                        try {{
                            if (iframe.contentWindow === window) {{
                                iframe.style.position = 'fixed'; 
                                iframe.style.top = '0'; 
                                iframe.style.left = '0';
                                iframe.style.width = '100vw'; 
                                iframe.style.height = '100vh'; 
                                iframe.style.zIndex = '999999'; 
                                iframe.style.border = 'none';
                            }}
                        }} catch(e) {{}}
                    }});
                }}
            }} catch(e) {{}}
        }}
        expandIframeToFullscreen();

        function updateClock() {{
            const now = new Date();
            const timeStr = new Intl.DateTimeFormat('fr-FR', {{ timeZone: 'Europe/Paris', hour: '2-digit', minute: '2-digit', second: '2-digit', hour12: false }}).format(now);
            const el = document.getElementById('clock-display');
            if (el) el.textContent = timeStr;
        }}
        setInterval(updateClock, 1000); updateClock();

        let scene, camera, renderer, globeGroup;
        function init3DGlobe() {{
            const canvas = document.getElementById('canvas-3d');
            scene = new THREE.Scene();
            camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.z = 24;
            renderer = new THREE.WebGLRenderer({{ canvas: canvas, alpha: true, antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

            globeGroup = new THREE.Group();
            scene.add(globeGroup);

            const globeMesh = new THREE.Mesh(
                new THREE.SphereGeometry(9.2, 32, 32),
                new THREE.MeshBasicMaterial({{ color: 0xf0b90b, wireframe: true, transparent: true, opacity: 0.20 }})
            );
            globeGroup.add(globeMesh);

            const ptsGeo = new THREE.BufferGeometry();
            const ptsPos = new Float32Array(1800 * 3);
            for (let i = 0; i < 1800; i++) {{
                const u = Math.random(), v = Math.random();
                const theta = u * Math.PI * 2, phi = Math.acos(2 * v - 1), r = 9.25;
                ptsPos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
                ptsPos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
                ptsPos[i * 3 + 2] = r * Math.cos(phi);
            }}
            ptsGeo.setAttribute('position', new THREE.BufferAttribute(ptsPos, 3));
            globeGroup.add(new THREE.Points(ptsGeo, new THREE.PointsMaterial({{ size: 0.18, color: 0x089981, transparent: true, opacity: 0.85 }})));

            const ringMesh = new THREE.Mesh(
                new THREE.RingGeometry(11.8, 11.9, 64),
                new THREE.MeshBasicMaterial({{ color: 0xf0b90b, side: THREE.DoubleSide, transparent: true, opacity: 0.4 }})
            );
            ringMesh.rotation.x = Math.PI / 2.2;
            globeGroup.add(ringMesh);

            window.addEventListener('resize', () => {{
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }});
            animate();
        }}

        function animate() {{
            requestAnimationFrame(animate);
            if (globeGroup) globeGroup.rotation.y += 0.003;
            renderer.render(scene, camera);
        }}
        window.onload = init3DGlobe;
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=0)


# Lancement de l'écran 3D au démarrage
render_welcome_screen(audio_b64)

# ---------------------------------------------------------
# 5. BARRE LATÉRALE (SIDEBAR) & SELECTION D'ACTIFS
# ---------------------------------------------------------
with st.sidebar:
    st.image(
        "https://img.icons8.com/fluency/96/000000/financial-analytics.png",
        width=60,
    )
    st.title("⚡ TERMINAL PRO")
    st.caption("Version 4.2 — Institutional Grade")

    st.markdown("---")
    selected_asset = st.selectbox(
        "🎯 Actif Principal",
        [
            "BINANCE:BTCUSDT",
            "BINANCE:ETHUSDT",
            "CAPITALCOM:US100",
            "CAPITALCOM:US500",
            "FX:EURUSD",
            "TVC:GOLD",
        ],
        index=0,
    )

    timeframe = st.select_slider(
        "⏱️ Unité de Temps (UT)",
        options=["1", "5", "15", "60", "240", "D"],
        value="15",
    )

    st.markdown("---")
    st.subheader("💼 Portefeuille Simulé")
    st.session_state.capital = st.number_input(
        "Capital Total ($)", value=st.session_state.capital, step=1000.0
    )

    st.markdown("---")
    audio_enabled = st.toggle("🔔 Notifications Sonores", value=True)
    if audio_b64:
        st.success("🎵 Musique AC/DC prête")
    else:
        st.warning("⚠️ acdc.mp3 non détecté")

# ---------------------------------------------------------
# 6. EN-TÊTE PRINCIPAL DE LA PAGE D'ACCUEIL
# ---------------------------------------------------------
now_str = datetime.datetime.now().strftime("%H:%M:%S")

st.markdown(
    f"""
<div class="header-container">
    <div>
        <h2 style="margin:0; font-weight:900; color:#fff; font-family:'JetBrains Mono';">
            ⚡ TERMINAL TRADER PRO — <span style="color:#f0b90b;">{selected_asset.split(':')[-1]}</span>
        </h2>
        <span style="color:#848e9c; font-size:0.8rem;">Session En Cours | Heure Serveur : {now_str} UTC</span>
    </div>
    <div class="status-badge">
        <span class="pulse-dot"></span> SERVEUR FLUX EN DIRECT
    </div>
</div>
""",
    unsafe_allow_html=True,
)

# Banner Metrics
m1, m2, m3, m4, m5 = st.columns(5)
with m1:
    st.markdown(
        """<div class="metric-card"><div class="metric-title">BITCOIN</div><div class="metric-val">$96,480</div><div class="val-up">+3.42% ⚡</div></div>""",
        unsafe_allow_html=True,
    )
with m2:
    st.markdown(
        """<div class="metric-card"><div class="metric-title">NASDAQ (US100)</div><div class="metric-val">21,145</div><div class="val-up">+0.88% 📈</div></div>""",
        unsafe_allow_html=True,
    )
with m3:
    st.markdown(
        """<div class="metric-card"><div class="metric-title">S&P 500</div><div class="metric-val">5,980</div><div class="val-up">+0.45% 📈</div></div>""",
        unsafe_allow_html=True,
    )
with m4:
    st.markdown(
        """<div class="metric-card"><div class="metric-title">EUR / USD</div><div class="metric-val">1.0482</div><div class="val-down">-0.21% 📉</div></div>""",
        unsafe_allow_html=True,
    )
with m5:
    st.markdown(
        """<div class="metric-card"><div class="metric-title">OR (GOLD)</div><div class="metric-val">$2,685</div><div class="val-up">+0.62% 📈</div></div>""",
        unsafe_allow_html=True,
    )

st.markdown("<br>", unsafe_allow_html=True)

# ---------------------------------------------------------
# 7. ONGLETS DE NAVIGATION DU TERMINAL
# ---------------------------------------------------------
tab_chart, tab_alerts, tab_news, tab_calc = st.tabs(
    [
        "📈 Graphique & Carnet d'Ordres",
        "🚨 Système d'Alertes",
        "📰 Actualités & Macro",
        "🧮 Calculateur de Risque",
    ]
)

# =========================================================
# TAB 1 : GRAPHIQUE TRADINGVIEW & CARNET D'ORDRES
# =========================================================
with tab_chart:
    col_chart, col_side = st.columns([3, 1])

    with col_chart:
        st.subheader("📊 Chart Interactif temps réel")

        tv_chart_code = f"""
        <div class="tradingview-widget-container" style="height:580px;width:100%;">
          <div id="tradingview_advanced" style="height:580px;width:100%;"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/tv.js"></script>
          <script type="text/javascript">
          new TradingView.widget({{
            "autosize": true,
            "symbol": "{selected_asset}",
            "interval": "{timeframe}",
            "timezone": "Europe/Paris",
            "theme": "dark",
            "style": "1",
            "locale": "fr",
            "toolbar_bg": "#f1f3f6",
            "enable_publishing": false,
            "hide_side_toolbar": false,
            "allow_symbol_change": true,
            "container_id": "tradingview_advanced"
          }});
          </script>
        </div>
        """
        components.html(tv_chart_code, height=590)

    with col_side:
        st.subheader("⚡ Analyse Technique")

        tv_tech_code = f"""
        <div class="tradingview-widget-container">
          <div class="tradingview-widget-container__widget"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-technical-analysis.js" async>
          {{
            "interval": "15m",
            "width": "100%",
            "isTransparent": true,
            "height": 280,
            "symbol": "{selected_asset}",
            "showIntervalTabs": true,
            "displayMode": "single",
            "locale": "fr",
            "colorTheme": "dark"
          }}
          </script>
        </div>
        """
        components.html(tv_tech_code, height=290)

        st.subheader("📖 Carnet d'Ordres (Simulé)")
        # Simulation d'un Carnet d'ordres rapide
        bids = [
            [96475.0, 1.25],
            [96470.0, 2.10],
            [96465.0, 0.85],
            [96460.0, 3.40],
        ]
        asks = [
            [96485.0, 0.90],
            [96490.0, 1.80],
            [96495.0, 2.50],
            [96500.0, 4.10],
        ]

        st.markdown(
            "**Vendeurs (Asks)**",
        )
        for p, q in reversed(asks):
            st.markdown(
                f"<div style='display:flex; justify-between; color:#f6465d; font-family:monospace; font-size:0.8rem;'><span>{p:.1f}</span> <span>{q:.2f} BTC</span></div>",
                unsafe_allow_html=True,
            )

        st.markdown(
            "<hr style='margin:4px 0; border-color:#2b313a;'>",
            unsafe_allow_html=True,
        )

        st.markdown("**Acheteurs (Bids)**")
        for p, q in bids:
            st.markdown(
                f"<div style='display:flex; justify-between; color:#0ecb81; font-family:monospace; font-size:0.8rem;'><span>{p:.1f}</span> <span>{q:.2f} BTC</span></div>",
                unsafe_allow_html=True,
            )

# =========================================================
# TAB 2 : SYSTÈME D'ALERTES INTELILGENTES
# =========================================================
with tab_alerts:
    st.subheader("🚨 Gestionnaire d'Alertes de Prix")

    col_add, col_list = st.columns([1, 2])

    with col_add:
        st.markdown("### ➕ Créer une Alerte")
        with st.form("form_add_alert", clear_on_submit=True):
            sym = st.selectbox(
                "Actif", ["BTCUSDT", "ETHUSDT", "US100", "EURUSD", "GOLD"]
            )
            target = st.number_input("Prix Cible", value=98000.0, step=10.0)
            alert_type = st.selectbox(
                "Condition",
                [
                    "Franchissement Haussier",
                    "Franchissement Baissier",
                    "Ecart %",
                ],
            )

            submitted = st.form_submit_button("🔔 Programmer l'Alerte")
            if submitted:
                new_id = len(st.session_state.alerts) + 1
                new_alert = {
                    "id": new_id,
                    "symbol": sym,
                    "target": target,
                    "type": alert_type,
                    "status": "Active",
                    "created": datetime.datetime.now().strftime("%H:%M:%S"),
                }
                st.session_state.alerts.append(new_alert)
                st.success(f"Alerte créée pour {sym} à {target} !")

        st.markdown("---")
        st.markdown("### 🧪 Tester le Déclencheur")
        if st.button("🔊 Tester Sonnette d'Alerte"):
            st.toast("🚨 ALERTE DÉCLENCHÉE : BTCUSDT a franchi 98,000 $ !")
            st.balloons()

    with col_list:
        st.markdown("### 📋 Alertes Actives")

        if len(st.session_state.alerts) > 0:
            df_alerts = pd.DataFrame(st.session_state.alerts)
            st.dataframe(df_alerts, use_container_width=True, hide_index=True)

            if st.button("🗑️ Effacer toutes les alertes"):
                st.session_state.alerts = []
                st.rerun()
        else:
            st.info("Aucune alerte configurée pour le moment.")

# =========================================================
# TAB 3 : ACTUALITÉS & CALENDRIER ÉCONOMIQUE
# =========================================================
with tab_news:
    col_n1, col_n2 = st.columns(2)

    with col_n1:
        st.subheader("📰 Fil d'Actualités Financières")
        tv_news_code = """
        <div class="tradingview-widget-container">
          <div class="tradingview-widget-container__widget"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-timeline.js" async>
          {
          "feedMode": "all_symbols",
          "colorTheme": "dark",
          "isTransparent": true,
          "displayMode": "regular",
          "width": "100%",
          "height": 550,
          "locale": "fr"
        }
          </script>
        </div>
        """
        components.html(tv_news_code, height=560)

    with col_n2:
        st.subheader("📅 Calendrier Économique Macro")
        tv_cal_code = """
        <div class="tradingview-widget-container">
          <div class="tradingview-widget-container__widget"></div>
          <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-events.js" async>
          {
          "colorTheme": "dark",
          "isTransparent": true,
          "width": "100%",
          "height": 550,
          "locale": "fr",
          "importanceFilter": "-1,0,1"
        }
          </script>
        </div>
        """
        components.html(tv_cal_code, height=560)

# =========================================================
# TAB 4 : CALCULATEUR DE RISQUE & TAILLE DE POSITION
# =========================================================
with tab_calc:
    st.subheader("🧮 Calculateur de Management du Risque")

    c1, c2 = st.columns(2)

    with c1:
        cap = st.number_input(
            "Capital de Compte ($)", value=st.session_state.capital
        )
        risk_pct = st.slider("Risque par Trade (%)", 0.25, 5.0, 1.0, step=0.25)
        entry_price = st.number_input(
            "Prix d'Entrée ($)", value=96500.0, step=50.0
        )
        stop_loss = st.number_input(
            "Prix Stop Loss ($)", value=95200.0, step=50.0
        )
        take_profit = st.number_input(
            "Prix Take Profit ($)", value=99500.0, step=50.0
        )

    with c2:
        risk_amount = cap * (risk_pct / 100.0)
        sl_distance = abs(entry_price - stop_loss)
        tp_distance = abs(take_profit - entry_price)

        if sl_distance > 0:
            position_size = risk_amount / sl_distance
            ratio = tp_distance / sl_distance
            potential_gain = position_size * tp_distance
        else:
            position_size = 0
            ratio = 0
            potential_gain = 0

        st.markdown("### 📊 Résultats du Calcul")
        st.metric("Montant Risqué ($)", f"{risk_amount:.2f} $")
        st.metric(
            "Taille de Position Recommandée", f"{position_size:.4f} Unités"
        )
        st.metric("Ratio Risque / Récompense (R:R)", f"1 : {ratio:.2f}")
        st.metric("Gain Potentiel", f"+{potential_gain:.2f} $")
