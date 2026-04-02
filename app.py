import streamlit as st
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Rifa Pro Tony AFK", layout="wide")

LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
CLAVE_ADMIN = "tonyjm20"
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl"

# --- 2. FUNCIÓN DE LECTURA CRÍTICA ---
def obtener_datos_frescos():
    # Limpiamos la memoria de Streamlit
    st.cache_data.clear()
    try:
        # Generamos un token único por cada milisegundo para romper el caché de Google
        token_seguridad = int(time.time() * 1000)
        url_ultra_fresca = f"{LINK_CSV}&cache_step={token_seguridad}"
        
        df = pd.read_csv(url_ultra_fresca)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

# --- 3. MANEJO DE SESIÓN ---
if 'conectado' not in st.session_state:
    st.session_state['conectado'] = False

# --- 4. NAVEGACIÓN ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

if es_seguidor:
    # --- VISTA SEGUIDOR (PayPal y Registro intactos) ---
    st.title("🎟️ Registro para el Sorteo")
    with st.form("registro"):
        c1, c2 = st.columns(2)
        with c1:
            n = st.text_input("Nombre")
            a = st.text_input("Apellido")
            e = st.text_input("Email")
        with c2:
            u = st.text_input("User del Juego")
            i = st.text_input("ID del Juego")
        if st.form_submit_button("Guardar Datos"):
            st.session_state['temp'] = {"n":n,"a":a,"u":u,"i":i,"e":e}
            st.success("Datos listos. Paga abajo.")
    
    if 'temp' in st.session_state:
        paypal_code = f"""
        <script src="https://www.paypal.com/sdk/js?client-id={CLIENT_ID_PAYPAL}&currency=USD"></script>
        <div id="paypal-button-container"></div>
        <script>
            paypal.Buttons({{
                createOrder: function(data, actions) {{
                    return actions.order.create({{ purchase_units: [{{ amount: {{ value: '20.00' }} }}] }});
                }},
                onApprove: function(data, actions) {{
                    return actions.order.capture().then(function(details) {{
                        window.location.href = window.location.origin + "/?view=registro&pago=ok";
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_code, height=500)
    
    if params.get("pago") == "ok":
        st.balloons()
        st.success("¡Pago exitoso! Estás registrado.")

else:
    # --- VISTA ADMIN (PANEL DE CONTROL) ---
    if not st.session_state['conectado']:
        st.sidebar.title("🔐 Acceso")
        pw = st.sidebar.text_input("Clave", type="password")
        if st.sidebar.button("Entrar"):
            if pw == CLAVE_ADMIN:
                st.session_state['conectado'] = True
                st.rerun()
            else: st.error("Error")
    else:
        st.title("📺 Panel de Transmisión")
        
        # Controles
        st.sidebar.header("⚙️ Configuración")
        meta = st.sidebar.number_input("Meta", min_value=1, value=50)
        
        # Botón de Actualizar: Ahora garantiza limpieza
        if st.sidebar.button("🔄 ACTUALIZAR DATOS", type="primary", use_container_width=True):
            st.rerun()

        st.sidebar.divider()
        
        # BOTÓN DE SORTEO: Hace una lectura extra de seguridad antes de elegir
        if st.sidebar.button("🎰 REALIZAR SORTEO", use_container_width=True):
            with st.spinner("Verificando lista final..."):
                df_final = obtener_datos_frescos()
                if not df_final.empty:
                    ganador = random.choice(df_final['Nombre'].tolist())
                    st.balloons()
                    st.title(f"🏆 GANADOR: {ganador.upper()} 🏆")
                    st.confetti = True # Visual opcional
                else:
                    st.error("Lista vacía en Sheets.")

        # MOSTRAR LISTA
        df = obtener_datos_frescos()
        total = len(df)
        
        st.progress(min(total / meta, 1.0))
        st.subheader(f"📊 Participantes: {total} / {meta}")
        
        if not df.empty:
            for index, row in df.iterrows():
                st.write(f"### {index + 1}. {row['Nombre']} {row['Apellido']} — ✅")
        
        if st.sidebar.button("Cerrar Sesión"):
            st.session_state['conectado'] = False
            st.rerun()
