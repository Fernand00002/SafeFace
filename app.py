import streamlit as st
import face_recognition
import numpy as np
from supabase import create_client
from PIL import Image
import uuid
import os
from dotenv import load_dotenv

# --- CARGAR VARIABLES DE ENTORNO ---
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# --- CONFIGURACIÓN DE PÁGINA Y TEMA ---
st.set_page_config(
    page_title="SafeFace - Plataforma Biométrica",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- INYECCIÓN DE CSS PARA DISEÑO PROFESIONAL ---
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .hero-header {
        background: linear-gradient(135deg, #0f2027, #203a43, #2c5364);
        padding: 2rem;
        border-radius: 15px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
    }
    .hero-header h1 {
        color: #ffffff !important;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .hero-header p {
        color: #e0e0e0;
        font-size: 1.1rem;
    }
    .badge-match {
        background-color: #28a745;
        color: white;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: bold;
        font-size: 0.9rem;
        display: inline-block;
        margin-bottom: 10px;
    }
    .stButton>button {
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    </style>
""", unsafe_allow_html=True)

# --- MANEJO DE SESIÓN PARA ADMINISTRADOR ---
if "autenticado" not in st.session_state:
    st.session_state["autenticado"] = False

# --- MENÚ LATERAL ---
with st.sidebar:
    st.image("https://cdn-icons-png.flaticon.com/512/1077/1077114.png", width=70)
    st.title("SafeFace System")
    st.caption("Sistema Biométrico de Búsqueda Humanitaria")
    st.divider()
    
    opcion = st.radio(
        "Navegación del Sistema:",
        ["📝 Registrar Desaparecido", "👁️ Búsqueda Biométrica", "📋 Base de Datos Privada"]
    )
    
    st.divider()
    if st.session_state["autenticado"]:
        st.success("🟢 Sesión de Administrador activa")
        if st.button("🚪 Cerrar Sesión Privada", use_container_width=True):
            st.session_state["autenticado"] = False
            st.rerun()
    else:
        st.info("🌐 Modo Público")

# ---------------------------------------------------------
# OPCIÓN 1: REGISTRO (PÚBLICO)
# ---------------------------------------------------------
if opcion == "📝 Registrar Desaparecido":
    st.markdown("""
        <div class="hero-header">
            <h1>📝 Módulo de Registro Biométrico</h1>
            <p>Incorpore nuevas fichas a la red de búsqueda SafeFace con análisis vectorial inmediato.</p>
        </div>
    """, unsafe_allow_html=True)
    
    col_form, col_info = st.columns([2, 1])
    
    with col_form:
        with st.container(border=True):
            st.subheader("📋 Datos Personales de la Ficha")
            with st.form("form_registro", clear_on_submit=True):
                nombre = st.text_input("Nombre Completo de la Persona", placeholder="Ej. Juan Carlos Pérez")
                fecha_nac = st.date_input("Fecha de Nacimiento")
                ultima_vez = st.text_input("Última vez visto/a", placeholder="Ej. San Salvador, Calle Principal - 12 de Octubre")
                contacto = st.text_input("Contacto de Emergencia", placeholder="Ej. +503 7000-0000 / Familia Pérez")
                foto = st.file_uploader("Fotografía Frontal Clara (JPG/PNG)", type=["jpg", "jpeg", "png"])
                
                btn_guardar = st.form_submit_button("💾 Guardar Ficha en SafeFace", use_container_width=True, type="primary")
                
                if btn_guardar:
                    if nombre and foto:
                        try:
                            imagen_pil = Image.open(foto)
                            imagen_np = np.array(imagen_pil)
                            encodings = face_recognition.face_encodings(imagen_np)
                            
                            if len(encodings) == 0:
                                st.error("❌ No se detectó ningún rostro en la imagen. Suba una foto donde el rostro esté claro.")
                            else:
                                vector = encodings[0].tolist()
                                foto_bytes = foto.getvalue()
                                nombre_limpio = "".join(c for c in nombre if c.isalnum())
                                nombre_archivo = f"{nombre_limpio}_{uuid.uuid4().hex[:6]}.jpg"
                                
                                supabase.storage.from_("fotos_desaparecidos").upload(
                                    file=foto_bytes,
                                    path=nombre_archivo,
                                    file_options={"content-type": "image/jpeg"}
                                )
                                foto_url = supabase.storage.from_("fotos_desaparecidos").get_public_url(nombre_archivo)
                                
                                datos = {
                                    "nombre": nombre,
                                    "fecha_nacimiento": str(fecha_nac),
                                    "ultima_vez_visto": ultima_vez,
                                    "contacto_emergencia": contacto,
                                    "foto_url": foto_url,
                                    "embedding": vector
                                }
                                supabase.table("personas").insert(datos).execute()
                                st.balloons()
                                st.success(f"✅ ¡Ficha biométrica de **{nombre}** registrada exitosamente!")
                        except Exception as e:
                            st.error(f"❌ Error al procesar el registro: {e}")
                    else:
                        st.warning("⚠️ Complete el nombre y adjunte una fotografía antes de continuar.")

    with col_info:
        with st.container(border=True):
            st.markdown("### 💡 Recomendaciones")
            st.write("• **Fotografía:** Iluminación uniforme y rostro centrado.")
            st.write("• **Evite:** Sombreros, lentes oscuros o filtros.")
            st.write("• **Sincronización:** El vector se codifica en 128 dimensiones matemáticas en tiempo real.")

# ---------------------------------------------------------
# OPCIÓN 2: BÚSQUEDA BIOMÉTRICA (PÚBLICO)
# ---------------------------------------------------------
elif opcion == "👁️ Búsqueda Biométrica":
    st.markdown("""
        <div class="hero-header">
            <h1>👁️ Reconocimiento e Identificación Biométrica</h1>
            <p>Escanee imágenes o use la cámara web para encontrar coincidencias vectoriales en la base de datos.</p>
        </div>
    """, unsafe_allow_html=True)
    
    modo = st.radio("Método de entrada:", ["Subir Imagen", "Cámara Web Instantánea"], horizontal=True)
    
    if modo == "Subir Imagen":
        c_input, c_result = st.columns([1, 1])
        with c_input:
            with st.container(border=True):
                st.subheader("📷 Cargar Fotografía")
                foto_busqueda = st.file_uploader("Adjunte la imagen a analizar", type=["jpg", "jpeg", "png"])
                if foto_busqueda:
                    imagen_pil = Image.open(foto_busqueda)
                    st.image(imagen_pil, caption="Imagen cargada", use_container_width=True)

        with c_result:
            with st.container(border=True):
                st.subheader("🔍 Resultados del Análisis")
                if foto_busqueda is not None:
                    if st.button("🚀 Iniciar Análisis Facial", use_container_width=True, type="primary"):
                        imagen_np = np.array(Image.open(foto_busqueda))
                        with st.spinner("Procesando vector biométrico y consultando Supabase..."):
                            vectores = face_recognition.face_encodings(imagen_np)
                            if len(vectores) > 0:
                                respuesta = supabase.rpc(
                                    "buscar_rostro",
                                    {"consulta": vectores[0].tolist(), "umbral": 0.4, "max_resultados": 1}
                                ).execute()
                                coincidencias = respuesta.data
                                if coincidencias:
                                    res = coincidencias[0]
                                    similitud = round(res['similitud'] * 100, 2)
                                    st.markdown(f'<div class="badge-match">🎯 Coincidencia Encontrada: {similitud}% Similitud</div>', unsafe_allow_html=True)
                                    st.progress(similitud / 100)
                                    
                                    # Consultar foto desde la tabla personas
                                    reg_db = supabase.table("personas").select("foto_url").eq("id", res["id"]).execute()
                                    foto_coincidente = reg_db.data[0]["foto_url"] if reg_db.data else ""
                                    
                                    col_img, col_txt = st.columns(2)
                                    with col_img:
                                        if foto_coincidente:
                                            st.image(foto_coincidente, caption="Registro Coincidente", use_container_width=True)
                                    with col_txt:
                                        st.markdown(f"**Nombre:**\n### {res['nombre']}")
                                        st.markdown(f"📍 **Última vez visto:**\n{res['ultima_vez_visto']}")
                                        st.markdown(f"📞 **Contacto:**\n{res['contacto_emergencia']}")
                                else:
                                    st.warning("⚠️ No se registraron coincidencias en la base de datos.")
                            else:
                                st.error("❌ No se detectó ningún rostro reconocible en la foto.")
                else:
                    st.info("Cargue una imagen para habilitar el análisis.")
    else:
        st.subheader("📸 Captura Rápida de Cámara Web")
        st.write("Colóquese frente a la cámara y tome la foto; el sistema realizará la búsqueda biométrica **al instante** automáticamente.")
        
        col_cam, col_res = st.columns([1, 1])
        
        with col_cam:
            with st.container(border=True):
                foto_camara = st.camera_input("Tomar fotografía en vivo")
                
        with col_res:
            with st.container(border=True):
                st.subheader("🎯 Resultado del Escaneo")
                if foto_camara is not None:
                    imagen_pil = Image.open(foto_camara)
                    imagen_np = np.array(imagen_pil)
                    
                    with st.spinner("Analizando vector biométrico en Supabase..."):
                        vectores = face_recognition.face_encodings(imagen_np)
                        
                        if len(vectores) > 0:
                            respuesta = supabase.rpc(
                                "buscar_rostro",
                                {"consulta": vectores[0].tolist(), "umbral": 0.4, "max_resultados": 1}
                            ).execute()
                            
                            coincidencias = respuesta.data
                            if coincidencias:
                                res = coincidencias[0]
                                similitud = round(res['similitud'] * 100, 2)
                                st.markdown(f'<div class="badge-match">🎯 MATCH: {similitud}%</div>', unsafe_allow_html=True)
                                
                                reg_db = supabase.table("personas").select("foto_url").eq("id", res["id"]).execute()
                                foto_coincidente = reg_db.data[0]["foto_url"] if reg_db.data else ""
                                
                                c_im, c_tx = st.columns(2)
                                with c_im:
                                    if foto_coincidente:
                                        st.image(foto_coincidente, caption="Registro Coincidente", use_container_width=True)
                                with c_tx:
                                    st.markdown(f"**Nombre:**\n### {res['nombre']}")
                                    st.markdown(f"📍 **Última vez visto/a:**\n{res['ultima_vez_visto']}")
                                    st.markdown(f"📞 **Contacto:**\n{res['contacto_emergencia']}")
                            else:
                                st.warning("⚠️ No se encontraron coincidencias en la base de datos.")
                        else:
                            st.error("❌ No se detectó ningún rostro claro. Verifique la iluminación.")
                else:
                    st.info("Tome una foto con la cámara para iniciar el análisis automático.")

# ---------------------------------------------------------
# OPCIÓN 3: BASE DE DATOS COMPLETA (PROTEGIDO)
# ---------------------------------------------------------
else:
    st.markdown("""
        <div class="hero-header">
            <h1>📋 Módulo de Administración de Datos</h1>
            <p>Acceso exclusivo para personal y autoridades autorizadas.</p>
        </div>
    """, unsafe_allow_html=True)
    
    if not st.session_state["autenticado"]:
        col_c, _ = st.columns([1, 1])
        with col_c:
            with st.container(border=True):
                st.subheader("🔒 Autenticación Requerida")
                usuario = st.text_input("Usuario")
                clave = st.text_input("Contraseña", type="password")
                
                if st.button("🔓 Iniciar Sesión", use_container_width=True, type="primary"):
                    if usuario == "admin" and clave == "safeface2026":
                        st.session_state["autenticado"] = True
                        st.success("Acceso concedido.")
                        st.rerun()
                    else:
                        st.error("❌ Credenciales incorrectas.")
    else:
        respuesta = supabase.table("personas").select("id, nombre, ultima_vez_visto, contacto_emergencia, foto_url").execute()
        
        m1, m2, m3 = st.columns(3)
        with m1:
            st.metric("Total Fichas Activas", len(respuesta.data) if respuesta.data else 0)
        with m2:
            st.metric("Estado del Algoritmo", "pgvector (Activo)")
        with m3:
            st.metric("Nivel de Tolerancia", "0.4 Threshold")
            
        st.divider()
        st.subheader("📑 Registros Almacenados")
        
        if respuesta.data:
            for persona in respuesta.data:
                with st.container():
                    c1, c2, c3 = st.columns([1, 3, 1])
                    with c1:
                        if persona["foto_url"]:
                            st.image(persona["foto_url"], width=110)
                    with c2:
                        st.markdown(f"### {persona['nombre']}")
                        st.write(f"📍 **Última vez visto/a:** {persona['ultima_vez_visto']}")
                        st.write(f"📞 **Contacto de Alerta:** {persona['contacto_emergencia']}")
                    with c3:
                        st.caption(f"ID Registro:\n`{persona['id'][:8]}...`")
                    st.divider()
        else:
            st.info("No hay registros en la base de datos.")