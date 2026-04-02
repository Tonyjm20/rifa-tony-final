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

def leer_datos():
    try:
        url_fresca = f"{LINK_CSV}&t={int(time.time())}"
        df = pd.read_csv(url_fresca)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

# --- SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# --- NAVEGACIÓN ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

if es_seguidor:
    # --- VISTA SEGUIDOR (PAGO) ---
    st.title("🎟️ Registro para el Sorteo")
    # (Aquí mantén tu bloque de PayPal y formulario que ya funciona)
else:
    # --- VISTA ADMIN ---
    if not st.session_state['autenticado']:
        st.sidebar.title("🔐 Acceso")
        pass_input = st.sidebar.text_input("Clave", type="password")
        if st.sidebar.button("Entrar"):
            if pass_input == CLAVE_ADMIN:
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("Incorrecto")
    else:
        st.title("📺 Panel de Transmisión (Auto-Refresh)")
        
        meta = st.sidebar.number_input("Meta de Sorteo", min_value=1, value=50)

        # --- ZONA QUE SE ACTUALIZA SOLA (FRAGMENTO) ---
        @st.fragment(run_every=5) # <--- AQUÍ ESTÁ LA MAGIA: Actualiza cada 5s sin parpadear
        def mostrar_lista_viva():
            datos = leer_datos()
            total = len(datos)
            
            # Barra de progreso
            st.progress(min(total / meta, 1.0))
            st.subheader(f"📊 Participantes: {total} / {meta}")
            
            st.divider()
            
            if not datos.empty:
                for index, row in datos.iterrows():
                    st.markdown(f"### **{index + 1}. {row['Nombre']} {row['Apellido']}** — ✅")
            else:
                st.info("Esperando registros...")
        
        # Llamamos al fragmento
        mostrar_lista_viva()

        # --- BOTÓN DE SORTEO (FUERA DEL FRAGMENTO PARA QUE NO DE ERROR) ---
        st.sidebar.divider()
        if st.sidebar.button("🎰 REALIZAR SORTEO", type="primary"):
            df_para_sorteo = leer_datos()
            if not df_para_sorteo.empty:
                ganador = random.choice(df_para_sorteo['Nombre'].tolist())
                st.balloons()
                st.success(f"🎊 ¡TENEMOS UN GANADOR! 🎊")
                st.title(f"🏆 {ganador.upper()} 🏆")
            else:
                st.sidebar.warning("No hay nadie para sortear aún.")

        if st.sidebar.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()
