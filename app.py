import streamlit as st
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Rifa TonyJM20", layout="wide")

# Usamos la memoria del navegador para guardar los datos (Simple y sin errores)
if 'participantes' not in st.session_state:
    st.session_state.participantes = []
if 'ganador' not in st.session_state:
    st.session_state.ganador = None
if 'config' not in st.session_state:
    st.session_state.config = {
        "meta": 50, 
        "precio": 10.0, 
        "premio": "Nuevo Insecto Especial",
        "client_id": "TU_CLIENT_ID_AQUI" # <--- PEGA TU CLIENT ID AQUÍ
    }

# --- 2. NAVEGACIÓN ---
st.sidebar.title("🎮 Sorteo TonyJM")
menu = st.sidebar.radio("Ir a:", ["🎟️ Registro y Pago", "📺 Pantalla Stream", "🔐 Admin"])

# ==========================================
# SECCIÓN 1: REGISTRO Y PAGO
# ==========================================
if menu == "🎟️ Registro y Pago":
    st.title(f"Participa por: {st.session_state.config['premio']}")
    
    col_pago, col_datos = st.columns([1, 1])
    
    with col_pago:
        st.subheader("1. Pagar con PayPal o Tarjeta")
        # Este bloque es el que genera los botones de PayPal y Tarjeta
        paypal_html = f"""
            <div id="paypal-button-container" style="width: 100%; min-height: 500px;"></div>
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
                            alert('¡Pago de ' + details.payer.name.given_name + ' exitoso! Ahora llena tus datos a la derecha.');
                        }});
                    }}
                }}).render('#paypal-button-container');
            </script>
        """
        components.html(paypal_html, height=550, scrolling=True)

    with col_datos:
        st.subheader("2. Ingresa tus datos")
        with st.form("form_registro"):
            nombre = st.text_input("Nombre")
            apellido = st.text_input("Apellido")
            u_game = st.text_input("Usuario en el Juego")
            id_game = st.text_input("ID de Cuenta")
            email = st.text_input("Email")
            
            if st.form_submit_button("CONFIRMAR REGISTRO"):
                if nombre and id_game:
                    # Guardamos en la lista temporal
                    nuevo = {"Nombre": nombre, "Apellido": apellido, "User": u_game, "ID": id_game, "Email": email, "Fecha": time.strftime("%H:%M")}
                    st.session_state.participantes.append(nuevo)
                    st.success("¡Registrado! Revisa la pantalla del stream.")
                else:
                    st.error("Faltan datos obligatorios.")

# ==========================================
# SECCIÓN 2: PANTALLA STREAM (OBS)
# ==========================================
elif menu == "📺 Pantalla Stream":
    st.title(f"🏆 Sorteo: {st.session_state.config['premio']}")
    
    total = len(st.session_state.participantes)
    meta = st.session_state.config['meta']
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Boletos", f"{total} / {meta}")
    c2.metric("Precio", f"${st.session_state.config['precio']}")
    c3.progress(min(total/meta, 1.0) if meta > 0 else 0)

    st.divider()
    
    col_l, col_s = st.columns([2, 1])
    with col_l:
        st.subheader("👥 Participantes")
        if st.session_state.participantes:
            df = pd.DataFrame(st.session_state.participantes)
            st.table(df[["Nombre", "Apellido"]].iloc[::-1].head(10))
    
    with col_s:
        st.subheader("🎲 Sorteo")
        if st.button("🎰 TIRAR RULETA", use_container_width=True):
            if total > 0:
                with st.spinner("Eligiendo..."):
                    time.sleep(3)
                    st.session_state.ganador = random.choice(st.session_state.participantes)
                    st.balloons()
        
        if st.session_state.ganador:
            st.success(f"¡GANADOR: {st.session_state.ganador['Nombre']} {st.session_state.ganador['Apellido']}!")

# ==========================================
# SECCIÓN 3: ADMIN
# ==========================================
elif menu == "🔐 Admin":
    contra = st.text_input("Clave", type="password")
    if contra == "tonyjm": # <--- Tu clave
        st.session_state.config['meta'] = st.number_input("Meta", value=st.session_state.config['meta'])
        st.session_state.config['precio'] = st.number_input("Precio", value=st.session_state.config['precio'])
        
        if st.button("Reiniciar Rifa"):
            st.session_state.participantes = []
            st.session_state.ganador = None
            st.rerun()
            
        if st.session_state.participantes:
            st.subheader("Descargar Datos")
            df_admin = pd.DataFrame(st.session_state.participantes)
            st.dataframe(df_admin)
            # Botón para que descargues los datos y no los pierdas
            csv = df_admin.to_csv(index=False).encode('utf-8')
            st.download_button("Descargar Excel (CSV)", csv, "rifa.csv", "text/csv")
