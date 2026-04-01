import streamlit as st
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Rifa Automática TonyJM20", layout="wide", initial_sidebar_state="collapsed")

# Persistencia de datos en la sesión actual
if 'participantes' not in st.session_state:
    st.session_state.participantes = []
if 'ganador' not in st.session_state:
    st.session_state.ganador = None

# --- CONFIGURACIÓN TÉCNICA ---
# RECUERDA: Pega tu Client ID real aquí
CLIENT_ID_PAYPAL = "AQUÍ_PEGA_TU_CLIENT_ID_DE_PAYPAL" 
CLAVE_MAESTRO = "tonyjm" 

if 'config' not in st.session_state:
    st.session_state.config = {
        "meta": 50, 
        "precio": "10.00", 
        "premio": "Insecto Especial - The Ants"
    }

# --- 2. FILTRO DE VISTA ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

# ==========================================
# VISTA SEGUIDOR (AUTOMATIZADA)
# ==========================================
if es_seguidor:
    st.title(f"🎟️ Sorteo: {st.session_state.config['premio']}")
    st.markdown(f"### Valor: **${st.session_state.config['precio']} USD**")
    
    st.info("Escribe tus datos y paga. Al finalizar el pago, aparecerás automáticamente en el stream.")
    
    # Campos de datos
    nom = st.text_input("Nombre y Apellido")
    u_g = st.text_input("Usuario / ID del Juego")

    st.divider()

    if nom and u_g:
        # SCRIPT DE PAYPAL CON AUTO-REGISTRO
        # Este script detecta el pago y recarga la página enviando los datos a la URL
        paypal_html = f"""
        <div id="paypal-button-container"></div>
        <script src="https://www.paypal.com/sdk/js?client-id={CLIENT_ID_PAYPAL}&currency=USD"></script>
        <script>
            paypal.Buttons({{
                style: {{ layout: 'vertical', color: 'gold', shape: 'rect' }},
                createOrder: function(data, actions) {{
                    return actions.order.create({{
                        purchase_units: [{{ amount: {{ value: '{st.session_state.config['precio']}' }} }}]
                    }});
                }},
                onApprove: function(data, actions) {{
                    return actions.order.capture().then(function(details) {{
                        // Al pagar con éxito, redirigimos con los datos en la URL para que Python los guarde
                        const url = new URL(window.location.href);
                        url.searchParams.set('pago', 'exitoso');
                        url.searchParams.set('n', '{nom}');
                        url.searchParams.set('id', '{u_g}');
                        window.location.href = url.href;
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_html, height=550)
        
        # LÓGICA DE CAPTURA POST-PAGO
        # Si la URL contiene 'pago=exitoso', guardamos al usuario automáticamente
        if params.get("pago") == "exitoso":
            nuevo_nombre = params.get("n")
            nuevo_id = params.get("id")
            
            # Verificamos si ya está para no duplicar al refrescar
            existe = any(p['Nombre'] == nuevo_nombre for p in st.session_state.participantes)
            if not existe:
                st.session_state.participantes.append({
                    "Nombre": nuevo_nombre,
                    "ID": nuevo_id,
                    "Hora": time.strftime("%H:%M")
                })
                st.success(f"¡Pago verificado! {nuevo_nombre}, ya estás en la lista.")
                time.sleep(2)
                # Limpiamos la URL para que no se duplique al refrescar manualmente
                st.query_params.clear()
                st.query_params.update({"view": "registro"})
    else:
        st.warning("⚠️ Debes completar tu Nombre e ID para habilitar el pago.")

# ==========================================
# VISTA TONY (ADMIN & STREAM)
# ==========================================
else:
    st.sidebar.title("🔐 Panel Maestro")
    if st.sidebar.text_input("Clave", type="password") == CLAVE_MAESTRO:
        menu = st.sidebar.radio("Ir a:", ["📺 Pantalla Stream", "⚙️ Ajustes"])

        if menu == "📺 Pantalla Stream":
            st.title(f"🏆 Rifa en Vivo: {st.session_state.config['premio']}")
            total = len(st.session_state.participantes)
            st.metric("Participantes Automáticos", f"{total} / {st.session_state.config['meta']}")
            
            st.divider()
            if st.session_state.participantes:
                df = pd.DataFrame(st.session_state.participantes)
                st.table(df[["Nombre", "Hora"]].iloc[::-1])
            else:
                st.write("Esperando pagos...")

            if st.button("🎰 SORTEAR"):
                if total > 0:
                    st.session_state.ganador = random.choice(st.session_state.participantes)
                    st.balloons()
            
            if st.session_state.ganador:
                st.success(f"¡GANADOR: {st.session_state.ganador['Nombre']}!")

        elif menu == "⚙️ Ajustes":
            st.title("Configuración")
            st.session_state.config['precio'] = st.text_input("Precio ($)", value=st.session_state.config['precio'])
            st.write(f"Link para seguidores: `https://rifa-tony-final-n6sp2uzx2pwyrnx4gkkn8r.streamlit.app`")
            
            if st.button("🗑️ Resetear Todo"):
                st.session_state.participantes = []
                st.rerun()
