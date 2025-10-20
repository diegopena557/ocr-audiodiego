import streamlit as st
import os
import time
import glob
import cv2
import numpy as np
import pytesseract
from PIL import Image
from gtts import gTTS
from googletrans import Translator


text = " "

# --- NUEVA FUNCIÓN ---
def mostrar_mensaje_interesante():
    """
    Muestra un pequeño mensaje animado o de transición antes de desplegar el texto reconocido.
    """
    mensaje = "💡 Interesante... veamos qué dice 👀"
    st.info(mensaje)
    time.sleep(1.5)  # Pausa breve para dar efecto


# --- FUNCIÓN PARA CONVERTIR TEXTO A AUDIO ---
def text_to_speech(input_language, output_language, text, tld):
    translation = translator.translate(text, src=input_language, dest=output_language)
    trans_text = translation.text
    tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
    try:
        my_file_name = text[0:20]
    except:
        my_file_name = "audio"
    tts.save(f"temp/{my_file_name}.mp3")
    return my_file_name, trans_text


# --- FUNCIÓN PARA LIMPIAR ARCHIVOS ANTIGUOS ---
def remove_files(n):
    mp3_files = glob.glob("temp/*mp3")
    if len(mp3_files) != 0:
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)
                print("Deleted ", f)


remove_files(7)


# --- INTERFAZ PRINCIPAL ---
st.title("🧠 Reconocimiento Óptico de Caracteres (OCR)")
st.subheader("Elige la fuente de la imagen: cámara o archivo")

cam_ = st.checkbox("Usar Cámara")

if cam_:
    img_file_buffer = st.camera_input("📸 Toma una Foto")
else:
    img_file_buffer = None

with st.sidebar:
    st.subheader("⚙️ Procesamiento para Cámara")
    filtro = st.radio("Filtro para imagen con cámara", ('Sí', 'No'))


# --- CARGAR IMAGEN DESDE ARCHIVO ---
bg_image = st.file_uploader("📂 Cargar Imagen:", type=["png", "jpg", "jpeg"])
if bg_image is not None:
    uploaded_file = bg_image
    st.image(uploaded_file, caption='📸 Imagen cargada.', use_container_width=True)
    
    # Guardar la imagen localmente
    with open(uploaded_file.name, 'wb') as f:
        f.write(uploaded_file.read())
    
    st.success(f"✅ Imagen guardada como {uploaded_file.name}")
    img_cv = cv2.imread(f'{uploaded_file.name}')
    img_rgb = cv2.cvtColor(img_cv, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

    if text and len(text.strip()) > 0:
        mostrar_mensaje_interesante()
        st.subheader("📄 Texto detectado:")
        st.write(text)


# --- CAPTURA DESDE CÁMARA ---
if img_file_buffer is not None:
    bytes_data = img_file_buffer.getvalue()
    cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

    if filtro == 'Sí':
        cv2_img = cv2.bitwise_not(cv2_img)

    img_rgb = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
    text = pytesseract.image_to_string(img_rgb)

    if text and len(text.strip()) > 0:
        mostrar_mensaje_interesante()
        st.subheader("📄 Texto detectado:")
        st.write(text)


# --- CONFIGURACIÓN DE TRADUCCIÓN ---
with st.sidebar:
    st.subheader("🌍 Parámetros de traducción")
    
    try:
        os.mkdir("temp")
    except:
        pass

    translator = Translator()

    in_lang = st.selectbox(
        "Seleccione el lenguaje de entrada",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"),
    )
    lang_dict = {
        "Inglés": "en",
        "Español": "es",
        "Bengali": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja"
    }
    input_language = lang_dict[in_lang]

    out_lang = st.selectbox(
        "Seleccione el lenguaje de salida",
        ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"),
    )
    output_language = lang_dict[out_lang]

    english_accent = st.selectbox(
        "Seleccione el acento",
        (
            "Default",
            "India",
            "United Kingdom",
            "United States",
            "Canada",
            "Australia",
            "Ireland",
            "South Africa",
        ),
    )

    tld_map = {
        "Default": "com",
        "India": "co.in",
        "United Kingdom": "co.uk",
        "United States": "com",
        "Canada": "ca",
        "Australia": "com.au",
        "Ireland": "ie",
        "South Africa": "co.za",
    }
    tld = tld_map[english_accent]

    display_output_text = st.checkbox("Mostrar texto traducido")

    if st.button("🔊 Convertir texto a audio"):
        if text.strip() == "":
            st.warning("⚠️ Primero carga o toma una imagen con texto.")
        else:
            result, output_text = text_to_speech(input_language, output_language, text, tld)
            audio_file = open(f"temp/{result}.mp3", "rb")
            audio_bytes = audio_file.read()
            st.markdown("## 🎧 Tu audio generado:")
            st.audio(audio_bytes, format="audio/mp3", start_time=0)
        
            if display_output_text:
                st.markdown("## 📝 Texto traducido:")
                st.write(output_text)

 
    
    
