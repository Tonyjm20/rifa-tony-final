import streamlit as st
import pandas as pd
import random
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(page_title="Rifa TonyJM20 - The Ants", layout="wide")

# --- 2. CONEXIÓN A GOOGLE SHEETS (BASE DE DATOS) ---
def conectar_google_sheets():
    try:
        scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
        # Usa las credenciales guardadas en los Secrets de Streamlit
        creds_dict = st.secrets["gcp_service_account"]
        creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
        client = gspread.authorize(creds)
        # Debe coincidir exactamente con el nombre de tu archivo en Google Drive
        return client.open("Rifa_TonyJM").sheet1
    except Exception as e:
        st.error(f"Error de conexión a Base de Datos: {e}")
        return None

# --- 3. INICIALIZACIÓN DE VARIABLES DE SESIÓN ---
if 'ganador' not in st.session_state:
    st.session_state.ganador = None

# Configuración inicial de la rifa (Se puede cambiar en el Panel Admin)
if 'config' not in st.session_state:
    st.session_state.config = {
        "meta": 50, 
        "precio": 10.0, 
        "premio": "Insecto Especial (The Ants)", 
        "client_id": "TU_CLIENT_ID_DE_PAYPAL" # <--- PEGA TU CLIENT ID AQUÍ
    }

# --- 4. NAVEGACIÓN LATERAL ---
st.sidebar.title("🎮 Menú de Rifa")
menu = st.sidebar.radio("Ir a:", ["🎟️ Registro y Pago", "📺 Pantalla OBS (En Vivo)", "🔐 Panel Admin"])

# ==========================================
# SECCIÓN 1: REGISTRO Y PAGO (USUARIO)
# ==========================================
if menu == "🎟️ Registro y Pago":
    st.title(f"Participa por: {st.session_state.config['premio']}")
    st.markdown(f"### Valor del Boleto: **${st.session_state.config['precio']} USD**")
    
    st.info("Paso 1: Realiza el pago. Paso 2: Completa el formulario de abajo.")

    # --- BOTONES DE PAYPAL Y TARJETA ---
    paypal_html = f"""
        <div id="paypal-button-container" style="width: 100%; min-height: 500px;"></div>
        <script src="https://www.paypal.com/sdk/js?client-id={st.session_state.config['client_id']}&currency=USD&components=buttons"></script>
        <script>
            paypal.Buttons({{
                style: {{ layout: 'vertical', color: 'gold', shape: 'rect', label: 'paypal' }},
                createOrder: function(data, actions) {{
                    return actions.order.create({{
                        purchase_units: [{{ amount: {{ value: '{st.session_state.config["precio"]}' }} }}]
                    }});
                }},
                onApprove: function(data, actions) {{
                    return actions.order.capture().then(function(details) {{
                        alert('¡Pago de ' + details.payer.name.given_name + ' exitoso! Ahora llena el formulario y dale a Registrarme.');
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
    """
    components.html(paypal_html, height=550, scrolling=True)

    st.divider()

    # --- FORMULARIO DE REGISTRO ---
    with st.form("registro_usuario"):
        st.subheader("Datos del Participante")
        c1, c2 = st.columns(2)
        nombre = c1.text_input("Nombre")
        apellido = c1.text_input("Apellido")
        u_game = c2.text_input("Usuario en el Juego")
        id_game = c2.text_input("ID de Cuenta")
        email = st.text_input("Correo Electrónico (para contactarte)")
        
        btn_reg = st.form_submit_button("REGISTRARME EN LA RIFA")
        
        if btn_reg:
            if nombre and id_game and email:
                sheet = conectar_google_sheets()
                if sheet:
                    sheet.append_row([nombre, apellido, u_game, id_game, email, time.strftime("%Y-%m-%d %H:%M")])
                    st.success("¡Registro Exitoso! Ya apareces en la pantalla de transmisión.")
            else:
                st.warning("Por favor, rellena todos los campos antes de registrarte.")

# ==========================================
# SECCIÓN 2: PANTALLA DE TRANSMISIÓN (OBS)
# ==========================================
elif menu == "📺 Pantalla OBS (En Vivo)":
    st.title(f"🏆 Rifa: {st.session_state.config['premio']}")
    
    sheet = conectar_google_sheets()
    if sheet:
        # Obtener datos y calcular progreso
        datos = pd.DataFrame(sheet.get_all_records())
        total_actual = len(datos)
        meta = st.session_state.config['meta']
        progreso = min(total_actual / meta, 1.0) if meta > 0 else 0
        
        # Métricas visuales
        m1, m2, m3 = st.columns(3)
        m1.metric("Participantes", f"{total_actual} / {meta}")
        m2.metric("Precio", f"${st.session_state.config['precio']}")
        m3.metric("Faltan", max(0, meta - total_actual))
        
        st.write("**Progreso para el Sorteo:**")
        st.progress(progreso)

        st.divider()

        col_izq, col_der = st.columns([2, 1])
        
        with col_izq:
            st.subheader("📋 Lista de Participantes")
            if not datos.empty:
                st.table(datos[["Nombre", "Apellido"]].iloc[::-1].head(10)) # Muestra los últimos 10
            else:
                st.write("Esperando registros...")

        with col_der:
            st.subheader("🎲 ¡Sorteo!")
            if st.button("🔥 GENERAR GANADOR 🔥", use_container_width=True):
                if total_actual > 0:
                    with st.spinner("Eligiendo ganador..."):
                        time.sleep(3)
                        # Elegir un ganador al azar de la tabla
                        ganador_fila = datos.sample().iloc[0]
                        st.session_state.ganador = ganador_fila
                        st.balloons()
                else:
                    st.error("No hay participantes todavía.")
            
            if st.session_state.ganador is not None:
                st.markdown(f"""
                    <div style="background-color:#FFD700; padding:20px; border-radius:10px; text-align:center; color:black;">
                        <h3>🏆 EL GANADOR ES:</h3>
                        <h2>{st.session_state.ganador['Nombre']} {st.session_state.ganador['Apellido']}</h2>
                    </div>
                """, unsafe_allow_html=True)

# ==========================================
# SECCIÓN 3: PANEL ADMIN (PRIVADO)
# ==========================================
elif menu == "🔐 Panel Admin":
    st.title("Administración")
    pass_admin = st.text_input("Contraseña de Admin", type="password")
    
    if pass_admin == "TU_CLAVE_DE_ADMIN": # <--- CAMBIA ESTO
        st.subheader("Ajustes del Sorteo")
        st.session_state.config['premio'] = st.text_input("Nombre del Premio", st.session_state.config['premio'])
        st.session_state.config['meta'] = st.number_input("Meta de Boletos", value=st.session_state.config['meta'])
        st.session_state.config['precio'] = st.number_input("Precio del Boleto ($)", value=st.session_state.config['precio'])
        
        if st.button("Borrar Ganador Actual"):
            st.session_state.ganador = None
            st.rerun()
            
        st.divider()
        st.subheader("Ver Base de Datos (Google Sheets)")
        sheet = conectar_google_sheets()
        if sheet:
            datos_completos = pd.DataFrame(sheet.get_all_records())
            st.dataframe(datos_completos)
