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
# 3. CSS
# ==========================================
st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

html, body, .stApp {
    background: #080c14 !important;
    color: #e8eaf0 !important;
    font-family: 'Sora', sans-serif !important;
}

[data-testid="stSidebar"] {
    display:none;
}

header {
    display:none;
}

footer {
    display:none;
}

.block-container {
    padding:0 !important;
    max-width:100% !important;
}

.navbar {
    width:100%;
    height:62px;
    background:#060a12;
    border-bottom:1px solid #1a2744;
    padding:0 60px;
    display:flex;
    align-items:center;
    justify-content:space-between;
}

.nav-logo {
    font-family:'Space Mono', monospace;
    font-size:1rem;
    font-weight:700;
    color:#fff;
    letter-spacing:3px;
    text-transform:uppercase;
}

.nav-right {
    display:flex;
    align-items:center;
    gap:10px;
}

.lang-btn button {
    background:rgba(0,102,255,0.08) !important;
    color:#0066ff !important;
    border:1px solid rgba(0,102,255,0.3) !important;
    border-radius:6px !important;
    font-family:'Space Mono', monospace !important;
    font-size:0.68rem !important;
    font-weight:700 !important;
}

.logout-btn button {
    background:rgba(255,75,75,0.08) !important;
    color:#ff4b4b !important;
    border:1px solid rgba(255,75,75,0.2) !important;
    border-radius:6px !important;
    font-family:'Space Mono', monospace !important;
    font-size:0.68rem !important;
    font-weight:700 !important;
}

.hero {
    background: linear-gradient(135deg, #080c14 0%, #0d1829 100%);
    padding: 70px 80px 50px 80px;
    border-bottom: 1px solid #1a2744;
}

.hero-title {
    font-size:3rem;
    font-weight:700;
    color:#fff;
}

.hero-title em {
    color:#0066ff;
    font-style:normal;
}

.hero-sub {
    margin-top:15px;
    color:#6b7c96;
    max-width:600px;
}

.empty-state {
    display:flex;
    flex-direction:column;
    justify-content:center;
    align-items:center;
    min-height:280px;
    border:1px dashed #1a2744;
    border-radius:16px;
    background:#090f1a;
}

.zone-label {
    font-family:'Space Mono', monospace;
    font-size:0.72rem;
    letter-spacing:2px;
    text-transform:uppercase;
    color:#0066ff;
    margin-bottom:20px;
    font-weight:700;
}

</style>
""", unsafe_allow_html=True)

# ==========================================
# LOGIN
# ==========================================
if not st.session_state.autenticado:

    col1, col2, col3 = st.columns([1,1.2,1])

    with col2:

        st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)

        st.markdown("""
        <div style="text-align:center; margin-bottom:30px;">

            <div style="
                font-family:'Space Mono',monospace;
                font-size:2rem;
                font-weight:700;
                color:#fff;
            ">
                Object<span style="color:#0066ff">Vision</span>
                <span style="color:#4a6080; font-size:1rem;">AI</span>
            </div>

            <div style="
                font-size:0.72rem;
                color:#2a3a54;
                letter-spacing:2px;
                text-transform:uppercase;
                margin-top:8px;
                font-family:'Space Mono',monospace;
            ">
                Portal de acceso · 2026
            </div>

            <div style="height:1px; background:#1a2744; margin:24px 0;"></div>

        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs([
            "🔑 Iniciar Sesión",
            "📝 Crear Cuenta"
        ])

        with tab_login:

            usuario_input = st.text_input(
                "Usuario",
                placeholder="Tu ID de usuario"
            ).strip().lower()

            contrasena_input = st.text_input(
                "Contraseña",
                type="password",
                placeholder="••••••••"
            )

            if st.button("Acceder al Sistema", use_container_width=True):

                db = st.session_state.usuarios_db

                if usuario_input in db and db[usuario_input]["clave"] == contrasena_input:

                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = db[usuario_input]["rol"]

                    st.success("✅ Acceso autorizado.")
                    time.sleep(0.5)
                    st.rerun()

                else:
                    st.error("❌ Credenciales incorrectas.")

        with tab_reg:

            nuevo_u = st.text_input(
                "Nombre de usuario",
                key="nuevo_user"
            ).strip().lower()

            nueva_p = st.text_input(
                "Contraseña",
                type="password",
                key="nuevo_pass"
            )

            confirmar_p = st.text_input(
                "Repite la contraseña",
                type="password",
                key="confirmar_pass"
            )

            if st.button("Crear Cuenta", use_container_width=True):

                if nuevo_u in st.session_state.usuarios_db:
                    st.error("Usuario ya existe.")

                elif nueva_p != confirmar_p:
                    st.error("Las contraseñas no coinciden.")

                else:

                    st.session_state.usuarios_db[nuevo_u] = {
                        "clave": nueva_p,
                        "rol": f"{nuevo_u.upper()} (CLIENTE)"
                    }

                    st.success("Cuenta creada correctamente.")

    st.stop()

# ==========================================
# NAVBAR
# ==========================================
st.markdown("""
<div class="navbar">

    <div class="nav-logo">
        Object<span style="color:#0066ff">Vision</span>
    </div>

</div>
""", unsafe_allow_html=True)

col_space, col_es, col_en, col_fr, col_logout = st.columns([8,1,1,1,2])

with col_es:
    if st.button("ES"):
        st.session_state.idioma = "es"
        st.rerun()

with col_en:
    if st.button("EN"):
        st.session_state.idioma = "en"
        st.rerun()

with col_fr:
    if st.button("FR"):
        st.session_state.idioma = "fr"
        st.rerun()

with col_logout:
    if st.button("🔴 SALIR"):
        st.session_state.autenticado = False
        st.session_state.rol_usuario = ""
        st.rerun()

# ==========================================
# TEXTOS
# ==========================================
TEXTOS = {
    "es": {
        "titulo": "Visión artificial que <em>entiende</em> tu mundo.",
        "subtitulo": "Sube cualquier imagen y nuestra IA identifica objetos."
    },
    "en": {
        "titulo": "Artificial vision that <em>understands</em> your world.",
        "subtitulo": "Upload any image and our AI identifies objects."
    },
    "fr": {
        "titulo": "Vision artificielle qui <em>comprend</em> votre monde.",
        "subtitulo": "Téléchargez une image et notre IA identifie les objets."
    }
}

t = TEXTOS[st.session_state.idioma]

# ==========================================
# HERO
# ==========================================
st.markdown(f"""
<div class="hero">

    <div class="hero-title">
        {t["titulo"]}
    </div>

    <div class="hero-sub">
        {t["subtitulo"]}
    </div>

</div>
""", unsafe_allow_html=True)

# ==========================================
# MODELO IA
# ==========================================
@st.cache_resource
def cargar_modelo():
    modelo = models.mobilenet_v2(weights="IMAGENET1K_V1")
    modelo.eval()
    return modelo

modelo = cargar_modelo()

@st.cache_resource
def cargar_etiquetas():
    url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"

    with urllib.request.urlopen(url) as f:
        return json.load(f)

etiquetas = cargar_etiquetas()

transformacion = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize(
        [0.485,0.456,0.406],
        [0.229,0.224,0.225]
    )
])

# ==========================================
# ANALIZADOR
# ==========================================
st.markdown("<div style='padding:40px 80px;'>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:

    st.markdown(
        '<div class="zone-label">— Entrada</div>',
        unsafe_allow_html=True
    )

    archivo = st.file_uploader(
        "",
        type=["jpg","jpeg","png"]
    )

    if archivo:
        imagen = Image.open(archivo).convert("RGB")
        st.image(imagen, use_container_width=True)

with col2:

    st.markdown(
        '<div class="zone-label">— Análisis</div>',
        unsafe_allow_html=True
    )

    if archivo:

        tensor = transformacion(imagen).unsqueeze(0)

        with torch.no_grad():
            salida = modelo(tensor)

        probs = torch.nn.functional.softmax(salida[0], dim=0)

        top3 = torch.topk(probs, 3)

        for i in range(3):

            nombre = etiquetas[top3.indices[i].item()]
            prob = top3.values[i].item() * 100

            st.markdown(f"""
            <div style="
                background:#0d1422;
                border:1px solid #1a2744;
                border-radius:12px;
                padding:18px;
                margin-bottom:14px;
            ">
                <div style="
                    display:flex;
                    justify-content:space-between;
                    align-items:center;
                ">
                    <span style="color:#fff;font-weight:600;">
                        {nombre}
                    </span>

                    <span style="
                        color:#00d4aa;
                        font-family:'Space Mono', monospace;
                    ">
                        {prob:.1f}%
                    </span>
                </div>
            </div>
            """, unsafe_allow_html=True)

    else:

        st.markdown("""
        <div class="empty-state">
            <div style="font-size:2rem; opacity:0.2;">⬡</div>
            <div style="color:#4a6080;">
                Esperando imagen...
            </div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)