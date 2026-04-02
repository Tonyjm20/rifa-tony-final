import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Panel Control Tony AFK", layout="wide")

LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
CLAVE_ADMIN = "tonyjm20"
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl"

conn = st.connection("gsheets", type=GSheetsConnection)

def leer_datos():
    try:
        # Forzamos lectura fresca con un timestamp
        url_fresca = f"{LINK_CSV}&t={int(time.time())}"
        df = pd.read_csv(url_fresca)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

# --- MANEJO DE SESIÓN (ESTO EVITA QUE TE PIDA LA CLAVE) ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# --- LÓGICA DE VISTAS ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

if es_seguidor:
    # --- VISTA SEGUIDOR ---
    st.title("🎟️ Registro para el Sorteo")
    # (Aquí mantén tu bloque de formulario y PayPal)
else:
    # --- VISTA ADMIN ---
    if not st.session_state['autenticado']:
        st.sidebar.title("🔐 Acceso Admin")
        pass_input = st.sidebar.text_input("Introduce la Clave", type="password")
        if st.sidebar.button("Entrar"):
            if pass_input == CLAVE_ADMIN:
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("Clave incorrecta")
    else:
        # --- PANEL DE CONTROL ---
        st.title("📺 Panel de Transmisión")
        
        # Botones de Control en la Sidebar para no estorbar la vista principal
        st.sidebar.header("Controles")
        btn_update = st.sidebar.button("🔄 ACTUALIZAR LISTA", use_container_width=True)
        meta = st.sidebar.number_input("Meta de Sorteo", min_value=1, value=50)

        # Leemos los datos (se activará al entrar o al dar click en actualizar)
        df = leer_datos()
        total = len(df)

        # Barra de progreso
        st.progress(min(total / meta, 1.0))
        st.subheader(f"📊 Participantes actuales: {total} de {meta}")
        
        st.divider()

        if not df.empty:
            # Lista de participantes
            for index, row in df.iterrows():
                st.markdown(f"### **{index + 1}. {row['Nombre']} {row['Apellido']}** — ✅")
            
            st.divider()
            
            # Botón de Sorteo
            if st.sidebar.button("🎰 REALIZAR SORTEO", type="primary", use_container_width=True):
                ganador = random.choice(df['Nombre'].tolist())
                st.balloons()
                st.success(f"🎊 ¡TENEMOS UN GANADOR! 🎊")
                st.title(f"🏆 {ganador.upper()} 🏆")
        else:
            st.info("La lista está vacía. Agrega nombres en el Google Sheet y presiona 'Actualizar Lista'.")

        if st.sidebar.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()
