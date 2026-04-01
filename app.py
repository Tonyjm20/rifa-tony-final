import streamlit as st
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Rifa TonyJM20", layout="wide")

# Base de datos temporal (Se mantiene mientras la pestaña esté abierta)
if 'participantes' not in st.session_state:
    st.session_state.participantes = []
if 'ganador' not in st.session_state:
    st.session_state.ganador = None
if 'config' not in st.session_state:
    st.session_state.config = {
        "meta": 50, 
        "precio": 10.0, 
        "premio": "Insecto Especial",
        "client_id": "TU_CLIENT_ID_AQUI" # <--- REEMPLAZA ESTO
    }

# --- 2. NAVEGACIÓN ---
st.sidebar.title("🎮 Menú Rifa")
menu = st.sidebar.radio("Secciones", ["🎟️ Registro y Pago", "📺 Pantalla Stream", "🔐 Admin"])

# ==========================================
# SECCIÓN 1: REGISTRO Y PAGO
# ==========================================
if menu == "🎟️ Registro y Pago":
    st.title(f"🎟️ Participa por: {st.session_state.config['premio']}")
    st.write(f"Valor del boleto: **${st.session_state.config['precio']} USD**")
    
    # --- PASO 1: DATOS ---
    st.subheader("Paso 1: Ingresa tus datos")
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
        email = st.text_input("Correo Electrónico")
    with col2:
        u_game = st.text_input("Usuario en el Juego")
        id_game = st.text_input("ID de Cuenta")

    st.divider()

    # --- PASO 2: PAGO ---
    st.subheader("Paso 2: Realiza el pago")
    st.info("Al completar el pago con PayPal o Tarjeta, presiona el botón 'FINALIZAR REGISTRO' abajo.")
    
    # Código de PayPal optimizado
    paypal_js = f"""
        <html>
        <head><meta name="viewport" content="width=device-width, initial-scale=1"></head>
        <body>
            <div id="paypal-button-container"></div>
            <script src="https://www.paypal.com/sdk/js?client-id={st.session_state.config['client_id']}&currency=USD"></script>
            <script>
                paypal.Buttons({{
                    style: {{ layout: 'vertical', color: 'gold', shape: 'rect' }},
                    createOrder: function(data, actions) {{
                        return actions.order.create({{
                            purchase_units: [{{ amount: {{ value: '{st.session_state.config["precio"]}' }} }}]
                        }});
                    }},
                    onApprove: function(data, actions) {{
                        return actions.order.capture().then(function(details) {{
                            alert('¡Pago de ' + details.payer.name.given_name + ' completado! Ahora haz clic en el botón verde de abajo.');
                        }});
                    }}
                }}).render('#paypal-button-container');
            </script>
        </body>
        </html>
    """
    # Altura de 500 para que el botón de tarjeta se vea SI O SI
    components.html(paypal_js, height=500, scrolling=False)

    # --- PASO 3: CONFIRMACIÓN ---
    if st.button("✅ FINALIZAR REGISTRO Y APARECER EN STREAM", use_container_width=True):
        if nombre and id_game and email:
            nuevo_p = {
                "Nombre": nombre, "Apellido": apellido, 
                "User": u_game, "ID": id_game, 
                "Email": email, "Fecha": time.strftime("%H:%M")
            }
            st.session_state.participantes.append(nuevo_p)
            st.success(f"¡Hecho {nombre}! Ya estás en la lista. ¡Mucha suerte!")
        else:
            st.error("Por favor, llena tus datos antes de finalizar.")

# ==========================================
# SECCIÓN 2: PANTALLA STREAM (OBS)
# ==========================================
elif menu == "📺 Pantalla Stream":
    st.title(f"🏆 Sorteo en Vivo: {st.session_state.config['premio']}")
    
    total = len(st.session_state.participantes)
    meta = st.session_state.config['meta']
    progreso = min(total/meta, 1.0) if meta > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Boletos Vendidos", f"{total} / {meta}")
    c2.metric("Precio", f"${st.session_state.config['precio']}")
    c3.metric("Faltan", max(0, meta - total))

    st.progress(progreso)
    st.divider()
    
    col_l, col_s = st.columns([2, 1])
    with col_l:
        st.subheader("📋 Participantes")
        if st.session_state.participantes:
            df = pd.DataFrame(st.session_state.participantes)
            st.table(df[["Nombre", "Apellido"]].iloc[::-1].head(12))
    
    with col_s:
        st.subheader("🎲 El Sorteo")
        if st.button("🔥 ¡GIRAR RULETA! 🔥", use_container_width=True):
            if total > 0:
                with st.spinner("Sorteando..."):
                    time.sleep(3)
                    st.session_state.ganador = random.choice(st.session_state.participantes)
                    st.balloons()
        
        if st.session_state.ganador:
            st.markdown(f"""
                <div style="background-color:#FFD700; padding:20px; border-radius:10px; text-align:center; color:black;">
                    <h3>🏆 GANADOR:</h3>
                    <h2>{st.session_state.ganador['Nombre']} {st.session_state.ganador['Apellido']}</h2>
                </div>
            """, unsafe_allow_html=True)

# ==========================================
# SECCIÓN 3: ADMIN
# ==========================================
elif menu == "🔐 Admin":
    clave = st.text_input("Clave de Admin", type="password")
    if clave == "tonyjm": # <--- Cambia esto
        st.subheader("Ajustes del Sorteo")
        st.session_state.config['meta'] = st.number_input("Meta de Boletos", value=st.session_state.config['meta'])
        st.session_state.config['precio'] = st.number_input("Precio ($)", value=st.session_state.config['precio'])
        
        if st.button("Limpiar Lista / Nueva Rifa"):
            st.session_state.participantes = []
            st.session_state.ganador = None
            st.rerun()

        if st.session_state.participantes:
            st.divider()
            df_admin = pd.DataFrame(st.session_state.participantes)
            st.dataframe(df_admin)
            csv = df_admin.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar Backup Excel", csv, "rifa.csv", "text/csv")
