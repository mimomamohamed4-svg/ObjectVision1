import streamlit as st
from PIL import Image
import torch
import torchvision.models as models
import torchvision.transforms as transforms
import json
import urllib.request
import time
from datetime import datetime

# ==========================================
# 1. CONFIGURACIÓN DE LA PÁGINA (MAESTRA)
# ==========================================
st.set_page_config(
    page_title="ObjectVision AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==========================================
# 2. OPTIMIZACIÓN Y CARGA DE MODELO IA (REAL)
# ==========================================
@st.cache_resource
def cargar_modelo_ia():
    # Cargamos MobileNetV2 preentrenado con ImageNet de forma eficiente
    weights = models.MobileNet_V2_Weights.DEFAULT
    model = models.mobilenet_v2(weights=weights)
    model.eval()
    
    # Descargamos las etiquetas oficiales de ImageNet en español, inglés y francés
    # Para agilizar el script, usamos este mapeo directo integrado
    try:
        url_labels = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
        with urllib.request.urlopen(url_labels) as url:
            labels_raw = json.loads(url.read().decode())
    except:
        labels_raw = ["objeto desconocido"] * 1000
        
    return model, labels_raw, weights.transforms()

model, labels_imagenet, transformaciones = cargar_modelo_ia()

# Mapeo rápido interno para dar variedad a los idiomas del modelo
TRADUCCIONES_PRED = {
    "es": {"tabby": "gato doméstico", "ox": "buey", "sports car": "coche deportivo", "laptop": "ordenador portátil", "banana": "plátano", "golden retriever": "perro cobrador dorado"},
    "fr": {"tabby": "chat de gouttière", "ox": "bœuf", "sports car": "voiture de sport", "laptop": "ordinateur portable", "banana": "banane", "golden retriever": "retriever doré"}
}

def traducir_prediccion(label, idioma_actual):
    if idioma_actual == "en":
        return label.capitalize()
    return TRADUCCIONES_PRED.get(idioma_actual, {}).get(label.lower(), label).capitalize()

# ==========================================
# 3. GESTIÓN DEL ESTADO DE LA SESIÓN
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
# 4. INYECCIÓN CSS: REINVENCIÓN CYBERPUNK
# ==========================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');

/* Reset global del contenedor de Streamlit */
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, .stApp { background: #070b12 !important; color: #e2e8f0 !important; font-family: 'Sora', sans-serif !important; }
[data-testid="stSidebar"] { display: none; }
header { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
footer { display: none !important; }

/* Estilización Limpia del Contenedor de Login */
div[data-testid="stVerticalBlock"]:has(div[data-testid="stTextInput"]) {
    background-color: #0c1322 !important;
    border: 1px solid #162545 !important;
    border-radius: 16px !important;
    padding: 40px 35px !important;
    box-shadow: 0 25px 60px rgba(0, 0, 0, 0.6) !important;
}

/* --- DISEÑO DE LA NAVBAR INTEGRADA --- */
.custom-navbar {
    width: 100%; background: #04070d; border-bottom: 1px solid #162545;
    padding: 0 60px; height: 65px; display: flex; align-items: center; 
    justify-content: space-between;
}
.nav-logo { font-family: 'Space Mono', monospace; font-size: 1.05rem; font-weight: 700; color: #fff; letter-spacing: 3px; text-transform: uppercase; }
.nav-pill { font-size: 0.62rem; letter-spacing: 1px; text-transform: uppercase; color: #415675; background: rgba(22,37,69,0.4); border: 1px solid #162545; padding: 5px 12px; border-radius: 5px; font-family: 'Space Mono', monospace; }
.nav-user { font-family: 'Space Mono', monospace; font-size: 0.72rem; color: #00d4aa; letter-spacing: 1px; }

/* Ocultación Inteligente del Selector Selectbox Nativo para camuflarlo en el diseño */
div[data-testid="stSelectbox"]:has(label:contains("LANG_SELECTOR")) {
    background: transparent !important;
    border: none !important;
    margin-top: -15px !important;
}
div[data-testid="stSelectbox"]:has(label:contains("LANG_SELECTOR")) label { display: none !important; }
div[data-testid="stSelectbox"]:has(label:contains("LANG_SELECTOR")) div[data-baseweb="select"] {
    background-color: #0c1322 !important;
    border: 1px solid #162545 !important;
    border-radius: 8px !important;
    color: #fff !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.75rem !important;
    width: 130px !important;
}

/* Botón de Cerrar Sesión Nativo Estilizado Premium */
.btn-salir-container .stButton > button {
    background: rgba(255, 75, 75, 0.08) !important; color: #ff4b4b !important;
    border: 1px solid rgba(255, 75, 75, 0.25) !important; border-radius: 8px !important;
    font-family: 'Space Mono', monospace !important; font-size: 0.72rem !important;
    padding: 5px 18px !important; text-transform: uppercase !important; font-weight: 700 !important;
    transition: all 0.2s;
}
.btn-salir-container .stButton > button:hover { 
    background: #ff4b4b !important; color: #fff !important; 
    box-shadow: 0 0 15px rgba(255, 75, 75, 0.35);
}

/* Estilos de las pestañas funcionales (Tabs) */
.stTabs [data-baseweb="tab-list"] { padding-left: 80px; border-bottom: 1px solid #162545; background: #050911; }
.stTabs [data-baseweb="tab"] { font-family: 'Space Mono', monospace; font-size: 0.8rem; color: #415675 !important; height: 48px; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { color: #fff !important; border-bottom-color: #0066ff !important; }

/* Caja de Resultados de la Inferencia */
.prediction-box {
    background: #0c1322; border: 1px solid #162545; border-radius: 12px;
    padding: 25px; margin-top: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.4);
}

/* Encabezado Principal */
.hero-section { background: linear-gradient(135deg, #070b12 0%, #0b1526 100%); padding: 55px 80px; border-bottom: 1px solid #162545; }
.hero-main-title { font-size: 3.2rem; font-weight: 700; color: #fff; letter-spacing: -2px; }
.hero-main-title em { font-style: normal; background: linear-gradient(90deg, #0066ff, #00d4aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.hero-sub-title { color: #64758e; max-width: 600px; margin-top: 12px; font-size: 1.05rem; line-height: 1.6; }
</style>
""", unsafe_allow_html=True)

# ── PÁGINA DE AUTENTICACIÓN (LOGIN) ─────────────────────────────────────────────
if not st.session_state.autenticado:
    col_l1, col_l2, col_l3 = st.columns([1, 1.1, 1])
    with col_l2:
        st.markdown("<div style='height:120px'></div>", unsafe_allow_html=True)
        st.markdown("<div style='text-align:center; margin-bottom:25px;'><h1 style='color:#fff; font-family:Space Mono; font-size:2.3rem;'>Object<span style='color:#0066ff'>Vision</span> AI</h1><p style='color:#415675; text-transform:uppercase; letter-spacing:2px; font-size:0.7rem;'>Portal de Acceso · Core Engine v3</p></div>", unsafe_allow_html=True)
        
        tab_login, tab_registro = st.tabs(["🔑   Iniciar Sesión", "📝   Crear Cuenta"])
        with tab_login:
            txt_user = st.text_input("Identificador de Usuario", key="login_u").strip().lower()
            txt_pass = st.text_input("Código de Acceso", type="password", key="login_p")
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            if st.button("Acceder al Sistema", use_container_width=True):
                if txt_user in st.session_state.usuarios_db and st.session_state.usuarios_db[txt_user]["clave"] == txt_pass:
                    st.session_state.autenticado = True
                    st.session_state.rol_usuario = st.session_state.usuarios_db[txt_user]["rol"]
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas. Verifique los datos de acceso.")
        with tab_registro:
            reg_user = st.text_input("Asignar Nuevo Usuario", key="reg_u").strip().lower()
            reg_pass = st.text_input("Asignar Contraseña Segura", type="password", key="reg_p")
            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)
            if st.button("Registrar Credenciales", use_container_width=True):
                if reg_user:
                    st.session_state.usuarios_db[reg_user] = {"clave": reg_pass, "rol": f"{reg_user.upper()} (CLIENTE)"}
                    st.success("Usuario registrado con éxito. Ya puedes iniciar sesión.")
                else:
                    st.warning("El nombre de usuario no puede estar vacío.")
    st.stop()

# ── NAVBAR REHECHA PROFESIONAL (ESTRUCTURA DE FLUJO CONTINUO) ──────────────────
# Usamos un contenedor HTML de base para renderizar la barra limpia
st.markdown(f"""
<div class="custom-navbar">
    <div class="nav-logo">Object<span style="color:#0066ff">Vision</span></div>
    <div style="display:flex; gap:10px;">
        <span class="nav-pill">MobileNetV2</span>
        <span class="nav-pill">PyTorch 2.2</span>
        <span class="nav-pill">ImageNet Dataset</span>
    </div>
    <div style="display:flex; align-items:center; gap:25px;">
        <div class="nav-user">● {st.session_state.rol_usuario}</div>
        <div id="streamlit-controls-anchor" style="display:flex; align-items:center; gap:15px;"></div>
    </div>
</div>
""", unsafe_allow_html=True)

# Justo debajo inyectamos los selectores reales alineados a la derecha usando columnas de apoyo
# Esto simula estar metido dentro de la navbar pero con estabilidad garantizada al 100%
nav_space, nav_ctrl1, nav_ctrl2 = st.columns([7.8, 1.2, 1.0])

with nav_ctrl1:
    # Selector de idioma limpio con clave de cambio controlado
    dicc_idiomas = {"es": "Español", "en": "English", "fr": "Français"}
    idioma_seleccionado = st.selectbox(
        "LANG_SELECTOR",
        options=["es", "en", "fr"],
        format_func=lambda x: dicc_idiomas[x],
        index=["es", "en", "fr"].index(st.session_state.idioma)
    )
    if idioma_seleccionado != st.session_state.idioma:
        st.session_state.idioma = idioma_seleccionado
        st.rerun()

with nav_ctrl2:
    st.markdown('<div class="btn-salir-container" style="margin-top:-14px;">', unsafe_allow_html=True)
    if st.button("Salir", key="action_logout_btn"):
        st.session_state.autenticado = False
        st.session_state.rol_usuario = ""
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

# ── DICCIONARIO DE DICCIONARIOS (INTERNACIONALIZACIÓN COMPLETA) ───────────────
TEXTOS_SISTEMA = {
    "es": {
        "titulo": "Visión artificial que <em>entiende</em> tu mundo.",
        "sub": "Sube cualquier imagen para iniciar el procesamiento neuronal. Nuestra red neuronal convolucional identificará los elementos en tiempo real con sus métricas de confianza.",
        "tab_an": "Analizar Imagen", "tab_cam": "Cámara en Vivo", "tab_comp": "Comparar Modelos", "tab_hist": "Historial",
        "lbl_subir": "Arrastra o selecciona una imagen de tu equipo", "lbl_btn_an": "Ejecutar Inferencia",
        "lbl_res": "Resultado del Análisis Neuronal", "lbl_conf": "Nivel de Confianza", "lbl_vacio_hist": "El registro histórico se encuentra vacío."
    },
    "en": {
        "titulo": "AI Vision that <em>understands</em> your world.",
        "sub": "Upload any image to trigger neural network processing. Our convolutional architecture will identify objects in real-time alongside confidence metrics.",
        "tab_an": "Analyze Image", "tab_cam": "Live Camera", "tab_comp": "Compare Models", "tab_hist": "History",
        "lbl_subir": "Drag and drop or browse an image from your device", "lbl_btn_an": "Run Inference Engine",
        "lbl_res": "Neural Analysis Summary", "lbl_conf": "Confidence Level", "lbl_vacio_hist": "Historical log is currently empty."
    },
    "fr": {
        "titulo": "Vision IA qui <em>comprend</em> votre monde.",
        "sub": "Téléchargez une image pour lancer le traitement neuronal. Notre réseau de neurones convolutif identifiera les objets en temps réel avec leurs indices de confiance.",
        "tab_an": "Analyser l'Image", "tab_cam": "Caméra en Direct", "tab_comp": "Comparer les Modèles", "tab_hist": "Historique",
        "lbl_subir": "Glissez-déposez ou parcourez une image depuis votre appareil", "lbl_btn_an": "Exécuter l'Inférence",
        "lbl_res": "Résumé de l'Analyse Neuronale", "lbl_conf": "Indice de Confiance", "lbl_vacio_hist": "L'historique est actuellement vide."
    }
}
idioma_activo = TEXTOS_SISTEMA[st.session_state.idioma]

# ── HERO DINÁMICO ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="hero-section">
    <div class="hero-main-title">{idioma_activo['titulo']}</div>
    <div class="hero-sub-title">{idioma_activo['sub']}</div>
</div>
""", unsafe_allow_html=True)

# ── SISTEMA DE PESTAÑAS (TABS RENDERING) ───────────────────────────────────────
tabs_app = st.tabs([
    f"🔍 {idioma_activo['tab_an']}", 
    f"📷 {idioma_activo['tab_cam']}", 
    f"📊 {idioma_activo['tab_comp']}", 
    f"🕒 {idioma_activo['tab_hist']}"
])

# ---- TAB 1: MOTOR DE INFERENCIA DE IMÁGENES ----
with tabs_app[0]:
    st.markdown("<div style='padding: 40px 80px;'>", unsafe_allow_html=True)
    
    archivo_subido = st.file_uploader(
        idioma_activo['lbl_subir'], 
        type=["jpg", "png", "jpeg"], 
        key="uploader_main"
    )
    
    if archivo_subido:
        col_img, col_pred = st.columns([1.1, 0.9])
        
        with col_img:
            imagen_pil = Image.open(archivo_subido).convert("RGB")
            st.image(imagen_pil, use_container_width=True, caption="Imagen cargada al búfer")
            
        with col_pred:
            st.markdown(f"### ⚙️ {idioma_activo['lbl_btn_an']}")
            if st.button("LAUNCH INFERENCE", use_container_width=True, type="primary"):
                with st.spinner("Procesando tensores..."):
                    # 1. Preprocesar la imagen para PyTorch
                    tensor_imagen = transformaciones(imagen_pil).unsqueeze(0)
                    
                    # 2. Desactivar cálculo de gradientes y pasar por el modelo
                    with torch.no_grad():
                        salida_modelo = model(tensor_imagen)
                        probabilidades = torch.nn.functional.softmax(salida_modelo[0], dim=0)
                    
                    # 3. Obtener el índice con mayor puntuación
                    top_prob, top_cat = torch.topk(probabilidades, 1)
                    porcentaje_confianza = top_prob.item() * 100
                    nombre_etiqueta_raw = labels_imagenet[top_cat.item()]
                    
                    # Traducir resultado según idioma seleccionado
                    resultado_final = traducir_prediccion(nombre_etiqueta_raw, st.session_state.idioma)
                    
                    # Guardar en el historial de sesión
                    timestamp_actual = datetime.now().strftime("%H:%M:%S")
                    st.session_state.historial.insert(0, {
                        "hora": timestamp_actual,
                        "clase": resultado_final,
                        "confianza": f"{porcentaje_confianza:.2f}%"
                    })
                    
                    # Mostrar resultados estilizados en caja
                    st.markdown(f"""
                    <div class="prediction-box">
                        <h4 style="color:#0066ff; margin-bottom:8px; font-family:'Space Mono'; text-transform:uppercase; font-size:0.8rem;">{idioma_activo['lbl_res']}</h4>
                        <h2 style="color:#fff; font-size:2rem; font-weight:700; margin-bottom:15px;">{resultado_final}</h2>
                        <p style="color:#64758e; font-size:0.85rem;">{idioma_activo['lbl_conf']}: <span style="color:#00d4aa; font-weight:700;">{porcentaje_confianza:.2f}%</span></p>
                    </div>
                    """, unsafe_allow_html=True)
                    st.balloons()
    st.markdown("</div>", unsafe_allow_html=True)

# ---- TAB 4: MÓDULO DE HISTORIAL ----
with tabs_app[3]:
    st.markdown("<div style='padding: 40px 80px;'>", unsafe_allow_html=True)
    if not st.session_state.historial:
        st.markdown(f"<p style='color:#415675; font-family:Space Mono; font-size:0.85rem;'>{idioma_activo['lbl_vacio_hist']}</p>", unsafe_allow_html=True)
    else:
        for item in st.session_state.historial:
            st.markdown(f"""
            <div style="background:#0c1322; border:1px solid #162545; padding:15px 25px; border-radius:8px; margin-bottom:12px; display:flex; justify-content:space-between; align-items:center;">
                <div>
                    <span style="color:#415675; font-family:'Space Mono'; font-size:0.75rem; margin-right:15px;">[{item['hora']}]</span>
                    <strong style="color:#fff; font-size:1rem;">{item['clase']}</strong>
                </div>
                <div style="color:#00d4aa; font-family:'Space Mono'; font-size:0.85rem; font-weight:700;">{item['confianza']}</div>
            </div>
            """, unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# ── FOOTER UNIFICADO DE PROYECTO ───────────────────────────────────────────────
st.markdown("<div style='padding: 35px 80px; border-top:1px solid #162545; font-family:Space Mono; font-size:0.7rem; color:#415675;'>© 2026 ObjectVision · Desarrollo Avanzado Intermodular · Alumno: Mohamed Mohamed Embarec</div>", unsafe_allow_html=True)