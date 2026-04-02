import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Panel Ultra-Rápido Tony AFK", layout="wide")

LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
CLAVE_ADMIN = "tonyjm20"
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl"

# Conexión
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_datos():
    try:
        # Forzamos la lectura fresca cada 5 segundos
        url_fresca = f"{LINK_CSV}&nocache={time.time()}"
        df = pd.read_csv(url_fresca)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

# --- LÓGICA DE NAVEGACIÓN ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

if es_seguidor:
    # --- VISTA SEGUIDOR (PAGO) ---
    st.title("🎟️ Registro y Pago")
    # [Aquí mantienes tu bloque de formulario y PayPal intacto]
    # ... (código anterior de seguidor)
    
else:
    # --- VISTA ADMIN (CON AUTO-REFRESH DE 5s) ---
    if 'autenticado' not in st.session_state:
        st.session_state['autenticado'] = False

    if not st.session_state['autenticado']:
        st.sidebar.title("🔐 Acceso Admin")
        pass_input = st.sidebar.text_input("Clave", type="password")
        if st.sidebar.button("Entrar"):
            if pass_input == CLAVE_ADMIN:
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("Clave incorrecta")
    else:
        # --- SCRIPT DE AUTO-RECARGA (CADA 5 SEGUNDOS) ---
        components.html(
            """
            <script>
            setTimeout(function(){
                window.parent.location.reload();
            }, 5000); // 5000 ms = 5 segundos exactos
            </script>
            """,
            height=0
        )

        st.title("📺 Panel en Vivo (Actualización: 5s)")
        
        # Configuración de Meta
        meta = st.sidebar.number_input("Meta de Sorteo", min_value=1, value=50)
        
        df = leer_datos()
        total = len(df)
        
        # Barra de progreso visual
        porcentaje = min(total / meta, 1.0)
        st.progress(porcentaje)
        st.subheader(f"📊 Progreso: {total} / {meta}")
        
        st.divider()
        
        if not df.empty:
            for index, row in df.iterrows():
                # Formato limpio para que se vea bien en el OBS
                st.markdown(f"### **{index + 1}. {row['Nombre']} {row['Apellido']}** — ✅")
            
            st.divider()
            if st.button("🎰 REALIZAR SORTEO", type="primary"):
                ganador = random.choice(df['Nombre'].tolist())
                st.header(f"🎊 ¡GANADOR: {ganador.upper()}! 🎊")
                st.balloons()
        else:
            st.info("Esperando nuevos registros en el Sheets...")

        if st.sidebar.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()
