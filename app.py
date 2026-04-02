import streamlit as st
import pandas as pd
import random
import time
import urllib.request

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Rifa Tony AFK - Estable", layout="wide")

LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
CLAVE_ADMIN = "tonyjm20"

# --- FUNCIÓN DE LECTURA "ANTI-FANTASMA" ---
def leer_datos():
    # 1. Borramos la memoria de Streamlit
    st.cache_data.clear()
    
    # 2. Creamos un link ÚNICO para cada segundo para engañar a Google
    # Añadimos un timestamp y un número aleatorio
    url_final = f"{LINK_CSV}&refresh={time.time()}&rand={random.randint(1, 1000)}"
    
    try:
        # 3. Usamos una técnica más fuerte para pedir el archivo (Request con Headers)
        # Esto le dice a los servidores de Google: "Prohibido usar caché"
        req = urllib.request.Request(
            url_final, 
            headers={'Cache-Control': 'no-cache', 'Pragma': 'no-cache'}
        )
        
        with urllib.request.urlopen(req) as response:
            df = pd.read_csv(response)
            df.columns = [c.strip() for c in df.columns]
            return df
    except Exception as e:
        # Si falla el método fuerte, usamos el normal de respaldo
        try:
            return pd.read_csv(url_final)
        except:
            return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

# --- MANEJO DE SESIÓN (PARA NO PEDIR CLAVE) ---
if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# --- LÓGICA DEL PANEL ---
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
    # --- PANEL ADMIN ---
    st.title("📺 Panel de Control - Datos en Tiempo Real")
    
    st.sidebar.header("⚙️ Controles")
    meta = st.sidebar.number_input("Meta", min_value=1, value=50)
    
    # Este botón ahora limpia hasta el último rastro de memoria
    if st.sidebar.button("🔄 REFRESCAR LISTA", type="primary", use_container_width=True):
        st.rerun()

    st.sidebar.divider()
    btn_sorteo = st.sidebar.button("🎰 REALIZAR SORTEO", use_container_width=True)

    # Lectura de datos con la nueva lógica
    df = leer_datos()
    total = len(df)
    
    st.progress(min(total / meta, 1.0))
    st.subheader(f"📊 Participantes: {total} / {meta}")
    
    st.divider()
    
    if not df.empty:
        for index, row in df.iterrows():
            st.markdown(f"### **{index + 1}. {row['Nombre']} {row['Apellido']}** — ✅")
        
        if btn_sorteo:
            ganador = random.choice(df['Nombre'].tolist())
            st.balloons()
            st.success(f"🎊 GANADOR: {ganador.upper()} 🎊")
            st.title(f"🏆 {ganador.upper()} 🏆")
    else:
        st.info("Esperando datos... Si acabas de anotar a alguien, espera 5 segundos y refresca.")

    if st.sidebar.button("Cerrar Sesión"):
        st.session_state['auth'] = False
        st.rerun()
