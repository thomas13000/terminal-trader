import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf
from google import genai
import pandas as pd

# ---------------------------------------------------------
# CONFIGURATION PAGE & STYLES
# ---------------------------------------------------------
st.set_page_config(
    page_title="TERMINAL TRADER PRO",
    page_icon="⚡",
    layout="wide"
)

# ---------------------------------------------------------
# HTML / CSS / JS : ÉCRAN D'ACCUEIL 3D BLOQUANT
# ---------------------------------------------------------
st.markdown("""
<!-- IMPORTation DES FONTS ET THREE.JS -->
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=JetBrains+Mono:wght@500;700;800&display=swap">
<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>

<style>
    /* Reset & Fond Général */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, sans-serif !important;
    }
    
    .stApp {
        background-color: #090a0f;
        color: #e1e3ea;
    }
    
    .block-container {
        padding-top: 2rem !important;
        padding-bottom: 1rem !important;
        max-width: 98% !important;
    }

    /* Scrollbars */
    ::-webkit-scrollbar { width: 4px; height: 4px; }
    ::-webkit-scrollbar-track { background: #090a0f; }
    ::-webkit-scrollbar-thumb { background: #1e2430; border-radius: 4px; }

    /* =========================================================
       ÉCRAN D'ACCUEIL 3D (FULLSCREEN OVERLAY)
       ========================================================= */
    #welcome-overlay {
        position: fixed;
        top: 0; left: 0;
        width: 100vw; height: 100vh;
        background: radial-gradient(circle at center, #0f1420 0%, #040508 100%);
        z-index: 99999999;
        display: flex;
        justify-content: center;
        align-items: center;
        user-select: none;
        transition: opacity 0.8s cubic-bezier(0.16, 1, 0.3, 1), visibility 0.8s ease;
    }

    #welcome-overlay.hidden {
        opacity: 0;
        visibility: hidden;
        pointer-events: none;
    }

    #globe-canvas {
        position: absolute;
        top: 0; left: 0;
        width: 100%; height: 100%;
        z-index: 1;
    }

    .welcome-card {
        position: relative;
        z-index: 2;
        text-align: center;
        background: rgba(13, 17, 26, 0.75);
        border: 1px solid rgba(240, 185, 11, 0.3);
        padding: 45px 55px;
        border-radius: 20px;
        backdrop-filter: blur(16px);
        box-shadow: 0 0 80px rgba(0, 0, 0, 0.85), 0 0 30px rgba(240, 185, 11, 0.15);
        max-width: 520px;
        width: 90%;
    }

    .welcome-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        font-family: 'JetBrains Mono', monospace;
        color: #f0b90b;
        font-size: 0.72rem;
        font-weight: 700;
        letter-spacing: 2px;
        text-transform: uppercase;
        background: rgba(240, 185, 11, 0.1);
        padding: 4px 12px;
        border-radius: 20px;
        border: 1px solid rgba(240, 185, 11, 0.25);
        margin-bottom: 12px;
    }

    .pulse-dot {
        width: 8px; height: 8px;
        background-color: #089981;
        border-radius: 50%;
        box-shadow: 0 0 8px #089981;
        animation: pulse 1.5s infinite;
    }

    @keyframes pulse {
        0% { transform: scale(0.95); opacity: 0.8; }
        50% { transform: scale(1.2); opacity: 1; box-shadow: 0 0 12px #089981; }
        100% { transform: scale(0.95); opacity: 0.8; }
    }

    .welcome-title {
        font-size: 1.1rem;
        font-weight: 800;
        color: #ffffff;
        letter-spacing: 1px;
    }

    .welcome-clock {
        font-family: 'JetBrains Mono', monospace;
        font-size: 4.5rem;
        font-weight: 800;
        color: #ffffff;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.2);
        margin: 10px 0;
        line-height: 1;
    }

    .welcome-sub {
        font-size: 0.75rem;
        color: #787b86;
        letter-spacing: 1.5px;
        text-transform: uppercase;
        margin-bottom: 28px;
    }

    .enter-btn {
        background: linear-gradient(135deg, #f0b90b 0%, #d4a007 100%);
        color: #090a0f;
        border: none;
        padding: 14px 36px;
        font-size: 0.88rem;
        font-weight: 800;
        letter-spacing: 1.5px;
        border-radius: 8px;
        cursor: pointer;
        transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
        box-shadow: 0 4px 20px rgba(240, 185, 11, 0.35);
        display: inline-flex;
        align-items: center;
        gap: 10px;
    }

    .enter-btn:hover {
        transform: translateY(-2px) scale(1.02);
        box-shadow: 0 6px 28px rgba(240, 185, 11, 0.55);
        background: linear-gradient(135deg, #fcd535 0%, #f0b90b 100%);
    }

    .enter-hint {
        margin-top: 14px;
        font-size: 0.65rem;
        color: #5d606b;
        letter-spacing: 0.5px;
    }

    /* Standard Cards UI */
    .metric-card-v2 {
        background: linear-gradient(145deg, #131722 0%, #0d1017 100%);
        border: 1px solid #1e222d;
        border-radius: 8px;
        padding: 8px 12px;
    }
    .metric-label { font-size: 0.68rem; font-weight: 600; color: #787b86; }
    .metric-price { font-family: 'JetBrains Mono'; font-size: 1.15rem; font-weight: 700; color: #f0f3fa; }
    .badge-bull { background: rgba(8, 153, 129, 0.15); color: #089981; padding: 2px 6px; border-radius: 4px; font-size:0.68rem; font-weight:600; }
    .badge-bear { background: rgba(242, 54, 69, 0.15); color: #f23645; padding: 2px 6px; border-radius: 4px; font-size:0.68rem; font-weight:600; }
    
    .stTabs [data-baseweb="tab-list"] { gap: 8px; background: #131722; padding: 6px; border-radius: 10px; border: 1px solid #1e222d; }
    .stTabs [data-baseweb="tab"] { background: transparent !important; border-radius: 6px !important; color: #787b86 !important; font-weight: 600 !important; font-size: 0.82rem !important; padding: 8px 22px !important; }
    .stTabs [aria-selected="true"] { color: #f0b90b !important; background: rgba(240, 185, 11, 0.1) !important; box-shadow: inset 0 0 0 1px rgba(240, 185, 11, 0.3) !important; }
</style>

<!-- STRUCTURE HTML DE L'ÉCRAN D'ACCUEIL -->
<div id="welcome-overlay" onclick="dismissWelcome()">
    <canvas id="globe-canvas"></canvas>
    <div class="welcome-card" onclick="event.stopPropagation()">
        <div class="welcome-badge">
            <span class="pulse-dot"></span> TERMINAL LIVE SESSION
        </div>
        <div class="welcome-title">TERMINAL TRADER PRO</div>
        <div class="welcome-clock" id="welcome-time">00:00:00</div>
        <div class="welcome-sub">HEURE DE PARIS — HEURE DU MARCHÉ</div>
        <button class="enter-btn" onclick="dismissWelcome()">
            <span>ENTRER DANS LE TERMINAL</span>
            <span style="font-size: 1.1rem;">➔</span>
        </button>
        <div class="enter-hint">Cliquez n'importe où pour déverrouiller l'accès</div>
    </div>
</div>

<!-- SCRIPT 3D GLOBE + HORLOGE + DÉVERROUILLAGE -->
<script>
(function() {
    let scene, camera, renderer, globeGroup;

    function init3DGlobe() {
        const canvas = parent.document.getElementById('globe-canvas') || document.getElementById('globe-canvas');
        if (!canvas) return;

        // Scene, Camera, Renderer
        scene = new THREE.Scene();
        camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.1, 1000);
        camera.position.z = 28;

        renderer = new THREE.WebGLRenderer({ canvas: canvas, alpha: true, antialias: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        globeGroup = new THREE.Group();
        scene.add(globeGroup);

        // 1. Sphère Maillée (Globe Wireframe Principal)
        const globeGeo = new THREE.SphereGeometry(10, 36, 36);
        const globeMat = new THREE.MeshBasicMaterial({
            color: 0xf0b90b,
            wireframe: true,
            transparent: true,
            opacity: 0.18
        });
        const globeMesh = new THREE.Mesh(globeGeo, globeMat);
        globeGroup.add(globeMesh);

        // 2. Points lumineux sur la surface (Continents / Villes)
        const ptsGeo = new THREE.BufferGeometry();
        const ptsCount = 1800;
        const ptsPos = new Float32Array(ptsCount * 3);

        for (let i = 0; i < ptsCount; i++) {
            const u = Math.random();
            const v = Math.random();
            const theta = u * Math.PI * 2;
            const phi = Math.acos(2 * v - 1);
            const r = 10.05;

            ptsPos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
            ptsPos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
            ptsPos[i * 3 + 2] = r * Math.cos(phi);
        }

        ptsGeo.setAttribute('position', new THREE.BufferAttribute(ptsPos, 3));
        const ptsMat = new THREE.PointsMaterial({
            size: 0.18,
            color: 0x089981,
            transparent: true,
            opacity: 0.75
        });
        const pointsMesh = new THREE.Points(ptsGeo, ptsMat);
        globeGroup.add(pointsMesh);

        // 3. Anneau Équatorial / Coordonnées Financial Tech
        const ringGeo = new THREE.RingGeometry(12.5, 12.6, 64);
        const ringMat = new THREE.MeshBasicMaterial({ color: 0xf0b90b, side: THREE.DoubleSide, transparent: true, opacity: 0.35 });
        const ringMesh = new THREE.Mesh(ringGeo, ringMat);
        ringMesh.rotation.x = Math.PI / 2;
        globeGroup.add(ringMesh);

        // 4. Champ de particules en arrière-plan
        const bgParticlesGeo = new THREE.BufferGeometry();
        const bgCount = 800;
        const bgPos = new Float32Array(bgCount * 3);
        for(let i=0; i<bgCount*3; i++) {
            bgPos[i] = (Math.random() - 0.5) * 100;
        }
        bgParticlesGeo.setAttribute('position', new THREE.BufferAttribute(bgPos, 3));
        const bgMat = new THREE.PointsMaterial({ size: 0.15, color: 0xffffff, transparent: true, opacity: 0.25 });
        const bgMesh = new THREE.Points(bgParticlesGeo, bgMat);
        scene.add(bgMesh);

        // Resize Event
        window.addEventListener('resize', () => {
            camera.aspect = window.innerWidth / window.innerHeight;
            camera.updateProjectionMatrix();
            renderer.setSize(window.innerWidth, window.innerHeight);
        });

        animate();
    }

    function animate() {
        requestAnimationFrame(animate);
        if (globeGroup) {
            globeGroup.rotation.y += 0.0025;
            globeGroup.rotation.x = 0.2;
        }
        renderer.render(scene, camera);
    }

    // Horloge Temps Réel
    function updateWelcomeClock() {
        const now = new Date();
        const timeStr = new Intl.DateTimeFormat('fr-FR', {
            timeZone: 'Europe/Paris',
            hour: '2-digit', minute: '2-digit', second: '2-digit',
            hour12: false
        }).format(now);

        const el = parent.document.getElementById('welcome-time') || document.getElementById('welcome-time');
        if (el) el.textContent = timeStr;
    }

    setInterval(updateWelcomeClock, 1000);
    updateWelcomeClock();

    // Démarrage 3D dès chargement du DOM
    setTimeout(init3DGlobe, 100);
})();

// Fonction globale pour masquer l'écran d'accueil au clic
function dismissWelcome() {
    const overlay = parent.document.getElementById('welcome-overlay') || document.getElementById('welcome-overlay');
    if (overlay) {
        overlay.classList.add('hidden');
    }
}
</script>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# DASHBOARD DE L'APPLICATION (SOUS L'ÉCRAN D'ACCUEIL)
# ---------------------------------------------------------

# En-tête de page avec horloges secondaires
header_html = """
<style>
    body { margin: 0; background: transparent; font-family: 'Inter', sans-serif; }
    .header-box { display: flex; justify-content: space-between; align-items: center; background: #131722; padding: 8px 16px; border: 1px solid #1e222d; border-radius: 8px; }
    .header-title { font-size: 1.1rem; font-weight: 900; color: #f0b90b; display: flex; align-items: center; gap: 8px; }
    .clocks-wrap { display: flex; gap: 10px; }
    .clock-card { background: #181c27; padding: 4px 12px; border-radius: 6px; border: 1px solid #2a2e39; text-align: center; min-width: 90px; }
    .clock-label { font-size: 0.6rem; color: #787b86; font-weight: 700; }
    .clock-time { font-family: 'JetBrains Mono', monospace; font-size: 0.92rem; color: #089981; font-weight: 600; }
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

# Bandeau de Marche
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
                data[name] = (curr, pct)
        except Exception:
            pass
    return data

mkt = fetch_market_data()
if mkt:
    cols = st.columns(len(mkt))
    for i, (k, (v, c)) in enumerate(mkt.items()):
        with cols[i]:
            badge_class = "badge-bull" if c >= 0 else "badge-bear"
            st.markdown(f"""
            <div class="metric-card-v2">
                <div style="display:flex; justify-content:space-between; align-items:center;">
                    <span class="metric-label">{k}</span>
                    <span class="{badge_class}">{c:+.2f}%</span>
                </div>
                <div class="metric-price">{v:,.2f}</div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 12px;'></div>", unsafe_allow_html=True)

# Navigation Principale
tab_main, tab_1, tab_2 = st.tabs(["⚡ Vue Marchés", "📈 Graphiques Pro", "📊 Portefeuille"])

with tab_main:
    st.markdown("### 🔥 Visualisation Heatmap Nasdaq 100")
    heatmap_html = """
    <div class="tradingview-widget-container" style="height: 520px; width: 100%;">
      <script type="text/javascript" src="https://s3.tradingview.com/external-embedding/embed-widget-stock-heatmap.js" async>
      {
        "dataSource": "NASDAQ100",
        "blockSize": "market_cap_basic",
        "blockColor": "change",
        "locale": "fr",
        "colorTheme": "dark",
        "hasTopBar": false,
        "isZoomEnabled": true,
        "width": "100%",
        "height": "520"
      }
      </script>
    </div>
    """
    components.html(heatmap_html, height=525)

with tab_1:
    st.info("Espace dédié aux analyses graphiques interactives.")

with tab_2:
    st.info("Espace dédié à la gestion des positions et portefeuilles.")
