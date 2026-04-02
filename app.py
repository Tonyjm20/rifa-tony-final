import streamlit as st
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Rifa Tony AFK - Oficial", layout="wide")

LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
CLAVE_ADMIN = "tonyjm20"
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl"

# --- 2. MANEJO DE SESIÓN (Para evitar que pida clave al refrescar) ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# --- 3. LÓGICA DE NAVEGACIÓN ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

if es_seguidor:
    # --- VISTA SEGUIDOR (REGISTRO + PAYPAL) ---
    st.title("🎟️ Registro y Pago del Sorteo")
    
    with st.form("formulario_registro"):
        st.subheader("Paso 1: Ingresa tus datos")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre")
            apellido = st.text_input("Apellido")
            correo = st.text_input("Email")
        with c2:
            usuario = st.text_input("User del Juego")
            id_juego = st.text_input("ID del Juego")
        
        btn_confirmar = st.form_submit_button("Confirmar Datos")

    if btn_confirmar:
        if nombre and id_juego and correo:
            st.session_state['datos_temp'] = {
                "n": nombre, "a": apellido, "u": usuario, "i": id_juego, "e": correo
            }
            st.success("✅ Datos guardados. Procede al pago abajo.")
        else:
            st.warning("⚠️ Completa los campos obligatorios.")

    if 'datos_temp' in st.session_state:
        st.divider()
        st.subheader("Paso 2: Pago con PayPal ($10.00)")
        d = st.session_state['datos_temp']
        
        # Botón de PayPal Intacto
        paypal_html = f"""
        <script src="https://www.paypal.com/sdk/js?client-id={CLIENT_ID_PAYPAL}&currency=USD"></script>
        <div id="paypal-button-container"></div>
        <script>
            paypal.Buttons({{
                createOrder: function(data, actions) {{
                    return actions.order.create({{
                        purchase_units: [{{ amount: {{ value: '10.00' }} }}]
                    }});
                }},
                onApprove: function(data, actions) {{
                    return actions.order.capture().then(function(details) {{
                        window.location.href = window.location.origin + "/?view=registro&pago=exito";
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_html, height=500)

    if params.get("pago") == "exito":
        st.balloons()
        st.success("¡Pago realizado con éxito! Tony te registrará en breve.")

else:
    # --- VISTA ADMIN (PANEL DE CONTROL) ---
    if not st.session_state['autenticado']:
        st.sidebar.title("🔐 Acceso Admin")
        pw = st.sidebar.text_input("Clave", type="password")
        if st.sidebar.button("Entrar"):
            if pw == CLAVE_ADMIN:
                st.session_state['autenticado'] = True
                st.rerun()
            else:
                st.error("Clave incorrecta")
    else:
        st.title("📺 Panel de Transmisión")
        
        # Sidebar
        st.sidebar.header("⚙️ Controles")
        meta = st.sidebar.number_input("Meta de Sorteo", min_value=1, value=50)
        
        # BOTÓN DE ACTUALIZAR (Refresca datos sin pedir clave)
        if st.sidebar.button("🔄 ACTUALIZAR LISTA", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.sidebar.divider()
        btn_sorteo = st.sidebar.button("🎰 REALIZAR SORTEO", use_container_width=True)

        # LECTURA DE DATOS (Original con pd.read_csv)
        try:
            url_fresca = f"{LINK_CSV}&t={int(time.time())}"
            df = pd.read_csv(url_fresca)
            df.columns = [c.strip() for c in df.columns]
        except:
            df = pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

        total = len(df)
        
        # BARRA DE PROGRESO (Tal cual la pediste)
        st.progress(min(total / meta, 1.0))
        st.subheader(f"📊 Participantes: {total} / {meta}")
        
        st.divider()
        
        if not df.empty:
            for index, row in df.iterrows():
                st.markdown(f"### **{index + 1}. {row['Nombre']} {row['Apellido']}** — ✅")
            
            if btn_sorteo:
                ganador = random.choice(df['Nombre'].tolist())
                st.balloons()
                st.success(f"🎊 ¡TENEMOS UN GANADOR! 🎊")
                st.title(f"🏆 {ganador.upper()} 🏆")
        else:
            st.info("Lista vacía. Dale a 'Actualizar Lista' cuando haya registros.")

        if st.sidebar.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()
