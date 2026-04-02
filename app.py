import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN (RECONECTA TUS LINKS AQUÍ) ---
st.set_page_config(page_title="Rifa Tony AFK", layout="wide")

# Tu link de "Publicar en la web" (CSV) es el que hace que la lectura funcione
LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
ID_SHEET = "1zBwqiaFjT3RfnAA19BBE37AHFGaz6oQZM2C3aVJC2uE"
CLAVE_ADMIN = "tonyjm20"
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl""

# Conexión oficial para escritura (aunque falle, la lectura seguirá por el LINK_CSV)
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_datos():
    try:
        # Esta es la parte que ya te funcionaba: lectura por link público
        url_fresca = f"{LINK_CSV}&cache={random.randint(1,99999)}"
        df = pd.read_csv(url_fresca)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        # Si el link falla, intentamos la conexión de gsheets
        try:
            return conn.read(worksheet="Hoja1", ttl=0)
        except:
            return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

# --- LÓGICA DE NAVEGACIÓN ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

# ==========================================
# VISTA SEGUIDOR (PAGO)
# ==========================================
if es_seguidor:
    st.title("🎟️ Registro de Participantes")
    with st.form("registro"):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre")
            ap = st.text_input("Apellido")
            cor = st.text_input("Email")
        with c2:
            usr = st.text_input("User del Juego")
            idx = st.text_input("ID del Juego")
        st.form_submit_button("Confirmar Datos")

    st.info("Realiza el pago para validar tu participación:")
    paypal_html = f"""
    <div id="paypal-button-container"></div>
    <script src="https://www.paypal.com/sdk/js?client-id={CLIENT_ID_PAYPAL}&currency=USD"></script>
    <script>
        paypal.Buttons({{
            createOrder: function(data, actions) {{
                return actions.order.create({{ purchase_units: [{{ amount: {{ value: '10.00' }} }}] }});
            }},
            onApprove: function(data, actions) {{
                return actions.order.capture().then(function(details) {{
                    alert('Pago realizado con éxito');
                }});
            }}
        }}).render('#paypal-button-container');
    </script>
    """
    components.html(paypal_html, height=500)

# ==========================================
# VISTA TONY (STREAM + SORTEO) - AQUÍ REGRESÓ TODO
# ==========================================
else:
    st.sidebar.title("🔐 Admin")
    if st.sidebar.text_input("Clave", type="password") == CLAVE_ADMIN:
        st.title("📺 Panel de Transmisión")
        
        df = leer_datos()
        total = len(df)
        
        st.metric("Total Participantes", total)
        st.divider()
        
        if not df.empty:
            # Mostramos la lista con el formato que te gustó
            for index, row in df.iterrows():
                st.markdown(f"### **{index + 1}. {row['Nombre']} {row['Apellido']}** — *¡Está participando!* ✅")
            
            st.divider()
            # REGRESÓ EL BOTÓN DE SORTEO
            if st.button("🎰 REALIZAR SORTEO"):
                ganador = random.choice(df['Nombre'].tolist())
                st.header(f"🎊 ¡GANADOR: {ganador.upper()}! 🎊")
                st.balloons()
        else:
            st.write("Esperando datos del Google Sheet...")
