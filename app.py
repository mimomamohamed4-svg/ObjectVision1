import streamlit as st
from PIL import Image
import torch
from torchvision import models, transforms
import urllib.request
import json

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

html, body, .stApp {
    background: #080c14 !important;
    color: #e8eaf0 !important;
    font-family: 'Sora', sans-serif !important;
}

[data-testid="stSidebar"] { display: none; }
[data-testid="collapsedControl"] { display: none; }
header { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
footer { display: none !important; }

.hero {
    background: linear-gradient(135deg, #080c14 0%, #0d1829 50%, #080c14 100%);
    padding: 60px 80px 40px 80px;
    position: relative;
    overflow: hidden;
    border-bottom: 1px solid #1a2744;
}

.hero::before {
    content: '';
    position: absolute;
    top: -50%;
    left: -50%;
    width: 200%;
    height: 200%;
    background: radial-gradient(ellipse at 30% 40%, rgba(0, 100, 255, 0.08) 0%, transparent 60%),
                radial-gradient(ellipse at 80% 20%, rgba(0, 200, 150, 0.05) 0%, transparent 50%);
    pointer-events: none;
}

.nav {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 80px;
}

.logo {
    font-family: 'Space Mono', monospace;
    font-size: 1.1rem;
    font-weight: 700;
    color: #ffffff;
    letter-spacing: 2px;
    text-transform: uppercase;
}

.logo span {
    color: #0066ff;
}

.nav-tags {
    display: flex;
    gap: 12px;
}

.nav-tag {
    font-size: 0.7rem;
    letter-spacing: 1.5px;
    text-transform: uppercase;
    color: #4a6080;
    border: 1px solid #1a2744;
    padding: 6px 14px;
    border-radius: 20px;
    font-family: 'Space Mono', monospace;
}

.hero-title {
    font-size: clamp(2.5rem, 5vw, 4.5rem);
    font-weight: 700;
    line-height: 1.1;
    letter-spacing: -2px;
    color: #ffffff;
    max-width: 700px;
    margin-bottom: 20px;
}

.hero-title em {
    font-style: normal;
    background: linear-gradient(90deg, #0066ff, #00d4aa);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-size: 1rem;
    color: #4a6080;
    max-width: 480px;
    line-height: 1.7;
    font-weight: 300;
}

.stats-bar {
    display: flex;
    gap: 40px;
    margin-top: 50px;
    padding-top: 40px;
    border-top: 1px solid #1a2744;
}

.stat {
    display: flex;
    flex-direction: column;
    gap: 4px;
}

.stat-number {
    font-family: 'Space Mono', monospace;
    font-size: 1.5rem;
    font-weight: 700;
    color: #ffffff;
}

.stat-label {
    font-size: 0.72rem;
    color: #4a6080;
    letter-spacing: 1px;
    text-transform: uppercase;
}

.main-area {
    padding: 60px 80px;
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 40px;
    min-height: 60vh;
}

.upload-zone {
    background: #0d1422;
    border: 1px solid #1a2744;
    border-radius: 16px;
    padding: 40px;
    display: flex;
    flex-direction: column;
    gap: 24px;
}

.zone-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.7rem;
    letter-spacing: 2px;
    text-transform: uppercase;
    color: #0066ff;
}

.results-zone {
    background: #0d1422;
    border: 1px solid #1a2744;
    border-radius: 16px;
    padding: 40px;
}

.result-item {
    padding: 20px 0;
    border-bottom: 1px solid #1a2744;
}

.result-item:last-child { border-bottom: none; }

.result-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 12px;
}

.result-name {
    font-size: 1.1rem;
    font-weight: 600;
    color: #e8eaf0;
}

.result-pct {
    font-family: 'Space Mono', monospace;
    font-size: 0.85rem;
    font-weight: 700;
}

.bar-track {
    height: 4px;
    background: #1a2744;
    border-radius: 2px;
    overflow: hidden;
}

.bar-fill {
    height: 100%;
    border-radius: 2px;
    transition: width 1s ease;
}

.rank-badge {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 3px 8px;
    border-radius: 4px;
    margin-right: 10px;
}

.empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 100%;
    gap: 16px;
    color: #2a3a54;
    text-align: center;
}

.empty-icon {
    font-size: 3rem;
    opacity: 0.3;
}

.empty-text {
    font-size: 0.85rem;
    color: #2a3a54;
    font-family: 'Space Mono', monospace;
    letter-spacing: 1px;
}

.bottom-bar {
    padding: 24px 80px;
    border-top: 1px solid #1a2744;
    display: flex;
    justify-content: space-between;
    align-items: center;
}

.bottom-left {
    font-size: 0.75rem;
    color: #2a3a54;
    font-family: 'Space Mono', monospace;
}

.bottom-right {
    display: flex;
    gap: 24px;
}

.bottom-tag {
    font-size: 0.7rem;
    color: #2a3a54;
    font-family: 'Space Mono', monospace;
    letter-spacing: 1px;
}

/* Streamlit overrides */
.stFileUploader {
    background: transparent !important;
}
.stFileUploader > div {
    background: #080c14 !important;
    border: 1px dashed #1a2744 !important;
    border-radius: 12px !important;
    color: #4a6080 !important;
}
.stFileUploader label { color: #4a6080 !important; }
.stImage img { border-radius: 12px !important; }
.stSpinner { color: #0066ff !important; }
div[data-testid="stImage"] img { border-radius: 12px; }
</style>
""", unsafe_allow_html=True)

# HERO
st.markdown("""
<div class="hero">
    <div class="nav">
        <div class="logo">Object<span>Vision</span></div>
        <div class="nav-tags">
            <div class="nav-tag">MobileNetV2</div>
            <div class="nav-tag">PyTorch</div>
            <div class="nav-tag">ImageNet</div>
        </div>
    </div>
    <div class="hero-title">Visión artificial<br>que <em>entiende</em><br>tu mundo.</div>
    <div class="hero-sub">Sube cualquier imagen y nuestra IA identifica los objetos al instante con datos de confianza en tiempo real.</div>
    <div class="stats-bar">
        <div class="stat">
            <div class="stat-number">1000+</div>
            <div class="stat-label">Clases reconocibles</div>
        </div>
        <div class="stat">
            <div class="stat-number">Top-3</div>
            <div class="stat-label">Predicciones</div>
        </div>
        <div class="stat">
            <div class="stat-number">Cloud</div>
            <div class="stat-label">Servidor remoto</div>
        </div>
        <div class="stat">
            <div class="stat-number">24/7</div>
            <div class="stat-label">Disponibilidad</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Modelo
@st.cache_resource
def cargar_modelo():
    m = models.mobilenet_v2(weights="IMAGENET1K_V1")
    m.eval()
    return m

@st.cache_data
def cargar_etiquetas():
    url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"
    with urllib.request.urlopen(url) as f:
        return json.load(f)

modelo = cargar_modelo()
etiquetas = cargar_etiquetas()

transformacion = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225])
])

TRADUCCIONES = {
    "car": "Coche", "sports car": "Coche deportivo", "convertible": "Descapotable",
    "dog": "Perro", "cat": "Gato", "bird": "Pájaro", "labrador retriever": "Labrador Retriever",
    "golden retriever": "Golden Retriever", "pizza": "Pizza", "hamburger": "Hamburguesa",
    "banana": "Plátano", "apple": "Manzana", "chair": "Silla", "laptop": "Portátil",
    "bicycle": "Bicicleta", "motorcycle": "Moto", "bus": "Autobús", "truck": "Camión",
    "airplane": "Avión", "lion": "León", "tiger": "Tigre", "elephant": "Elefante",
    "soccer ball": "Balón de fútbol", "keyboard": "Teclado", "bottle": "Botella",
    "cup": "Taza", "book": "Libro", "clock": "Reloj", "horse": "Caballo",
    "kuvasz": "Kuvasz", "chesapeake bay retriever": "Chesapeake Bay Retriever",
    "shield": "Escudo", "computer mouse": "Ratón de ordenador"
}

def traducir(n):
    return TRADUCCIONES.get(n.lower().replace("_", " "), n.replace("_", " ").title())

# MAIN
col_upload, col_results = st.columns(2, gap="large")

with col_upload:
    st.markdown('<div style="padding: 60px 0 0 80px;">', unsafe_allow_html=True)
    st.markdown('<div class="zone-label">— Entrada</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)
    archivo = st.file_uploader("", type=["jpg", "jpeg", "png"], label_visibility="collapsed")
    if archivo:
        imagen = Image.open(archivo).convert("RGB")
        st.image(imagen, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

with col_results:
    st.markdown('<div style="padding: 60px 80px 0 0;">', unsafe_allow_html=True)
    st.markdown('<div class="zone-label">— Análisis</div>', unsafe_allow_html=True)
    st.markdown('<div style="height:16px"></div>', unsafe_allow_html=True)

    if archivo:
        tensor = transformacion(imagen).unsqueeze(0)
        with st.spinner("Procesando..."):
            with torch.no_grad():
                salida = modelo(tensor)
            probs = torch.nn.functional.softmax(salida[0], dim=0)
            top3 = torch.topk(probs, 3)

        ranks = ["01", "02", "03"]
        badge_colors = ["#0066ff", "#00d4aa", "#6644ff"]
        bar_colors = ["#0066ff", "#00d4aa", "#6644ff"]
        pct_colors = ["#0066ff", "#00d4aa", "#6644ff"]

        for i in range(3):
            nombre = traducir(etiquetas[top3.indices[i].item()])
            prob = top3.values[i].item()
            pct = prob * 100
            nivel = "Alta" if prob >= 0.6 else "Media" if prob >= 0.3 else "Baja"

            st.markdown(f"""
            <div class="result-item">
                <div class="result-header">
                    <div style="display:flex;align-items:center">
                        <span class="rank-badge" style="background:{badge_colors[i]}22;color:{badge_colors[i]};border:1px solid {badge_colors[i]}44">#{ranks[i]}</span>
                        <span class="result-name">{nombre}</span>
                    </div>
                    <span class="result-pct" style="color:{pct_colors[i]}">{pct:.1f}%</span>
                </div>
                <div class="bar-track">
                    <div class="bar-fill" style="width:{pct}%;background:{bar_colors[i]}"></div>
                </div>
                <div style="margin-top:6px;font-size:0.7rem;color:#2a3a54;font-family:'Space Mono',monospace;letter-spacing:1px">CONFIANZA {nivel.upper()}</div>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div class="empty-state" style="min-height:300px">
            <div class="empty-icon">⬡</div>
            <div class="empty-text">Esperando imagen...</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# FOOTER
st.markdown("""
<div class="bottom-bar">
    <div class="bottom-left">© 2026 ObjectVision · Mohamed Mohamed Embarec · Proyecto Intermodular</div>
    <div class="bottom-right">
        <span class="bottom-tag">ODS 4</span>
        <span class="bottom-tag">ODS 9</span>
        <span class="bottom-tag">PyTorch + Streamlit</span>
    </div>
</div>
""", unsafe_allow_html=True)