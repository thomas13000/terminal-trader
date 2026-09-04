import streamlit as st
import streamlit.components.v1 as components
import yfinance as yf

# ---------------------------------------------------------
# CONFIGURATION DE LA PAGE
# ---------------------------------------------------------
st.set_page_config(
    page_title="TERMINAL TRADER PRO",
    page_icon="⚡",
    layout="wide"
)

# ---------------------------------------------------------
# RÉCUPÉRATION DES DONNÉES EN DIRECT (NASDAQ, S&P 500, DXY)
# ---------------------------------------------------------
@st.cache_data(ttl=60)
def fetch_welcome_market_data():
    tickers = {
        "NASDAQ 100": "^IXIC",
        "S&P 500": "^GSPC",
        "DOLLAR INDEX (DXY)": "DX-Y.NYB"
    }
    data = {}
    for name, ticker in tickers.items():
        try:
            df = yf.Ticker(ticker).history(period="2d")
            if len(df) >= 2:
                curr = df['Close'].iloc[-1]
                prev = df['Close'].iloc[-2]
                pct = ((curr - prev) / prev) * 100
                data[name] = {
                    "price": f"{curr:,.2f}",
                    "pct": f"{pct:+.2f}%",
                    "bull": pct >= 0
                }
            else:
                data[name] = {"price": "N/A", "pct": "0.00%", "bull": True}
        except Exception:
            data[name] = {"price": "N/A", "pct": "0.00%", "bull": True}
    return data

market_data = fetch_welcome_market_data()

# ---------------------------------------------------------
# COMPOSANT HTML 3D AUTONOME (GLOBE + HORLOGE + PRIX LATÉRAUX)
# ---------------------------------------------------------
def render_3d_welcome_overlay(mkt_data):
    # Formatage des cartes HTML du panneau latéral
    cards_html = ""
    for name, info in mkt_data.items():
        color = "#089981" if info["bull"] else "#f23645"
        bg_color = "rgba(8, 153, 129, 0.12)" if info["bull"] else "rgba(242, 54, 69, 0.12)"
        cards_html += f"""
        <div class="side-card">
            <div class="side-card-title">{name}</div>
            <div class="side-card-row">
                <span class="side-card-price">{info['price']}</span>
                <span class="side-card-badge" style="color: {color}; background: {bg_color};">{info['pct']}</span>
            </div>
        </div>
        """

    html_code = f"""
    <!DOCTYPE html>
    <html lang="fr">
    <head>
        <meta charset="UTF-8">
        <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;900&family=JetBrains+Mono:wght@500;700;800&display=swap">
        <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
        <style>
            * {{ margin: 0; padding: 0; box-sizing: border-box; user-select: none; }}
            body, html {{ width: 100%; height: 100%; overflow: hidden; font-family: 'Inter', sans-serif; background: #05070a; }}

            #welcome-screen-root {{
                position: fixed;
                top: 0; left: 0;
                width: 100vw; height: 100vh;
                background: radial-gradient(circle at center, #0e131f 0%, #030406 100%);
                z-index: 99999999;
                display: flex;
                align-items: center;
                justify-content: space-between;
                padding: 0 5vw;
                cursor: pointer;
            }}

            #canvas-3d {{
                position: absolute;
                top: 0; left: 0;
                width: 100%; height: 100%;
                z-index: 1;
            }}

            /* --- CENTRE : HORLOGE ET ACCUEIL --- */
            .center-content {{
                position: relative;
                z-index: 2;
                text-align: center;
                background: rgba(13, 17, 26, 0.75);
                border: 1px solid rgba(240, 185, 11, 0.35);
                padding: 40px 50px;
                border-radius: 20px;
                backdrop-filter: blur(16px);
                box-shadow: 0 0 60px rgba(0, 0, 0, 0.9), 0 0 25px rgba(240, 185, 11, 0.15);
                max-width: 480px;
            }}

            .badge-live {{
                display: inline-flex;
                align-items: center;
                gap: 8px;
                font-family: 'JetBrains Mono', monospace;
                color: #f0b90b;
                font-size: 0.7rem;
                font-weight: 700;
                letter-spacing: 2px;
                background: rgba(240, 185, 11, 0.1);
                padding: 4px 12px;
                border-radius: 20px;
                border: 1px solid rgba(240, 185, 11, 0.25);
                margin-bottom: 12px;
            }}

            .dot-pulse {{
                width: 8px; height: 8px;
                background-color: #089981;
                border-radius: 50%;
                box-shadow: 0 0 8px #089981;
                animation: pulse 1.5s infinite;
            }}

            @keyframes pulse {{
                0% {{ transform: scale(0.95); opacity: 0.8; }}
                50% {{ transform: scale(1.2); opacity: 1; box-shadow: 0 0 12px #089981; }}
                100% {{ transform: scale(0.95); opacity: 0.8; }}
            }}

            .clock-main {{
                font-family: 'JetBrains Mono', monospace;
                font-size: 4.8rem;
                font-weight: 800;
                color: #ffffff;
                text-shadow: 0 0 30px rgba(255, 255, 255, 0.25);
                margin: 8px 0;
                line-height: 1;
            }}

            .clock-sub {{
                font-size: 0.72rem;
                color: #787b86;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                margin-bottom: 24px;
            }}

            .btn-enter {{
                background: linear-gradient(135deg, #f0b90b 0%, #d4a007 100%);
                color: #090a0f;
                border: none;
                padding: 14px 32px;
                font-size: 0.85rem;
                font-weight: 800;
                letter-spacing: 1.5px;
                border-radius: 8px;
                cursor: pointer;
                box-shadow: 0 4px 20px rgba(240, 185, 11, 0.35);
                transition: transform 0.2s, box-shadow 0.2s;
            }}

            .btn-enter:hover {{
                transform: scale(1.03);
                box-shadow: 0 6px 28px rgba(240, 185, 11, 0.55);
            }}

            /* --- CÔTÉ DROIT : PANNEAU DES MARCHÉS --- */
            .side-panel {{
                position: relative;
                z-index: 2;
                display: flex;
                flex-direction: column;
                gap: 12px;
                width: 280px;
            }}

            .side-panel-header {{
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.72rem;
                font-weight: 700;
                color: #787b86;
                letter-spacing: 1.5px;
                text-transform: uppercase;
                margin-bottom: 4px;
                display: flex;
                align-items: center;
                gap: 6px;
            }}

            .side-card {{
                background: rgba(19, 23, 34, 0.82);
                border: 1px solid rgba(255, 255, 255, 0.08);
                border-left: 3px solid #f0b90b;
                padding: 12px 16px;
                border-radius: 8px;
                backdrop-filter: blur(12px);
                box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
            }}

            .side-card-title {{
                font-size: 0.68rem;
                font-weight: 700;
                color: #787b86;
                letter-spacing: 0.5px;
                margin-bottom: 4px;
            }}

            .side-card-row {{
                display: flex;
                justify-content: space-between;
                align-items: center;
            }}

            .side-card-price {{
                font-family: 'JetBrains Mono', monospace;
                font-size: 1.15rem;
                font-weight: 700;
                color: #ffffff;
            }}

            .side-card-badge {{
                font-family: 'JetBrains Mono', monospace;
                font-size: 0.7rem;
                font-weight: 700;
                padding: 2px 8px;
                border-radius: 4px;
            }}

            .hint-bottom {{
                margin-top: 12px;
                font-size: 0.65rem;
                color: #5d606b;
                text-align: center;
            }}
        </style>
    </head>
    <body>

    <div id="welcome-screen-root" onclick="dismissOverlay()">
        <!-- CANVAS THREE.JS -->
        <canvas id="canvas-3d"></canvas>

        <!-- CENTRE : HORLOGE + TITRE -->
        <div class="center-content" onclick="event.stopPropagation()">
            <div class="badge-live"><span class="dot-pulse"></span> TERMINAL LIVE SESSION</div>
            <div class="clock-main" id="clock-display">00:00:00</div>
            <div class="clock-sub">HEURE DE PARIS — MARKET STANDBY</div>
            <button class="btn-enter" onclick="dismissOverlay()">ENTRER DANS LE TERMINAL ➔</button>
            <div class="hint-bottom">Cliquez n'importe où pour ouvrir la session</div>
        </div>

        <!-- CÔTÉ DROIT : PRICING MARCHÉS -->
        <div class="side-panel" onclick="event.stopPropagation()">
            <div class="side-panel-header">⚡ MARCHÉS EN DIRECT</div>
            {cards_html}
        </div>
    </div>

    <script>
        // --- 1. Agrandir automatiquement le composant Streamlit sur tout l'écran ---
        function expandIframeToFullscreen() {{
            try {{
                const iframes = window.parent.document.querySelectorAll('iframe');
                iframes.forEach(iframe => {{
                    if (iframe.contentWindow === window) {{
                        iframe.style.position = 'fixed';
                        iframe.style.top = '0';
                        iframe.style.left = '0';
                        iframe.style.width = '100vw';
                        iframe.style.height = '100vh';
                        iframe.style.zIndex = '99999999';
                        iframe.style.border = 'none';
                    }}
                }});
            }} catch(e) {{
                console.log("Mode plein écran autonome actif");
            }}
        }}
        expandIframeToFullscreen();

        // --- 2. Fonction de Déverrouillage (Fermeture de l'écran d'accueil) ---
        function dismissOverlay() {{
            const root = document.getElementById('welcome-screen-root');
            if (root) root.style.display = 'none';

            try {{
                const iframes = window.parent.document.querySelectorAll('iframe');
                iframes.forEach(iframe => {{
                    if (iframe.contentWindow === window) {{
                        iframe.style.display = 'none';
                    }}
                }});
            }} catch(e) {{}}
        }}

        // --- 3. Horloge en Temps Réel ---
        function updateClock() {{
            const now = new Date();
            const timeStr = new Intl.DateTimeFormat('fr-FR', {{
                timeZone: 'Europe/Paris',
                hour: '2-digit', minute: '2-digit', second: '2-digit',
                hour12: false
            }}).format(now);
            const el = document.getElementById('clock-display');
            if (el) el.textContent = timeStr;
        }}
        setInterval(updateClock, 1000);
        updateClock();

        // --- 4. Globe Terrestre 3D avec Three.js ---
        let scene, camera, renderer, globeGroup;

        function init3DGlobe() {{
            const canvas = document.getElementById('canvas-3d');
            scene = new THREE.Scene();

            camera = new THREE.PerspectiveCamera(55, window.innerWidth / window.innerHeight, 0.1, 1000);
            camera.position.z = 25;

            renderer = new THREE.WebGLRenderer({{ canvas: canvas, alpha: true, antialias: true }});
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

            globeGroup = new THREE.Group();
            scene.add(globeGroup);

            // Sphere Wireframe principale
            const globeGeo = new THREE.SphereGeometry(9.5, 32, 32);
            const globeMat = new THREE.MeshBasicMaterial({{
                color: 0xf0b90b,
                wireframe: true,
                transparent: true,
                opacity: 0.18
            }});
            const globeMesh = new THREE.Mesh(globeGeo, globeMat);
            globeGroup.add(globeMesh);

            // Points Lumineux (Continents / Villes)
            const ptsGeo = new THREE.BufferGeometry();
            const ptsCount = 1600;
            const ptsPos = new Float32Array(ptsCount * 3);

            for (let i = 0; i < ptsCount; i++) {{
                const u = Math.random();
                const v = Math.random();
                const theta = u * Math.PI * 2;
                const phi = Math.acos(2 * v - 1);
                const r = 9.55;

                ptsPos[i * 3] = r * Math.sin(phi) * Math.cos(theta);
                ptsPos[i * 3 + 1] = r * Math.sin(phi) * Math.sin(theta);
                ptsPos[i * 3 + 2] = r * Math.cos(phi);
            }}

            ptsGeo.setAttribute('position', new THREE.BufferAttribute(ptsPos, 3));
            const ptsMat = new THREE.PointsMaterial({{
                size: 0.18,
                color: 0x089981,
                transparent: true,
                opacity: 0.8
            }});
            const pointsMesh = new THREE.Points(ptsGeo, ptsMat);
            globeGroup.add(pointsMesh);

            // Anneau orbital lumineux
            const ringGeo = new THREE.RingGeometry(12, 12.1, 64);
            const ringMat = new THREE.MeshBasicMaterial({{ color: 0xf0b90b, side: THREE.DoubleSide, transparent: true, opacity: 0.35 }});
            const ringMesh = new THREE.Mesh(ringGeo, ringMat);
            ringMesh.rotation.x = Math.PI / 2.2;
            globeGroup.add(ringMesh);

            // Ajustement redimensionnement
            window.addEventListener('resize', () => {{
                camera.aspect = window.innerWidth / window.innerHeight;
                camera.updateProjectionMatrix();
                renderer.setSize(window.innerWidth, window.innerHeight);
            }});

            animate();
        }}

        function animate() {{
            requestAnimationFrame(animate);
            if (globeGroup) {{
                globeGroup.rotation.y += 0.003;
            }}
            renderer.render(scene, camera);
        }}

        window.onload = init3DGlobe;
    </script>
    </body>
    </html>
    """
    components.html(html_code, height=0)

# Affichage de l'écran d'accueil
render_3d_welcome_overlay(market_data)

# ---------------------------------------------------------
# APPLICATION TERMINAL (ACCESSIBLE APRÈS DÉVERROUILLAGE)
# ---------------------------------------------------------

# Styles CSS du Terminal
st.markdown("""
<style>
    .stApp { background-color: #090a0f; color: #e1e3ea; }
    .block-container { padding-top: 1.5rem !important; max-width: 98% !important; }
    .header-box { display: flex; justify-content: space-between; align-items: center; background: #131722; padding: 10px 16px; border: 1px solid #1e222d; border-radius: 8px; margin-bottom: 12px; }
    .header-title { font-size: 1.15rem; font-weight: 900; color: #f0b90b; }
    .metric-card-v2 { background: linear-gradient(145deg, #131722 0%, #0d1017 100%); border: 1px solid #1e222d; border-radius: 8px; padding: 10px 14px; }
    .metric-label { font-size: 0.7rem; font-weight: 600; color: #787b86; }
    .metric-price { font-family: 'JetBrains Mono', monospace; font-size: 1.2rem; font-weight: 700; color: #f0f3fa; }
    .badge-bull { background: rgba(8, 153, 129, 0.15); color: #089981; padding: 2px 6px; border-radius: 4px; font-size:0.7rem; font-weight:600; }
    .badge-bear { background: rgba(242, 54, 69, 0.15); color: #f23645; padding: 2px 6px; border-radius: 4px; font-size:0.7rem; font-weight:600; }
</style>
""", unsafe_allow_html=True)

# Barre d'en-tête
st.markdown("""
<div class="header-box">
    <div class="header-title">⚡ TERMINAL TRADER PRO</div>
    <div style="font-family: 'JetBrains Mono', monospace; color: #089981; font-weight:600; font-size: 0.9rem;">
        ● LIVE SESSION CONNECTED
    </div>
</div>
""", unsafe_allow_html=True)

# Ligne des prix
cols = st.columns(len(market_data))
for i, (k, info) in enumerate(market_data.items()):
    with cols[i]:
        badge_class = "badge-bull" if info["bull"] else "badge-bear"
        st.markdown(f"""
        <div class="metric-card-v2">
            <div style="display:flex; justify-content:space-between; align-items:center;">
                <span class="metric-label">{k}</span>
                <span class="{badge_class}">{info['pct']}</span>
            </div>
            <div class="metric-price">{info['price']}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("<div style='margin-bottom: 16px;'></div>", unsafe_allow_html=True)

# Onglets du Terminal
tab_main, tab_1, tab_2 = st.tabs(["⚡ Vue Marchés", "📈 Graphiques Pro", "📊 Portefeuille"])

with tab_main:
    st.markdown("### 🔥 Visualisation Heatmap Nasdaq 100")
    heatmap_html = """
    <div class="tradingview-widget-container" style="height: 540px; width: 100%;">
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
        "height": "540"
      }
      </script>
    </div>
    """
    components.html(heatmap_html, height=545)

with tab_1:
    st.info("Espace dédié aux analyses graphiques avancées.")

with tab_2:
    st.info("Espace dédié à la gestion des positions.")
