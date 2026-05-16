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
# 1. CONFIGURACIÓN DE LA PÁGINA (Estricto inicio)
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
# 3. TRUCO DE INYECCIÓN CSS CRÍTICO
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght=400;600;700&family=Space+Mono:wght=400;700&display=swap');

/* Configuración del fondo global */
html, body, .stApp { 
    background-color: #080c14 !important; 
    color: #e8eaf0 !important; 
    font-family: 'Sora', sans-serif !important; 
}

/* Forzar ocultamiento de cabeceras redundantes de Streamlit */
header, footer, [data-testid="stSidebar"], [data-testid="collapsedControl"] { 
    display: none !important; 
}

/* Resetear paddings por defecto que deforman la app */
.block-container { 
    padding-top: 0px !important; 
    padding-bottom: 0px !important; 
    max-width: 100% !important; 
}

/* === EL ARREGLO MAESTRO PARA EL LOGIN === */
/* Forzamos que el elemento contenedor de Streamlit que aloja nuestro wrapper se centre y no se estire */
div:has(> .login-wrapper) {
    max-width: 450px !important;
    margin: 0 auto !important;
    padding-top: 8vh !important; /* Baja el bloque de forma elegante */
}

.login-wrapper {
    width: 100% !important;
    display: block !important;
}

/* Diseño de la Tarjeta de acceso */
.login-container-card {
    background-color: #0d1422 !important;
    border: 1px solid #1a2744 !important;
    border-radius: 16px !important;
    padding: 35px 30px !important;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6) !important;
    width: 100% !important;
}

/* Pestañas internas del login */
.stTabs [data-baseweb="tab-list"] {
    padding-left: 0px !important;
    background: transparent !important;
    gap: 10px !important;
    border-bottom: 1px solid #1a2744 !important;
}
.stTabs [data-baseweb="tab"] {
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
    height: 40px !important;
    background-color: transparent !important;
}

/* Inputs de texto en el Login */
div[data-testid="stTextInput"] div input {
    background-color: #080c14 !important;
    color: #ffffff !important;
    border: 1px solid #1a2744 !important;
    border-radius: 8px !important;
    height: 45px !important;
}
div[data-testid="stTextInput"] div input:focus {
    border-color: #0066ff !important;
    box-shadow: 0 0 0 1px #0066ff !important;
}

/* Botón de enviar */
.stButton > button {
    background: rgba(0, 102, 255, 0.1) !important;
    color: #0066ff !important;
    border: 1px solid rgba(0, 102, 255, 0.4) !important;
    border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important;
    font-weight: 700 !important;
    letter-spacing: 1px !important;
    height: 46px !important;
    text-transform: uppercase !important;
    width: 100% !important;
}
.stButton > button:hover {
    background: #0066ff !important;
    color: #ffffff !important;
    border-color: #0066ff !important;
}

/* Botón Salir (Rojo) */
div.stButton > button[key="logout_btn"] {
    background: rgba(255, 75, 75, 0.08) !important;
    color: #ff4b4b !important;
    border: 1px solid rgba(255, 75, 75, 0.3) !important;
    height: 38px !important;
}
div.stButton > button[key="logout_btn"]:hover {
    background: #ff4b4b !important;
    color: #fff !important;
}

/* Estilos de la aplicación interna (Post-Login) */
.hero { background: linear-gradient(135deg, #080c14 0%, #0d1829 100%); padding: 60px 80px; border-bottom: 1px solid #1a2744; }
.hero-title { font-size: 3rem; font-weight: 700; color: #fff; margin-bottom: 15px; }
.hero-title em { font-style: normal; background: linear-gradient(90deg, #0066ff, #00d4aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-sub { color: #6b7c96; max-width: 600px; line-height: 1.6; }

/* Reajustar pestañas de la app interna para que no se herede el estilo del login */
.stApp div[data-testid="stTabs"] [data-baseweb="tab-list"] { 
    padding-left: 80px !important; 
    background: #060a10 !important; 
    border-bottom: 1px solid #1a2744 !important; 
}
.zone-label { font-family: 'Space Mono', monospace; font-size: 0.75rem; color: #0066ff; letter-spacing: 2px; margin-bottom: 15px; font-weight: 700; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 250px; background: #090f1a; border-radius: 12px; border: 1px dashed #1a2744; }
.bottom-bar { padding: 30px 80px; border-top: 1px solid #1a2744; display: flex; justify-content: space-between; background: #05080f; margin-top: 40px; font-family: 'Space Mono', monospace; font-size: 0.75rem; color: #4a6080; }
</style>
""", unsafe_allow_html=True)

# ==========================================
# 4. RENDERIZADO DEL LOGIN CONTROLADO
# ==========================================
if not st.session_state.autenticado:
    # Encapsulamos el login completo dentro de divs puros HTML controlados por el CSS
    st.markdown('<div class="login-wrapper"><div class="login-container-card">', unsafe_allow_html=True)
    
    # Cabecera limpia del Login
    st.markdown("""
    <div style="text-align: center; margin-bottom: 25px;">
        <h2 style="font-family: 'Space Mono', monospace; font-size: 1.9rem; font-weight: 700; color: #ffffff; margin: 0;">
            Object<span style="color: #0066ff;">Vision</span> AI
        </h2>
        <p style="font-family: 'Space Mono', monospace; font-size: 0.7rem; color: #4a6080; letter-spacing: 3px; margin-top: 8px; text-transform: uppercase;">
            Portal de Acceso • 2026
        </p>
        <div style="height: 1px; background: #1a2744; margin-top: 20px;"></div>
    </div>
    """, unsafe_allow_html=True)
    
    # Pestañas de interacción (Ahora se renderizan de forma segura)
    tab_log, tab_sign = st.tabs(["🔑 Iniciar Sesión", "📝 Crear Cuenta"])
    
    with tab_log:
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        u_log = st.text_input("Usuario", placeholder="Introduce tu ID de usuario (ej: mohamed)", key="ulog_input", label_visibility="collapsed").strip().lower()
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        p_log = st.text_input("Contraseña", type="password", placeholder="Introduce tu contraseña", key="plog_input", label_visibility="collapsed")
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        if st.button("Verificar Identidad y Acceder", key="submit_log_btn", use_container_width=True):
            db = st.session_state.usuarios_db
            if u_log in db and db[u_log]["clave"] == p_log:
                st.session_state.autenticado = True
                st.session_state.rol_usuario = db[u_log]["rol"]
                st.rerun()
            else:
                st.error("❌ Credenciales incorrectas.")
                
    with tab_sign:
        st.markdown("<div style='height: 15px;'></div>", unsafe_allow_html=True)
        u_new = st.text_input("Nuevo Usuario", placeholder="Crea tu ID de usuario", key="unew_input", label_visibility="collapsed").strip().lower()
        st.markdown("<div style='height: 10px;'></div>", unsafe_allow_html=True)
        p_new = st.text_input("Contraseña Nueva", type="password", placeholder="Contraseña (mínimo 4 caracteres)", key="pnew_input", label_visibility="collapsed")
        st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
        
        if st.button("Registrar Nueva Cuenta", key="submit_sign_btn", use_container_width=True):
            if u_new and len(p_new) >= 4:
                if u_new not in st.session_state.usuarios_db:
                    st.session_state.usuarios_db[u_new] = {"clave": p_new, "rol": f"{u_new.upper()} (USER)"}
                    st.success("🎉 Cuenta registrada con éxito. Pasa a la pestaña de login.")
                else:
                    st.error("❌ El usuario ya existe.")
            else:
                st.warning("⚠️ Rellena los datos correctamente (mínimo 4 caracteres).")
                
    st.markdown('</div></div>', unsafe_allow_html=True)
    st.stop() # Congela la ejecución aquí para que no pinte nada del dashboard antes de loguearse

# ==========================================
# 5. PANEL DE CONTROL INTERNO (POST-LOGIN)
# ==========================================
# Cabecera de navegación superior una vez logueado
nav_1, nav_2, nav_3 = st.columns([6, 4, 2])
with nav_1:
    st.markdown("<h3 style='padding: 20px 0 0 80px; margin:0;'>Object<span style='color:#0066ff'>Vision</span></h3>", unsafe_allow_html=True)
with nav_2:
    st.markdown(f"<p style='padding-top:26px; text-align:right; color:#00d4aa; font-family:\"Space Mono\"; font-size:0.8rem;'>● {st.session_state.rol_usuario}</p>", unsafe_allow_html=True)
with nav_3:
    st.markdown("<div style='padding-top:20px; padding-right:80px;'></div>", unsafe_allow_html=True)
    if st.button("Salir", key="logout_btn", use_container_width=True):
        st.session_state.autenticado = False
        st.rerun()

st.markdown("<div class='hero'><div class='hero-title'>Visión artificial que <em>entiende</em> tu mundo.</div><div class='hero-sub'>Sube cualquier imagen y nuestra IA identificará los objetos en tiempo real empleando redes neuronales convolucionales avanzadas.</div></div>", unsafe_allow_html=True)

# Pestañas principales de la herramienta
t_analizar, t_historial = st.tabs(["🔍 Analizar Imagen", "📊 Historial"])

with t_analizar:
    st.markdown("<div style='padding: 40px 80px;'>", unsafe_allow_html=True)
    c1, c2 = st.columns(2, gap="large")
    with c1:
        st.markdown("<div class='zone-label'>— Entrada de datos</div>", unsafe_allow_html=True)
        archivo = st.file_uploader("Sube tu archivo", type=["png", "jpg", "jpeg"], key="main_uploader", label_visibility="collapsed")
        if archivo:
            st.image(Image.open(archivo), use_container_width=True)
    with c2:
        st.markdown("<div class='zone-label'>— Resultados del análisis</div>", unsafe_allow_html=True)
        if archivo:
            st.info("🤖 Procesando imagen mediante MobileNetV2...")
        else:
            st.markdown("<div class='empty-state'><p style='color:#4a6080; font-family:\"Space Mono\"; font-size:0.8rem;'>Esperando carga de archivo...</p></div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with t_historial:
    st.markdown("<div style='padding: 40px 80px;' class='empty-state'>Historial de análisis vacío.</div>", unsafe_allow_html=True)

# Pie de página definitivo
st.markdown("<div class='bottom-bar'><div>© 2026 ObjectVision · Mohamed Mohamed Embarec</div><div>Proyecto Intermodular · ODS 9</div></div>", unsafe_allow_html=True)