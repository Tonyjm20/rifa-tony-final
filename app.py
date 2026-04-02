import streamlit as st
import pandas as pd
import random
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Rifa Tony AFK - Panel Pro", layout="wide")

# Tus credenciales
LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
CLAVE_ADMIN = "tonyjm20"

# --- FUNCIÓN DE LECTURA SIMPLE (LA ORIGINAL) ---
def leer_datos():
    # Limpiamos la caché de Streamlit para forzar lectura nueva
    st.cache_data.clear()
    try:
        # Añadimos un pequeño truco al link para que Google no se quede pegado
        url_fresca = f"{LINK_CSV}&t={int(time.time())}"
        df = pd.read_csv(url_fresca)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

# --- MANEJO DE SESIÓN (PARA NO PEDIR CLAVE CADA VEZ) ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# --- NAVEGACIÓN ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

if es_seguidor:
    # --- VISTA SEGUIDOR ---
    st.title("🎟️ Registro para el Sorteo")
    # (Aquí mantén tu bloque de PayPal y formulario que ya tienes)
else:
    # --- VISTA ADMIN ---
    if not st.session_state['auth']:
        st.sidebar.title("🔐 Acceso Admin")
        pw = st.sidebar.text_input("Clave", type="password")
        if st.sidebar.button("Entrar"):
            if pw == CLAVE_ADMIN:
                st.session_state['auth'] = True
                st.rerun()
            else:
                st.error("Clave incorrecta")
    else:
        # --- PANEL DE CONTROL ---
        st.title("📺 Panel de Transmisión")
        
        # Barra lateral con controles
        st.sidebar.header("⚙️ Controles")
        meta = st.sidebar.number_input("Meta de Sorteo", min_value=1, value=50)
        
        # BOTÓN DE ACTUALIZAR (Este refresca sin pedir clave)
        if st.sidebar.button("🔄 ACTUALIZAR LISTA", type="primary", use_container_width=True):
            st.rerun()

        st.sidebar.divider()
        btn_sorteo = st.sidebar.button("🎰 REALIZAR SORTEO", use_container_width=True)

        # Cargar los datos
        df = leer_datos()
        total = len(df)
        
        # BARRA DE PROGRESO
        st.progress(min(total / meta, 1.0))
        st.subheader(f"📊 Participantes: {total} / {meta}")
        
        st.divider()
        
        if not df.empty:
            # Lista de participantes
            for index, row in df.iterrows():
                st.markdown(f"### **{index + 1}. {row['Nombre']} {row['Apellido']}** — ✅")
            
            # Botón de Sorteo
            if btn_sorteo:
                ganador = random.choice(df['Nombre'].tolist())
                st.balloons()
                st.success(f"🎊 ¡TENEMOS UN GANADOR! 🎊")
                st.title(f"🏆 {ganador.upper()} 🏆")
        else:
            st.info("Lista vacía. Pulsa 'Actualizar Lista' cuando haya nuevos registros.")

        if st.sidebar.button("Cerrar Sesión"):
            st.session_state['auth'] = False
            st.rerun()
