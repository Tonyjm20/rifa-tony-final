import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Panel Limpio Tony AFK", layout="wide")

LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
CLAVE_ADMIN = "tonyjm20"
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl"

# Conexión oficial
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIÓN DE LECTURA SIN MEMORIA (TTL=0) ---
def leer_datos_limpios():
    # 1. Limpiamos cualquier rastro de memoria vieja de Streamlit
    st.cache_data.clear()
    try:
        # 2. Forzamos a Google a darnos el archivo nuevo con un número aleatorio
        url_fresca = f"{LINK_CSV}&nocache={time.time()}"
        df = pd.read_csv(url_fresca)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        # 3. Si el CSV falla, usamos la conexión oficial pero con TTL=0 (Sin caché)
        return conn.read(worksheet="Hoja1", ttl=0)

# --- MANEJO DE SESIÓN ---
if 'admin_auth' not in st.session_state:
    st.session_state['admin_auth'] = False

# --- LÓGICA DE VISTAS ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

if es_seguidor:
    st.title("🎟️ Registro y Pago")
    # [Bloque de registro intacto]
else:
    if not st.session_state['admin_auth']:
        st.sidebar.title("🔐 Acceso")
        pass_input = st.sidebar.text_input("Clave", type="password")
        if st.sidebar.button("Entrar"):
            if pass_input == CLAVE_ADMIN:
                st.session_state['admin_auth'] = True
                st.rerun()
            else:
                st.error("Clave incorrecta")
    else:
        st.title("📺 Panel de Control (Datos Reales)")
        
        st.sidebar.header("⚙️ Controles")
        meta = st.sidebar.number_input("Meta", min_value=1, value=50)
        
        # BOTÓN DE REFRESCO QUE LIMPIA TODO
        if st.sidebar.button("🔄 REFRESCAR Y LIMPIAR", type="primary", use_container_width=True):
            # Al picar aquí, la función leer_datos_limpios() hará el trabajo
            st.rerun() 

        st.sidebar.divider()
        btn_sorteo = st.sidebar.button("🎰 REALIZAR SORTEO", use_container_width=True)
        
        # LECTURA DE DATOS
        df = leer_datos_limpios()
        total = len(df)
        
        # Barra de progreso
        st.progress(min(total / meta, 1.0))
        st.subheader(f"📊 Participantes confirmados: {total} / {meta}")
        
        st.divider()
        
        if not df.empty:
            for index, row in df.iterrows():
                st.markdown(f"### **{index + 1}. {row['Nombre']} {row['Apellido']}** — ✅")
            
            if btn_sorteo:
                ganador = random.choice(df['Nombre'].tolist())
                st.balloons()
                st.success(f"🎊 ¡GANADOR: {ganador.upper()}! 🎊")
                st.title(f"🏆 {ganador.upper()} 🏆")
        else:
            st.info("No hay datos nuevos. Asegúrate de que el Excel esté actualizado y presiona el botón de refrescar.")

        if st.sidebar.button("Cerrar Sesión"):
            st.session_state['admin_auth'] = False
            st.rerun()
