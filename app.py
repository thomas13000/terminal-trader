import base64
import os
import streamlit as st
import streamlit.components.v1 as components

# ---------------------------------------------------------
# 1. CONFIGURATION STREAMLIT
# ---------------------------------------------------------
st.set_page_config(page_title="TERMINAL TRADER PRO", page_icon="⚡", layout="wide")


# ---------------------------------------------------------
# 2. CHARGEMENT AUDIO EN BASE64
# ---------------------------------------------------------
def load_audio_b64(filename="acdc.mp3"):
    if os.path.exists(filename):
        with open(filename, "rb") as f:
            return base64.b64encode(f.read()).decode()
    return ""


audio_b64 = load_audio_b64("acdc.mp3")


# ---------------------------------------------------------
# 3. OVERLAY 3D & LECTURE AUDIO (10s -> 35s avec Fade)
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
            body, html {{ width: 100%; height: 100%; overflow: hidden; font-family: 'Inter', sans-serif; background: #05070a; }}
            
            #welcome-screen-root {{
                position: fixed; top: 0; left: 0; width: 100vw; height: 100vh;
                background: radial-gradient(circle at center, #0e131f 0%, #030406 100%);
                z-index: 99999999; display: flex; align-items: center; justify-content: space-between;
                padding: 0 4vw; cursor: pointer;
            }}
            #canvas-3d {{ position: absolute; top: 0; left: 0; width: 100%; height: 100%; z-index: 1; }}
            
            .left-panel {{
                position: relative; z-index: 2; text-align: center;
                background: rgba(13, 17, 26, 0.82); border: 1px solid rgba(240, 185, 11, 0.35);
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
                border: none; padding: 12px 24px; font-size: 0.8rem; font-weight: 800;
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
            <div class="hint-bottom">Cliquez pour activer la session audio</div>
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
        
        // --- TIMING MUSICAL DESIRÉ ---
        const startSecond = 10; // Début à 10s
        const endSecond   = 35; // Fin à 35s
        const fadeSec     = 2.5; // Durée du fondu (2.5s)

        function enterTerminalWithAudio() {{
            if (audioDataUri) {{
                try {{
                    const audio = new Audio(audioDataUri);
                    audio.volume = 0.85; // Volume initial
                    audio.currentTime = startSecond; // Saut direct à la 10ème seconde
                    audio.play().catch(e => console.log("Erreur lecture audio:", e));

                    // Durée totale de lecture (25 secondes)
                    const totalPlayMs = (endSecond - startSecond) * 1000;
                    // Moment où démarre le fondu (ex: à 22.5s de lecture = 32.5s dans la chanson)
                    const fadeStartMs = totalPlayMs - (fadeSec * 1000);

                    // Déclenchement du Fade Out
                    setTimeout(() => {{
                        const intervalMs = 50;
                        const steps = (fadeSec * 1000) / intervalMs;
                        const volStep = audio.volume / steps;

                        const fadeInterval = setInterval(() => {{
                            if (audio.volume > volStep) {{
                                audio.volume -= volStep;
                            }} else {{
                                audio.volume = 0;
                                audio.pause();
                                clearInterval(fadeInterval);
                            }}
                        }}, intervalMs);
                    }}, Math.max(0, fadeStartMs));

                }} catch(e) {{
                    console.log("Erreur audio:", e);
                }}
            }}
            dismissOverlay();
        }}

        function dismissOverlay() {{
            const root = document.getElementById('welcome-screen-root');
            if (root) root.style.display = 'none';
            try {{
                const iframes = window.parent.document.querySelectorAll('iframe');
                iframes.forEach(iframe => {{
                    if (iframe.contentWindow === window) iframe.style.display = 'none';
                }});
            }} catch(e) {{}}
        }}

        function expandIframeToFullscreen() {{
            try {{
                const iframes = window.parent.document.querySelectorAll('iframe');
                iframes.forEach(iframe => {{
                    if (iframe.contentWindow === window) {{
                        iframe.style.position = 'fixed'; iframe.style.top = '0'; iframe.style.left = '0';
                        iframe.style.width = '100vw'; iframe.style.height = '100vh'; iframe.style.zIndex = '99999999'; iframe.style.border = 'none';
                    }}
                }});
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


render_welcome_screen(audio_b64)

# ---------------------------------------------------------
# 4. INTERFACE DU TERMINAL DE TRADING
# ---------------------------------------------------------
st.markdown(
    """<style>.stApp { background-color: #090a0f; color: #e1e3ea; }</style>""",
    unsafe_allow_html=True,
)
st.title("⚡ TERMINAL TRADER PRO CONNECTÉ")
st.success("Session Iron Man active avec l'extrait musical AC/DC (10s ➔ 35s) !")
