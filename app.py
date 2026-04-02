import streamlit as st
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Rifa TonyJM20", layout="wide", initial_sidebar_state="collapsed")

if 'participantes' not in st.session_state:
    st.session_state.participantes = []
if 'config' not in st.session_state:
    st.session_state.config = {
        "meta": 25, 
        "precio": "1.00", 
        "premio": "Insecto Especial Sinergia V"
    }

# --- CONFIGURACIÓN TÉCNICA ---
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl" 
CLAVE_MAESTRO = "tonyjm20" 

# --- 2. DETECTOR DE VISTA ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

# ==========================================
# VISTA SEGUIDOR (AUTOMATIZADA)
# ==========================================
if es_seguidor:
    st.title(f"🎟️ Sorteo: {st.session_state.config['premio']}")
    p_actual = str(st.session_state.config['precio']).strip()
    st.write(f"### Costo: **${p_actual} USD**")
    
    # Formulario para evitar recargas constantes y errores de Type
    with st.form("datos_pago"):
        nom = st.text_input("Nombre y Apellido")
        u_g = st.text_input("Usuario / ID Juego")
        confirmar = st.form_submit_button("Habilitar Botones de Pago")

    if confirmar or (nom and u_g):
        st.success("¡Datos listos! Elige tu método de pago abajo:")
        
        paypal_html = f"""
        <div id="paypal-button-container" style="min-height: 600px;"></div>
        <script src="https://www.paypal.com/sdk/js?client-id={CLIENT_ID_PAYPAL}&currency=USD"></script>
        <script>
            paypal.Buttons({{
                style: {{ layout: 'vertical', color: 'gold', shape: 'rect' }},
                createOrder: function(data, actions) {{
                    return actions.order.create({{
                        purchase_units: [{{ amount: {{ value: '{p_actual}' }} }}]
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
        
        if params.get("pago") == "ok":
            nombre_pago = params.get("n")
            if not any(p['Nombre'] == nombre_pago for p in st.session_state.participantes):
                st.session_state.participantes.append({"Nombre": nombre_pago, "Hora": time.strftime("%H:%M")})
                st.success(f"✅ ¡Pago verificado! {nombre_pago}, ya estás en la lista.")
                st.balloons()
                time.sleep(2)
                st.query_params.clear()
                st.query_params.update({"view": "registro"})
    else:
        st.warning("Completa el nombre para ver las opciones de PayPal y Tarjeta.")

# ==========================================
# VISTA TONY (ADMINISTRADOR)
# ==========================================
else:
    st.sidebar.title("🔐 Panel Maestro")
    if st.sidebar.text_input("Clave", type="password") == CLAVE_MAESTRO:
        menu = st.sidebar.radio("Ir a:", ["📺 Stream", "⚙️ Ajustes"])

        if menu == "📺 Stream":
            st.title(f"🏆 Rifa: {st.session_state.config['premio']}")
            total = len(st.session_state.participantes)
            st.metric("Participantes Reales", f"{total} / {st.session_state.config['meta']}")
            
            if st.session_state.participantes:
                st.table(pd.DataFrame(st.session_state.participantes)[["Nombre", "Hora"]].iloc[::-1])

            if st.button("🎰 SORTEAR"):
                if total > 0:
                    ganador = random.choice(st.session_state.participantes)
                    st.success(f"¡EL GANADOR ES: {ganador['Nombre']}!")
                    st.balloons()

        elif menu == "⚙️ Ajustes":
            st.title("Configuración de la Rifa")
            st.session_state.config['premio'] = st.text_input("Premio", value=st.session_state.config['premio'])
            st.session_state.config['meta'] = st.number_input("Meta de Boletos", value=st.session_state.config['meta'])
            st.session_state.config['precio'] = st.text_input("Precio ($)", value=st.session_state.config['precio'])
            
            st.divider()
            
            # --- AQUÍ ESTÁ EL TEMA DEL LINK ---
            st.subheader("🔗 Link para tus Seguidores")
            st.write("Copia la URL de tu navegador y agrégale esto al final:")
            st.code("https://rifa-tony-final-n6sp2uzx2pwyrnx4gkkn8r.streamlit.app?view=registro")
            st.info("Ejemplo: https://tu-app.streamlit.app/?view=registro")
            
            if st.button("🗑️ Borrar Lista"):
                st.session_state.participantes = []
                st.rerun()
