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
# 3. CONTROL DE ESTILOS CSS (TU DISEÑO ORIGINAL PERFECTO)
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

/* === NAVBAR ORIGINAL ESTILIZADA === */
.custom-navbar { width: 100%; background: #060a12; border-bottom: 1px solid #1a2744; padding: 0 60px; height: 62px; display: flex; align-items: center; justify-content: space-between; }
.nav-badge { font-size: 0.65rem; letter-spacing: 1px; text-transform: uppercase; color: #4a6080; background: rgba(26,39,68,0.5); border: 1px solid #1a2744; padding: 5px 12px; border-radius: 6px; font-family: 'Space Mono', monospace; font-weight: 700; }

/* Estilos para que los botones de Streamlit en la Navbar se vean planos e idénticos a tu foto 1 */
.stButton > button { background: transparent !important; color: #4a6080 !important; border: none !important; font-family: 'Space Mono', monospace !important; font-size: 0.68rem !important; font-weight: 700 !important; padding: 4px 10px !important; }
.stButton > button:hover { color: #fff !important; background: rgba(254,254,254,0.05) !important; }

/* Botón Activo */
div[data-testid="stHorizontalBlock"] div:nth-child(1) .stButton > button { color: #00d4aa !important; background: rgba(0,212,170,0.08) !important; border: 1px solid rgba(0,212,170,0.2) !important; border-radius: 5px; }

/* Botón Salir */
.btn-salir > div > div > button { color: #ff4b4b !important; background: rgba(255,75,75,0.08) !important; border: 1px solid rgba(255,75,75,0.2) !important; border-radius: 6px !important; padding: 6px 14px !important; text-transform: uppercase; letter-spacing: 1px; }
.btn-salir > div > div > button:hover { background: #ff4b4b !important; color: #fff !important; }

/* === COMPONENTES GENERALES DE TU PANEL === */
.zone-label { font-family: 'Space Mono', monospace; font-size: 0.72rem; letter-spacing: 2px; text-transform: uppercase; color: #0066ff; margin-bottom: 20px; font-weight: 700; }
.hero { background: linear-gradient(135deg, #080c14 0%, #0d1829 100%); padding: 70px 80px 50px 80px; border-bottom: 1px solid #1a2744; }
.hero-title { font-size: clamp(2rem, 4vw, 3.8rem); font-weight: 700; line-height: 1.15; letter-spacing: -2px; color: #fff; max-width: 800px; margin-bottom: 18px; }
.hero-title em { font-style: normal; background: linear-gradient(90deg, #0066ff, #00d4aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero-sub { font-size: 1.05rem; color: #6b7c96; max-width: 520px; line-height: 1.7; margin-bottom: 40px; }
.stats-bar { display: flex; gap: 50px; padding-top: 30px; border-top: 1px solid #1a2744; }
.stat-number { font-family: 'Space Mono', monospace; font-size: 1.4rem; font-weight: 700; color: #fff; }
.stat-label { font-size: 0.68rem; color: #4a6080; letter-spacing: 1px; text-transform: uppercase; margin-top: 4px; }
.bottom-bar { padding: 28px 80px; border-top: 1px solid #1a2744; display: flex; justify-content: space-between; align-items: center; background: #05080f; }
.stTabs [data-baseweb="tab-list"] { gap: 24px; padding-left: 80px; border-bottom: 1px solid #1a2744; background: #060a10; }
.stTabs [data-baseweb="tab"] { height: 52px; background-color: transparent !important; color: #4a6080 !important; font-family: 'Space Mono', monospace; font-size: 0.82rem; font-weight: 700; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { color: #fff !important; border-bottom-color: #0066ff !important; }
</style>
""", unsafe_allow_html=True)

# ── PANTALLA DE ACCESO (LOGIN ORIGINAL) ───────────────────────────────────────
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
                    time.sleep(0.2)
                    st.rerun()
                else:
                    st.error("❌ Credenciales incorrectas.")
        st.stop()

# ── RENDERIZADO DE LA NAVBAR SEGURO (FOTO 1 EN ESTADO PURO) ───────────────────
# Usamos columnas integradas dentro del contenedor de la Navbar para alinear todo horizontalmente sin saltos
nav_col1, nav_col2, nav_col3 = st.columns([1.5, 2, 2.5])

with nav_col1:
    st.markdown("""
    <div style="padding-top: 15px; padding-left: 60px; font-family:'Space Mono',monospace; font-size:1rem; font-weight:700; color:#fff; letter-spacing:3px; text-transform:uppercase;">
        Object<span style="color:#0066ff">Vision</span>
    </div>
    """, unsafe_allow_html=True)

with nav_col2:
    st.markdown("""
    <div style="display:flex; gap:10px; padding-top: 18px; justify-content: center;">
        <span class="nav-badge">MobileNetV2</span>
        <span class="nav-badge">PyTorch</span>
        <span class="nav-badge">ImageNet</span>
    </div>
    """, unsafe_allow_html=True)

with nav_col3:
    # Sub-columnas internas para colocar el rol, el selector de idioma y el botón salir perfectamente en línea
    sub_c1, sub_c2, sub_c3, sub_c4, sub_c5 = st.columns([2.5, 0.6, 0.6, 0.6, 1.2])
    
    with sub_c1:
        st.markdown(f"""
        <div style="font-family:'Space Mono',monospace; font-size:0.72rem; color:#00d4aa; letter-spacing:1px; padding-top:20px; text-align:right; margin-right:10px;">
            <span style="color:#00d4aa; margin-right:6px;">●</span>{st.session_state.rol_usuario}
        </div>
        """, unsafe_allow_html=True)
        
    # Los botones cambian el estado en memoria al instante sin modificar URLs ni provocar deslogueos
    with sub_c2:
        if st.button("ES", key="lang_es"):
            st.session_state.idioma = "es"
            st.rerun()
    with sub_c3:
        if st.button("EN", key="lang_en"):
            st.session_state.idioma = "en"
            st.rerun()
    with sub_c4:
        if st.button("FR", key="lang_fr"):
            st.session_state.idioma = "fr"
            st.rerun()
            
    with sub_c5:
        st.markdown('<div class="btn-salir">', unsafe_allow_html=True)
        if st.button("🔴 Salir", key="btn_logout"):
            st.session_state.autenticado = False
            st.session_state.rol_usuario = ""
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# Línea divisoria inferior de la Navbar
st.markdown("<div style='border-bottom:1px solid #1a2744; width:100%; margin-top:10px;'></div>", unsafe_allow_html=True)

# ── TEXTOS MULTIDIOMA ORIGINALES Y CUERPO DE LA APP ───────────────────────────
idioma = st.session_state.idioma

TEXTOS = {
    "es": {
        "titulo": "Visión artificial que <em>entiende</em> tu mundo.",
        "subtitulo": "Sube cualquier imagen y nuestra IA identifica los objetos al instante con datos de confianza en tiempo real.",
        "tab_analizar": "Analizar imagen", "tab_camara": "Cámara en vivo", "tab_comparar": "Comparar modelos", "tab_historial": "Historial",
        "entrada": "— Entrada", "analisis": "— Análisis", "esperando": "Esperando imagen..."
    },
    "en": {
        "titulo": "Artificial vision that <em>understands</em> your world.",
        "subtitulo": "Upload any image and our AI instantly identifies objects with real-time confidence data.",
        "tab_analizar": "Analyze image", "tab_camara": "Live camera", "tab_comparar": "Compare models", "tab_historial": "History",
        "entrada": "— Input", "analisis": "— Analysis", "esperando": "Waiting for image..."
    },
    "fr": {
        "titulo": "Vision artificielle qui <em>comprend</em> votre monde.",
        "subtitulo": "Téléchargez une image et notre IA identifie les objets instantanément.",
        "tab_analizar": "Analyser image", "tab_camara": "Caméra live", "tab_comparar": "Comparer modèles", "tab_historial": "Historique",
        "entrada": "— Entrée", "analisis": "— Analyse", "esperando": "En attente..."
    }
}

t = TEXTOS[idioma]

# Renderizado de la Sección Hero original
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

# Pestañas del cuerpo de la aplicación intactas
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
        st.markdown(f'<div style="display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 280px; gap: 15px; background: #090f1a; border-radius: 16px; border: 1px dashed #1a2744;"><div style="font-size: 2.5rem; opacity: 0.2;">⬡</div><div style="font-size: 0.85rem; color: #4a6080; font-family: \'Space Mono\', monospace;">{t["esperando"]}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── FOOTER ORIGINAL ───────────────────────────────────────────────────────────
st.markdown("""
<div class="bottom-bar">
    <div style="font-size: 0.78rem; color: #4a6080; font-family: 'Space Mono', monospace;">© 2026 ObjectVision · Mohamed Mohamed Embarec · Proyecto Intermodular</div>
    <div><span style="font-size: 0.72rem; color: #4a6080; font-family: 'Space Mono', monospace; letter-spacing: 1px; margin-left: 28px;">PyTorch + Streamlit</span></div>
</div>
""", unsafe_allow_html=True)