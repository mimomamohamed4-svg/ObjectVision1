import streamlit as st
from PIL import Image
import torch
from torchvision import models, transforms
import urllib.request
import json
import io
import base64
import time
import os
from datetime import datetime

st.set_page_config(
    page_title="ObjectVision AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ── PERSISTENCIA DE USUARIOS ───────────────────────────────────────────────────
USUARIOS_FILE = "usuarios.json"

def cargar_usuarios():
    if os.path.exists(USUARIOS_FILE):
        with open(USUARIOS_FILE, "r") as f:
            return json.load(f)
    return {
        "mohamed": {"clave": "admin2026", "rol": "MOHAMED (ADMIN)"},
        "profesora": {"clave": "tribunal10", "rol": "PROFESORA (EVALUADOR)"},
        "invitado": {"clave": "invitado123", "rol": "INVITADO"}
    }

def guardar_usuarios(db):
    with open(USUARIOS_FILE, "w") as f:
        json.dump(db, f)

if "usuarios_db" not in st.session_state:
    st.session_state.usuarios_db = cargar_usuarios()
if "autenticado" not in st.session_state:
    st.session_state.autenticado = False
if "rol_usuario" not in st.session_state:
    st.session_state.rol_usuario = ""
if "historial" not in st.session_state:
    st.session_state.historial = []
if "idioma" not in st.session_state:
    st.session_state.idioma = "es"

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=DM+Mono:wght@300;400;500&family=Inter:wght@300;400;500;600;700&display=swap');
@import url('https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css');

* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, .stApp { background: #080c14 !important; color: #e8eaf0 !important; font-family: 'Inter', sans-serif !important; }
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
header { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
footer { display: none !important; }

div[data-testid="stVerticalBlock"]:has(div[data-testid="stTextInput"]) {
    background-color: #0d1422 !important;
    border: 1px solid #1a2744 !important;
    border-radius: 16px !important;
    padding: 35px 30px !important;
    box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6) !important;
    margin-top: 10px !important;
}
div[data-testid="stVerticalBlock"]:has(div[data-testid="stTextInput"]) .stTabs [data-baseweb="tab-list"] {
    padding-left: 0px !important;
    background: transparent !important;
}

.zone-label { font-family: 'DM Mono', monospace; font-size: 0.72rem; letter-spacing: 2px; text-transform: uppercase; color: #0066ff; margin-bottom: 20px; font-weight: 500; }
.result-item { padding: 22px 0; border-bottom: 1px solid #1a2744; }
.result-item:last-child { border-bottom: none; }
.result-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.result-name { font-size: 1.1rem; font-weight: 500; color: #e8eaf0; font-family: 'Inter', sans-serif; }
.result-pct { font-family: 'DM Mono', monospace; font-size: 0.95rem; font-weight: 500; }
.bar-track { height: 5px; background: #1a2744; border-radius: 3px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; }
.rank-badge { font-family: 'DM Mono', monospace; font-size: 0.68rem; padding: 4px 10px; border-radius: 6px; margin-right: 12px; font-weight: 500; }
.history-card { background: #0d1422; border: 1px solid #1a2744; border-radius: 12px; padding: 18px; display: flex; align-items: center; gap: 18px; margin-bottom: 14px; }
.history-thumb { width: 65px; height: 65px; object-fit: cover; border-radius: 8px; }
.history-name { font-weight: 600; color: #e8eaf0; font-size: 0.95rem; font-family: 'Inter', sans-serif; }
.history-meta { font-size: 0.75rem; color: #4a6080; font-family: 'DM Mono', monospace; margin-top: 6px; }
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 280px; gap: 15px; background: #090f1a; border-radius: 16px; border: 1px dashed #1a2744; }
.empty-icon { font-size: 2.5rem; opacity: 0.2; color: #0066ff; }
.empty-text { font-size: 0.85rem; color: #4a6080; font-family: 'DM Mono', monospace; }

.hero { background: linear-gradient(135deg, #080c14 0%, #0d1829 100%); padding: 70px 80px 50px 80px; border-bottom: 1px solid #1a2744; }
.hero-title { font-family: 'Bebas Neue', sans-serif; font-size: clamp(3rem, 7vw, 6rem); font-weight: 400; line-height: 1; letter-spacing: 4px; color: #fff; max-width: 900px; margin-bottom: 18px; }
.hero-title em { font-style: normal; background: linear-gradient(135deg, #0066ff, #00d4aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero-sub { font-size: 1.05rem; color: #6b7c96; max-width: 520px; line-height: 1.7; margin-bottom: 40px; font-family: 'Inter', sans-serif; font-weight: 300; }
.stats-bar { display: flex; gap: 50px; padding-top: 30px; border-top: 1px solid #1a2744; }
.stat-number { font-family: 'Bebas Neue', sans-serif; font-size: 2rem; font-weight: 400; color: #fff; letter-spacing: 2px; }
.stat-label { font-size: 0.68rem; color: #4a6080; letter-spacing: 2px; text-transform: uppercase; margin-top: 2px; font-family: 'DM Mono', monospace; }

.bottom-bar { padding: 28px 80px; border-top: 1px solid #1a2744; display: flex; justify-content: space-between; align-items: center; background: #05080f; }
.bottom-left { font-size: 0.78rem; color: #4a6080; font-family: 'DM Mono', monospace; }
.bottom-tag { font-size: 0.72rem; color: #4a6080; font-family: 'DM Mono', monospace; letter-spacing: 1px; margin-left: 28px; }

.stFileUploader > div { background: #0d1422 !important; border: 1px dashed #1a2744 !important; border-radius: 12px !important; }
.stImage img { border-radius: 12px !important; border: 1px solid #1a2744; }
div[data-testid="stTextInput"] > div > div > input { background: #080c14 !important; color: #fff !important; border: 1px solid #1a2744 !important; border-radius: 8px !important; font-family: 'Inter', sans-serif !important; }
.stTabs [data-baseweb="tab-list"] { gap: 24px; padding-left: 80px; border-bottom: 1px solid #1a2744; background: #060a10; }
.stTabs [data-baseweb="tab"] { height: 52px; background-color: transparent !important; color: #4a6080 !important; font-family: 'DM Mono', monospace; font-size: 0.82rem; font-weight: 500; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { color: #fff !important; border-bottom-color: #0066ff !important; }
.stButton > button { background: rgba(0,102,255,0.08) !important; color: #0066ff !important; border: 1px solid rgba(0,102,255,0.3) !important; border-radius: 8px !important; font-family: 'DM Mono', monospace !important; font-size: 0.75rem !important; font-weight: 500 !important; text-transform: uppercase !important; letter-spacing: 1px !important; }
.stButton > button:hover { background: #0066ff !important; color: #fff !important; }
</style>
""", unsafe_allow_html=True)

# ── LOGIN ──────────────────────────────────────────────────────────────────────
if not st.session_state.autenticado:
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("<div style='height:80px'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="text-align:center; margin-bottom:30px;">
            <div style="font-family:'Bebas Neue',sans-serif; font-size:3rem; font-weight:400; color:#fff; letter-spacing:6px;">
                OBJECT<span style="color:#0066ff">VISION</span> <span style="color:#4a6080; font-size:1.5rem; letter-spacing:3px;">AI</span>
            </div>
            <div style="font-size:0.72rem; color:#2a3a54; letter-spacing:2px; text-transform:uppercase; margin-top:8px; font-family:'DM Mono',monospace;">
                Portal de acceso · 2026
            </div>
            <div style="height:1px; background:#1a2744; margin:24px 0;"></div>
        </div>
        """, unsafe_allow_html=True)

        tab_login, tab_reg = st.tabs(["  Iniciar Sesión", "  Crear Cuenta"])

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
                    st.success("Acceso autorizado.")
                    time.sleep(0.4)
                    st.rerun()
                else:
                    st.error("Credenciales incorrectas.")

        with tab_reg:
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            nuevo_u = st.text_input("Nombre de usuario", placeholder="Ej: pedro99", key="r_u").strip().lower()
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            nueva_p = st.text_input("Contraseña", type="password", placeholder="Mínimo 4 caracteres", key="r_p")
            st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
            confirmar_p = st.text_input("Repite la contraseña", type="password", placeholder="••••••••", key="r_p2")
            st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
            if st.button("Crear Cuenta", key="btn_reg", use_container_width=True):
                if not nuevo_u or not nueva_p:
                    st.warning("Rellena todos los campos.")
                elif len(nueva_p) < 4:
                    st.error("Mínimo 4 caracteres.")
                elif nueva_p != confirmar_p:
                    st.error("Las contraseñas no coinciden.")
                elif nuevo_u in st.session_state.usuarios_db:
                    st.error("Usuario ya existe.")
                else:
                    st.session_state.usuarios_db[nuevo_u] = {
                        "clave": nueva_p,
                        "rol": f"{nuevo_u.upper()} (CLIENTE)"
                    }
                    guardar_usuarios(st.session_state.usuarios_db)
                    st.success(f"Cuenta '{nuevo_u}' creada.")
    st.stop()

# ── NAVBAR ─────────────────────────────────────────────────────────────────────
nav_col1, nav_col2, nav_col3 = st.columns([1.5, 2, 2.5])

with nav_col1:
    st.markdown("""
    <div style="padding-top:5px;font-family:'Bebas Neue',sans-serif;font-size:1.4rem;font-weight:400;color:#fff;letter-spacing:4px;text-transform:uppercase;">
        Object<span style="color:#0066ff">Vision</span>
    </div>
    """, unsafe_allow_html=True)

with nav_col2:
    st.markdown("""
    <div style="display:flex;gap:6px;padding-top:8px;">
        <span style="font-size:0.6rem;letter-spacing:1px;text-transform:uppercase;color:#4a6080;background:rgba(26,39,68,0.5);border:1px solid #1a2744;padding:3px 8px;border-radius:4px;font-family:'DM Mono',monospace;">MobileNetV2</span>
        <span style="font-size:0.6rem;letter-spacing:1px;text-transform:uppercase;color:#4a6080;background:rgba(26,39,68,0.5);border:1px solid #1a2744;padding:3px 8px;border-radius:4px;font-family:'DM Mono',monospace;">PyTorch</span>
    </div>
    """, unsafe_allow_html=True)

with nav_col3:
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:flex-end;padding-top:8px;">
        <span style="font-family:'DM Mono',monospace;font-size:0.7rem;color:#00d4aa;margin-right:5px;">
            <i class="fa-solid fa-circle" style="font-size:0.5rem;"></i> {st.session_state.rol_usuario}
        </span>
    </div>
    """, unsafe_allow_html=True)
    sub_c1, sub_c2, sub_c3, sub_c4 = st.columns([1, 1, 1, 1.5])
    with sub_c1:
        if st.button("ES", key="btn_lang_es", use_container_width=True):
            st.session_state.idioma = "es"
            st.rerun()
    with sub_c2:
        if st.button("EN", key="btn_lang_en", use_container_width=True):
            st.session_state.idioma = "en"
            st.rerun()
    with sub_c3:
        if st.button("FR", key="btn_lang_fr", use_container_width=True):
            st.session_state.idioma = "fr"
            st.rerun()
    with sub_c4:
        if st.button("Salir", key="btn_navbar_logout", use_container_width=True):
            st.session_state.autenticado = False
            st.session_state.rol_usuario = ""
            st.rerun()

idioma = st.session_state.idioma

TEXTOS = {
    "es": {
        "titulo": "VISIÓN ARTIFICIAL QUE <em>ENTIENDE</em> TU MUNDO.",
        "subtitulo": "Sube cualquier imagen y nuestra IA identifica los objetos al instante con datos de confianza en tiempo real.",
        "tab_analizar": "Analizar imagen", "tab_camara": "Cámara en vivo",
        "tab_comparar": "Comparar modelos", "tab_historial": "Historial",
        "entrada": "— Entrada", "analisis": "— Análisis",
        "alta": "CONFIANZA ALTA", "media": "CONFIANZA MEDIA", "baja": "CONFIANZA BAJA",
        "esperando": "Esperando imagen...", "procesando": "Procesando...",
        "historial_vacio": "Sin análisis todavía", "camara_info": "Activa la cámara y toma una foto",
        "comparar_info": "Sube una imagen para comparar modelos",
        "modelo_a": "— MobileNetV2 (Rápido)", "modelo_b": "— ResNet50 (Preciso)",
        "boton_voz": "Escuchar resultado",
        "boton_dl": "Descargar reporte",
    },
    "en": {
        "titulo": "ARTIFICIAL VISION THAT <em>UNDERSTANDS</em> YOUR WORLD.",
        "subtitulo": "Upload any image and our AI instantly identifies objects with real-time confidence data.",
        "tab_analizar": "Analyze image", "tab_camara": "Live camera",
        "tab_comparar": "Compare models", "tab_historial": "History",
        "entrada": "— Input", "analisis": "— Analysis",
        "alta": "HIGH CONFIDENCE", "media": "MEDIUM CONFIDENCE", "baja": "LOW CONFIDENCE",
        "esperando": "Waiting for image...", "procesando": "Processing...",
        "historial_vacio": "No analysis yet", "camara_info": "Activate camera and take a photo",
        "comparar_info": "Upload an image to compare models",
        "modelo_a": "— MobileNetV2 (Fast)", "modelo_b": "— ResNet50 (Accurate)",
        "boton_voz": "Listen to result",
        "boton_dl": "Download report",
    },
    "fr": {
        "titulo": "VISION ARTIFICIELLE QUI <em>COMPREND</em> VOTRE MONDE.",
        "subtitulo": "Téléchargez une image et notre IA identifie les objets instantanément.",
        "tab_analizar": "Analyser image", "tab_camara": "Caméra live",
        "tab_comparar": "Comparer modèles", "tab_historial": "Historique",
        "entrada": "— Entrée", "analisis": "— Analyse",
        "alta": "HAUTE CONFIANCE", "media": "CONFIANCE MOYENNE", "baja": "FAIBLE CONFIANCE",
        "esperando": "En attente...", "procesando": "Traitement...",
        "historial_vacio": "Pas encore d'analyse", "camara_info": "Activez la caméra",
        "comparar_info": "Téléchargez une image pour comparer",
        "modelo_a": "— MobileNetV2 (Rapide)", "modelo_b": "— ResNet50 (Précis)",
        "boton_voz": "Écouter le résultat",
        "boton_dl": "Télécharger rapport",
    }
}

TRADUCCIONES = {
    "car": "Coche", "sports car": "Coche deportivo", "convertible": "Descapotable",
    "dog": "Perro", "cat": "Gato", "bird": "Pájaro", "labrador retriever": "Labrador Retriever",
    "golden retriever": "Golden Retriever", "pizza": "Pizza", "hamburger": "Hamburguesa",
    "banana": "Plátano", "apple": "Manzana", "chair": "Silla", "laptop": "Portátil",
    "bicycle": "Bicicleta", "motorcycle": "Moto", "bus": "Autobús", "truck": "Camión",
    "airplane": "Avión", "lion": "León", "tiger": "Tigre", "elephant": "Elefante",
    "soccer ball": "Balón de fútbol", "keyboard": "Teclado", "bottle": "Botella",
    "cup": "Taza", "book": "Libro", "clock": "Reloj", "horse": "Caballo",
    "kuvasz": "Kuvasz", "shield": "Escudo", "minivan": "Minivan",
    "chesapeake bay retriever": "Chesapeake Bay Retriever",
    "computer mouse": "Ratón de ordenador", "sunglasses": "Gafas de sol",
    "backpack": "Mochila", "table lamp": "Lámpara"
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

# sufijo para hacer keys únicas en comparar modelos
def mostrar_resultados(top3, t, idm, umbral, sufijo=""):
    badge_colors = ["#0066ff", "#00d4aa", "#6644ff"]
    visibles = 0
    reporte = f"OBJECTVISION AI — REPORTE\nFecha: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n\n"
    for i in range(3):
        nombre = traducir(etiquetas[top3.indices[i].item()], idm)
        prob = top3.values[i].item()
        pct = prob * 100
        if pct < umbral:
            continue
        visibles += 1
        color_bar, nivel = nivel_confianza(prob, t)
        reporte += f"#{i+1} {nombre}: {pct:.1f}%\n"
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
            <div style="margin-top:6px;font-size:0.72rem;color:#4a6080;font-family:'DM Mono',monospace;letter-spacing:1px">{nivel}</div>
        </div>
        """, unsafe_allow_html=True)

    if visibles == 0:
        st.markdown(f'<div class="empty-state"><div class="empty-icon"><i class="fa-solid fa-triangle-exclamation"></i></div><div class="empty-text">Ningún objeto supera el {umbral}% mínimo.</div></div>', unsafe_allow_html=True)
        return

    nombre_top = traducir(etiquetas[top3.indices[0].item()], idm)
    prob_top = top3.values[0].item() * 100
    if idm == "es":
        msg_voz = f"Objeto detectado: {nombre_top}, con un {prob_top:.0f} por ciento de certeza."
        lang_voz = "es-ES"
    elif idm == "en":
        msg_voz = f"Object detected: {nombre_top}, with {prob_top:.0f} percent confidence."
        lang_voz = "en-US"
    else:
        msg_voz = f"Objet détecté: {nombre_top}, avec {prob_top:.0f} pourcent de confiance."
        lang_voz = "fr-FR"

    col_b1, col_b2 = st.columns(2)
    with col_b1:
        if st.button(f"▶  {t['boton_voz']}", key=f"voz_{nombre_top}_{idm}_{sufijo}"):
            st.components.v1.html(f"""
            <script>
                var msg = new SpeechSynthesisUtterance("{msg_voz}");
                msg.lang = "{lang_voz}";
                msg.rate = 0.95;
                window.speechSynthesis.speak(msg);
            </script>
            """, height=0)
    with col_b2:
        st.download_button(
            f"↓  {t['boton_dl']}",
            data=reporte,
            file_name=f"reporte_{sufijo}.txt",
            mime="text/plain",
            key=f"dl_{nombre_top}_{idm}_{sufijo}"
        )

t = TEXTOS[idioma]

st.markdown(f"""
<div class="hero">
    <div class="hero-title">{t["titulo"]}</div>
    <div class="hero-sub">{t["subtitulo"]}</div>
    <div class="stats-bar">
        <div><div class="stat-number">1000+</div><div class="stat-label">Clases</div></div>
        <div><div class="stat-number">Top-3</div><div class="stat-label">Predicciones</div></div>
        <div><div class="stat-number">Cloud</div><div class="stat-label">Servidor remoto</div></div>
        <div><div class="stat-number">24/7</div><div class="stat-label">Disponibilidad</div></div>
    </div>
</div>
""", unsafe_allow_html=True)

st.markdown("<div style='padding: 20px 80px 0 80px;'>", unsafe_allow_html=True)
umbral_sel = st.slider("Filtro de certeza mínima", min_value=5, max_value=90, value=25, step=5, format="%d%%")
st.markdown("</div>", unsafe_allow_html=True)

es_admin = "MOHAMED (ADMIN)" in st.session_state.rol_usuario
lista_tabs = [t["tab_analizar"], t["tab_camara"], t["tab_comparar"], t["tab_historial"]]
if es_admin:
    lista_tabs.append("Panel Admin")

tabs_render = st.tabs(lista_tabs)

# TAB 1 — ANALIZAR
with tabs_render[0]:
    st.markdown("<div style='padding: 40px 80px;'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown(f'<div class="zone-label">{t["entrada"]}</div>', unsafe_allow_html=True)
        archivo = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="up1")
        if archivo:
            imagen = Image.open(archivo).convert("RGB")
            st.image(imagen, use_container_width=True)
    with col2:
        st.markdown(f'<div class="zone-label">{t["analisis"]}</div>', unsafe_allow_html=True)
        if archivo:
            with st.spinner(t["procesando"]):
                t0 = time.time()
                top3 = predecir(imagen, mobilenet)
                ms = (time.time() - t0) * 1000
            st.markdown(f"<span style='font-family:DM Mono;font-size:0.72rem;color:#00d4aa;letter-spacing:1px'><i class='fa-solid fa-bolt'></i> INFERENCIA: {ms:.0f}ms</span>", unsafe_allow_html=True)
            mostrar_resultados(top3, t, idioma, umbral_sel, sufijo="analizar")
            buf = io.BytesIO()
            imagen.save(buf, format="JPEG")
            img_b64 = base64.b64encode(buf.getvalue()).decode()
            nombre_top = traducir(etiquetas[top3.indices[0].item()], idioma)
            prob_top = top3.values[0].item()
            if not st.session_state.historial or st.session_state.historial[0]["nombre"] != nombre_top:
                st.session_state.historial.insert(0, {"nombre": nombre_top, "prob": prob_top, "img": img_b64, "hora": datetime.now().strftime("%H:%M")})
                st.session_state.historial = st.session_state.historial[:5]
        else:
            st.markdown(f'<div class="empty-state"><div class="empty-icon"><i class="fa-regular fa-image"></i></div><div class="empty-text">{t["esperando"]}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# TAB 2 — CÁMARA
with tabs_render[1]:
    st.markdown("<div style='padding: 40px 80px;'>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown(f'<div class="zone-label">{t["entrada"]}</div>', unsafe_allow_html=True)
        foto = st.camera_input("", label_visibility="collapsed")
    with col2:
        st.markdown(f'<div class="zone-label">{t["analisis"]}</div>', unsafe_allow_html=True)
        if foto:
            img_cam = Image.open(foto).convert("RGB")
            with st.spinner(t["procesando"]):
                t0 = time.time()
                top3_cam = predecir(img_cam, mobilenet)
                ms = (time.time() - t0) * 1000
            st.markdown(f"<span style='font-family:DM Mono;font-size:0.72rem;color:#00d4aa;letter-spacing:1px'><i class='fa-solid fa-bolt'></i> INFERENCIA: {ms:.0f}ms</span>", unsafe_allow_html=True)
            mostrar_resultados(top3_cam, t, idioma, umbral_sel, sufijo="camara")
        else:
            st.markdown(f'<div class="empty-state"><div class="empty-icon"><i class="fa-solid fa-camera"></i></div><div class="empty-text">{t["camara_info"]}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# TAB 3 — COMPARAR
with tabs_render[2]:
    st.markdown("<div style='padding: 40px 80px;'>", unsafe_allow_html=True)
    archivo_comp = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed", key="up2")
    if archivo_comp:
        img_comp = Image.open(archivo_comp).convert("RGB")
        st.image(img_comp, width=380)
        st.markdown("<div style='height:24px'></div>", unsafe_allow_html=True)
        col_a, col_b = st.columns(2, gap="large")
        with col_a:
            st.markdown(f'<div class="zone-label">{t["modelo_a"]}</div>', unsafe_allow_html=True)
            with st.spinner(t["procesando"]):
                top3_mob = predecir(img_comp, mobilenet)
            mostrar_resultados(top3_mob, t, idioma, umbral_sel, sufijo="mobilenet")
        with col_b:
            st.markdown(f'<div class="zone-label">{t["modelo_b"]}</div>', unsafe_allow_html=True)
            resnet = cargar_resnet()
            with st.spinner(t["procesando"]):
                top3_res = predecir(img_comp, resnet)
            mostrar_resultados(top3_res, t, idioma, umbral_sel, sufijo="resnet")
    else:
        st.markdown(f'<div class="empty-state"><div class="empty-icon"><i class="fa-solid fa-code-compare"></i></div><div class="empty-text">{t["comparar_info"]}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# TAB 4 — HISTORIAL
with tabs_render[3]:
    st.markdown("<div style='padding: 40px 80px;'>", unsafe_allow_html=True)
    st.markdown(f'<div class="zone-label">{t["tab_historial"]}</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    if st.session_state.historial:
        for item in st.session_state.historial:
            st.markdown(f"""
            <div class="history-card">
                <img class="history-thumb" src="data:image/jpeg;base64,{item['img']}" />
                <div><div class="history-name">{item['nombre']}</div>
                <div class="history-meta">{item['prob']*100:.1f}% · {item['hora']}</div></div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="empty-state"><div class="empty-icon"><i class="fa-regular fa-clock"></i></div><div class="empty-text">{t["historial_vacio"]}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# TAB 5 — ADMIN
if es_admin:
    with tabs_render[4]:
        st.markdown("<div style='padding: 40px 80px;'>", unsafe_allow_html=True)
        st.markdown('<div class="zone-label">— Panel de Administración</div>', unsafe_allow_html=True)
        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
        filas = ""
        for usr, datos in st.session_state.usuarios_db.items():
            es_adm = "ADMIN" in datos["rol"]
            badge = "background:rgba(0,102,255,0.15);color:#0066ff;border:1px solid rgba(0,102,255,0.3);" if es_adm else "background:rgba(0,212,170,0.1);color:#00d4aa;border:1px solid rgba(0,212,170,0.2);"
            clave_oculta = "*" * len(datos["clave"])
            filas += f"""
            <tr>
                <td style="padding:14px 16px;border-bottom:1px solid #1a2744;color:#e8eaf0;font-family:'DM Mono',monospace;font-weight:500">{usr}</td>
                <td style="padding:14px 16px;border-bottom:1px solid #1a2744;color:#4a6080;font-family:'DM Mono',monospace">{clave_oculta}</td>
                <td style="padding:14px 16px;border-bottom:1px solid #1a2744"><span style="font-family:'DM Mono',monospace;font-size:0.72rem;padding:4px 10px;border-radius:4px;{badge}">{datos['rol']}</span></td>
            </tr>"""
        st.components.v1.html(f"""
        <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.0/css/all.min.css">
        <table style="width:100%;border-collapse:collapse;background:#0d1422;border-radius:8px;border:1px solid #1a2744;">
            <thead><tr style="background:#111a2e;color:#0066ff;font-family:'DM Mono',monospace;font-size:0.75rem;letter-spacing:1px;text-align:left">
                <th style="padding:12px 16px"><i class="fa-solid fa-user"></i> USUARIO</th>
                <th style="padding:12px 16px"><i class="fa-solid fa-lock"></i> CONTRASEÑA</th>
                <th style="padding:12px 16px"><i class="fa-solid fa-shield-halved"></i> ROL</th>
            </tr></thead>
            <tbody>{filas}</tbody>
        </table>
        """, height=300, scrolling=True)
        st.markdown("</div>", unsafe_allow_html=True)

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