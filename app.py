import streamlit as st
from PIL import Image
import torch
from torchvision import models, transforms
import numpy as np
import urllib.request
import json

st.set_page_config(page_title="ObjectVision", layout="wide")
st.title("🔍 ObjectVision — Reconocimiento de objetos con IA")
st.markdown("Sube una imagen y la inteligencia artificial identificará qué hay en ella.")

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

archivo = st.file_uploader("📁 Sube una imagen (JPG o PNG)", type=["jpg", "jpeg", "png"])

if archivo is not None:
    imagen = Image.open(archivo).convert("RGB")
    col1, col2 = st.columns(2)

    with col1:
        st.image(imagen, caption="Imagen subida", use_container_width=True)

    tensor = transformacion(imagen).unsqueeze(0)

    with st.spinner("La IA está analizando..."):
        with torch.no_grad():
            salida = modelo(tensor)
        probabilidades = torch.nn.functional.softmax(salida[0], dim=0)
        top3 = torch.topk(probabilidades, 3)

    with col2:
        st.subheader("Resultados:")
        for i in range(3):
            nombre = etiquetas[top3.indices[i].item()].replace("_", " ").title()
            prob = top3.values[i].item()
            st.write(f"**{i+1}. {nombre}**")
            st.progress(float(prob))
            st.caption(f"Confianza: {prob*100:.2f}%")
else:
    st.info("⬆️ Sube una imagen para empezar.")