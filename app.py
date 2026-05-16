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

st.markdown("""
    <style>
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

# Traducciones español
TRADUCCIONES = {
    "car": "Coche", "sports car": "Coche deportivo", "convertible": "Descapotable",
    "dog": "Perro", "cat": "Gato", "bird": "Pájaro", "fish": "Pez",
    "labrador retriever": "Labrador Retriever", "golden retriever": "Golden Retriever",
    "pizza": "Pizza", "hamburger": "Hamburguesa", "hot dog": "Perrito caliente",
    "banana": "Plátano", "apple": "Manzana", "orange": "Naranja",
    "chair": "Silla", "table": "Mesa", "laptop": "Portátil", "phone": "Teléfono",
    "bicycle": "Bicicleta", "motorcycle": "Moto", "bus": "Autobús", "truck": "Camión",
    "airplane": "Avión", "boat": "Barco", "train": "Tren",
    "lion": "León", "tiger": "Tigre", "elephant": "Elefante", "bear": "Oso",
    "zebra": "Cebra", "giraffe": "Jirafa", "horse": "Caballo", "cow": "Vaca",
    "sheep": "Oveja", "rabbit": "Conejo", "mouse": "Ratón",
    "cup": "Taza", "bottle": "Botella", "book": "Libro", "clock": "Reloj",
    "keyboard": "Teclado", "computer mouse": "Ratón de ordenador",
    "shield": "Escudo", "soccer ball": "Balón de fútbol",
    "kuvasz": "Kuvasz (raza de perro)", "chesapeake bay retriever": "Chesapeake Bay Retriever"
}

MENSAJES = {
    "perro": "🐶 ¡Es un perro! Los perros son los animales más leales del mundo.",
    "gato": "🐱 ¡Es un gato! Los gatos duermen hasta 16 horas al día.",
    "coche": "🚗 ¡Es un coche! Los primeros coches apenas llegaban a 15 km/h.",
    "pizza": "🍕 ¡Es una pizza! La pizza más cara del mundo cuesta más de 12.000€.",
    "avión": "✈️ ¡Es un avión! Volar es el medio de transporte más seguro del mundo.",
    "león": "🦁 ¡Es un león! El rugido de un león se escucha a 8 km de distancia.",
}

def traducir(nombre_ingles):
    nombre_lower = nombre_ingles.lower().replace("_", " ")
    return TRADUCCIONES.get(nombre_lower, nombre_ingles.replace("_", " ").title())

def color_barra(prob):
    if prob >= 0.6:
        return "verde"
    elif prob >= 0.3:
        return "amarillo"
    else:
        return "rojo"

def mensaje_curioso(nombre_es):
    for clave, msg in MENSAJES.items():
        if clave in nombre_es.lower():
            return msg
    return None

# Inicializar contador
if "contador" not in st.session_state:
    st.session_state.contador = 0

# Sidebar
with st.sidebar:
    st.markdown("## 🔍 ObjectVision")
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
    st.metric("📸 Imágenes analizadas", st.session_state.contador)
    st.markdown("---")
    st.markdown("**ODS 4** — Educación de calidad")
    st.markdown("**ODS 9** — Innovación e infraestructura")
    st.markdown("---")
    st.caption("Proyecto Intermodular 2025/2026")
    st.caption("Mohamed Mohamed Embarec")

# Título
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

    st.session_state.contador += 1

    with col2:
        st.markdown('<div class="result-box">', unsafe_allow_html=True)
        st.subheader("📊 Resultados del análisis")
        st.markdown("---")

        colores_emoji = ["🥇", "🥈", "🥉"]
        primer_nombre = None

        for i in range(3):
            nombre_en = etiquetas[top3.indices[i].item()]
            nombre_es = traducir(nombre_en)
            prob = top3.values[i].item()
            nivel = color_barra(prob)

            if i == 0:
                primer_nombre = nombre_es

            if nivel == "verde":
                color_hex = "#28a745"
                etiqueta_nivel = "✅ Alta confianza"
            elif nivel == "amarillo":
                color_hex = "#ffc107"
                etiqueta_nivel = "⚠️ Confianza media"
            else:
                color_hex = "#dc3545"
                etiqueta_nivel = "❌ Confianza baja"

            st.markdown(f"#### {colores_emoji[i]} {nombre_es}")
            st.markdown(
                f'<div style="background:{color_hex};height:18px;width:{int(prob*100)}%;border-radius:8px;margin-bottom:4px"></div>',
                unsafe_allow_html=True
            )
            st.caption(f"Confianza: {prob*100:.2f}% · {etiqueta_nivel}")

            if i < 2:
                st.markdown("---")

        st.markdown('</div>', unsafe_allow_html=True)

        # Dato curioso
        if primer_nombre:
            msg = mensaje_curioso(primer_nombre)
            if msg:
                st.info(msg)

else:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.info("⬆️ Sube una imagen en el recuadro de arriba para que la IA la analice.")

st.markdown('<div class="footer">ObjectVision © 2026 · Proyecto Educativo de IA · Desarrollado con Streamlit y PyTorch</div>', unsafe_allow_html=True)