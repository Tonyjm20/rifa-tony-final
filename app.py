import streamlit as st
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN BASE ---
st.set_page_config(page_title="Rifa TonyJM20", layout="wide", initial_sidebar_state="collapsed")

# Inicializar variables si no existen
if 'participantes' not in st.session_state:
    st.session_state.participantes = []
if 'config' not in st.session_state:
    st.session_state.config = {
        "meta": 50, 
        "precio": "10.00", 
        "premio": "Insecto Especial"
    }

# --- CONFIGURACIÓN TÉCNICA (CAMBIA TU ID AQUÍ) ---
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQlL" 
CLAVE_MAESTRO = "tonyjm20" 

# --- 2. DETECTOR DE VISTA (URL) ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

# ==========================================
# VISTA SEGUIDOR (PÚBLICA)
# ==========================================
if es_seguidor:
    st.title(f"🎟️ Sorteo: {st.session_state.config['premio']}")
    precio_actual = st.session_state.config['precio']
    st.write(f"### Costo: **${precio_actual} USD**")
    
    # Formulario simple
    nom = st.text_input("Nombre y Apellido", key="nom_seg")
    u_g = st.text_input("Usuario / ID Juego", key="id_seg")

    st.divider()

    if nom and u_g:
        # Script de PayPal corregido para evitar la pantalla en negro
        paypal_html = f"""
        <div id="paypal-button-container" style="min-height: 600px;"></div>
        <script src="https://www.paypal.com/sdk/js?client-id={CLIENT_ID_PAYPAL}&currency=USD"></script>
        <script>
            paypal.Buttons({{
                style: {{ layout: 'vertical', color: 'gold', shape: 'rect' }},
                createOrder: function(data, actions) {{
                    return actions.order.create({{
                        purchase_units: [{{ amount: {{ value: '{precio_actual}' }} }}]
                    }});
                }},
                onApprove: function(data, actions) {{
                    return actions.order.capture().then(function(details) {{
                        const url = new URL(window.location.href);
                        url.searchParams.set('pago', 'ok');
                        url.searchParams.set('n', '{nom}');
                        window.location.href = url.href;
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_html, height=750, scrolling=True)
        
        # Procesar éxito del pago
        if params.get("pago") == "ok":
            nombre_pago = params.get("n")
            if not any(p['Nombre'] == nombre_pago for p in st.session_state.participantes):
                st.session_state.participantes.append({
                    "Nombre": nombre_pago,
                    "Hora": time.strftime("%H:%M")
                })
                st.success(f"✅ ¡Registrado con éxito, {nombre_pago}!")
                st.balloons()
                time.sleep(2)
                st.query_params.clear()
                st.query_params.update({"view": "registro"})
    else:
        st.warning("Escribe tu nombre para activar el pago.")

# ==========================================
# VISTA TONY (ADMINISTRADOR)
# ==========================================
else:
    st.sidebar.title("🔐 Panel Maestro")
    acceso = st.sidebar.text_input("Contraseña", type="password")
    
    if acceso != CLAVE_MAESTRO:
        st.title("🛡️ Área de Administración")
        st.info("Ingresa la clave en la barra lateral para ver el panel.")
    else:
        menu = st.sidebar.radio("Ir a:", ["📺 Stream", "⚙️ Ajustes"])

        if menu == "📺 Stream":
            st.title(f"🏆 Rifa: {st.session_state.config['premio']}")
            total = len(st.session_state.participantes)
            meta = st.session_state.config['meta']
            
            st.metric("Vendidos", f"{total} / {meta}")
            st.progress(min(total/meta, 1.0) if meta > 0 else 0)
            
            if st.session_state.participantes:
                df = pd.DataFrame(st.session_state.participantes)
                st.table(df[["Nombre", "Hora"]].iloc[::-1])

            if st.button("🎰 SORTEAR"):
                if total > 0:
                    ganador = random.choice(st.session_state.participantes)
                    st.success(f"¡GANADOR: {ganador['Nombre']}!")
                    st.balloons()

        elif menu == "⚙️ Ajustes":
            st.title("Configuración")
            st.session_state.config['premio'] = st.text_input("Premio", value=st.session_state.config['premio'])
            st.session_state.config['meta'] = st.number_input("Meta", value=st.session_state.config['meta'])
            st.session_state.config['precio'] = st.text_input("Precio ($)", value=st.session_state.config['precio'])
            
            st.divider()
            st.subheader("🔗 Link para tus seguidores")
            # Este es el link que debes pegar en WhatsApp o el chat
            st.code("https://rifa-tony-final.streamlit.app/?view=registro")
            
            if st.button("🗑️ Resetear Lista"):
                st.session_state.participantes = []
                st.rerun()
