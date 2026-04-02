import streamlit as st
import pandas as pd
import random
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Rifa Tony AFK", layout="wide")

# Tus datos exactos
LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
CLAVE_ADMIN = "tonyjm20"
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl"

# --- FUNCIÓN DE LECTURA (LA QUE TE FUNCIONABA) ---
def leer_datos():
    # Limpiamos la memoria interna de Streamlit para que no use datos viejos
    st.cache_data.clear()
    try:
        # Añadimos un número aleatorio al final del link para "engañar" a Google 
        # y que nos dé el archivo más nuevo con los 4 registros.
        url_fresca = f"{LINK_CSV}&cache_buster={time.time()}"
        df = pd.read_csv(url_fresca)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

# --- MANEJO DE SESIÓN (PARA QUE NO TE PIDA CLAVE SIEMPRE) ---
if 'conectado' not in st.session_state:
    st.session_state['conectado'] = False

# --- NAVEGACIÓN ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

if es_seguidor:
    # --- VISTA SEGUIDOR ---
    st.title("🎟️ Registro y Pago")
    # [Aquí mantén tu bloque de formulario y PayPal de antes]
else:
    # --- VISTA ADMIN ---
    if not st.session_state['conectado']:
        st.sidebar.title("🔐 Acceso Admin")
        password = st.sidebar.text_input("Clave", type="password")
        if st.sidebar.button("Entrar"):
            if password == CLAVE_ADMIN:
                st.session_state['conectado'] = True
                st.rerun()
            else:
                st.error("Clave incorrecta")
    else:
        # --- PANEL DE TRANSMISIÓN ---
        st.title("📺 Panel de Control")
        
        # Controles en la barra lateral
        st.sidebar.header("⚙️ Controles")
        meta = st.sidebar.number_input("Meta de Sorteo", min_value=1, value=50)
        
        # EL BOTÓN QUE REFRESCARÁ LA LISTA SIN PEDIR CLAVE
        if st.sidebar.button("🔄 ACTUALIZAR LISTA", type="primary", use_container_width=True):
            st.rerun()

        st.sidebar.divider()
        btn_sorteo = st.sidebar.button("🎰 REALIZAR SORTEO", use_container_width=True)

        # LEEMOS LOS DATOS
        df = leer_datos()
        total = len(df)
        
        # BARRA DE PROGRESO (LA QUE QUERÍAS)
        st.progress(min(total / meta, 1.0))
        st.subheader(f"📊 Participantes: {total} / {meta}")
        
        st.divider()
        
        if not df.empty:
            # Lista limpia para el OBS
            for index, row in df.iterrows():
                st.markdown(f"### **{index + 1}. {row['Nombre']} {row['Apellido']}** — ✅")
            
            # Lógica del sorteo
            if btn_sorteo:
                ganador = random.choice(df['Nombre'].tolist())
                st.balloons()
                st.success(f"🎊 ¡GANADOR: {ganador.upper()}! 🎊")
                st.title(f"🏆 {ganador.upper()} 🏆")
        else:
            st.info("Lista vacía. Actualiza el Excel y dale al botón 'Actualizar Lista'.")

        if st.sidebar.button("Cerrar Sesión"):
            st.session_state['conectado'] = False
            st.rerun()
