import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Rifa Tony AFK", layout="wide")

# Datos actualizados
LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
ID_SHEET = "1zBwqiaFjT3RfnAA19BBE37AHFGaz6oQZM2C3aVJC2uE"
CLAVE_ADMIN = "tonyjm20"
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl"

# Conexión oficial para procesos internos
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_datos():
    try:
        # Lectura por link público: Rápida, estable y sin errores 401
        # Añadimos un timestamp para evitar que Google devuelva datos viejos (caché)
        url_fresca = f"{LINK_CSV}&t={int(time.time())}"
        df = pd.read_csv(url_fresca)
        # Limpiar espacios en los nombres de las columnas
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        # Si falla el CSV, intentamos la conexión de respaldo
        try:
            return conn.read(worksheet="Hoja1", ttl=0)
        except:
            # Si todo falla, devolvemos una tabla vacía con la estructura correcta
            return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

# --- NAVEGACIÓN ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

# ==========================================
# VISTA SEGUIDOR (PAGO Y REGISTRO)
# ==========================================
if es_seguidor:
    st.title("🎟️ Registro de Participantes")
    st.markdown("Llena tus datos y realiza el pago para entrar en el sorteo.")
    
    with st.form("registro_datos"):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre")
            ap = st.text_input("Apellido")
            cor = st.text_input("Email de contacto")
        with c2:
            usr = st.text_input("User del Juego")
            idx = st.text_input("ID del Juego")
        st.form_submit_button("Confirmar Datos")

    st.divider()
    st.info("Paga tu entrada aquí para validar tu participación:")
    
    paypal_html = f"""
    <div id="paypal-button-container" style="text-align: center;"></div>
    <script src="https://www.paypal.com/sdk/js?client-id={CLIENT_ID_PAYPAL}&currency=USD"></script>
    <script>
        paypal.Buttons({{
            createOrder: function(data, actions) {{
                return actions.order.create({{
                    purchase_units: [{{ amount: {{ value: '10.00' }} }}]
                }});
            }},
            onApprove: function(data, actions) {{
                return actions.order.capture().then(function(details) {{
                    alert('¡Pago realizado con éxito, ' + details.payer.name.given_name + '!');
                }});
            }}
        }}).render('#paypal-button-container');
    </script>
    """
    components.html(paypal_html, height=500)

# ==========================================
# VISTA TONY (STREAM + SORTEO)
# ==========================================
else:
    st.sidebar.title("🔐 Panel Admin")
    password = st.sidebar.text_input("Introduce la Clave", type="password")
    
    if password == CLAVE_ADMIN:
        st.title("📺 Control de Transmisión - Rifa Tony AFK")
        
        df = leer_datos()
        total_p = len(df)
        
        # Métricas principales
        st.metric("Participantes Inscritos", total_p)
        st.divider()
        
        if not df.empty:
            # Lista de participantes con formato llamativo para el OBS
            st.subheader("Lista de Participantes:")
            for index, row in df.iterrows():
                # Formato: 1. Nombre Apellido - ¡Participando!
                st.markdown(f"### **{index + 1}. {row['Nombre']} {row['Apellido']}** — ✅ *¡Está participando!*")
            
            st.divider()
            
            # Sección del Sorteo
            st.subheader("🎰 Zona de Premiación")
            if st.button("¡REALIZAR SORTEO AHORA!", type="primary"):
                if total_p > 0:
                    ganador = random.choice(df['Nombre'].tolist())
                    # Mostramos al ganador en grande
                    st.header("🎊 ¡TENEMOS UN GANADOR! 🎊")
                    st.title(f"🏆 {ganador.upper()} 🏆")
                    st.balloons()
                else:
                    st.warning("No hay participantes para sortear.")
        else:
            st.info("Esperando que ingreses datos en el Google Sheet...")
            st.write("Asegúrate de que el Excel tenga los nombres en la Hoja1.")
    
    elif password != "":
        st.sidebar.error("Clave incorrecta")
