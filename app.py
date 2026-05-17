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
# 2. GESTIÓN DE SESIÓN
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
# 3. INYECCIÓN CSS MAESTRA (DISEÑO PREMIUM)
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, .stApp { background: #080c14 !important; color: #e8eaf0 !important; font-family: 'Sora', sans-serif !important; }
[data-testid="stSidebar"] { display: none; }
header { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
footer { display: none !important; }

/* LOGIN CARD CLEANUP */
div[data-testid="stVerticalBlock"]:has(div[data-testid="stTextInput"]) {
    background-color: #0d1422 !important;
    border: 1px solid #1a2744 !important;
    border-radius: 16px !important;
    padding: 35px 30px !important;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6) !important;
}

/* NAVBAR VISUAL STRUCTURE */
.nav-visual-container {
    width: 100%; background: #05080f; border-bottom: 1px solid #1a2744;
    padding: 0 60px; height: 62px; display: flex; align-items: center; 
    justify-content: space-between; position: relative;
}
.nav-logo { font-family: 'Space Mono', monospace; font-size: 1rem; font-weight: 700; color: #fff; letter-spacing: 3px; text-transform: uppercase; }
.nav-tech-pill { font-size: 0.65rem; letter-spacing: 1px; text-transform: uppercase; color: #4a6080; background: rgba(26,39,68,0.5); border: 1px solid #1a2744; padding: 5px 12px; border-radius: 6px; font-family: 'Space Mono', monospace; font-weight: 700; }
.user-badge { font-family: 'Space Mono', monospace; font-size: 0.72rem; color: #00d4aa; letter-spacing: 1px; }

/* TRUCO: BOTONES INVISIBLES SOBRE LA NAVBAR */
.floating-nav-controls {
    position: absolute; top: 18px; right: 60px; display: flex; align-items: center; gap: 8px; z-index: 1000;
}
/* Estilo para los botones de idioma invisibles que disparan el cambio */
.floating-nav-controls .stButton > button {
    background: transparent !important; border: none !important; color: transparent !important;
    min-width: 35px !important; width: 35px !important; height: 28px !important; padding: 0 !important; margin: 0 !important; box-shadow: none !important;
}

/* BOTÓN SALIR REAL */
.logout-container .stButton > button {
    background: rgba(255, 75, 75, 0.1) !important; color: #ff4b4b !important;
    border: 1px solid rgba(255, 75, 75, 0.3) !important; border-radius: 6px !important;
    font-family: 'Space Mono', monospace !important; font-size: 0.7rem !important;
    padding: 4px 15px !important; text-transform: uppercase !important; font-weight: 700 !important;
}
.logout-container .stButton > button:hover { background: #ff4b4b !important; color: #fff !important; }

/* TABS STYLING */
.stTabs [data-baseweb="tab-list"] { padding-left: 80px; border-bottom: 1px solid #1a2744; background: #060a10; }
.stTabs [data-baseweb="tab"] { font-family: 'Space Mono', monospace; font-size: 0.8rem; color: #4a6080 !important; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { color: #fff !important; border-bottom-color: #0066ff !important; }

/* ELEMENTOS DE DISEÑO HERO */
.hero { background: linear-gradient(135deg, #080c14 0%, #0d1829 100%); padding: 60px 80px; border-bottom: 1px solid #1a2744; }
.hero-title { font-size: 3.5rem; font-weight: 700; color: #fff; letter-spacing: -2px; }
.hero-title em { font-style: normal; background: linear-gradient(90deg, #0066ff, #00d4aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-sub { color: #6b7c96; max-width: 500px; margin-top: 15px; font-size: 1.1rem; }
</style>
""", unsafe_allow_html=True)

# ── LOGIN PAGE ─────────────────────────────────────────────────────────────────
if not st.session_state.autenticado:
    c1, c2, c3 = st.columns([1, 1.2, 1])
    with c2:
        st.markdown("<div style='height:100px'></div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; margin-bottom:20px;'><h1 style='color:#fff; font-family:Space Mono; font-size:2.2rem;'>Object<span style='color:#0066ff'>Vision</span> AI</h1><p style='color:#4a6080; text-transform:uppercase; letter-spacing:2px; font-size:0.7rem;'>Portal de Acceso · 2026</p></div>", unsafe_allow_html=True)
        t_log, t_reg = st.tabs(["🔑   Acceso", "📝   Registro"])
        with t_log:
            u = st.text_input("Usuario", key="u_in").strip().lower()
            p = st.text_input("Contraseña", type="password", key="p_in")
            if st.button("Entrar", use_container_width=True):
                if u in st.session_state.usuarios_db and st.session_state.usuarios_db[u]["clave"] == p:
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = st.session_state.usuarios_db[u]["rol"]
                    st.rerun()
                else: st.error("Error de credenciales")
        with t_reg:
            nu = st.text_input("Nuevo Usuario", key="nu").strip().lower()
            np = st.text_input("Clave", type="password", key="np")
            if st.button("Crear Cuenta", use_container_width=True):
                st.session_state.usuarios_db[nu] = {"clave": np, "rol": f"{nu.upper()} (CLIENTE)"}
                st.success("Cuenta creada")
    st.stop()

# ── NAVBAR TOTALMENTE INTEGRADA (SIN SALTOS) ───────────────────────────────────
idm_curr = st.session_state.idioma

# PARTE 1: El diseño visual de la barra
st.markdown(f"""
<div class="nav-visual-container">
    <div class="nav-logo">Object<span style="color:#0066ff">Vision</span></div>
    <div style="display:flex; gap:10px;">
        <span class="nav-tech-pill">MobileNetV2</span>
        <span class="nav-tech-pill">PyTorch</span>
        <span class="nav-tech-pill">ImageNet</span>
    </div>
    <div style="display:flex; align-items:center; gap:25px;">
        <div class="user-badge">● {st.session_state.rol_usuario}</div>
        <div style="display:flex; gap:4px; background:rgba(13,20,34,0.6); padding:4px; border-radius:8px; border:1px solid #1a2744;">
            <div style="padding:4px 8px; font-family:'Space Mono'; font-size:0.65rem; font-weight:700; color:{'#00d4aa' if idm_curr=='es' else '#4a6080'}; border:{'1px solid #00d4aa' if idm_curr=='es' else 'none'}; border-radius:5px;">ES</div>
            <div style="padding:4px 8px; font-family:'Space Mono'; font-size:0.65rem; font-weight:700; color:{'#00d4aa' if idm_curr=='en' else '#4a6080'}; border:{'1px solid #00d4aa' if idm_curr=='en' else 'none'}; border-radius:5px;">EN</div>
            <div style="padding:4px 8px; font-family:'Space Mono'; font-size:0.65rem; font-weight:700; color:{'#00d4aa' if idm_curr=='fr' else '#4a6080'}; border:{'1px solid #00d4aa' if idm_curr=='fr' else 'none'}; border-radius:5px;">FR</div>
        </div>
        <div style="width:70px;"></div> </div>
</div>
""", unsafe_allow_html=True)

# PARTE 2: Botones reales de Streamlit invisibles puestos encima
# Usamos un contenedor absoluto para que coincidan con la posición ES, EN, FR y Salir
st.markdown('<div class="floating-nav-controls">', unsafe_allow_html=True)
if st.button(" ", key="nav_es"): st.session_state.idioma = "es"; st.rerun()
if st.button(" ", key="nav_en"): st.session_state.idioma = "en"; st.rerun()
if st.button(" ", key="nav_fr"): st.session_state.idioma = "fr"; st.rerun()
st.markdown('<div class="logout-container">', unsafe_allow_html=True)
if st.button("Salir", key="nav_logout"):
    st.session_state.autenticado = False
    st.session_state.rol_usuario = ""
    st.rerun()
st.markdown('</div></div>', unsafe_allow_html=True)

# ── LOGICA DE TRADUCCIÓN Y HERO ────────────────────────────────────────────────
TEXTOS = {
    "es": {"titulo": "Visión artificial que <em>entiende</em> tu mundo.", "sub": "Sube cualquier imagen e identificala con IA.", "analizar": "Analizar", "cam": "Cámara", "hist": "Historial", "comp": "Comparar", "proc": "Procesando..."},
    "en": {"titulo": "AI Vision that <em>understands</em> your world.", "sub": "Upload any image and identify it with AI.", "analizar": "Analyze", "cam": "Camera", "hist": "History", "comp": "Compare", "proc": "Processing..."},
    "fr": {"titulo": "Vision IA qui <em>comprend</em> votre monde.", "sub": "Téléchargez une image et identifiez-la.", "analizar": "Analyser", "cam": "Caméra", "hist": "Historique", "comp": "Comparer", "proc": "Traitement..."}
}
t = TEXTOS[st.session_state.idioma]

st.markdown(f"""<div class="hero"><div class="hero-title">{t['titulo']}</div><div class="hero-sub">{t['sub']}</div></div>""", unsafe_allow_html=True)

# ── TABS RENDERING ─────────────────────────────────────────────────────────────
tabs = st.tabs([f"🔍 {t['analizar']}", f"📷 {t['cam']}", f"📊 {t['comp']}", f"🕒 {t['hist']}"])

# TAB 1: ANALIZAR
with tabs[0]:
    st.markdown("<div style='padding: 40px 80px;'>", unsafe_allow_html=True)
    f = st.file_uploader("Cargar imagen", type=["jpg","png","jpeg"], label_visibility="collapsed")
    if f:
        img = Image.open(f).convert("RGB")
        st.image(img, width=400)
        st.info("Sistema de Inferencia Listo")

# TAB 4: HISTORIAL
with tabs[3]:
    st.markdown("<div style='padding: 40px 80px;'>", unsafe_allow_html=True)
    if not st.session_state.historial:
        st.markdown("<p style='color:#4a6080; font-family:Space Mono;'>Sin registros previos.</p>", unsafe_allow_html=True)

# FOOTER
st.markdown("<div style='padding: 30px 80px; border-top:1px solid #1a2744; font-family:Space Mono; font-size:0.7rem; color:#4a6080;'>© 2026 ObjectVision · Mohamed Mohamed Embarec</div>", unsafe_allow_html=True)