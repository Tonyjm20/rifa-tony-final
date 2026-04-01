import streamlit as st
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="Rifa TonyJM20", layout="wide", initial_sidebar_state="collapsed")

# Memoria de la rifa (Se mantiene mientras TU pestaña de PC esté abierta)
if 'participantes' not in st.session_state:
    st.session_state.participantes = []
if 'ganador' not in st.session_state:
    st.session_state.ganador = None

# --- CONFIGURACIÓN CRÍTICA ---
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl" 
CLAVE_MAESTRO = "tonyjm20" 

if 'config' not in st.session_state:
    st.session_state.config = {
        "meta": 50, 
        "precio": "10.00", 
        "premio": "Insecto Especial - The Ants"
    }

# --- 2. EL FILTRO DE ENTRADA (AQUÍ ESTÁ LA SOLUCIÓN) ---
# Revisamos la URL. Si contiene 'view=registro', es UN SEGUIDOR.
query_params = st.query_params
es_seguidor = query_params.get("view") == "registro"

# ==========================================
# BLOQUE A: INTERFAZ EXCLUSIVA PARA SEGUIDORES
# ==========================================
if es_seguidor:
    st.title(f"🎟️ Sorteo: {st.session_state.config['premio']}")
    st.info(f"Costo por participación: ${st.session_state.config['precio']} USD")
    
    st.subheader("1. Datos de Registro")
    c1, c2 = st.columns(2)
    with c1:
        nom = st.text_input("Nombre")
        ape = st.text_input("Apellido")
    with c2:
        u_g = st.text_input("Usuario Juego")
        id_g = st.text_input("ID Cuenta")
    
    mail = st.text_input("Correo Electrónico")

    st.divider()

    st.subheader("2. Pago con PayPal o Tarjeta")
    if CLIENT_ID_PAYPAL == "AQUÍ_PEGA_TU_CLIENT_ID_DE_PAYPAL":
        st.error("Error: PayPal no configurado.")
    else:
        paypal_code = f"""
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
                        alert('¡Pago recibido con éxito!');
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_code, height=500)

    if st.button("✅ FINALIZAR REGISTRO", use_container_width=True):
        if nom and id_g:
            st.session_state.participantes.append({
                "Nombre": nom, "Apellido": ape, "User": u_g, "ID": id_g, "Email": mail, "Hora": time.strftime("%H:%M")
            })
            st.success("¡Registrado! Ya apareces en el Stream.")
        else:
            st.error("Llena tus datos antes de finalizar.")

# ==========================================
# BLOQUE B: INTERFAZ EXCLUSIVA PARA TONY (ADMIN)
# ==========================================
else:
    # Si entran por el link normal (sin ?view=registro), pedimos clave
    st.sidebar.title("🔐 Acceso TonyJM20")
    acceso = st.sidebar.text_input("Contraseña", type="password")
    
    if acceso != CLAVE_MAESTRO:
        st.title("🛡️ Panel de Control Protegido")
        st.write("Ingresa tu clave en la barra lateral para gestionar la rifa.")
    else:
        menu = st.sidebar.radio("Ir a:", ["📺 Pantalla Stream", "⚙️ Ajustes"])

        if menu == "📺 Pantalla Stream":
            st.title(f"🏆 Rifa: {st.session_state.config['premio']}")
            total = len(st.session_state.participantes)
            meta = st.session_state.config['meta']
            
            c1, c2 = st.columns(2)
            c1.metric("Boletos Vendidos", f"{total} / {meta}")
            c2.progress(min(total/meta, 1.0) if meta > 0 else 0)
            
            st.divider()
            if st.session_state.participantes:
                df = pd.DataFrame(st.session_state.participantes)
                st.table(df[["Nombre", "Apellido", "Hora"]].iloc[::-1].head(10))

            if st.button("🎰 SORTEAR AHORA"):
                if total > 0:
                    st.session_state.ganador = random.choice(st.session_state.participantes)
                    st.balloons()
            
            if st.session_state.ganador:
                st.success(f"¡GANADOR: {st.session_state.ganador['Nombre']} {st.session_state.ganador['Apellido']}!")

        elif menu == "⚙️ Ajustes":
            st.title("Configuración y Links")
            st.session_state.config['meta'] = st.number_input("Meta de boletos", value=st.session_state.config['meta'])
            st.session_state.config['precio'] = st.text_input("Precio ($)", value=st.session_state.config['precio'])
            
            st.divider()
            st.subheader("🔗 LINK PARA COMPARTIR EN EL CHAT")
            
            # Cambia esta URL por la tuya de Streamlit Cloud
            url_base = "https://rifa-tony-final-n6sp2uzx2pwyrnx4gkkn8r.streamlit.app" 
            link_para_chat = f"{url_base}?view=registro"
            
            st.code(link_para_chat)
            st.info("Copia el link de arriba. Cualquier persona que use ese link entrará DIRECTO al registro sin ver el Admin.")

            if st.button("🗑️ Borrar Participantes"):
                st.session_state.participantes = []
                st.session_state.ganador = None
                st.rerun()
