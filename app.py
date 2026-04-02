import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Panel Pro Tony AFK", layout="wide")

LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
CLAVE_ADMIN = "tonyjm20"
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl"

conn = st.connection("gsheets", type=GSheetsConnection)

# Función de lectura optimizada
def leer_datos():
    try:
        url_fresca = f"{LINK_CSV}&t={int(time.time())}"
        df = pd.read_csv(url_fresca)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

# --- MANEJO DE SESIÓN ---
# Usamos session_state para que la validación sea permanente en esta pestaña
if 'admin_auth' not in st.session_state:
    st.session_state['admin_auth'] = False

# --- NAVEGACIÓN ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

if es_seguidor:
    st.title("🎟️ Registro y Pago")
    # [Aquí mantén tu bloque de formulario y PayPal]
else:
    # VISTA ADMIN
    if not st.session_state['admin_auth']:
        st.sidebar.title("🔐 Acceso")
        pass_input = st.sidebar.text_input("Clave", type="password")
        if st.sidebar.button("Entrar"):
            if pass_input == CLAVE_ADMIN:
                st.session_state['admin_auth'] = True
                st.rerun() # Solo recarga una vez para entrar
            else:
                st.error("Clave incorrecta")
    else:
        # --- INTERFAZ DE TRANSMISIÓN ---
        st.title("📺 Panel de Control")
        
        # Sidebar con controles fijos
        st.sidebar.header("⚙️ Controles")
        meta = st.sidebar.number_input("Meta de Sorteo", min_value=1, value=50)
        
        # EL BOTÓN MÁGICO: Al presionarlo, Streamlit vuelve a ejecutar el código 
        # y como 'admin_auth' es True, no pide clave.
        btn_refresh = st.sidebar.button("🔄 REFRESCAR LISTA", type="primary", use_container_width=True)
        
        st.sidebar.divider()
        btn_sorteo = st.sidebar.button("🎰 REALIZAR SORTEO", use_container_width=True)
        
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state['admin_auth'] = False
            st.rerun()

        # --- ÁREA DINÁMICA (LA LISTA Y LA BARRA) ---
        df = leer_datos()
        total = len(df)
        
        # Barra de progreso
        porcentaje = min(total / meta, 1.0)
        st.progress(porcentaje)
        st.subheader(f"📊 Participantes: {total} / {meta}")
        
        st.divider()
        
        if not df.empty:
            # Mostramos a los ganadores en formato lista limpia
            for index, row in df.iterrows():
                st.markdown(f"### **{index + 1}. {row['Nombre']} {row['Apellido']}** — ✅")
            
            # Lógica del sorteo
            if btn_sorteo:
                ganador = random.choice(df['Nombre'].tolist())
                st.balloons()
                st.success(f"🎊 ¡GANADOR: {ganador.upper()}! 🎊")
                st.title(f"🏆 {ganador.upper()} 🏆")
        else:
            st.info("Esperando datos... Dale a 'Refrescar Lista' cuando anotes a alguien en el Excel.")
