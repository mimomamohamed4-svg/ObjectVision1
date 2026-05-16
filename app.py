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

# 1. CONFIGURACIÓN DE LA PÁGINA (Debe ser lo primero)
st.set_page_config(
    page_title="ObjectVision AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 2. PERSISTENCIA DE DATOS Y GESTIÓN DE SESIÓN
if "usuarios_db" not in st.session_state:
    st.session_state.usuarios_db = {
        "mohamed": {"clave": "admin2026", "rol": "MOHAMED (ADMIN)"},
        "profesora": {"clave": "tribunal10", "rol": "PROFESORA (EVALUADOR)"},
        "invitado": {"clave": "invitado123", "rol": "INVITADO"},
        "mimo": {"clave": "usuario.26", "rol": "MIMO (CLIENTE)"}
    }

if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "rol_usuario" not in st.session_state:
    st.session_state.rol_usuario = ""
if "historial" not in st.session_state:
    st.session_state.historial = []
if "idioma" not in st.session_state:
    st.session_state.idioma = "es"

# 3. INTERFAZ CSS GLOBAL (Aislamiento absoluto de componentes)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght=300;400;500;600;700&family=Space+Mono:wght=400;700&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, .stApp { background: #080c14 !important; color: #e8eaf0 !important; font-family: 'Sora', sans-serif !important; }

/* Ocultar elementos nativos molestos */
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
header { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
footer { display: none !important; }

/* Barra de navegación superior integrada mediante CSS Puro */
.custom-navbar {
    background: #060a12; 
    padding: 15px 80px; 
    border-bottom: 1px solid #1a2744; 
    display: flex; 
    align-items: center; 
    justify-content: space-between;
    width: 100%;
    margin-bottom: 0px;
}
.nav-logo { font-family: 'Space Mono', monospace; font-size: 1.3rem; font-weight: 700; color: #fff; letter-spacing: 2px; text-transform: uppercase; }
.nav-logo span { color: #0066ff; }
.nav-badges { display: flex; gap: 12px; align-items: center; }
.nav-badge-item { font-size: 0.7rem; letter-spacing: 1px; text-transform: uppercase; color: #4a6080; background: rgba(26, 39, 68, 0.3); border: 1px solid #1a2744; padding: 5px 14px; border-radius: 6px; font-family: 'Space Mono', monospace; font-weight: 700; }
.nav-badge-active { color: #00d4aa; background: rgba(0, 212, 170, 0.05); border: 1px solid rgba(0, 212, 170, 0.2); }
.nav-user { font-family: 'Space Mono', monospace; font-size: 0.75rem; font-weight: 700; padding: 6px 14px; border-radius: 6px; }

/* Tarjeta del Login Estilizada */
.login-box-container { 
    background: #0d1422 !important; 
    border: 1px solid #1a2744 !important; 
    border-radius: 16px 16px 0 0 !important; 
    padding: 35px 35px 15px 35px !important; 
    margin-top: 50px;
}
.login-header-text { text-align: center; }
.login-title { font-size: 1.8rem; font-weight: 700; color: #fff; margin-bottom: 4px; letter-spacing: -1px; }
.login-title span { color: #0066ff; font-family: 'Space Mono', monospace; }
.login-subtitle { font-size: 0.8rem; color: #4a6080; font-family: 'Space Mono', monospace; letter-spacing: 0.5px; text-transform: uppercase; }

/* Wrapper seguro para envolver las pestañas del login */
.login-tabs-wrapper {
    background: #0d1422 !important;
    border-left: 1px solid #1a2744 !important;
    border-right: 1px solid #1a2744 !important;
    border-bottom: 1px solid #1a2744 !important;
    border-radius: 0 0 16px 16px !important;
    padding: 0px 35px 35px 35px !important;
}

# --- SOLUCIÓN DE AISLAMIENTO CSS --- #

/* 1. ESTILOS EXCLUSIVOS PARA LAS PESTAÑAS DEL LOGIN */
.login-tabs-wrapper div[data-baseweb="tab-list"] {
    background-color: transparent !important;
    border-bottom: 1px solid #1a2744 !important;
    gap: 10px !important;
    justify-content: center !important;
    width: 100% !important;
}
.login-tabs-wrapper div[data-baseweb="tab"] {
    background-color: transparent !important;
    color: #4a6080 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    padding: 12px 20px !important;
    flex-grow: 1 !important;
    text-align: center !important;
}
.login-tabs-wrapper div[data-baseweb="tab"][aria-selected="true"] {
    color: #fff !important;
    border-bottom: 2px solid #0066ff !important;
    font-weight: 700 !important;
}

/* 2. ESTILOS EXCLUSIVOS PARA LAS PESTAÑAS DEL PANEL PRINCIPAL (POST-LOGIN) */
.main-interface-tabs div[data-baseweb="tab-list"] {
    padding-left: 80px !important;
    background: #060a10 !important;
    border-bottom: 1px solid #1a2744 !important;
    gap: 20px !important;
    justify-content: flex-start !important;
    width: 100% !important;
}
.main-interface-tabs div[data-baseweb="tab"] {
    background-color: transparent !important;
    color: #4a6080 !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    padding: 16px 24px !important;
    flex-grow: 0 !important;
    text-align: left !important;
}
.main-interface-tabs div[data-baseweb="tab"][aria-selected="true"] {
    color: #fff !important;
    border-bottom: 2px solid #0066ff !important;
    font-weight: 700 !important;
}

/* Forzar reset global de paneles de pestañas */
div[data-baseweb="tab-panel"] { padding: 20px 0 0 0 !important; }

/* Hero Principal */
.hero-limpio { background: linear-gradient(135deg, #080c14 0%, #0d1829 100%); padding: 40px 80px; border-bottom: 1px solid #1a2744; }
.hero-title { font-size: clamp(2.2rem, 4.5vw, 3.5rem); font-weight: 700; line-height: 1.2; letter-spacing: -1.5px; color: #fff; max-width: 800px; margin-bottom: 16px; }
.hero-title em { font-style: normal; background: linear-gradient(90deg, #0066ff, #00d4aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero-sub { font-size: 1.05rem; color: #6b7c96; max-width: 520px; line-height: 1.6; font-weight: 400; margin-bottom: 30px; }

/* Contadores barra */
.stats-bar { display: flex; gap: 50px; padding-top: 30px; border-top: 1px solid #1a2744; }
.stat { display: flex; flex-direction: column; gap: 4px; }
.stat-number { font-family: 'Space Mono', monospace; font-size: 1.3rem; font-weight: 700; color: #fff; }
.stat-label { font-size: 0.7rem; color: #4a6080; letter-spacing: 1px; text-transform: uppercase; font-weight: 500; }

/* Secciones de análisis y resultados */
.zone-label { font-family: 'Space Mono', monospace; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; color: #0066ff; margin-bottom: 20px; font-weight: 700; }
.result-item { padding: 20px 0; border-bottom: 1px solid #1a2744; }
.result-item:last-child { border-bottom: none; }
.result-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.result-name { font-size: 1.1rem; font-weight: 500; color: #e8eaf0; }
.result-pct { font-family: 'Space Mono', monospace; font-size: 0.95rem; font-weight: 700; }
.bar-track { height: 6px; background: #1a2744; border-radius: 3px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; }
.rank-badge { font-family: 'Space Mono', monospace; font-size: 0.7------rem; letter-spacing: 1px; text-transform: uppercase; padding: 4px 10px; border-radius: 6px; margin-right: 12px; font-weight: 700; }

/* Historial */
.history-card { background: #0d1422; border: 1px solid #1a2744; border-radius: 12px; padding: 18px; display: flex; align-items: center; gap: 18px; margin-bottom: 14px; }
.history-thumb { width: 65px; height: 65px; object-fit: cover; border-radius: 8px; border: 1px solid #1a2744; }
.history-info { flex: 1; }
.history-name { font-weight: 600; color: #e8eaf0; font-size: 0.95rem; }
.history-meta { font-size: 0.75rem; color: #4a6080; font-family: 'Space Mono', monospace; margin-top: 6px; }

/* Estados vacíos */
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 280px; gap: 15px; background: #090f1a; border-radius: 16px; border: 1px dashed #1a2744; }
.empty-icon { font-size: 2.5rem; opacity: 0.2; color: #0066ff; }
.empty-text { font-size: 0.85rem; color: #4a6080; font-family: 'Space Mono', monospace; }

/* Footer barra inferior */
.bottom-bar { padding: 30px 80px; border-top: 1px solid #1a2744; display: flex; justify-content: space-between; align-items: center; background: #05080f; margin-top: 40px; }
.bottom-left { font-size: 0.8rem; color: #4a6080; font-family: 'Space Mono', monospace; }
.bottom-tag { font-size: 0.75rem; color: #4a6080; font-family: 'Space Mono', monospace; letter-spacing: 1px; margin-left: 28px; font-weight: 700; }

/* Reescritura de componentes nativos standard */
.stFileUploader > div { background: #0d1422 !important; border: 1px dashed #1a2744 !important; border-radius: 12px !important; }
.stImage img { border-radius: 12px !important; border: 1px solid #1a2744; }
.stSelectbox > div > div { background: #0d1422 !important; border: 1px solid #1a2744 !important; color: #e8eaf0 !important; }
div[data-testid="stTextInput"] > div > div > input { background: #080c14 !important; color: #fff !important; border: 1px solid #1a2744 !important; }

/* Botones de acción general */
.stButton > button { background: rgba(0, 102, 255, 0.1) !important; color: #0066ff !important; border: 1px solid #0066ff !important; padding: 10px 20px !important; border-radius: 8px !important; font-family: 'Space Mono', monospace !important; font-size: 0.75rem !important; font-weight: 700 !important; text-transform: uppercase !important; width: 100%; margin-top: 10px; }
.stButton > button:hover { background: linear-gradient(90deg, #0066ff, #00d4aa) !important; color: white !important; border: none !important; box-shadow: 0 4px 15px rgba(0,102,255,0.3); }
</style>
""", unsafe_allow_html=True)

# 4. FLUJO DE CONTROL: LOGIN / REGISTRO
if not st.session_state.autenticado:
    col_l1, col_l2, col_l3 = st.columns([1, 1.4, 1])
    
    with col_l2:
        st.markdown("""
        <div class="login-box-container">
            <div class="login-header-text">
                <div class="login-title">Object<span>Vision</span> AI</div>
                <div class="login-subtitle">Sistema de Control de Acceso</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # El truco: Envolvemos las pestañas de login en una clase contenedora exclusiva
        st.markdown('<div class="login-tabs-wrapper">', unsafe_allow_html=True)
        login_tabs = st.tabs(["🔑 INICIAR SESIÓN", "📝 CREAR CUENTA"])
        
        # SUB-PANEL 1: INICIAR SESIÓN
        with login_tabs[0]:
            usuario_input = st.text_input("Usuario", placeholder="Tu ID de usuario", key="login_user").strip().lower()
            contrasena_input = st.text_input("Contraseña", type="password", placeholder="••••••••", key="login_pass")
            btn_login = st.button("Acceder al Sistema", key="btn_execute_login")
            
            if btn_login:
                if usuario_input in st.session_state.usuarios_db and st.session_state.usuarios_db[usuario_input]["clave"] == contrasena_input:
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = st.session_state.usuarios_db[usuario_input]["rol"]
                    st.success("Acceso autorizado. Cargando interfaz...")
                    time.sleep(0.4)
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas o usuario no registrado.")
        
        # SUB-PANEL 2: CREAR CUENTA
        with login_tabs[1]:
            nuevo_usuario = st.text_input("Elige un Nombre de Usuario", placeholder="Ej: pedro99", key="reg_user").strip().lower()
            nueva_contrasena = st.text_input("Crea una Contraseña Segura", type="password", placeholder="Mínimo 4 caracteres", key="reg_pass")
            confirmar_pass = st.text_input("Repite la Contraseña", type="password", placeholder="••••••••", key="reg_pass_conf")
            btn_registrar = st.button("Finalizar Registro", key="btn_execute_register")
            
            if btn_registrar:
                if not nuevo_usuario or not nueva_contrasena:
                    st.warning("Por favor, rellena todos los campos.")
                elif len(nueva_contrasena) < 4:
                    st.error("La contraseña debe tener al menos 4 caracteres.")
                elif nueva_contrasena != confirmar_pass:
                    st.error("Las contraseñas no coinciden.")
                elif nuevo_usuario in st.session_state.usuarios_db:
                    st.error("Ese nombre de usuario ya está ocupado.")
                else:
                    st.session_state.usuarios_db[nuevo_usuario] = {
                        "clave": nueva_contrasena,
                        "rol": f"{nuevo_usuario.upper()} (CLIENTE)"
                    }
                    st.success(f"¡Usuario '{nuevo_usuario}' registrado! Pasa a la pestaña de Iniciar Sesión.")
        st.markdown('</div>', unsafe_allow_html=True)
    st.stop()

# --- TEXTOS E IDIOMAS ---
TEXTOS = {
    "es": {
        "titulo": "Visión artificial que <em>entiende</em> tu mundo.",
        "subtitulo": "Sube cualquier imagen y nuestra IA identifica los objetos al instante.",
        "tab_analizar": "Analizar imagen",
        "tab_camara": "Cámara en vivo",
        "tab_comparar": "Comparar modelos",
        "tab_historial": "Historial",
        "entrada": "— Entrada",
        "analisis": "— Análisis",
        "alta": "CONFIANZA ALTA",
        "media": "CONFIANZA MEDIA",
        "baja": "CONFIANZA BAJA",
        "esperando": "Esperando imagen...",
        "procesando": "Procesando...",
        "historial_vacio": "Sin análisis todavía",
        "camara_info": "Activa la cámara y toma una foto",
        "comparar_info": "Sube una imagen para comparar modelos",
        "modelo_a": "— MobileNetV2 (Rápido)",
        "modelo_b": "— ResNet50 (Preciso)",
        "boton_voz": "🔊 Escuchar resultado",
    },
    "en": {
        "titulo": "Artificial vision that <em>understands</em> your world.",
        "subtitulo": "Upload any image and our AI instantly identifies objects.",
        "tab_analizar": "Analyze image",
        "tab_camara": "Live camera",
        "tab_comparar": "Compare models",
        "tab_historial": "History",
        "entrada": "— Input",
        "analisis": "— Analysis",
        "alta": "HIGH CONFIDENCE",
        "media": "MEDIUM CONFIDENCE",
        "baja": "LOW CONFIDENCE",
        "esperando": "Waiting for image...",
        "procesando": "Processing...",
        "historial_vacio": "No analysis yet",
        "camara_info": "Activate camera and take a photo",
        "comparar_info": "Upload an image to compare models",
        "modelo_a": "— MobileNetV2 (Fast)",
        "modelo_b": "— ResNet50 (Accurate)",
        "boton_voz": "🔊 Listen to result",
    }
}

TRADUCCIONES = {
    "car": "Coche", "sports car": "Coche deportivo", "convertible": "Descapotable",
    "dog": "Perro", "cat": "Gato", "bird": "Pájaro", "labrador retriever": "Labrador Retriever",
    "golden retriever": "Golden Retriever", "pizza": "Pizza", "hamburger": "Hamburguesa",
    "banana": "Plátano", "apple": "Manzana", "chair": "Silla", "laptop": "Portátil",
    "bicycle": "Bicicleta", "motorcycle": "Moto", "bus": "Autobús", "truck": "Camión",
    "airplane": "Avión", "soccer ball": "Balón de fútbol", "keyboard": "Teclado", "bottle": "Botella"
}

def traducir(n, idm="es"):
    if idm != "es":
        return n.replace("_", " ").title()
    return TRADUCCIONES.get(n.lower().replace("_", " "), n.replace("_", " ").title())

def nivel_confianza(prob, t):
    if prob >= 0.6:
        return "#28a745", t["alta"]
    elif prob >= 0.3:
        return "#ffc107", t["media"]
    else:
        return "#dc3545", t["baja"]

@st.cache_resource
def cargar_mobilenet():
    m = models.mobilenet_v2(weights="IMAGENET1K_V1")
    m.eval()
    return m

@st.cache_resource
def cargar_resnet():
    m = models.resnet50(weights="IMAGENET1K_V1")
    m.eval()
    return m

@st.cache_resource
def cargar_etiquetas():
    try:
        url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
        with urllib.request.urlopen(url, timeout=5) as f:
            return json.load(f)
    except Exception:
        return ["background", "laptop", "golden retriever", "sports car", "backpack", "pizza"]

mobilenet = cargar_mobilenet()
etiquetas = cargar_etiquetas()

transformacion = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

def predecir(imagen, modelo):
    tensor = transformacion(imagen).unsqueeze(0)
    with torch.no_grad():
        salida = modelo(tensor)
    probs = torch.nn.functional.softmax(salida[0], dim=0)
    return torch.topk(probs, 3)

def mostrar_resultados(top3, t, idm, umbral_minimo=10):
    badge_colors = ["#0066ff", "#00d4aa", "#6644ff"]
    elementos_visibles = 0
    reporte_txt = f"--- AUDITORIA OBJECTVISION AI ---\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\nResultados:\n"
    
    for i in range(3):
        nombre = traducir(etiquetas[top3.indices[i].item()], idm)
        prob = top3.values[i].item()
        pct = prob * 100
        
        if pct >= umbral_minimo:
            elementos_visibles += 1
            color_bar, nivel = nivel_confianza(prob, t)
            reporte_txt += f"- {nombre}: {pct:.1f}%\n"
            st.markdown(f"""
            <div class="result-item">
                <div class="result-header">
                    <div style="display:flex;align-items:center">
                        <span class="rank-badge" style="background:{badge_colors[i]}22;color:{badge_colors[i]};border:1px solid {badge_colors[i]}44">#{str(i+1).zfill(2)}</span>
                        <span class="result-name">{nombre}</span>
                    </div>
                    <span class="result-pct" style="color:{badge_colors[i]}">{pct:.1f}%</span>
                </div>
                <div class="bar-track">
                    <div class="bar-fill" style="width:{pct}%;background:{color_bar}"></div>
                </div>
                <div style="margin-top:6px;font-size:0.75rem;color:#4a6080;font-family:'Space Mono',monospace;letter-spacing:1px">{nivel}</div>
            </div>
            """, unsafe_allow_html=True)

    if elementos_visibles == 0:
        st.markdown(f'<div class="empty-state"><div class="empty-icon">⚠️</div><div class="empty-text">Ningún objeto supera el {umbral_minimo}% de confianza establecido.</div></div>', unsafe_allow_html=True)
        return

    nombre_top = traducir(etiquetas[top3.indices[0].item()], idm)
    prob_top = top3.values[0].item() * 100

    if idm == "es":
        mensaje_voz = f"Objeto detectado: {nombre_top}, con un {prob_top:.0f} por ciento de certeza."
        lang_voz = "es-ES"
    else:
        mensaje_voz = f"Object detected: {nombre_top}, with {prob_top:.0f} percent confidence."
        lang_voz = "en-US"

    col_btn1, col_btn2 = st.columns([1, 1])
    with col_btn1:
        if st.button(t["boton_voz"], key=f"voz_{nombre_top}"):
            st.components.v1.html(f"""
            <script>
                var msg = new SpeechSynthesisUtterance("{mensaje_voz}");
                msg.lang = "{lang_voz}";
                msg.rate = 0.95;
                window.speechSynthesis.speak(msg);
            </script>
            """, height=0)
            
    with col_btn2:
        st.download_button(
            label="📥 Descargar Reporte",
            data=reporte_txt,
            file_name="reporte_objectvision.txt",
            mime="text/plain",
            key=f"dl_{nombre_top}"
        )

# --- 5. BARRA DE NAVEGACIÓN SUPERIOR CON FLUJO NATIVO ---
badge_bg = "rgba(255, 75, 75, 0.15)" if "ADMIN" in st.session_state.rol_usuario else "rgba(0, 102, 255, 0.15)"
badge_txt = "#ff4b4b" if "ADMIN" in st.session_state.rol_usuario else "#0066ff"
badge_border = "rgba(255, 75, 75, 0.4)" if "ADMIN" in st.session_state.rol_usuario else "rgba(0, 102, 255, 0.4)"

st.markdown(f"""
<div class="custom-navbar">
    <div class="nav-logo">Object<span>Vision</span></div>
    <div class="nav-badges">
        <div class="nav-badge-item nav-badge-active">MobileNetV2</div>
        <div class="nav-badge-item">PyTorch</div>
        <div class="nav-badge-item">ImageNet</div>
    </div>
    <div class="nav-user" style="background:{badge_bg}; color:{badge_txt}; border:1px solid {badge_border};">
        👤 {st.session_state.rol_usuario}
    </div>
</div>
""", unsafe_allow_html=True)

# Botones nativos de acciones
col_nav_actions = st.columns([6, 1, 1])
with col_nav_actions[1]:
    lang_map = {"Español": "es", "English": "en"}
    lang_sel = st.selectbox("", list(lang_map.keys()), label_visibility="collapsed", key="lang_selector_top")
    st.session_state.idioma = lang_map[lang_sel]
    idioma = st.session_state.idioma
    t = TEXTOS[idioma]
with col_nav_actions[2]:
    if st.button("🔴 SALIR", key="logout_system_btn"):
        st.session_state.autenticado = False
        st.session_state.rol_usuario = ""
        st.clear_cache()
        st.rerun()

# 6. HERO SECCIÓN PRINCIPAL
st.markdown(f"""
<div class="hero-limpio">
    <div class="hero-title">{t["titulo"]}</div>
    <div class="hero-sub">{t["subtitulo"]}</div>
    <div class="stats-bar">
        <div class="stat"><div class="stat-number">1000+</div><div class="stat-label">Clases</div></div>
        <div class="stat"><div class="stat-number">Top-3</div><div class="stat-label">Predicciones</div></div>
        <div class="stat"><div class="stat-number">Cloud</div><div class="stat-label">Servidor remoto</div></div>
        <div class="stat"><div class="stat-number">24/7</div><div class="stat-label">Disponibilidad</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Filtro de certeza mínimo
st.markdown("<div style='padding: 20px 80px 0 80px;'>", unsafe_allow_html=True)
umbral_sel = st.slider("Filtro de Certeza Mínima", min_value=5, max_value=90, value=25, step=5, format="%d%%")
st.markdown("</div>", unsafe_allow_html=True)

# 7. GESTIÓN DE PESTAÑAS (PANEL GENERAL PRINCIPAL POST-LOGIN)
lista_tabs = [t["tab_analizar"], t["tab_camara"], t["tab_comparar"], t["tab_historial"]]
es_admin = "MOHAMED (ADMIN)" in st.session_state.rol_usuario

if es_admin:
    lista_tabs.append("👥 Panel Admin (Usuarios)")

# Envolvemos las pestañas principales en un div exclusivo para proteger su estilo original ancho
st.markdown('<div class="main-interface-tabs">', unsafe_allow_html=True)
tabs_render = st.tabs(lista_tabs)
st.markdown('</div>', unsafe_allow_html=True)

# TAB — ANALIZAR IMAGEN
with tabs_render[0]:
    st.markdown("<div style='padding: 40px 80px;'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown(f'<div class="zone-label">{t["entrada"]}</div>', unsafe_allow_html=True)
        archivo = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="upload1")
        if archivo:
            imagen = Image.open(archivo).convert("RGB")
            st.image(imagen, use_container_width=True)
    with col2:
        st.markdown(f'<div class="zone-label">{t["analisis"]}</div>', unsafe_allow_html=True)
        if archivo:
            with st.spinner(t["procesando"]):
                t_inicio = time.time()
                top3 = predecir(imagen, mobilenet)
                t_final = time.time()
                ms = (t_final - t_inicio) * 1000
            
            st.markdown(f"<span style='font-family:Space Mono; font-size:0.75rem; color:#00d4aa; letter-spacing:1px'>⚡ INFERENCIA: {ms:.0f}ms</span>", unsafe_allow_html=True)
            mostrar_resultados(top3, t, idioma, umbral_sel)
            
            # Guardar en Historial
            buf = io.BytesIO()
            imagen.save(buf, format="JPEG")
            img_b64 = base64.b64encode(buf.getvalue()).decode()
            nombre_top = traducir(etiquetas[top3.indices[0].item()], idioma)
            prob_top = top3.values[0].item()
            if len(st.session_state.historial) == 0 or st.session_state.historial[-1]["nombre"] != nombre_top:
                st.session_state.historial.insert(0, {
                    "nombre": nombre_top,
                    "prob": prob_top,
                    "img": img_b64,
                    "hora": datetime.now().strftime("%H:%M")
                })
                st.session_state.historial = st.session_state.historial[:5]
        else:
            st.markdown(f'<div class="empty-state"><div class="empty-icon">⬡</div><div class="empty-text">{t["esperando"]}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# TAB — CÁMARA EN VIVO
with tabs_render[1]:
    st.markdown("<div style='padding: 40px 80px;'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown(f'<div class="zone-label">{t["entrada"]}</div>', unsafe_allow_html=True)
        foto = st.camera_input("", label_visibility="collapsed")
    with col2:
        st.markdown(f'<div class="zone-label">{t["analisis"]}</div>', unsafe_allow_html=True)
        if foto:
            imagen_cam = Image.open(foto).convert("RGB")
            with st.spinner(t["procesando"]):
                t_inicio = time.time()
                top3_cam = predecir(imagen_cam, mobilenet)
                t_final = time.time()
                ms = (t_final - t_inicio) * 1000
            st.markdown(f"<span style='font-family:Space Mono; font-size:0.75rem; color:#00d4aa; letter-spacing:1px'>⚡ INFERENCIA: {ms:.0f}ms</span>", unsafe_allow_html=True)
            mostrar_resultados(top3_cam, t, idioma, umbral_sel)
        else:
            st.markdown(f'<div class="empty-state"><div class="empty-icon">📷</div><div class="empty-text">{t["camara_info"]}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# TAB — COMPARAR MODELOS
with tabs_render[2]:
    st.markdown("<div style='padding: 40px 80px;'>", unsafe_allow_html=True)
    archivo_comp = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="upload2")
    if archivo_comp:
        imagen_comp = Image.open(archivo_comp).convert("RGB")
        st.image(imagen_comp, width=400)
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2, gap="large")
        with col_a:
            st.markdown(f'<div class="zone-label">{t["modelo_a"]}</div>', unsafe_allow_html=True)
            with st.spinner(t["procesando"]):
                top3_mobile = predecir(imagen_comp, mobilenet)
            mostrar_resultados(top3_mobile, t, idioma, umbral_sel)
        with col_b:
            st.markdown(f'<div class="zone-label">{t["modelo_b"]}</div>', unsafe_allow_html=True)
            resnet = cargar_resnet()
            with st.spinner(t["procesando"]):
                top3_resnet = predecir(imagen_comp, resnet)
            mostrar_resultados(top3_resnet, t, idioma, umbral_sel)
    else:
        st.markdown(f'<div class="empty-state"><div class="empty-icon">⬡</div><div class="empty-text">{t["comparar_info"]}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# TAB — HISTORIAL DE CONSULTAS
with tabs_render[3]:
    st.markdown("<div style='padding: 40px 80px;'>", unsafe_allow_html=True)
    st.markdown(f'<div class="zone-label">{t["tab_historial"]}</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    if st.session_state.historial:
        for item in st.session_state.historial:
            st.markdown(f"""
            <div class="history-card">
                <img class="history-thumb" src="data:image/jpeg;base64,{item['img']}" />
                <div class="history-info">
                    <div class="history-name">{item['nombre']}</div>
                    <div class="history-meta">{item['prob']*100:.1f}% · {item['hora']}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="empty-state"><div class="empty-icon">🕐</div><div class="empty-text">{t["historial_vacio"]}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# TAB — PANEL DE ADMINISTRACIÓN
if es_admin:
    with tabs_render[4]:
        st.markdown("<div style='padding: 40px 80px 10px 80px;'>", unsafe_allow_html=True)
        st.markdown('<div class="zone-label">— AUDITORÍA DE SEGURIDAD INTERNA</div>', unsafe_allow_html=True)
        st.markdown("<p style='color:#6b7c96; margin-bottom: 20px; font-size:0.9rem;'>Lista de credenciales y perfiles almacenados temporalmente en la memoria del servidor.</p>", unsafe_allow_html=True)
        st.markdown("</div>", unsafe_allow_html=True)
        
        tabla_contenido = ""
        for usr, datos in st.session_state.usuarios_db.items():
            if "ADMIN" in datos["rol"]:
                badge_style = "background: rgba(255, 75, 75, 0.1); color: #ff4b4b; border: 1px solid rgba(255, 75, 75, 0.2);"
            else:
                badge_style = "background: rgba(0, 212, 170, 0.1); color: #00d4aa; border: 1px solid rgba(0, 212, 170, 0.2);"
            
            tabla_contenido += f"""
            <tr>
                <td style="padding: 14px 16px; border-bottom: 1px solid #1a2744; color: #e8eaf0; font-family: 'Space Mono', monospace; font-weight: 700;">{usr}</td>
                <td style="padding: 14px 16px; border-bottom: 1px solid #1a2744; color: #a2b4d2; font-family: 'Space Mono', monospace;">{datos['clave']}</td>
                <td style="padding: 14px 16px; border-bottom: 1px solid #1a2744;"><span style="font-family: 'Space Mono', monospace; font-size: 0.75rem; padding: 4px 8px; border-radius: 4px; {badge_style}">{datos['rol']}</span></td>
            </tr>
            """
        
        html_completo = f"""
        <div style="padding: 0 80px; background: #080c14; box-sizing: border-box;">
            <table style="width: 100%; border-collapse: collapse; background: #0d1422; border-radius: 8px; overflow: hidden; border: 1px solid #1a2744; font-family: 'Sora', sans-serif;">
                <thead>
                    <tr style="background: #111a2e; color: #0066ff; font-family: 'Space Mono', monospace; font-size: 0.8rem; text-align: left; letter-spacing: 1px;">
                        <th style="padding: 12px 16px;">ID USUARIO</th>
                        <th style="padding: 12px 16px;">CONTRASEÑA EN CLARO</th>
                        <th style="padding: 12px 16px;">ROL ASIGNADO</th>
                    </tr>
                </thead>
                <tbody>
                    {tabla_contenido}
                </tbody>
            </table>
        </div>
        """
        st.components.v1.html(html_completo, height=350, scrolling=True)

# 8. PIE DE PÁGINA (FOOTER CORPORATIVO)
st.markdown("""
<div class="bottom-bar">
    <div class="bottom-left">© 2026 ObjectVision · Mohamed Mohamed Embarec · Proyecto Intermodular</div>
    <div>
        <span class="bottom-tag">ODS 4</span>
        <span class="bottom-tag">ODS 9</span>
        <span class="bottom-tag">PyTorch + Streamlit</span>
    </div>
</div>
""", unsafe_allow_html=True)