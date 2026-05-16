import streamlit as st
from PIL import Image
import torch
from torchvision import models, transforms
import urllib.request
import json
import io
import base64
from datetime import datetime

st.set_page_config(
    page_title="ObjectVision AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700&family=Space+Mono:wght@400;700&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, .stApp { background: #080c14 !important; color: #e8eaf0 !important; font-family: 'Sora', sans-serif !important; }
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
header { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
footer { display: none !important; }

.hero {
    background: linear-gradient(135deg, #080c14 0%, #0d1829 50%, #080c14 100%);
    padding: 40px 80px 30px 80px;
    border-bottom: 1px solid #1a2744;
    position: relative;
    overflow: hidden;
}
.hero::before {
    content: '';
    position: absolute;
    top: -50%; left: -50%;
    width: 200%; height: 200%;
    background: radial-gradient(ellipse at 30% 40%, rgba(0,100,255,0.08) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 20%, rgba(0,200,150,0.05) 0%, transparent 50%);
    pointer-events: none;
}
.nav { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; }
.logo { font-family: 'Space Mono', monospace; font-size: 1.1rem; font-weight: 700; color: #fff; letter-spacing: 2px; text-transform: uppercase; }
.logo span { color: #0066ff; }
.nav-tags { display: flex; gap: 12px; }
.nav-tag { font-size: 0.7rem; letter-spacing: 1.5px; text-transform: uppercase; color: #4a6080; border: 1px solid #1a2744; padding: 6px 14px; border-radius: 20px; font-family: 'Space Mono', monospace; }
.hero-title { font-size: clamp(2rem, 4vw, 3.5rem); font-weight: 700; line-height: 1.1; letter-spacing: -2px; color: #fff; max-width: 700px; margin-bottom: 16px; }
.hero-title em { font-style: normal; background: linear-gradient(90deg, #0066ff, #00d4aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero-sub { font-size: 1rem; color: #4a6080; max-width: 480px; line-height: 1.7; font-weight: 300; }
.stats-bar { display: flex; gap: 40px; margin-top: 30px; padding-top: 30px; border-top: 1px solid #1a2744; }
.stat { display: flex; flex-direction: column; gap: 4px; }
.stat-number { font-family: 'Space Mono', monospace; font-size: 1.3rem; font-weight: 700; color: #fff; }
.stat-label { font-size: 0.72rem; color: #4a6080; letter-spacing: 1px; text-transform: uppercase; }

.tabs-bar { display: flex; gap: 0; border-bottom: 1px solid #1a2744; padding: 0 80px; background: #080c14; }
.tab-btn { padding: 16px 28px; font-family: 'Space Mono', monospace; font-size: 0.72rem; letter-spacing: 1.5px; text-transform: uppercase; color: #4a6080; cursor: pointer; border-bottom: 2px solid transparent; transition: all 0.2s; background: none; border-top: none; border-left: none; border-right: none; }
.tab-btn.active { color: #0066ff; border-bottom-color: #0066ff; }

.zone-label { font-family: 'Space Mono', monospace; font-size: 0.7rem; letter-spacing: 2px; text-transform: uppercase; color: #0066ff; margin-bottom: 16px; }

.result-item { padding: 20px 0; border-bottom: 1px solid #1a2744; }
.result-item:last-child { border-bottom: none; }
.result-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; }
.result-name { font-size: 1.1rem; font-weight: 600; color: #e8eaf0; }
.result-pct { font-family: 'Space Mono', monospace; font-size: 0.85rem; font-weight: 700; }
.bar-track { height: 4px; background: #1a2744; border-radius: 2px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 2px; }
.rank-badge { font-family: 'Space Mono', monospace; font-size: 0.65rem; letter-spacing: 1px; text-transform: uppercase; padding: 3px 8px; border-radius: 4px; margin-right: 10px; }

.history-card { background: #0d1422; border: 1px solid #1a2744; border-radius: 12px; padding: 16px; display: flex; align-items: center; gap: 16px; margin-bottom: 12px; }
.history-thumb { width: 60px; height: 60px; object-fit: cover; border-radius: 8px; }
.history-info { flex: 1; }
.history-name { font-weight: 600; color: #e8eaf0; font-size: 0.9rem; }
.history-meta { font-size: 0.72rem; color: #4a6080; font-family: 'Space Mono', monospace; margin-top: 4px; }

.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 300px; gap: 16px; }
.empty-icon { font-size: 3rem; opacity: 0.2; }
.empty-text { font-size: 0.85rem; color: #2a3a54; font-family: 'Space Mono', monospace; letter-spacing: 1px; }

.bottom-bar { padding: 20px 80px; border-top: 1px solid #1a2744; display: flex; justify-content: space-between; align-items: center; }
.bottom-left { font-size: 0.75rem; color: #2a3a54; font-family: 'Space Mono', monospace; }
.bottom-tag { font-size: 0.7rem; color: #2a3a54; font-family: 'Space Mono', monospace; letter-spacing: 1px; margin-left: 24px; }

.stFileUploader > div { background: #080c14 !important; border: 1px dashed #1a2744 !important; border-radius: 12px !important; color: #4a6080 !important; }
.stImage img { border-radius: 12px !important; }
div[data-testid="stImage"] img { border-radius: 12px; }
.stSelectbox > div > div { background: #0d1422 !important; border: 1px solid #1a2744 !important; color: #e8eaf0 !important; }
.stRadio > div { gap: 12px; }
</style>
""", unsafe_allow_html=True)

# TEXTOS MULTIIDIOMA
TEXTOS = {
    "es": {
        "titulo": "Visión artificial que <em>entiende</em> tu mundo.",
        "subtitulo": "Sube cualquier imagen y nuestra IA identifica los objetos al instante con datos de confianza en tiempo real.",
        "tab_analizar": "Analizar imagen",
        "tab_camara": "Cámara en vivo",
        "tab_comparar": "Comparar modelos",
        "tab_historial": "Historial",
        "entrada": "— Entrada",
        "analisis": "— Análisis",
        "resultados": "Resultados del análisis",
        "confianza": "Confianza",
        "alta": "CONFIANZA ALTA",
        "media": "CONFIANZA MEDIA",
        "baja": "CONFIANZA BAJA",
        "esperando": "Esperando imagen...",
        "subir": "Sube una imagen para analizar",
        "procesando": "Procesando...",
        "historial_vacio": "Sin análisis todavía",
        "camara_info": "Activa la cámara y toma una foto para analizarla",
        "comparar_info": "Sube una imagen para comparar ambos modelos",
        "modelo_a": "— MobileNetV2 (Rápido)",
        "modelo_b": "— ResNet50 (Preciso)",
        "idioma": "Idioma",
    },
    "en": {
        "titulo": "Artificial vision that <em>understands</em> your world.",
        "subtitulo": "Upload any image and our AI instantly identifies objects with real-time confidence data.",
        "tab_analizar": "Analyze image",
        "tab_camara": "Live camera",
        "tab_comparar": "Compare models",
        "tab_historial": "History",
        "entrada": "— Input",
        "analisis": "— Analysis",
        "resultados": "Analysis results",
        "confianza": "Confidence",
        "alta": "HIGH CONFIDENCE",
        "media": "MEDIUM CONFIDENCE",
        "baja": "LOW CONFIDENCE",
        "esperando": "Waiting for image...",
        "subir": "Upload an image to analyze",
        "procesando": "Processing...",
        "historial_vacio": "No analysis yet",
        "camara_info": "Activate the camera and take a photo to analyze it",
        "comparar_info": "Upload an image to compare both models",
        "modelo_a": "— MobileNetV2 (Fast)",
        "modelo_b": "— ResNet50 (Accurate)",
        "idioma": "Language",
    },
    "fr": {
        "titulo": "Vision artificielle qui <em>comprend</em> votre monde.",
        "subtitulo": "Téléchargez n'importe quelle image et notre IA identifie les objets instantanément.",
        "tab_analizar": "Analyser image",
        "tab_camara": "Caméra live",
        "tab_comparar": "Comparer modèles",
        "tab_historial": "Historique",
        "entrada": "— Entrée",
        "analisis": "— Analyse",
        "resultados": "Résultats de l'analyse",
        "confianza": "Confiance",
        "alta": "HAUTE CONFIANCE",
        "media": "CONFIANCE MOYENNE",
        "baja": "FAIBLE CONFIANCE",
        "esperando": "En attente d'image...",
        "subir": "Téléchargez une image à analyser",
        "procesando": "Traitement...",
        "historial_vacio": "Pas encore d'analyse",
        "camara_info": "Activez la caméra et prenez une photo pour l'analyser",
        "comparar_info": "Téléchargez une image pour comparer les deux modèles",
        "modelo_a": "— MobileNetV2 (Rapide)",
        "modelo_b": "— ResNet50 (Précis)",
        "idioma": "Langue",
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
    "computer mouse": "Ratón de ordenador", "table lamp": "Lámpara",
    "sunglasses": "Gafas de sol", "backpack": "Mochila"
}

def traducir(n, idioma="es"):
    if idioma != "es":
        return n.replace("_", " ").title()
    return TRADUCCIONES.get(n.lower().replace("_", " "), n.replace("_", " ").title())

def nivel_confianza(prob, t):
    if prob >= 0.6:
        return "#28a745", t["alta"]
    elif prob >= 0.3:
        return "#ffc107", t["media"]
    else:
        return "#dc3545", t["baja"]

# Session state
if "historial" not in st.session_state:
    st.session_state.historial = []
if "idioma" not in st.session_state:
    st.session_state.idioma = "es"
if "tab" not in st.session_state:
    st.session_state.tab = "analizar"

# Modelos
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

@st.cache_data
def cargar_etiquetas():
    url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
    with urllib.request.urlopen(url) as f:
        return json.load(f)

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
    top3 = torch.topk(probs, 3)
    return top3

def mostrar_resultados(top3, t, idioma):
    badge_colors = ["#0066ff", "#00d4aa", "#6644ff"]
    for i in range(3):
        nombre = traducir(etiquetas[top3.indices[i].item()], idioma)
        prob = top3.values[i].item()
        pct = prob * 100
        color_bar, nivel = nivel_confianza(prob, t)
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
            <div style="margin-top:6px;font-size:0.7rem;color:#2a3a54;font-family:'Space Mono',monospace;letter-spacing:1px">{nivel}</div>
        </div>
        """, unsafe_allow_html=True)

# HERO
idioma = st.session_state.idioma
t = TEXTOS[idioma]

st.markdown(f"""
<div class="hero">
    <div class="nav">
        <div class="logo">Object<span>Vision</span></div>
        <div class="nav-tags">
            <div class="nav-tag">MobileNetV2</div>
            <div class="nav-tag">PyTorch</div>
            <div class="nav-tag">ImageNet</div>
        </div>
    </div>
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

# SELECTOR DE IDIOMA
col_lang = st.columns([4, 1])
with col_lang[1]:
    lang_map = {"Español": "es", "English": "en", "Français": "fr"}
    lang_sel = st.selectbox("", list(lang_map.keys()), label_visibility="collapsed")
    st.session_state.idioma = lang_map[lang_sel]
    idioma = st.session_state.idioma
    t = TEXTOS[idioma]

# TABS
tab1, tab2, tab3, tab4 = st.tabs([
    t["tab_analizar"],
    t["tab_camara"],
    t["tab_comparar"],
    t["tab_historial"]
])

# TAB 1 — ANALIZAR
with tab1:
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
                top3 = predecir(imagen, mobilenet)
            mostrar_resultados(top3, t, idioma)
            # Guardar en historial
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

# TAB 2 — CÁMARA
with tab2:
    st.markdown("<div style='padding: 40px 80px;'>", unsafe_allow_html=True)
    st.markdown(f'<div class="zone-label">{t["tab_camara"]}</div>', unsafe_allow_html=True)
    st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        foto = st.camera_input("", label_visibility="collapsed")
        if foto:
            imagen_cam = Image.open(foto).convert("RGB")
    with col2:
        if foto:
            with st.spinner(t["procesando"]):
                top3_cam = predecir(imagen_cam, mobilenet)
            mostrar_resultados(top3_cam, t, idioma)
        else:
            st.markdown(f'<div class="empty-state"><div class="empty-icon">📷</div><div class="empty-text">{t["camara_info"]}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# TAB 3 — COMPARAR
with tab3:
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
            mostrar_resultados(top3_mobile, t, idioma)
        with col_b:
            st.markdown(f'<div class="zone-label">{t["modelo_b"]}</div>', unsafe_allow_html=True)
            resnet = cargar_resnet()
            with st.spinner(t["procesando"]):
                top3_resnet = predecir(imagen_comp, resnet)
            mostrar_resultados(top3_resnet, t, idioma)
    else:
        st.markdown(f'<div class="empty-state"><div class="empty-icon">⬡</div><div class="empty-text">{t["comparar_info"]}</div></div>', unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

# TAB 4 — HISTORIAL
with tab4:
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

# FOOTER
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