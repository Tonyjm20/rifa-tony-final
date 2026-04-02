import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Panel VIP Tony AFK", layout="wide")

# Datos de conexión directa
ID_SHEET = "1zBwqiaFjT3RfnAA19BBE37AHFGaz6oQZM2C3aVJC2uE"
CLAVE_ADMIN = "tonyjm20"
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl"

# Conexión oficial de Streamlit para Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)

# --- FUNCIÓN DE LECTURA DIRECTA (SIN CACHÉ) ---
def leer_datos_reales():
    # Eliminamos el caché de Streamlit por completo
    st.cache_data.clear()
    try:
        # Leemos directamente de la hoja usando la URL de edición (Interna)
        # Esto no pasa por los servidores de "Publicar en la web", es directo a tu archivo
        url_interna = f"https://docs.google.com/spreadsheets/d/{ID_SHEET}/edit#gid=0"
        df = conn.read(spreadsheet=url_interna, worksheet="Hoja1", ttl=0)
        # Limpiamos nombres de columnas
        df.columns = [str(c).strip() for c in df.columns]
        return df
    except Exception as e:
        st.error(f"Error de conexión directa: {e}")
        return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

# --- MANEJO DE SESIÓN PERSISTENTE ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# --- LÓGICA DE VISTAS ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

if es_seguidor:
    st.title("🎟️ Registro para el Sorteo")
    # [Aquí mantén tu bloque de PayPal y formulario]
else:
    # --- VISTA ADMIN ---
    if not st.session_state['autenticado']:
        st.sidebar.title("🔐 Acceso Admin")
        pass_input = st.sidebar.text_input("Clave de Acceso", type="password")
        if st.sidebar.button("Entrar al Panel"):
            if pass_input == CLAVE_ADMIN:
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("Clave incorrecta")
    else:
        st.title("📺 Panel de Control - Transmisión en Vivo")
        
        # CONTROLES EN SIDEBAR
        st.sidebar.header("🕹️ Controles")
        meta = st.sidebar.number_input("Meta de Participantes", min_value=1, value=50)
        
        # BOTÓN DE ACTUALIZACIÓN MANUAL (ÚNICA FORMA DE EVITAR EL PARPADEO)
        if st.sidebar.button("🔄 ACTUALIZAR LISTA", type="primary", use_container_width=True):
            st.rerun()

        st.sidebar.divider()
        btn_sorteo = st.sidebar.button("🎰 REALIZAR SORTEO", use_container_width=True)
        
        # --- LECTURA Y VISUALIZACIÓN ---
        df = leer_datos_reales()
        total = len(df)
        
        # Barra de progreso
        st.progress(min(total / meta, 1.0))
        st.subheader(f"📊 Estado: {total} de {meta} participantes")
        
        st.divider()

        if not df.empty:
            # Mostramos la lista
            for index, row in df.iterrows():
                nombre_completo = f"{row.get('Nombre', '')} {row.get('Apellido', '')}"
                st.markdown(f"### **{index + 1}. {nombre_completo}** — ✅")
            
            st.divider()
            
            # Sorteo
            if btn_sorteo:
                ganador = random.choice(df['Nombre'].tolist())
                st.balloons()
                st.success(f"🎊 ¡TENEMOS UN GANADOR! 🎊")
                st.title(f"🏆 {ganador.upper()} 🏆")
        else:
            st.info("No hay datos registrados. Actualiza el Excel y pulsa el botón.")

        if st.sidebar.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()
