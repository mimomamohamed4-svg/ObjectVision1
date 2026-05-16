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

# INTERFAZ CSS MEJORADA (Fuentes, botones y espacios optimizados)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=Space+Mono:wght@400;700&display=swap');
* { margin: 0; padding: 0; box-sizing: border-box; }
html, body, .stApp { background: #080c14 !important; color: #e8eaf0 !important; font-family: 'Sora', sans-serif !important; }
[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
header { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
footer { display: none !important; }

/* Hero principal */
.hero { background: linear-gradient(135deg, #080c14 0%, #0d1829 50%, #080c14 100%); padding: 50px 80px 40px 80px; border-bottom: 1px solid #1a2744; position: relative; overflow: hidden; }
.hero::before { content: ''; position: absolute; top: -50%; left: -50%; width: 200%; height: 200%; background: radial-gradient(ellipse at 30% 40%, rgba(0,100,255,0.08) 0%, transparent 60%), radial-gradient(ellipse at 80% 20%, rgba(0,200,150,0.05) 0%, transparent 50%); pointer-events: none; }
.nav { display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; }
.logo { font-family: 'Space Mono', monospace; font-size: 1.2rem; font-weight: 700; color: #fff; letter-spacing: 2px; text-transform: uppercase; }
.logo span { color: #0066ff; }
.nav-tags { display: flex; gap: 12px; }
.nav-tag { font-size: 0.75rem; letter-spacing: 1.5px; text-transform: uppercase; color: #5efaf2; background: rgba(0,102,255,0.1); border: 1px solid #1a2744; padding: 6px 16px; border-radius: 20px; font-family: 'Space Mono', monospace; font-weight: 700; }

.hero-title { font-size: clamp(2.2rem, 4.5vw, 3.8rem); font-weight: 700; line-height: 1.15; letter-spacing: -1.5px; color: #fff; max-width: 800px; margin-bottom: 20px; }
.hero-title em { font-style: normal; background: linear-gradient(90deg, #0066ff, #00d4aa); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text; }
.hero-sub { font-size: 1.05rem; color: #6b7c96; max-width: 520px; line-height: 1.7; font-weight: 400; }

/* Contadores barra */
.stats-bar { display: flex; gap: 50px; margin-top: 35px; padding-top: 35px; border-top: 1px solid #1a2744; }
.stat { display: flex; flex-direction: column; gap: 6px; }
.stat-number { font-family: 'Space Mono', monospace; font-size: 1.4rem; font-weight: 700; color: #fff; letter-spacing: -0.5px; }
.stat-label { font-size: 0.75rem; color: #4a6080; letter-spacing: 1.5px; text-transform: uppercase; font-weight: 500; }

/* Secciones de análisis */
.zone-label { font-family: 'Space Mono', monospace; font-size: 0.75rem; letter-spacing: 2px; text-transform: uppercase; color: #0066ff; margin-bottom: 20px; font-weight: 700; }
.result-item { padding: 22px 0; border-bottom: 1px solid #1a2744; }
.result-item:last-child { border-bottom: none; }
.result-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 14px; }
.result-name { font-size: 1.15rem; font-weight: 500; color: #e8eaf0; letter-spacing: -0.3px; }
.result-pct { font-family: 'Space Mono', monospace; font-size: 0.95rem; font-weight: 700; }
.bar-track { height: 6px; background: #1a2744; border-radius: 3px; overflow: hidden; }
.bar-fill { height: 100%; border-radius: 3px; transition: width 0.6s ease-in-out; }
.rank-badge { font-family: 'Space Mono', monospace; font-size: 0.7rem; letter-spacing: 1px; text-transform: uppercase; padding: 4px 10px; border-radius: 6px; margin-right: 12px; font-weight: 700; }

/* Historial */
.history-card { background: #0d1422; border: 1px solid #1a2744; border-radius: 12px; padding: 18px; display: flex; align-items: center; gap: 18px; margin-bottom: 14px; transition: transform 0.2s; }
.history-card:hover { transform: translateY(-2px); border-color: #0066ff; }
.history-thumb { width: 65px; height: 65px; object-fit: cover; border-radius: 8px; border: 1px solid #1a2744; }
.history-info { flex: 1; }
.history-name { font-weight: 600; color: #e8eaf0; font-size: 0.95rem; }
.history-meta { font-size: 0.75rem; color: #4a6080; font-family: 'Space Mono', monospace; margin-top: 6px; }

/* Estados vacíos */
.empty-state { display: flex; flex-direction: column; align-items: center; justify-content: center; min-height: 320px; gap: 20px; background: #090f1a; border-radius: 16px; border: 1px dashed #1a2744; }
.empty-icon { font-size: 3.5rem; opacity: 0.15; color: #0066ff; }
.empty-text { font-size: 0.9rem; color: #4a6080; font-family: 'Space Mono', monospace; letter-spacing: 1px; }

/* Footer barra inferior */
.bottom-bar { padding: 30px 80px; border-top: 1px solid #1a2744; display: flex; justify-content: space-between; align-items: center; background: #05080f; }
.bottom-left { font-size: 0.8rem; color: #4a6080; font-family: 'Space Mono', monospace; }
.bottom-tag { font-size: 0.75rem; color: #4a6080; font-family: 'Space Mono', monospace; letter-spacing: 1px; margin-left: 28px; font-weight: 700; }

/* Elementos nativos de Streamlit modificados por CSS */
.stFileUploader { padding: 10px 0; }
.stFileUploader > div { background: #0d1422 !important; border: 1px dashed #1a2744 !important; border-radius: 12px !important; padding: 20px !important; }
.stImage img { border-radius: 16px !important; border: 1px solid #1a2744; }
.stSelectbox > div > div { background: #0d1422 !important; border: 1px solid #1a2744 !important; color: #e8eaf0 !important; border-radius: 8px !important; }

/* Botón de Voz estilizado con estilo Cyberpunk */
.stButton > button { background: rgba(0, 102, 255, 0.1) !important; color: #0066ff !important; border: 1px solid #0066ff !important; padding: 10px 20px !important; border-radius: 8px !important; font-family: 'Space Mono', monospace !important; font-size: 0.75rem !important; letter-spacing: 1px !important; text-transform: uppercase !important; width: auto !important; margin-top: 16px !important; font-weight: 700 !important; transition: all 0.3s; }
.stButton > button:hover { background: linear-gradient(90deg, #0066ff, #00d4aa) !important; color: white !important; border: none !important; transform: scale(1.02); box-shadow: 0 4px 15px rgba(0,102,255,0.3); }

/* Ajuste fino de pestañas (Tabs) */
.stTabs [data-baseweb="tab-list"] { gap: 24px; padding-left: 80px; border-bottom: 1px solid #1a2744; background: #060a10; }
.stTabs [data-baseweb="tab"] { height: 50px; background-color: transparent !important; color: #4a6080 !important; font-family: 'Space Mono', monospace; font-size: 0.85rem; letter-spacing: 1px; text-transform: uppercase; font-weight: 700; }
.stTabs [data-baseweb="tab"][aria-selected="true"] { color: #fff !important; border-bottom-color: #0066ff !important; }
</style>
""", unsafe_allow_html=True)

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
    },
    "fr": {
        "titulo": "Vision artificielle qui <em>comprend</em> votre monde.",
        "subtitulo": "Téléchargez une image et notre IA identifie les objets instantanément.",
        "tab_analizar": "Analyser image",
        "tab_camara": "Caméra live",
        "tab_comparar": "Comparer modèles",
        "tab_historial": "Historique",
        "entrada": "— Entrée",
        "analisis": "— Analyse",
        "alta": "HAUTE CONFIANCE",
        "media": "CONFIANZA MOYENNE",
        "baja": "FAIBLE CONFIANCE",
        "esperando": "En attente...",
        "procesando": "Traitement...",
        "historial_vacio": "Pas encore d'analyse",
        "camara_info": "Activez la caméra et prenez une photo",
        "comparar_info": "Téléchargez une image pour comparer",
        "modelo_a": "— MobileNetV2 (Rapide)",
        "modelo_b": "— ResNet50 (Précis)",
        "boton_voz": "🔊 Écouter le résultat",
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

if "historial" not in st.session_state:
    st.session_state.historial = []
if "idioma" not in st.session_state:
    st.session_state.idioma = "es"

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
    return torch.topk(probs, 3)

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
            <div style="margin-top:6px;font-size:0.75rem;color:#4a6080;font-family:'Space Mono',monospace;letter-spacing:1px">{nivel}</div>
        </div>
        """, unsafe_allow_html=True)

    nombre_top = traducir(etiquetas[top3.indices[0].item()], idioma)
    prob_top = top3.values[0].item() * 100

    if idioma == "es":
        mensaje_voz = f"Objeto detectado: {nombre_top}, con un {prob_top:.0f} por ciento de certeza."
        lang_voz = "es-ES"
    elif idioma == "en":
        mensaje_voz = f"Object detected: {nombre_top}, with {prob_top:.0f} percent confidence."
        lang_voz = "en-US"
    else:
        mensaje_voz = f"Objet détecté: {nombre_top}, avec {prob_top:.0f} pourcent de confiance."
        lang_voz = "fr-FR"

    if st.button(t["boton_voz"], key=f"voz_{nombre_top}"):
        st.components.v1.html(f"""
        <script>
            var msg = new SpeechSynthesisUtterance("{mensaje_voz}");
            msg.lang = "{lang_voz}";
            msg.rate = 0.95;
            msg.pitch = 1.0;
            msg.volume = 1.0;
            window.speechSynthesis.speak(msg);
        </script>
        """, height=0)

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

col_lang = st.columns([4, 1])
with col_lang[1]:
    lang_map = {"Español": "es", "English": "en", "Français": "fr"}
    lang_sel = st.selectbox("", list(lang_map.keys()), label_visibility="collapsed")
    st.session_state.idioma = lang_map[lang_sel]
    idioma = st.session_state.idioma
    t = TEXTOS[idioma]

tab1, tab2, tab3, tab4 = st.tabs([
    t["tab_analizar"], t["tab_camara"], t["tab_comparar"], t["tab_historial"]
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
    col1, col2 = st.columns(2, gap="large")
    with col1:
        st.markdown(f'<div class="zone-label">{t["entrada"]}</div>', unsafe_allow_html=True)
        foto = st.camera_input("", label_visibility="collapsed")
    with col2:
        st.markdown(f'<div class="zone-label">{t["analisis"]}</div>', unsafe_allow_html=True)
        if foto:
            imagen_cam = Image.open(foto).convert("RGB")
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