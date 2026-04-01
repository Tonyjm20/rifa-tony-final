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

# --- CONFIGURACIÓN TÉCNICA ---
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl" 
CLAVE_MAESTRO = "tonyjm20" 

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
# VISTA SEGUIDOR (PRECIO SINCRONIZADO)
# ==========================================
if es_seguidor:
    st.title(f"🎟️ Sorteo: {st.session_state.config['premio']}")
    precio_actual = st.session_state.config['precio']
    st.markdown(f"### Costo: **${precio_actual} USD**")
    
    st.info("Completa tus datos y paga. El registro es automático tras el pago.")
    
    c1, c2 = st.columns(2)
    with c1:
        nom = st.text_input("Nombre y Apellido")
    with c2:
        u_g = st.text_input("Usuario / ID del Juego")

    st.divider()

    if nom and u_g:
        # Usamos una clave única (key) basada en el precio para forzar el refresco del componente
        # Si cambias el precio en Admin, este bloque se destruye y se crea de nuevo con el nuevo valor
        paypal_html = f"""
        <div id="paypal-button-container" style="width: 100%; min-height: 700px;"></div>
        <script src="https://www.paypal.com/sdk/js?client-id={CLIENT_ID_PAYPAL}&currency=USD&disable-funding=credit"></script>
        <script>
            // Limpiamos el contenedor por si acaso
            document.getElementById('paypal-button-container').innerHTML = '';
            
            paypal.Buttons({{
                style: {{ layout: 'vertical', color: 'gold', shape: 'rect', label: 'pay' }},
                createOrder: function(data, actions) {{
                    return actions.order.create({{
                        purchase_units: [{{ 
                            amount: {{ 
                                value: '{precio_actual}' 
                            }} 
                        }}]
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
        # La 'key' en st.html o components.html es vital para que se actualice al cambiar el precio
        components.html(paypal_html, height=800, scrolling=True)
        
        if params.get("pago") == "ok":
            n_pago = params.get("n")
            id_pago = params.get("id")
            
            if not any(p['Nombre'] == n_pago for p in st.session_state.participantes):
                st.session_state.participantes.append({
                    "Nombre": n_pago,
                    "ID": id_pago,
                    "Hora": time.strftime("%H:%M")
                })
                st.success(f"✅ ¡Pago Verificado! {n_pago}, estás en la lista.")
                time.sleep(2)
                st.query_params.clear()
                st.query_params.update({"view": "registro"})
    else:
        st.warning("⚠️ Escribe tu nombre e ID para habilitar el pago.")

# ==========================================
# VISTA TONY (ADMIN)
# ==========================================
else:
    st.sidebar.title("🔐 Panel Maestro")
    if st.sidebar.text_input("Clave", type="password") == CLAVE_MAESTRO:
        menu = st.sidebar.radio("Navegar:", ["📺 Pantalla Stream", "⚙️ Configuración"])

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
                st.table(df[["Nombre", "Hora"]].iloc[::-1])

            if st.button("🎰 SORTEAR"):
                if total > 0:
                    st.session_state.ganador = random.choice(st.session_state.participantes)
                    st.balloons()
            
            if st.session_state.ganador:
                st.success(f"¡EL GANADOR ES: {st.session_state.ganador['Nombre']}!")

        elif menu == "⚙️ Configuración":
            st.title("Ajustes")
            st.session_state.config['premio'] = st.text_input("Premio", value=st.session_state.config['premio'])
            st.session_state.config['meta'] = st.number_input("Meta", value=st.session_state.config['meta'])
            
            # Al cambiar este valor, el seguidor verá el cambio reflejado en su botón de PayPal
            st.session_state.config['precio'] = st.text_input("Precio ($)", value=st.session_state.config['precio'])
            
            st.divider()
            st.subheader("🔗 Link para el Chat")
            st.code("https://rifa-tony-final-n6sp2uzx2pwyrnx4gkkn8r.streamlit.app")
            
            if st.button("🗑️ Resetear Lista"):
                st.session_state.participantes = []
                st.session_state.ganador = None
                st.rerun()
