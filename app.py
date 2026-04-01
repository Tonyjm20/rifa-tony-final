import streamlit as st
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Rifa TonyJM20", layout="wide")

# Memoria temporal para la rifa (No cerrar la pestaña del navegador)
if 'participantes' not in st.session_state:
    st.session_state.participantes = []
if 'ganador' not in st.session_state:
    st.session_state.ganador = None
if 'config' not in st.session_state:
    st.session_state.config = {
        "meta": 50, 
        "precio": "10.00", 
        "premio": "Insecto Especial - The Ants",
        "client_id": "TU_CLIENT_ID_AQUI" # <--- PEGA AQUÍ TU CLIENT ID DE PAYPAL
    }

# --- 2. NAVEGACIÓN ---
st.sidebar.title("🎮 Panel de Rifa")
menu = st.sidebar.radio("Ir a:", ["🎟️ Registro y Pago", "📺 Pantalla Stream", "🔐 Admin"])

# ==========================================
# SECCIÓN 1: REGISTRO Y PAGO
# ==========================================
if menu == "🎟️ Registro y Pago":
    st.title(f"🎟️ Sorteo: {st.session_state.config['premio']}")
    
    # --- PASO 1: DATOS DEL USUARIO ---
    st.subheader("Paso 1: Tus Datos")
    col1, col2 = st.columns(2)
    with col1:
        nombre = st.text_input("Nombre")
        apellido = st.text_input("Apellido")
    with col2:
        u_game = st.text_input("Usuario del Juego")
        id_game = st.text_input("ID de Cuenta")
    
    email = st.text_input("Correo Electrónico")

    st.write("---")

    # --- PASO 2: MÉTODO DE PAGO ---
    st.subheader("Paso 2: Realizar Pago")
    st.warning("Selecciona PayPal o Tarjeta de Débito/Crédito abajo.")

    # Código de PayPal encapsulado para evitar bloqueos de Streamlit
    paypal_component = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <style>
            body {{ margin: 0; display: flex; justify-content: center; }}
            #paypal-button-container {{ width: 100%; max-width: 400px; }}
        </style>
    </head>
    <body>
        <div id="paypal-button-container"></div>
        <script src="https://www.paypal.com/sdk/js?client-id={st.session_state.config['client_id']}&currency=USD&components=buttons"></script>
        <script>
            paypal.Buttons({{
                style: {{ layout: 'vertical', color: 'gold', shape: 'rect', label: 'paypal' }},
                createOrder: function(data, actions) {{
                    return actions.order.create({{
                        purchase_units: [{{ amount: {{ value: '{st.session_state.config['precio']}' }} }}]
                    }});
                }},
                onApprove: function(data, actions) {{
                    return actions.order.capture().then(function(details) {{
                        alert('¡Pago de ' + details.payer.name.given_name + ' completado con éxito!');
                        window.parent.postMessage("pago_ok", "*");
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
    </body>
    </html>
    """
    
    # Renderizamos el pago con suficiente altura para que se vea la tarjeta
    components.html(paypal_component, height=500)

    st.write("---")

    # --- PASO 3: CONFIRMACIÓN FINAL ---
    if st.button("✅ FINALIZAR REGISTRO", use_container_width=True):
        if nombre and id_game and email:
            nuevo = {{
                "Nombre": nombre, "Apellido": apellido, 
                "User": u_game, "ID": id_game, 
                "Email": email, "Hora": time.strftime("%H:%M:%S")
            }}
            st.session_state.participantes.append(nuevo)
            st.success("¡Registrado correctamente! Ya apareces en la pantalla del Stream.")
        else:
            st.error("Por favor, llena todos tus datos antes de finalizar.")

# ==========================================
# SECCIÓN 2: PANTALLA STREAM (LO QUE VE EL PÚBLICO)
# ==========================================
elif menu == "📺 Pantalla Stream":
    st.title(f"🏆 Rifa: {st.session_state.config['premio']}")
    
    total = len(st.session_state.participantes)
    meta = st.session_state.config['meta']
    progreso = min(total / meta, 1.0) if meta > 0 else 0
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Boletos Vendidos", f"{total} / {meta}")
    c2.metric("Precio", f"${st.session_state.config['precio']}")
    c3.metric("Faltan", max(0, meta - total))
    
    st.progress(progreso)
    st.write(f"Cargando meta: {int(progreso*100)}%")

    st.divider()

    col_l, col_s = st.columns([2, 1])
    
    with col_l:
        st.subheader("📋 Últimos Participantes")
        if st.session_state.participantes:
            df = pd.DataFrame(st.session_state.participantes)
            st.table(df[["Nombre", "Apellido"]].iloc[::-1].head(10))
        else:
            st.info("Esperando los primeros registros...")

    with col_s:
        st.subheader("🎲 Sorteo")
        if st.button("🔥 ¡GIRAR RULETA! 🔥", use_container_width=True):
            if total > 0:
                with st.spinner("Eligiendo ganador..."):
                    time.sleep(3)
                    st.session_state.ganador = random.choice(st.session_state.participantes)
                    st.balloons()
            else:
                st.error("No hay nadie en la lista.")
        
        if st.session_state.ganador:
            st.markdown(f"""
                <div style="background-color:#FFD700; padding:20px; border-radius:10px; text-align:center; color:black; border: 2px solid white;">
                    <h3>🏆 GANADOR:</h3>
                    <h2 style="margin:0;">{st.session_state.ganador['Nombre']} {st.session_state.ganador['Apellido']}</h2>
                </div>
            """, unsafe_allow_html=True)

# ==========================================
# SECCIÓN 3: ADMIN
# ==========================================
elif menu == "🔐 Admin":
    clave = st.text_input("Password", type="password")
    if clave == "tonyjm": # <--- Tu clave para entrar
        st.subheader("Configuración")
        st.session_state.config['meta'] = st.number_input("Meta de boletos", value=st.session_state.config['meta'])
        st.session_state.config['precio'] = st.text_input("Precio ($)", value=st.session_state.config['precio'])
        
        if st.button("Limpiar Sorteo"):
            st.session_state.participantes = []
            st.session_state.ganador = None
            st.rerun()
            
        if st.session_state.participantes:
            st.divider()
            df_admin = pd.DataFrame(st.session_state.participantes)
            st.dataframe(df_admin)
            csv = df_admin.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar Lista (CSV)", csv, "rifa_tony.csv", "text/csv")
