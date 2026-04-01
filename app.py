import streamlit as st
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Rifa TonyJM20", layout="wide", initial_sidebar_state="collapsed")

if 'participantes' not in st.session_state:
    st.session_state.participantes = []
if 'ganador' not in st.session_state:
    st.session_state.ganador = None

# --- CONFIGURACIÓN TÉCNICA (EDITA AQUÍ) ---
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl" 
CLAVE_MAESTRO = "tonyjm20" 

# Mantenemos tus variables de control originales
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
# VISTA SEGUIDOR (INTERFAZ ORIGINAL)
# ==========================================
if es_seguidor:
    st.title(f"🎟️ Sorteo: {st.session_state.config['premio']}")
    st.markdown(f"### Costo: **${st.session_state.config['precio']} USD**")
    
    st.info("Completa tus datos y realiza el pago para aparecer en la lista automáticamente.")
    
    # Tus campos de siempre
    c1, c2 = st.columns(2)
    with c1:
        nom = st.text_input("Nombre y Apellido")
    with c2:
        u_g = st.text_input("Usuario / ID del Juego")

    st.divider()

    if nom and u_g:
        # EL BOTÓN DE PAYPAL QUE HACE TODO EL TRABAJO
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
                        const url = new URL(window.location.href);
                        url.searchParams.set('pago', 'ok');
                        url.searchParams.set('n', '{nom}');
                        url.searchParams.set('id', '{u_g}');
                        window.location.href = url.href;
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_html, height=550)
        
        # CAPTURA AUTOMÁTICA TRAS EL PAGO
        if params.get("pago") == "ok":
            n_pago = params.get("n")
            id_pago = params.get("id")
            
            # Evitar duplicados por refresco de página
            if not any(p['Nombre'] == n_pago for p in st.session_state.participantes):
                st.session_state.participantes.append({
                    "Nombre": n_pago,
                    "ID": id_pago,
                    "Hora": time.strftime("%H:%M")
                })
                st.success(f"✅ ¡Pago Verificado! Bienvenido a la rifa, {n_pago}.")
                time.sleep(2)
                st.query_params.clear()
                st.query_params.update({"view": "registro"})
    else:
        st.warning("⚠️ Escribe tu nombre e ID para habilitar el pago.")

# ==========================================
# VISTA TONY (INTERFAZ ORIGINAL)
# ==========================================
else:
    st.sidebar.title("🔐 Panel Maestro")
    if st.sidebar.text_input("Clave", type="password") == CLAVE_MAESTRO:
        menu = st.sidebar.radio("Navegar:", ["📺 Pantalla Stream", "⚙️ Configuración"])

        if menu == "📺 Pantalla Stream":
            st.title(f"🏆 Rifa: {st.session_state.config['premio']}")
            total = len(st.session_state.participantes)
            meta = st.session_state.config['meta']
            
            # Tus métricas de siempre
            c1, c2 = st.columns(2)
            c1.metric("Boletos Vendidos", f"{total} / {meta}")
            c2.progress(min(total/meta, 1.0) if meta > 0 else 0)
            
            st.divider()
            if st.session_state.participantes:
                df = pd.DataFrame(st.session_state.participantes)
                st.table(df[["Nombre", "Hora"]].iloc[::-1])

            if st.button("🎰 SORTEAR"):
                if total > 0:
                    st.session_state.ganador = random.choice(st.session_state.participantes)
                    st.balloons()
            
            if st.session_state.ganador:
                st.success(f"¡EL GANADOR ES: {st.session_state.ganador['Nombre']}!")

        elif menu == "⚙️ Configuración":
            st.title("Ajustes del Sorteo")
            # He devuelto todos tus campos de control
            st.session_state.config['premio'] = st.text_input("Nombre del Premio", value=st.session_state.config['premio'])
            st.session_state.config['meta'] = st.number_input("Meta de Boletos (Número)", value=st.session_state.config['meta'])
            st.session_state.config['precio'] = st.text_input("Precio por Boleto ($)", value=st.session_state.config['precio'])
            
            st.divider()
            st.subheader("🔗 Link para el Chat")
            url_app = "https://rifa-tony-final-n6sp2uzx2pwyrnx4gkkn8r.streamlit.app" 
            st.code(f"{url_app}?view=registro")
            
            if st.button("🗑️ Resetear Lista de Participantes"):
                st.session_state.participantes = []
                st.session_state.ganador = None
                st.rerun()
