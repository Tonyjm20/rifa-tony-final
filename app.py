import streamlit as st
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN DE SEGURIDAD ---
st.set_page_config(page_title="Sorteo Oficial TonyJM20", layout="wide", initial_sidebar_state="collapsed")

# Memoria de la sesión (No cerrar la pestaña del PC de transmisión)
if 'participantes' not in st.session_state:
    st.session_state.participantes = []
if 'ganador' not in st.session_state:
    st.session_state.ganador = None

# --- CONFIGURACIÓN CRÍTICA (EDITA AQUÍ) ---
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl" 
CLAVE_MAESTRO = "tonyjm20" # Esta es la llave para entrar a TU panel

if 'config' not in st.session_state:
    st.session_state.config = {
        "meta": 50, 
        "precio": "10.00", 
        "premio": "Insecto Especial - The Ants"
    }

# --- 2. DETECTOR DE ROL (¿Quién está entrando?) ---
params = st.query_params
# Si el link termina en ?view=public, es un seguidor.
es_seguidor = params.get("view") == "public"

# ==========================================
# INTERFAZ PARA SEGUIDORES (Link de Chat)
# ==========================================
if es_seguidor:
    st.title(f"🎟️ Sorteo: {st.session_state.config['premio']}")
    st.info(f"Participa por solo ${st.session_state.config['precio']} USD")
    
    st.subheader("1. Tus Datos")
    c1, c2 = st.columns(2)
    with c1:
        nom = st.text_input("Nombre")
        ape = st.text_input("Apellido")
    with c2:
        u_g = st.text_input("User Juego")
        id_g = st.text_input("ID Cuenta")
    
    st.divider()

    st.subheader("2. Pago Seguro")
    if CLIENT_ID_PAYPAL == "AQUÍ_PEGA_TU_CLIENT_ID_DE_PAYPAL":
        st.error("Error: PayPal no configurado.")
    else:
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
                        alert('¡Pago exitoso! Presiona el botón de abajo para terminar.');
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_html, height=500)

    if st.button("✅ FINALIZAR MI REGISTRO", use_container_width=True):
        if nom and id_g:
            st.session_state.participantes.append({
                "Nombre": nom, "Apellido": ape, "User": u_g, "ID": id_g, "Hora": time.strftime("%H:%M")
            })
            st.success("¡Registrado! Ya puedes ver tu nombre en el directo.")
        else:
            st.error("Completa tus datos.")

# ==========================================
# INTERFAZ PARA TONY (Link Maestro)
# ==========================================
else:
    st.sidebar.title("🔐 Acceso Maestro")
    pass_input = st.sidebar.text_input("Contraseña", type="password")
    
    if pass_input != CLAVE_MAESTRO:
        st.title("🛡️ Área Protegida")
        st.warning("Ingresa la contraseña en el menú de la izquierda para gestionar el sorteo.")
    else:
        menu = st.sidebar.radio("Ir a:", ["📺 Pantalla Stream", "⚙️ Ajustes", "🎟️ Vista Registro"])

        # --- PANTALLA STREAM ---
        if menu == "📺 Pantalla Stream":
            st.title(f"🏆 Rifa en Vivo: {st.session_state.config['premio']}")
            total = len(st.session_state.participantes)
            meta = st.session_state.config['meta']
            
            st.metric("Participantes", f"{total} / {meta}")
            st.progress(min(total/meta, 1.0) if meta > 0 else 0)
            
            st.divider()
            if st.session_state.participantes:
                df = pd.DataFrame(st.session_state.participantes)
                st.table(df[["Nombre", "Apellido", "Hora"]].iloc[::-1].head(12))

            if st.button("🎰 SORTEAR"):
                st.session_state.ganador = random.choice(st.session_state.participantes)
                st.balloons()
            
            if st.session_state.ganador:
                st.success(f"GANADOR: {st.session_state.ganador['Nombre']}")

        # --- AJUSTES ---
        elif menu == "⚙️ Ajustes":
            st.title("Configuración")
            st.session_state.config['meta'] = st.number_input("Meta", value=st.session_state.config['meta'])
            st.session_state.config['precio'] = st.text_input("Precio ($)", value=st.session_state.config['precio'])
            
            st.divider()
            st.subheader("🔗 LINKS DE TRANSMISIÓN")
            
            # Generamos el link de los seguidores
            url_base = "https://rifa-tony-final.streamlit.app/"
            link_publico = f"{url_base}?view=public"
            
            st.write("Copia este link para el chat de YouTube:")
            st.code(link_publico)
            
            if st.button("🗑️ Resetear Lista"):
                st.session_state.participantes = []
                st.session_state.ganador = None
                st.rerun()

        # --- VISTA PREVIA ---
        elif menu == "🎟️ Vista Registro":
            st.info("Esta es una vista previa de lo que ven tus seguidores.")
            # Simplemente llamamos a una función o lógica de espejo aquí
            st.write("---")
