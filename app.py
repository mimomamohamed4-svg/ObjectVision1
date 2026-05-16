import streamlit as st
from PIL import Image
import torch
from torchvision import models, transforms
import urllib.request
import json

st.set_page_config(
    page_title="ObjectVision",
    page_icon="🔍",
    layout="wide"
)

# Estilo CSS personalizado
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    .title { 
        font-size: 2.5em; 
        font-weight: bold; 
        color: #1a1a2e;
        text-align: center;
        padding: 20px 0 5px 0;
    }
    .subtitle {
        text-align: center;
        color: #555;
        font-size: 1.1em;
        margin-bottom: 30px;
    }
    .result-box {
        background-color: white;
        border-radius: 12px;
        padding: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.08);
    }
    .footer {
        text-align: center;
        color: #aaa;
        font-size: 0.85em;
        margin-top: 40px;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/1/10/PyTorch_logo_icon.svg/496px-PyTorch_logo_icon.svg.png", width=60)
    st.markdown("## ⚙️ ObjectVision")
    st.markdown("---")
    st.markdown("**Modelo:** MobileNetV2")
    st.markdown("**Framework:** PyTorch")
    st.markdown("**Dataset:** ImageNet (1000 clases)")
    st.markdown("---")
    st.markdown("### ¿Cómo funciona?")
    st.markdown("1. Sube una imagen 📤")
    st.markdown("2. La IA la analiza 🧠")
    st.markdown("3. Ver los resultados 📊")
    st.markdown("---")
    st.markdown("### Formatos aceptados")
    st.markdown("JPG · JPEG · PNG")
    st.markdown("---")
    st.markdown("**ODS 4** — Educación de calidad")
    st.markdown("**ODS 9** — Innovación e infraestructura")
    st.markdown("---")
    st.caption("Proyecto Intermodular 2025/2026")
    st.caption("Mohamed Mohamed Embarec")

# Título principal
st.markdown('<div class="title">🔍 ObjectVision</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Reconocimiento de objetos con Inteligencia Artificial</div>', unsafe_allow_html=True)
st.markdown("---")

@st.cache_resource
def cargar_modelo():
    modelo = models.mobilenet_v2(weights="IMAGENET1K_V1")
    modelo.eval()
    return modelo

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

archivo = st.file_uploader("📁 Sube una imagen para analizar", type=["jpg", "jpeg", "png"])

if archivo is not None:
    imagen = Image.open(archivo).convert("RGB")
    col1, col2 = st.columns([1, 1], gap="large")

    with col1:
        st.image(imagen, caption="Imagen subida", use_container_width=True)

    tensor = transformacion(imagen).unsqueeze(0)

    with st.spinner("🧠 Analizando con IA..."):
        with torch.no_grad():
            salida = modelo(tensor)
        probabilidades = torch.nn.functional.softmax(salida[0], dim=0)
        top3 = torch.topk(probabilidades, 3)

    with col2:
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.subheader("📊 Resultados del análisis")
        st.markdown("---")

        colores = ["🥇", "🥈", "🥉"]
        for i in range(3):
            nombre = etiquetas[top3.indices[i].item()].replace("_", " ").title()
            prob = top3.values[i].item()
            st.markdown(f"#### {colores[i]} {nombre}")
            st.progress(float(prob))
            st.caption(f"Confianza: {prob*100:.2f}%")
            if i < 2:
                st.markdown("---")

        st.markdown('</div>', unsafe_allow_html=True)

else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("⬆️ Sube una imagen en el recuadro de arriba para que la IA la analice.")

st.markdown('<div class="footer">ObjectVision © 2026 · Proyecto Educativo de IA · Desarrollado con Streamlit y PyTorch</div>', unsafe_allow_html=True)