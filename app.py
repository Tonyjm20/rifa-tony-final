import streamlit as st
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN INICIAL ---
st.set_page_config(page_title="Sorteo TonyJM20", layout="wide", initial_sidebar_state="collapsed")

# Memoria local (No cierres la pestaña de tu PC)
if 'participantes' not in st.session_state:
    st.session_state.participantes = []
if 'ganador' not in st.session_state:
    st.session_state.ganador = None

# --- CONFIGURACIÓN (CAMBIA TU ID AQUÍ) ---
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl" 
CLAVE_MAESTRO = "tonyjm20" 

if 'config' not in st.session_state:
    st.session_state.config = {
        "meta": 50, 
        "precio": "10.00", 
        "premio": "Insecto Especial - The Ants"
    }

# --- 2. DETECTOR DE ROL (LÓGICA DE ENTRADA) ---
# Obtenemos los parámetros de la URL
params = st.query_params
es_seguidor = "view" in params and params["view"] == "public"

# ==========================================
# OPCIÓN A: VISTA DEL PÚBLICO (Link con ?view=public)
# ==========================================
if es_seguidor:
    st.title(f"🎟️ Sorteo Oficial: {st.session_state.config['premio']}")
    st.info(f"Participa por: ${st.session_state.config['precio']} USD")
    
    # --- PASO 1: DATOS ---
    st.subheader("1. Registra tus datos")
    col1, col2 = st.columns(2)
    with col1:
        nom = st.text_input("Nombre")
        ape = st.text_input("Apellido")
    with col2:
        u_g = st.text_input("Usuario en el Juego")
        id_g = st.text_input("ID de Cuenta")
    
    st.divider()

    # --- PASO 2: PAGO ---
    st.subheader("2. Realizar Pago Seguro")
    if CLIENT_ID_PAYPAL == "AQUÍ_PEGA_TU_CLIENT_ID_DE_PAYPAL":
        st.error("Error: PayPal no está configurado por el administrador.")
    else:
        # Script de PayPal con altura fija para evitar recortes
        paypal_html = f"""
        <div id="paypal-button-container" style="display: flex; justify-content: center;"></div>
        <script src="https://www.paypal.com/sdk/js?client-id={CLIENT_ID_PAYPAL}&currency=USD&components=buttons"></script>
        <script>
            paypal.Buttons({{
                style: {{ layout: 'vertical', color: 'gold', shape: 'rect' }},
                createOrder: function(data, actions) {{
                    return actions.order.create({{
                        purchase_units: [{{ amount: {{ value: '{st.session_state.config['precio']}' }} }}]
                    }});
                }},
                onApprove: function(data, actions) {{
                    return actions.order.capture().then(function(d) {{
                        alert('¡Pago completado! Haz clic en el botón de abajo para finalizar.');
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_html, height=550)

    if st.button("✅ FINALIZAR REGISTRO", use_container_width=True):
        if nom and id_g:
            st.session_state.participantes.append({
                "Nombre": nom, "Apellido": ape, "User": u_g, "ID": id_g, "Hora": time.strftime("%H:%M")
            })
            st.success("¡Registro Exitoso! Ya estás en la lista del directo.")
        else:
            st.error("Por favor, llena los datos antes de registrarte.")

# ==========================================
# OPCIÓN B: VISTA DE TONY (Link normal)
# ==========================================
else:
    st.sidebar.title("🔐 Panel de Control")
    password = st.sidebar.text_input("Contraseña Maestro", type="password")
    
    if password != CLAVE_MAESTRO:
        st.title("🛡️ Acceso Restringido")
        st.write("Bienvenido, Tony. Por seguridad, ingresa tu clave en la barra lateral para ver el panel de administración.")
    else:
        menu = st.sidebar.radio("Navegar:", ["📺 Pantalla Stream", "⚙️ Configuración"])

        # --- PANTALLA PARA EL OBS ---
        if menu == "📺 Pantalla Stream":
            st.title(f"🏆 Rifa: {st.session_state.config['premio']}")
            total = len(st.session_state.participantes)
            meta = st.session_state.config['meta']
            
            c1, c2 = st.columns(2)
            c1.metric("Participantes", f"{total} / {meta}")
            c2.progress(min(total/meta, 1.0) if meta > 0 else 0)
            
            st.divider()
            if st.session_state.participantes:
                df = pd.DataFrame(st.session_state.participantes)
                st.table(df[["Nombre", "Apellido", "Hora"]].iloc[::-1].head(15))
            else:
                st.info("Esperando los primeros participantes...")

            if st.button("🎰 SORTEAR AHORA", use_container_width=True):
                if total > 0:
                    st.session_state.ganador = random.choice(st.session_state.participantes)
                    st.balloons()
            
            if st.session_state.ganador:
                st.success(f"🏆 EL GANADOR ES: {st.session_state.ganador['Nombre']} {st.session_state.ganador['Apellido']}")

        # --- AJUSTES Y LINKS ---
        elif menu == "⚙️ Configuración":
            st.title("Ajustes del Sorteo")
            st.session_state.config['meta'] = st.number_input("Meta de boletos", value=st.session_state.config['meta'])
            st.session_state.config['precio'] = st.text_input("Precio del boleto (USD)", value=st.session_state.config['precio'])
            st.session_state.config['premio'] = st.text_input("Nombre del premio", value=st.session_state.config['premio'])

            st.divider()
            st.subheader("🔗 LINK PARA LOS SEGUIDORES")
            
            # Cambia esta URL por la de tu app real si es diferente
            url_real = "https://rifa-tony-final-n6sp2uzx2pwyrnx4gkkn8r.streamlit.app?modo=registro" 
            link_chat = f"{url_real}?view=public"
            
            st.code(link_chat)
            st.info("Copia el link de arriba y pégalo en el chat de tu directo.")
            
            if st.button("🗑️ Borrar toda la lista"):
                st.session_state.participantes = []
                st.session_state.ganador = None
                st.rerun()
