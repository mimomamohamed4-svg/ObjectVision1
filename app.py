# =========================================================
# OBJECTVISION AI — VERSION PROFESIONAL MODULAR
# Streamlit + PyTorch + Seguridad + UI Premium
# =========================================================

import streamlit as st
from PIL import Image
import torch
from torchvision import models, transforms
import urllib.request
import json
import hashlib
import time
import io
import base64
from datetime import datetime

# =========================================================
# CONFIGURACIÓN
# =========================================================

st.set_page_config(
    page_title="ObjectVision AI",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# CSS PREMIUM
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&display=swap');

html, body, .stApp {
    background: #070b12;
    color: white;
    font-family: 'Sora', sans-serif;
}

header, footer {
    display:none;
}

.block-container {
    padding-top:0rem;
    padding-bottom:0rem;
    max-width:100%;
}

[data-testid="stSidebar"] {
    display:none;
}

.hero {
    padding: 60px;
    background: linear-gradient(135deg,#08101c,#0d1828);
    border-bottom:1px solid #1a2744;
}

.hero-title {
    font-size:4rem;
    font-weight:700;
    line-height:1.1;
    max-width:700px;
}

.hero-title span {
    color:#0066ff;
}

.hero-sub {
    color:#7c8aa5;
    margin-top:15px;
    font-size:1.1rem;
}

.card {
    background:#0d1422;
    border:1px solid #1a2744;
    border-radius:18px;
    padding:25px;
}

.zone {
    font-size:0.8rem;
    color:#0066ff;
    letter-spacing:2px;
    margin-bottom:20px;
    text-transform:uppercase;
}

.result-box {
    background:#10192a;
    border:1px solid #1a2744;
    border-radius:14px;
    padding:18px;
    margin-bottom:15px;
}

.bar {
    height:8px;
    border-radius:10px;
    background:#1a2744;
    overflow:hidden;
    margin-top:8px;
}

.fill {
    height:100%;
    border-radius:10px;
    background:linear-gradient(90deg,#0066ff,#00d4aa);
}

.admin-table {
    width:100%;
    border-collapse:collapse;
}

.admin-table th {
    background:#111c30;
    color:#0066ff;
    padding:14px;
    text-align:left;
}

.admin-table td {
    padding:14px;
    border-bottom:1px solid #1a2744;
}

.stButton button {
    width:100%;
    background:#0066ff;
    color:white;
    border:none;
    border-radius:10px;
    padding:12px;
    font-weight:600;
}

.stButton button:hover {
    background:#0050d4;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SEGURIDAD
# =========================================================

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# =========================================================
# BASE DE DATOS SIMPLE
# =========================================================

if "users" not in st.session_state:
    st.session_state.users = {
        "mohamed": {
            "password": hash_password("admin2026"),
            "role": "ADMIN"
        },
        "invitado": {
            "password": hash_password("1234"),
            "role": "CLIENTE"
        }
    }

if "logged" not in st.session_state:
    st.session_state.logged = False

if "role" not in st.session_state:
    st.session_state.role = ""

if "history" not in st.session_state:
    st.session_state.history = []

# =========================================================
# LOGIN
# =========================================================

if not st.session_state.logged:

    st.markdown("""
    <div class="hero">
        <div class="hero-title">
            Object<span>Vision</span> AI
        </div>
        <div class="hero-sub">
            Plataforma profesional de visión artificial.
        </div>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1,2,1])

    with col2:

        st.markdown("<br>", unsafe_allow_html=True)

        with st.container(border=True):

            st.subheader("🔐 Iniciar sesión")

            user = st.text_input("Usuario")
            password = st.text_input("Contraseña", type="password")

            if st.button("ACCEDER"):

                if user in st.session_state.users:

                    saved = st.session_state.users[user]["password"]

                    if saved == hash_password(password):

                        st.session_state.logged = True
                        st.session_state.role = st.session_state.users[user]["role"]

                        st.success("Acceso autorizado")

                        time.sleep(1)

                        st.rerun()

                st.error("Credenciales incorrectas")

    st.stop()

# =========================================================
# NAVBAR
# =========================================================

col1, col2, col3 = st.columns([2,4,1])

with col1:
    st.markdown("## Object<span style='color:#0066ff'>Vision</span>", unsafe_allow_html=True)

with col2:
    st.caption("MobileNetV2 • PyTorch • ImageNet")

with col3:
    if st.button("SALIR"):
        st.session_state.logged = False
        st.rerun()

# =========================================================
# HERO
# =========================================================

st.markdown("""
<div class="hero">
    <div class="hero-title">
        Visión artificial que <span>entiende</span> tu mundo.
    </div>

    <div class="hero-sub">
        Analiza imágenes usando inteligencia artificial en tiempo real.
    </div>
</div>
""", unsafe_allow_html=True)

# =========================================================
# CARGA MODELO
# =========================================================

@st.cache_resource
def load_model():
    model = models.mobilenet_v2(weights="IMAGENET1K_V1")
    model.eval()
    return model

@st.cache_data
def load_labels():

    url = "https://raw.githubusercontent.com/anishathalye/imagenet-simple-labels/master/imagenet-simple-labels.json"

    with urllib.request.urlopen(url) as f:
        return json.load(f)

model = load_model()
labels = load_labels()

transform = transforms.Compose([
    transforms.Resize((224,224)),
    transforms.ToTensor(),
    transforms.Normalize([0.485,0.456,0.406],[0.229,0.224,0.225])
])

# =========================================================
# IA
# =========================================================

def predict(image):

    tensor = transform(image).unsqueeze(0)

    with torch.no_grad():
        output = model(tensor)

    probs = torch.nn.functional.softmax(output[0], dim=0)

    return torch.topk(probs, 3)

# =========================================================
# TABS
# =========================================================

tabs = ["🔍 Analizar", "📷 Cámara", "🕓 Historial"]

if st.session_state.role == "ADMIN":
    tabs.append("👑 Admin")

tab_objects = st.tabs(tabs)

# =========================================================
# TAB ANALIZAR
# =========================================================

with tab_objects[0]:

    st.markdown("<br>", unsafe_allow_html=True)

    col1, col2 = st.columns(2)

    with col1:

        st.markdown('<div class="zone">ENTRADA</div>', unsafe_allow_html=True)

        file = st.file_uploader(
            "Sube imagen",
            type=["jpg","jpeg","png"]
        )

        if file:
            image = Image.open(file).convert("RGB")
            st.image(image, use_container_width=True)

    with col2:

        st.markdown('<div class="zone">ANÁLISIS</div>', unsafe_allow_html=True)

        if file:

            with st.spinner("Procesando IA..."):

                start = time.time()

                top3 = predict(image)

                end = time.time()

                inference = (end-start)*1000

            st.success(f"Inferencia completada en {inference:.0f} ms")

            for i in range(3):

                idx = top3.indices[i].item()

                prob = top3.values[i].item() * 100

                label = labels[idx]

                st.markdown(f"""
                <div class="result-box">

                    <div style="
                        display:flex;
                        justify-content:space-between;
                    ">

                        <b>{label}</b>

                        <span>{prob:.1f}%</span>

                    </div>

                    <div class="bar">
                        <div class="fill" style="width:{prob}%"></div>
                    </div>

                </div>
                """, unsafe_allow_html=True)

            # GUARDAR HISTORIAL

            buffer = io.BytesIO()
            image.save(buffer, format="JPEG")

            img64 = base64.b64encode(buffer.getvalue()).decode()

            st.session_state.history.insert(0,{
                "name": labels[top3.indices[0].item()],
                "prob": top3.values[0].item()*100,
                "img": img64,
                "time": datetime.now().strftime("%H:%M")
            })

            st.session_state.history = st.session_state.history[:10]

# =========================================================
# TAB CÁMARA
# =========================================================

with tab_objects[1]:

    st.markdown("<br>", unsafe_allow_html=True)

    cam = st.camera_input("Captura imagen")

    if cam:

        img = Image.open(cam).convert("RGB")

        st.image(img, width=400)

        top3 = predict(img)

        st.success(
            f"Objeto detectado: {labels[top3.indices[0].item()]}"
        )

# =========================================================
# TAB HISTORIAL
# =========================================================

with tab_objects[2]:

    st.markdown("<br>", unsafe_allow_html=True)

    if len(st.session_state.history) == 0:

        st.info("Sin análisis todavía")

    else:

        for item in st.session_state.history:

            st.markdown(f"""
            <div class="card">

                <div style="
                    display:flex;
                    gap:20px;
                    align-items:center;
                ">

                    <img src="data:image/jpeg;base64,{item['img']}"
                    width="90"
                    style="border-radius:12px;" />

                    <div>

                        <h4>{item['name']}</h4>

                        <div style="color:#7c8aa5">
                            {item['prob']:.1f}% · {item['time']}
                        </div>

                    </div>

                </div>

            </div>

            <br>
            """, unsafe_allow_html=True)

# =========================================================
# PANEL ADMIN
# =========================================================

if st.session_state.role == "ADMIN":

    with tab_objects[3]:

        st.markdown("<br>", unsafe_allow_html=True)

        st.subheader("👑 Panel Administración")

        html = """
        <table class="admin-table">

        <tr>
            <th>Usuario</th>
            <th>Hash</th>
            <th>Rol</th>
        </tr>
        """

        for user, data in st.session_state.users.items():

            short_hash = data["password"][:15] + "..."

            html += f"""
            <tr>
                <td>{user}</td>
                <td>{short_hash}</td>
                <td>{data['role']}</td>
            </tr>
            """

        html += "</table>"

        st.markdown(html, unsafe_allow_html=True)

# =========================================================
# FOOTER
# =========================================================

st.markdown("<br><br>", unsafe_allow_html=True)

st.markdown("""
<div style="
padding:30px;
border-top:1px solid #1a2744;
text-align:center;
color:#6d7a95;
">

© 2026 ObjectVision AI · Mohamed Mohamed Embarec

</div>
""", unsafe_allow_html=True)