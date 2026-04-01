import streamlit as st
import pandas as pd
import random
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit.components.v1 as components

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Sorteo TonyJM20", layout="wide")

# --- CONEXIÓN A GOOGLE SHEETS ---
# (Configuraremos las llaves en el Paso 4)
def conectar_google_sheets():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds_dict = st.secrets["gcp_service_account"]
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    client = gspread.authorize(creds)
    return client.open("Rifa_TonyJM").sheet1

# --- ESTADO DE LA APP ---
if 'ganador' not in st.session_state:
    st.session_state.ganador = None
if 'config' not in st.session_state:
    st.session_state.config = {"meta": 50, "precio": 10.0, "premio": "Insecto Especial", "client_id": "PEGA_AQUI_TU_CLIENT_ID"}

# --- NAVEGACIÓN ---
menu = st.sidebar.radio("Navegación", ["🎟️ Registro y Pago", "📺 Pantalla de Stream", "🔐 Admin"])

# 1. REGISTRO
if menu == "🎟️ Registro y Pago":
    st.title(f"Sorteo: {st.session_state.config['premio']}")
    st.write(f"Costo del boleto: **${st.session_state.config['precio']} USD**")
    
    with st.form("form_registro"):
        col1, col2 = st.columns(2)
        nombre = col1.text_input("Nombre")
        apellido = col1.text_input("Apellido")
        u_game = col2.text_input("Usuario Juego")
        id_game = col2.text_input("ID Cuenta")
        email = st.text_input("Correo Electrónico")
        
        st.subheader("Pago Seguro (Tarjeta o PayPal)")
        # Componente de PayPal
        paypal_html = f"""
            <div id="paypal-button-container"></div>
            <script src="https://www.paypal.com/sdk/js?client-id={st.session_state.config['client_id']}&currency=USD"></script>
            <script>
                paypal.Buttons({{
                    createOrder: function(data, actions) {{
                        return actions.order.create({{ purchase_units: [{{ amount: {{ value: '{st.session_state.config['precio']}' }} }}] }});
                    }},
                    onApprove: function(data, actions) {{
                        return actions.order.capture().then(function(det) {{
                            alert('Pago de ' + det.payer.name.given_name + ' exitoso. ¡Dale a Registrarme!');
                        }});
                    }}
                }}).render('#paypal-button-container');
            </script>
        """
        components.html(paypal_html, height=350)
        
        if st.form_submit_button("REGISTRARME AHORA"):
            try:
                sheet = conectar_google_sheets()
                sheet.append_row([nombre, apellido, u_game, id_game, email, time.strftime("%Y-%m-%d %H:%M")])
                st.success("¡Registro guardado en la base de datos!")
            except:
                st.error("Error al conectar con la base de datos. Verifica los permisos.")

# 2. PANTALLA STREAM
elif menu == "📺 Pantalla de Stream":
    st.title("PROGRESO DEL SORTEO")
    try:
        sheet = conectar_google_sheets()
        datos = pd.DataFrame(sheet.get_all_records())
        total = len(datos)
        meta = st.session_state.config['meta']
        
        c1, c2 = st.columns(2)
        c1.metric("Boletos Vendidos", f"{total} / {meta}")
        c2.progress(min(total/meta, 1.0))
        
        st.subheader("Últimos Participantes")
        st.table(datos[["Nombre", "Apellido"]].iloc[::-1].head(10))
        
        if st.button("🎰 SORTEAR AHORA"):
            with st.spinner("Girando..."):
                time.sleep(3)
                st.session_state.ganador = datos.sample().iloc[0]
                st.balloons()
        
        if st.session_state.ganador is not None:
            st.success(f"¡GANADOR: {st.session_state.ganador['Nombre']} {st.session_state.ganador['Apellido']}!")
    except:
        st.info("Esperando registros...")

# 3. ADMIN
elif menu == "🔐 Admin":
    clave = st.text_input("Clave Admin", type="password")
    if clave == "tonyjm":
        st.session_state.config['meta'] = st.number_input("Meta de boletos", value=st.session_state.config['meta'])
        st.session_state.config['precio'] = st.number_input("Precio", value=st.session_state.config['precio'])
        if st.button("Ver Base de Datos"):
            sheet = conectar_google_sheets()
            st.write(pd.DataFrame(sheet.get_all_records()))
