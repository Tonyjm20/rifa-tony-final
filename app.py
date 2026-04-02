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

# --- FUNCIÓN DE LECTURA (Cero Caché) ---
def leer_datos():
    try:
        # El parámetro t= asegura que Google no nos de datos viejos
        url_fresca = f"{LINK_CSV}&t={int(time.time())}"
        df = pd.read_csv(url_fresca)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

# --- MANEJO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# --- NAVEGACIÓN ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

if es_seguidor:
    # --- VISTA SEGUIDOR (Registro y Pago) ---
    st.title("🎟️ Registro para el Sorteo")
    # [Aquí va tu bloque de registro y PayPal que ya funciona]
    
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
        # --- PANEL EN VIVO (ESTO ES LO QUE NO PARPADEA) ---
        st.title("📺 Panel de Transmisión (Auto-Update)")
        
        meta = st.sidebar.number_input("Meta", min_value=1, value=50)
        
        # Usamos un contenedor vacío para actualizar solo el contenido
        placeholder = st.empty()

        # Bucle de actualización suave (sin recargar la página)
        while True:
            with placeholder.container():
                df = leer_datos()
                total = len(df)
                
                # Barra y Métricas
                st.progress(min(total / meta, 1.0))
                st.subheader(f"📊 Participantes: {total} / {meta}")
                
                st.divider()
                
                if not df.empty:
                    # Mostramos los participantes
                    for index, row in df.iterrows():
                        st.write(f"### {index + 1}. {row['Nombre']} {row['Apellido']} — ✅")
                    
                    st.divider()
                    # Botón de sorteo (este detendrá el bucle para mostrar al ganador)
                    if st.button("🎰 SORTEAR AHORA"):
                        ganador = random.choice(df['Nombre'].tolist())
                        st.header(f"🎊 ¡GANADOR: {ganador.upper()}! 🎊")
                        st.balloons()
                        st.stop() # Pausa el refresco para que se vea el ganador
                else:
                    st.info("Esperando nuevos registros...")
            
            # Tiempo de espera entre actualizaciones (5 segundos)
            time.sleep(5)
            # st.rerun() no es necesario aquí porque el while refresca el container
