import os
import streamlit as st
import numpy as np
from PIL import Image
from keras.models import load_model
import paho.mqtt.client as mqtt
import json
import platform
import base64
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events

# =====================================================
# CONFIG STREAMLIT
# =====================================================

st.set_page_config(
    page_title="VAULT//SYSTEM",
    page_icon="🔐",
    layout="centered"
)

# =====================================================
# CYBERPUNK CSS
# =====================================================

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&family=Share+Tech+Mono&display=swap');

/* ── ROOT VARIABLES ── */
:root {
    --cyan:    #00f5ff;
    --magenta: #ff2d78;
    --dark:    #080b14;
    --panel:   rgba(8, 11, 20, 0.85);
    --glass:   rgba(0, 245, 255, 0.05);
    --border:  rgba(0, 245, 255, 0.25);
    --text:    #c8f0f5;
    --dim:     rgba(200, 240, 245, 0.45);
}

/* ── GLOBAL BACKGROUND ── */
.stApp {
    background-color: var(--dark) !important;
    background-image:
        repeating-linear-gradient(
            0deg,
            transparent,
            transparent 2px,
            rgba(0, 245, 255, 0.018) 2px,
            rgba(0, 245, 255, 0.018) 4px
        ),
        radial-gradient(ellipse 80% 60% at 50% 0%, rgba(255,45,120,0.12) 0%, transparent 70%),
        radial-gradient(ellipse 60% 40% at 80% 100%, rgba(0,245,255,0.10) 0%, transparent 70%);
    font-family: 'Share Tech Mono', monospace !important;
    color: var(--text) !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding-top: 1.5rem !important; max-width: 760px; }

/* ── TITLE / HEADER ── */
h1 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 900 !important;
    font-size: 2rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase;
    background: linear-gradient(90deg, var(--cyan), var(--magenta));
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    text-align: center;
    margin-bottom: 0.15rem !important;
    filter: drop-shadow(0 0 18px rgba(0,245,255,0.55));
}

/* ── SUBHEADERS ── */
h2, h3 {
    font-family: 'Orbitron', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.22em !important;
    text-transform: uppercase;
    color: var(--cyan) !important;
    border-left: 3px solid var(--magenta);
    padding-left: 0.65rem;
    margin-top: 1.5rem !important;
    text-shadow: 0 0 10px rgba(0,245,255,0.6);
}

/* ── PANELS / SECTIONS ── */
div[data-testid="stVerticalBlock"] > div {
    border-radius: 2px;
}

/* HUD panel wrapper — applied via markdown */
.hud-panel {
    background: var(--glass);
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 1.2rem 1.4rem;
    margin-bottom: 1.2rem;
    position: relative;
    box-shadow:
        0 0 0 1px rgba(0,245,255,0.06),
        inset 0 1px 0 rgba(0,245,255,0.12),
        0 4px 32px rgba(0,0,0,0.6);
}

/* Corner accents */
.hud-panel::before,
.hud-panel::after {
    content: '';
    position: absolute;
    width: 12px; height: 12px;
    border-color: var(--cyan);
    border-style: solid;
}
.hud-panel::before { top: -1px; left: -1px; border-width: 2px 0 0 2px; }
.hud-panel::after  { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; }

.hud-label {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.65rem;
    letter-spacing: 0.3em;
    color: var(--magenta);
    text-transform: uppercase;
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}
.hud-label::before {
    content: '';
    display: inline-block;
    width: 18px; height: 1px;
    background: var(--magenta);
}
.hud-label::after {
    content: '';
    flex: 1;
    height: 1px;
    background: linear-gradient(90deg, var(--magenta), transparent);
}

/* ── STREAMLIT ELEMENTS ── */

/* Buttons */
.stButton > button {
    font-family: 'Orbitron', sans-serif !important;
    font-size: 0.72rem !important;
    letter-spacing: 0.18em !important;
    text-transform: uppercase;
    background: transparent !important;
    color: var(--cyan) !important;
    border: 1px solid var(--cyan) !important;
    border-radius: 2px !important;
    padding: 0.55rem 1.4rem !important;
    transition: all 0.2s ease !important;
    box-shadow: 0 0 10px rgba(0,245,255,0.2), inset 0 0 10px rgba(0,245,255,0.04) !important;
    width: 100%;
}
.stButton > button:hover {
    background: rgba(0,245,255,0.1) !important;
    box-shadow: 0 0 20px rgba(0,245,255,0.5), inset 0 0 16px rgba(0,245,255,0.08) !important;
    color: #fff !important;
}

/* Camera input */
div[data-testid="stCameraInput"] {
    border: 1px solid var(--border) !important;
    border-radius: 4px;
    background: var(--glass) !important;
    padding: 0.5rem;
}
div[data-testid="stCameraInput"] label {
    font-family: 'Share Tech Mono', monospace !important;
    color: var(--dim) !important;
    font-size: 0.8rem !important;
}

/* Alerts */
div[data-testid="stAlert"] {
    border-radius: 2px !important;
    font-family: 'Share Tech Mono', monospace !important;
    font-size: 0.82rem !important;
}
/* Success */
div[data-testid="stAlert"][data-baseweb="notification"]:has(svg[data-testid="stAlertDynamicIcon-success"]),
.element-container:has(.stSuccess) > div {
    background: rgba(0, 255, 120, 0.06) !important;
    border-left: 3px solid #00ff88 !important;
    color: #00ff88 !important;
}
/* Error */
.element-container:has(.stError) > div {
    background: rgba(255, 45, 120, 0.07) !important;
    border-left: 3px solid var(--magenta) !important;
    color: var(--magenta) !important;
}
/* Warning */
.element-container:has(.stWarning) > div {
    background: rgba(255, 180, 0, 0.06) !important;
    border-left: 3px solid #ffb400 !important;
    color: #ffb400 !important;
}

/* st.write / st.text */
p, .stMarkdown p {
    font-family: 'Share Tech Mono', monospace !important;
    color: var(--text) !important;
    font-size: 0.82rem !important;
}

/* Divider */
hr {
    border-color: rgba(0,245,255,0.12) !important;
    margin: 1.5rem 0 !important;
}

/* ── SCROLLBAR ── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: var(--dark); }
::-webkit-scrollbar-thumb { background: var(--magenta); border-radius: 2px; }

/* ── SCANLINE OVERLAY (decorative) ── */
.stApp::after {
    content: '';
    position: fixed;
    inset: 0;
    background: repeating-linear-gradient(
        to bottom,
        transparent 0px,
        transparent 3px,
        rgba(0,0,0,0.07) 3px,
        rgba(0,0,0,0.07) 4px
    );
    pointer-events: none;
    z-index: 9999;
}

/* ── PYTHON VERSION LINE ── */
.version-tag {
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.65rem;
    color: var(--dim);
    text-align: center;
    letter-spacing: 0.12em;
    margin-top: -0.4rem;
    margin-bottom: 1.2rem;
}

/* ── VOICE RESULT TEXT ── */
.voice-detected {
    font-family: 'Orbitron', sans-serif;
    font-size: 0.85rem;
    text-align: center;
    color: var(--cyan);
    letter-spacing: 0.1em;
    padding: 0.6rem;
    border: 1px solid rgba(0,245,255,0.2);
    background: rgba(0,245,255,0.04);
    border-radius: 2px;
    text-shadow: 0 0 12px rgba(0,245,255,0.7);
}

/* ── STATUS BADGE ── */
.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    font-family: 'Orbitron', sans-serif;
    font-size: 0.68rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    padding: 0.3rem 0.8rem;
    border-radius: 2px;
    margin: 0.4rem 0;
}
.status-badge.authorized {
    color: #00ff88;
    border: 1px solid rgba(0,255,136,0.4);
    background: rgba(0,255,136,0.06);
    text-shadow: 0 0 8px rgba(0,255,136,0.6);
}
.status-badge.locked {
    color: var(--magenta);
    border: 1px solid rgba(255,45,120,0.4);
    background: rgba(255,45,120,0.06);
    text-shadow: 0 0 8px rgba(255,45,120,0.6);
}
.status-dot {
    width: 7px; height: 7px;
    border-radius: 50%;
    animation: pulse-dot 1.4s ease-in-out infinite;
}
.status-badge.authorized .status-dot { background: #00ff88; box-shadow: 0 0 6px #00ff88; }
.status-badge.locked .status-dot { background: var(--magenta); box-shadow: 0 0 6px var(--magenta); }
@keyframes pulse-dot {
    0%, 100% { opacity: 1; transform: scale(1); }
    50%       { opacity: 0.5; transform: scale(0.7); }
}

/* ── VOICE BUTTON OVERRIDE (bokeh inside iframe) ── */
iframe { background: transparent !important; }

</style>
""", unsafe_allow_html=True)

# =====================================================
# HEADER
# =====================================================

st.markdown("<h1>VAULT // SYSTEM</h1>", unsafe_allow_html=True)
st.markdown(
    f"<div class='version-tag'>◈ PYTHON {platform.python_version()} &nbsp;·&nbsp; AI-SECURED &nbsp;·&nbsp; MQTT ONLINE ◈</div>",
    unsafe_allow_html=True
)

# =====================================================
# MQTT
# =====================================================

BROKER = "broker.mqttdashboard.com"
PUERTO = 1883
TOPIC_ESTADO = "cofre/estado"
TOPIC_VOZ = "cofre/voz"

client = mqtt.Client()
client.connect(BROKER, PUERTO, 60)
client.loop_start()

# =====================================================
# CARGAR MODELO
# =====================================================

model = load_model("keras_model.h5", compile=False)

with open("labels.txt", "r") as f:
    class_names = f.read().splitlines()

# =====================================================
# VARIABLES DE ESTADO
# =====================================================

if "autorizado" not in st.session_state:
    st.session_state.autorizado = False

if "cofre_abierto" not in st.session_state:
    st.session_state.cofre_abierto = False

# =====================================================
# FUNCIÓN MQTT
# =====================================================

def publicar(topic, mensaje):
    client.publish(topic, json.dumps(mensaje))

# =====================================================
# FUNCIÓN IMAGEN A BASE64
# =====================================================

def imagen_a_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode()

# =====================================================
# RECONOCIMIENTO FACIAL
# =====================================================

st.markdown("""
<div class='hud-panel'>
  <div class='hud-label'>módulo 01 — identificación biométrica</div>
""", unsafe_allow_html=True)

st.subheader("📷 Reconocimiento Facial")

img_file_buffer = st.camera_input("ACTIVAR ESCÁNER FACIAL")

if img_file_buffer is not None:
    image = Image.open(img_file_buffer).convert("RGB")
    image = image.resize((224, 224))
    image_array = np.array(image)
    normalized_image_array = (image_array.astype(np.float32) / 127.0) - 1

    data = np.ndarray(shape=(1, 224, 224, 3), dtype=np.float32)
    data[0] = normalized_image_array

    prediction = model.predict(data)
    index = np.argmax(prediction)
    class_name = class_names[index]
    confidence_score = prediction[0][index]

    st.markdown(f"<p>› CLASE DETECTADA: <span style='color:#00f5ff'>{class_name}</span></p>", unsafe_allow_html=True)
    st.markdown(f"<p>› CONFIANZA: <span style='color:#00f5ff'>{confidence_score:.2f}</span></p>", unsafe_allow_html=True)

    if (
        ("Dueño 1" in class_name or "Dueño 2" in class_name)
        and confidence_score > 0.85
    ):
        st.success("✅ Dueño reconocido — acceso concedido")
        publicar(TOPIC_ESTADO, {"estado": "DUENO"})
        st.session_state.autorizado = True
    else:
        st.error("🚨 Identidad no autorizada — alerta activada")
        publicar(TOPIC_ESTADO, {"estado": "INTRUSO"})
        st.session_state.autorizado = False

st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# CONTROL POR VOZ
# =====================================================

st.markdown("""
<div class='hud-panel'>
  <div class='hud-label'>módulo 02 — interfaz de voz</div>
""", unsafe_allow_html=True)

st.subheader("🎤 Control por Voz del Cofre")

if st.session_state.autorizado:

    st.markdown("""
        <p style='text-align:center; color:rgba(200,240,245,0.55); font-size:0.78rem; letter-spacing:0.1em;'>
            DI <span style='color:#ff2d78; font-weight:bold;'>ÁBRETE</span>
            &nbsp;o&nbsp;
            <span style='color:#ff2d78; font-weight:bold;'>CIÉRRATE</span>
            para controlar el cofre
        </p>
    """, unsafe_allow_html=True)

    stt_button = Button(
        label="◉  INICIAR ESCUCHA",
        width=220,
        button_type="success",
        stylesheets=["""
            .bk-btn {
                font-family: 'Orbitron', sans-serif !important;
                font-size: 11px !important;
                letter-spacing: 3px !important;
                text-transform: uppercase;
                background: transparent !important;
                color: #00f5ff !important;
                border: 1px solid #00f5ff !important;
                border-radius: 2px !important;
                padding: 10px 20px !important;
                box-shadow: 0 0 14px rgba(0,245,255,0.3) !important;
                transition: all 0.2s !important;
                width: 100%;
            }
            .bk-btn:hover {
                background: rgba(0,245,255,0.1) !important;
                box-shadow: 0 0 24px rgba(0,245,255,0.6) !important;
            }
        """]
    )

    stt_button.js_on_event("button_click", CustomJS(code="""
        var recognition = new webkitSpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'es-ES';

        recognition.onresult = function(e) {
            var value = "";
            for (var i = e.resultIndex; i < e.results.length; ++i) {
                if (e.results[i].isFinal) {
                    value += e.results[i][0].transcript;
                }
            }
            if (value != "") {
                document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
            }
        }
        recognition.start();
    """))

    result = streamlit_bokeh_events(
        stt_button,
        events="GET_TEXT",
        key="listen",
        refresh_on_update=False,
        override_height=75,
        debounce_time=0
    )

    # =====================================================
    # PROCESAR COMANDO DE VOZ
    # =====================================================

    if result and "GET_TEXT" in result:
        texto = result.get("GET_TEXT").strip().lower()

        st.markdown(
            f"<div class='voice-detected'>⬡ AUDIO CAPTADO: &nbsp;<i>{texto.upper()}</i></div>",
            unsafe_allow_html=True
        )

        comandos_abrir  = ["ábrete", "abrete", "abrir", "abre"]
        comandos_cerrar = ["ciérrate", "cierrate", "cerrar", "cierra"]

        if any(cmd in texto for cmd in comandos_abrir):
            publicar(TOPIC_VOZ, {"cofre": "ABRIR"})
            st.session_state.cofre_abierto = True
            st.success("📦 Cofre abierto")

        elif any(cmd in texto for cmd in comandos_cerrar):
            publicar(TOPIC_VOZ, {"cofre": "CERRAR"})
            st.session_state.cofre_abierto = False
            st.warning("📦 Cofre cerrado")

        else:
            st.error(f"❌ Comando no reconocido: '{texto}'")

else:
    st.markdown("""
        <div class='status-badge locked'>
            <span class='status-dot'></span>
            ACCESO DENEGADO — AUTENTICACIÓN REQUERIDA
        </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# ESTADO VISUAL DEL COFRE
# =====================================================

st.markdown("""
<div class='hud-panel'>
  <div class='hud-label'>módulo 03 — estado del sistema</div>
""", unsafe_allow_html=True)

st.subheader("📦 Estado del Cofre")

b64_cerrado = imagen_a_base64("safe_closed.png")
b64_abierto = imagen_a_base64("safe_opened.png")

op_cerrado = 0 if st.session_state.cofre_abierto else 1
op_abierto = 1 if st.session_state.cofre_abierto else 0

# Status badge
if st.session_state.cofre_abierto:
    st.markdown("""
        <div class='status-badge authorized'>
            <span class='status-dot'></span>
            COFRE: ABIERTO
        </div>
    """, unsafe_allow_html=True)
else:
    st.markdown("""
        <div class='status-badge locked'>
            <span class='status-dot'></span>
            COFRE: CERRADO
        </div>
    """, unsafe_allow_html=True)

st.components.v1.html(f"""
    <style>
        body {{ margin: 0; background: transparent; }}
        .vault-wrap {{
            position: relative;
            width: 300px;
            height: 300px;
            margin: 0 auto;
            filter: drop-shadow(0 0 18px rgba(0,245,255,0.35));
        }}
        .vault-wrap::before {{
            content: '';
            position: absolute;
            inset: -8px;
            border: 1px solid rgba(0,245,255,0.2);
            border-radius: 4px;
        }}
        .vault-wrap::after {{
            content: '';
            position: absolute;
            top: -8px; left: -8px;
            width: 14px; height: 14px;
            border-top: 2px solid #ff2d78;
            border-left: 2px solid #ff2d78;
        }}
    </style>
    <div class="vault-wrap">
        <img
            src="data:image/png;base64,{b64_cerrado}"
            style="
                position: absolute;
                top: 0; left: 0;
                width: 300px;
                opacity: {op_cerrado};
                transition: opacity 0.5s ease;
            "
        />
        <img
            src="data:image/png;base64,{b64_abierto}"
            style="
                position: absolute;
                top: 0; left: 0;
                width: 300px;
                opacity: {op_abierto};
                transition: opacity 0.5s ease;
            "
        />
    </div>
""", height=330)

if st.session_state.cofre_abierto:
    st.success("📦 Cofre abierto")
else:
    st.warning("📦 Cofre cerrado")

st.markdown("</div>", unsafe_allow_html=True)

# =====================================================
# FOOTER HUD
# =====================================================

st.markdown("""
<div style="
    text-align: center;
    font-family: 'Share Tech Mono', monospace;
    font-size: 0.6rem;
    letter-spacing: 0.22em;
    color: rgba(0,245,255,0.25);
    margin-top: 2rem;
    padding-top: 1rem;
    border-top: 1px solid rgba(0,245,255,0.08);
">
    ◈ VAULT SYSTEM v2.4 &nbsp;·&nbsp; SECURED BY AI &nbsp;·&nbsp; ALL ACCESS LOGGED ◈
</div>
""", unsafe_allow_html=True)
