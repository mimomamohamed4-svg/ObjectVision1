import streamlit as st
import tensorflow as tf
from PIL import Image
import numpy as np

st.set_page_config(page_title="ObjectVision", layout="wide")
st.title("🔍 ObjectVision — Reconocimiento de objetos con IA")
st.markdown("Sube una imagen y la inteligencia artificial identificará qué hay en ella.")

@st.cache_resource
def cargar_modelo():
    return tf.keras.applications.MobileNetV2(weights="imagenet")

modelo = cargar_modelo()

archivo = st.file_uploader("📁 Sube una imagen (JPG o PNG)", type=["jpg", "jpeg", "png"])

if archivo is not None:
    imagen = Image.open(archivo).convert("RGB")
    col1, col2 = st.columns(2)

    with col1:
        st.image(imagen, caption="Imagen subida", use_container_width=True)

    img_resized = imagen.resize((224, 224))
    img_array = np.array(img_resized)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = tf.keras.applications.mobilenet_v2.preprocess_input(img_array)

    with st.spinner("La IA está analizando tu imagen..."):
        predicciones = modelo.predict(img_array)
        resultados = tf.keras.applications.mobilenet_v2.decode_predictions(predicciones, top=3)[0]

    with col2:
        st.subheader("Resultados:")
        for i, (id_clase, nombre, prob) in enumerate(resultados):
            nombre_limpio = nombre.replace("_", " ").title()
            st.write(f"**{i+1}. {nombre_limpio}**")
            st.progress(float(prob))
            st.caption(f"Confianza: {prob*100:.2f}%")
else:
    st.info("⬆️ Sube una imagen para empezar.")