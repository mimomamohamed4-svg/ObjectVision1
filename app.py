import streamlit as st
from PIL import Image
import torch
from torchvision import models, transforms
import urllib.request
import json
import io
import base64
import time
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA
# ==========================================
st.set_page_config(
    page_title="ObjectVision AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. GESTIÓN DE SESIÓN (Persistente)
# ==========================================
if "usuarios_db" not in st.session_state:
    st.session_state.usuarios_db = {
        "mohamed": {"clave": "admin2026", "rol": "MOHAMED (ADMIN)"},
        "profesora": {"clave": "tribunal10", "rol": "PROFESORA (EVALUADOR)"},
        "invitado": {"clave": "invitado123", "rol": "INVITADO"}
    }
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "rol_usuario" not in st.session_state:
    st.session_state.rol_usuario = ""
if "historial" not in st.session_state:
    st.session_state.historial = []
if "idioma" not in st.session_state:
    st.session_state.idioma = "es"

# ==========================================
# 3. CONTROL DE ESTILOS CSS (Tu diseño exacto)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght=300;400;500;600;700&family=Space+Mono:wght=400;700&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, .stApp { background: #080c14 !important; color: #e8eaf0 !important; font-family: 'Sora', sans-serif !important; }
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
header { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
footer { display: none !important; }

/* === TARJETA DE LOGIN === */
div[data-testid="stVerticalBlock"]:has(div[data-testid="stTextInput"]) {
    background-color: #0d1422 !important;
    border: 1px solid #1a2744 !important;
    border-radius: 16px !important;
    padding: 35px 30px !important;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6) !important;
    margin-top: 10px !important;
}

/* === ESTILOS DE TU NAVBAR DE FOTO PERFECTA === */
.custom-navbar { width: 100%; background: #060a12; border-bottom: 1px solid #1a2744; padding: 0 60px; height: 62px; display: flex; align-items: center; justify-content: space-between; }
.nav-right-container { display: flex; align-items: center; gap: 20px; }
.nav-lang-menu { display: flex; gap: 4px; background: rgba(13,20,34,0.6); padding: 4px; border-radius: 8px; border: 1px solid #1a2744; }

/* Botones camuflados como texto plano para evitar recargas de URL */
.nav-lang-btn { font-family: 'Space Mono', monospace; font-size: 0.68rem; font-weight: 700; color: #4a6080; background: transparent; border: none; padding: 4px 10px; border-radius: 5px; cursor: pointer; transition: all 0.2s; }
.nav-lang-btn.active { color: #00d4aa; background: rgba(0,212,170,0.08); border: 1px solid rgba(0,212,170,0.2); }
.nav-lang-btn:hover:not(.active) { color: #fff; background: rgba(254,254,254,0.05); }

.nav-logout-btn { font-family: 'Space Mono', monospace; font-size: 0.68rem; font-weight: 700; color: #ff4b4b; background: rgba(255,75,75,0.08); border: 1px solid rgba(255,75,75,0.2); padding: 6px 14px; border-radius: 6px; text-transform: uppercase; letter-spacing: 1px; transition: all 0.2s; display: flex; align-items: center; gap: 4px; cursor: pointer; }
.nav-logout-btn:hover { background: #ff4b4b !important; color: #fff !important; box-shadow: 0 0 15px rgba(255,75,75,0.3); }

/* Componentes del cuerpo del panel */
.zone-label { font-family: 'Space Mono', monospace; font-size: 0.72rem; letter-spacing: 2px; text-transform: uppercase; color: #0066ff; margin-bottom: 20px; font-weight: 700; }
.result-item { padding: 22px 0; border-bottom: 1px solid #1a2744; }
.result-item:last-child { border-bottom: none; }
.result-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.result-name { font-size: 1.1rem; font-weight: 500; color: #e8eaf0; }
.result-pct { font-family: 'Space Mono', monospace; font-size: 0.95rem; font-weight: 700; }
.bar-track { height: 5px; background: #1a2744; border-radius: 3px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; }
.rank-badge { font-family: 'Space Mono', monospace; font-size: 0.68rem; padding: 4px 10px; border-radius: 6px; margin-right: 12px; font-weight: 700; }
.hero { background: linear-gradient(135deg, #080c14 0%, #0d1829 100%); padding: 70px 80px 50px 80px; border-bottom: 1px solid #1a2744; }
.hero-title { font-size: clamp(2rem, 4vw, 3.8rem); font-weight: 700; line-height: 1.15; letter-spacing: -2px; color: #fff; max-width: 800px; margin-bottom: 18px; }
.hero-title em { font-style: normal; background: linear-gradient(90deg, #0066ff, #00d4aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero-sub { font-size: 1.05rem; color: #6b7c96; max-width: 520px; line-height: 1.7; margin-bottom: 40px; }
.stats-bar { display: flex; gap: 50px; padding-top: 30px; border-top: 1px solid #1a2744; }
.stat-number { font-family: 'Space Mono', monospace; font-size: 1.4rem; font-weight: 700; color: #fff; }
.stat-label { font-size: 0.68rem; color: #4a6080; letter-spacing: 1px; text-transform: uppercase; margin-top: 4px; }
.bottom-bar { padding: 28px 80px; border-top: 1px solid #1a2744; display: flex; justify-content: space-between; align-items: center; background: #05080f; }
.bottom-left { font-size: 0.78rem; color: #4a6080; font-family: 'Space Mono', monospace; }
.bottom-tag { font-size: 0.72rem; color: #4a6080; font-family: 'Space Mono', monospace; letter-spacing: 1px; margin-left: 28px; }
.stTabs [data-baseweb="tab-list"] { gap: 24px; padding-left: 80px; border-bottom: 1px solid #1a2744; background: #060a10; }
.stTabs [data-baseweb="tab"] { height: 52px; background-color: transparent !important; color: #4a6080 !important; font-family: 'Space Mono', monospace; font-size: 0.82rem; font-weight: 700; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { color: #fff !important; border-bottom-color: #0066ff !important; }
</style>
""", unsafe_allow_html=True)


# ==========================================
# 4. CAPTURA DE ACCIONES DE LA NAVBAR (Canal limpio)
# ==========================================
# Creamos dos inputs invisibles que recogen la acción de la Navbar sin recargar la URL
lang_bridge = st.text_input("", key="lang_bridge", value="", label_visibility="collapsed")
logout_bridge = st.text_input("", key="logout_bridge", value="", label_visibility="collapsed")

# Procesamos los cambios de estado sin perder la sesión
if lang_bridge in ["es", "en", "fr"]:
    st.session_state.idioma = lang_bridge
    st.components.v1.html("""<script>parent.document.querySelector('input[aria-label="lang_bridge"]').value = "";</script>""", height=0)
    st.rerun()

if logout_bridge == "true":
    st.session_state.autenticado = False
    st.session_state.rol_usuario = ""
    st.components.v1.html("""<script>parent.document.querySelector('input[aria-label="logout_bridge"]').value = "";</script>""", height=0)
    st.rerun()

# Forzamos que los puentes ocultos no ocupen espacio visual en la app
st.markdown("""
<style>
div[data-testid="stTextInput"]:has(input[aria-label="lang_bridge"]),
div[data-testid="stTextInput"]:has(input[aria-label="logout_bridge"]) { display: none !important; }
</style>
""", unsafe_allow_html=True)


# ── PANTALLA DE ACCESO (LOGIN) ────────────────────────────────────────────────
if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; margin-bottom:30px;">
            <div style="font-family:'Space Mono',monospace; font-size:2rem; font-weight:700; color:#fff;">
                Object<span style="color:#0066ff">Vision</span> <span style="color:#4a6080; font-size:1rem;">AI</span>
            </div>
            <div style="font-size:0.72rem; color:#2a3a54; letter-spacing:2px; text-transform:uppercase; margin-top:8px; font-family:'Space Mono',monospace;">
                Portal de acceso · 2026
            </div>
            <div style="height:1px; background:#1a2744; margin:24px 0;"></div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs(["🔑   Iniciar Sesión", "📝   Crear Cuenta"])

        with tab_login:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            usuario_input = st.text_input("Usuario", placeholder="Tu ID de usuario", key="li_u").strip().lower()
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            contrasena_input = st.text_input("Contraseña", type="password", placeholder="••••••••", key="li_p")
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            if st.button("Acceder al Sistema", key="btn_login", use_container_width=True):
                db = st.session_state.usuarios_db
                if usuario_input in db and db[usuario_input]["clave"] == contrasena_input:
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = db[usuario_input]["rol"]
                    st.success("✅ Acceso autorizado.")
                    time.sleep(0.3)
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas.")
        st.stop()


# ── RENDERIZADO DE LA NAVBAR PERFECTA (IGUAL A TU FOTO 1 Y FOTO 3) ──────────────
idm_curr = st.session_state.idioma

st.markdown(f"""
<div class="custom-navbar">
    <div style="font-family:'Space Mono',monospace; font-size:1rem; font-weight:700; color:#fff; letter-spacing:3px; text-transform:uppercase;">
        Object<span style="color:#0066ff">Vision</span>
    </div>
    <div style="display:flex; gap:10px;">
        <span style="font-size:0.65rem; letter-spacing:1px; text-transform:uppercase; color:#4a6080; background:rgba(26,39,68,0.5); border:1px solid #1a2744; padding:5px 12px; border-radius:6px; font-family:'Space Mono',monospace; font-weight:700;">MobileNetV2</span>
        <span style="font-size:0.65rem; letter-spacing:1px; text-transform:uppercase; color:#4a6080; background:rgba(26,39,68,0.5); border:1px solid #1a2744; padding:5px 12px; border-radius:6px; font-family:'Space Mono',monospace; font-weight:700;">PyTorch</span>
        <span style="font-size:0.65rem; letter-spacing:1px; text-transform:uppercase; color:#4a6080; background:rgba(26,39,68,0.5); border:1px solid #1a2744; padding:5px 12px; border-radius:6px; font-family:'Space Mono',monospace; font-weight:700;">ImageNet</span>
    </div>
    <div class="nav-right-container">
        <div style="font-family:'Space Mono',monospace; font-size:0.72rem; color:#00d4aa; letter-spacing:1px; margin-right:10px;">
            <span style="color:#00d4aa; margin-right:6px;">●</span>{st.session_state.rol_usuario}
        </div>
        <div class="nav-lang-menu">
            <button onclick="cambiarIdioma('es')" class="nav-lang-btn {'active' if idm_curr == 'es' else ''}">ES</button>
            <button onclick="cambiarIdioma('en')" class="nav-lang-btn {'active' if idm_curr == 'en' else ''}">EN</button>
            <button onclick="cambiarIdioma('fr')" class="nav-lang-btn {'active' if idm_curr == 'fr' else ''}">FR</button>
        </div>
        <button onclick="cerrarSesion()" class="nav-logout-btn">🔴 Salir</button>
    </div>
</div>

<script>
function cambiarIdioma(lang) {{
    var inputPuente = parent.document.querySelector('input[aria-label="lang_bridge"]');
    if(inputPuente) {{
        inputPuente.value = lang;
        inputPuente.dispatchEvent(new Event('input', {{ bubbles: true }}));
    }}
}}
function cerrarSesion() {{
    var inputPuente = parent.document.querySelector('input[aria-label="logout_bridge"]');
    if(inputPuente) {{
        inputPuente.value = "true";
        inputPuente.dispatchEvent(new Event('input', {{ bubbles: true }}));
    }}
}}
</script>
""", unsafe_allow_html=True)


# ── TEXTOS Y CONTENIDO DEL CUERPO (ESTRUCTURADO Y LIMPIO) ─────────────────────
idioma = st.session_state.idioma

TEXTOS = {
    "es": {
        "titulo": "Visión artificial que <em>entiende</em> tu mundo.",
        "subtitulo": "Sube cualquier imagen y nuestra IA identifica los objetos al instante con datos de confianza en tiempo real.",
        "tab_analizar": "Analizar imagen", "tab_camara": "Cámara en vivo", "tab_comparar": "Comparar modelos", "tab_historial": "Historial",
        "entrada": "— Entrada", "analisis": "— Análisis", "procesando": "Procesando...", "esperando": "Esperando imagen..."
    },
    "en": {
        "titulo": "Artificial vision that <em>understands</em> your world.",
        "subtitulo": "Upload any image and our AI instantly identifies objects with real-time confidence data.",
        "tab_analizar": "Analyze image", "tab_camara": "Live camera", "tab_comparar": "Compare models", "tab_historial": "History",
        "entrada": "— Input", "analisis": "— Analysis", "procesando": "Processing...", "esperando": "Waiting for image..."
    },
    "fr": {
        "titulo": "Vision artificielle qui <em>comprend</em> votre monde.",
        "subtitulo": "Téléchargez une image et notre IA identifie les objets instantanément.",
        "tab_analizar": "Analyser image", "tab_camara": "Caméra live", "tab_comparar": "Comparer modèles", "tab_historial": "Historique",
        "entrada": "— Entrée", "analisis": "— Analyse", "procesando": "Traitement...", "esperando": "En attente..."
    }
}

t = TEXTOS[idioma]

# Bloque de cabecera principal (Hero)
st.markdown(f"""
<div class="hero">
    <div class="hero-title">{t["titulo"]}</div>
    <div class="hero-sub">{t["subtitulo"]}</div>
    <div class="stats-bar">
        <div><div class="stat-number">1000+</div><div class="stat-label">Clases</div></div>
        <div><div class="stat-number">Top-3</div><div class="stat-label">Predicciones</div></div>
        <div><div class="stat-number">Cloud</div><div class="stat-label">Servidor remoto</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Pestañas de la aplicación
lista_tabs = [t["tab_analizar"], t["tab_camara"], t["tab_comparar"], t["tab_historial"]]
tabs_render = st.tabs(lista_tabs)

with tabs_render[0]:
    st.markdown("<div style='padding: 40px 80px;'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown(f'<div class="zone-label">{t["entrada"]}</div>', unsafe_allow_html=True)
        archivo = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="up1")
    with col2:
        st.markdown(f'<div class="zone-label">{t["analisis"]}</div>', unsafe_allow_html=True)
        st.markdown(f'<div class="empty-state"><div class="empty-icon">⬡</div><div class="empty-text">{t["esperando"]}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── FOOTER SEGURO ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="bottom-bar">
    <div class="bottom-left">© 2026 ObjectVision · Mohamed Mohamed Embarec · Proyecto Intermodular</div>
    <div><span class="bottom-tag">PyTorch + Streamlit</span></div>
</div>
""", unsafe_allow_html=True)