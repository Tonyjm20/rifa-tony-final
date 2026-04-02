import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import time
import random
import streamlit.components.v1 as components

# --- CONFIGURACIÓN ---
st.set_page_config(page_title="Rifa Tony AFK", layout="wide")

# 1. Enlace de lectura pública (El que termina en .csv de "Publicar en la web")
# REEMPLAZA EL LINK DE ABAJO CON EL TUYO
LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
ID_SHEET = "1zBwqiaFjT3RfnAA19BBE37AHFGaz6oQZM2C3aVJC2uE"
CLAVE_ADMIN = "tonyjm20"
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl"

# 2. Conexión de escritura
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_datos():
    try:
        url_fresca = f"{LINK_CSV}&cache={random.randint(1,99999)}"
        df = pd.read_csv(url_fresca)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

def guardar_registro_forzado(n, ape, u, i, em):
    try:
        df_actual = leer_datos()
        nueva_fila = pd.DataFrame([{
            "Nombre": n, "Apellido": ape, "User": u, 
            "ID": i, "Email": em, "Fecha": time.strftime("%d/%m/%Y %H:%M:%S")
        }])
        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
        conn.update(worksheet="Hoja1", data=df_final)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error técnico al guardar: {e}")
        return False

# --- LÓGICA DE NAVEGACIÓN ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

if es_seguidor:
    st.header("🎟️ Registro para el Sorteo")
    
    with st.form("datos_usuario"):
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre")
            apellido = st.text_input("Apellido")
            email = st.text_input("Email")
        with c2:
            usuario = st.text_input("User del Juego")
            id_juego = st.text_input("ID del Juego")
        
        enviar_datos = st.form_submit_button("1. Registrar mis datos")

    if enviar_datos:
        if nombre and id_juego and email:
            exito = guardar_registro_forzado(nombre, apellido, usuario, id_juego, email)
            if exito:
                st.success("✅ Datos guardados. Ahora procede al pago para validar tu participación.")
                st.session_state['datos_listos'] = True
            else:
                st.error("Hubo un problema al conectar con el Excel. Intenta de nuevo.")
        else:
            st.warning("Por favor, llena todos los campos.")

    if st.session_state.get('datos_listos'):
        st.divider()
        st.info("💰 Paso final: Realiza el pago de $10.00 USD")
        
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
                        alert('¡Pago completado con éxito!');
                        window.location.href = window.location.origin + "/?view=registro&pago=exito";
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_html, height=500)

else:
    st.sidebar.title("Admin")
    if st.sidebar.text_input("Clave", type="password") == CLAVE_ADMIN:
        st.title("📺 Panel de Control - Stream")
        df = leer_datos()
        
        if not df.empty:
            for index, row in df.iterrows():
                st.markdown(f"### **{index + 1}. {row['Nombre']} {row['Apellido']}** — ID: {row['ID']} ✅")
        else:
            st.write("Sin participantes aún.")
