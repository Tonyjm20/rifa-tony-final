import streamlit as st
import pandas as pd
import random
import time
import requests
import io
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Rifa Pro Tony AFK", layout="wide")

# Link público del CSV
LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
CLAVE_ADMIN = "tonyjm20"
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl"

# --- 2. FUNCIÓN DE LECTURA DE ALTA PRIORIDAD (SIN CACHÉ) ---
def obtener_datos_reales():
    # Paso 1: Borrar cualquier memoria interna de Streamlit
    st.cache_data.clear()
    
    try:
        # Paso 2: Creamos un link ÚNICO cada milisegundo para engañar a Google
        # Esto obliga a Google a buscar el archivo real en su base de datos
        url_fresca = f"{LINK_CSV}&uuid={int(time.time() * 1000)}"
        
        # Paso 3: Petición con cabeceras que PROHÍBEN el caché al navegador y al servidor
        headers = {
            'Cache-Control': 'no-cache, no-store, must-revalidate',
            'Pragma': 'no-cache',
            'Expires': '0'
        }
        
        response = requests.get(url_fresca, headers=headers, timeout=10)
        
        if response.status_code == 200:
            # Convertimos el texto recibido en un DataFrame
            df = pd.read_csv(io.StringIO(response.text))
            # Limpiamos espacios en blanco en los nombres de las columnas
            df.columns = [c.strip() for c in df.columns]
            return df
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error de conexión con Google: {e}")
        return pd.DataFrame()

# --- 3. MANEJO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# --- 4. NAVEGACIÓN ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

if es_seguidor:
    # --- VISTA SEGUIDOR ---
    st.title("🎟️ Registro para el Sorteo ($20.00)")
    with st.form("registro_pago"):
        c1, c2 = st.columns(2)
        with c1:
            n = st.text_input("Nombre")
            a = st.text_input("Apellido")
            e = st.text_input("Email")
        with c2:
            u = st.text_input("User del Juego")
            id_j = st.text_input("ID del Juego")
        
        if st.form_submit_button("Confirmar Datos"):
            if n and id_j:
                st.session_state['temp_user'] = {"n":n,"a":a,"u":u,"i":id_j,"e":e}
                st.success("✅ Datos registrados. Procede al pago.")
            else:
                st.error("❌ Por favor completa los campos obligatorios.")
    
    if 'temp_user' in st.session_state:
        st.divider()
        paypal_html = f"""
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
        components.html(paypal_html, height=500)
    
    if params.get("pago") == "ok":
        st.balloons()
        st.success("¡Pago confirmado con éxito!")

else:
    # --- VISTA ADMIN ---
    if not st.session_state['autenticado']:
        st.sidebar.title("🔐 Acceso Admin")
        pw = st.sidebar.text_input("Contraseña", type="password")
        if st.sidebar.button("Entrar"):
            if pw == CLAVE_ADMIN:
                st.session_state['autenticado'] = True
                st.rerun()
            else: st.error("Clave incorrecta")
    else:
        st.title("📺 Panel de Transmisión - Tony AFK")
        
        st.sidebar.header("⚙️ Ajustes")
        meta = st.sidebar.number_input("Meta de Participantes", min_value=1, value=25)
        
        # BOTÓN REFRESCAR: Limpia todo y vuelve a leer
        if st.sidebar.button("🔄 ACTUALIZAR LISTA", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.sidebar.divider()
        
        # 1. LEEMOS LOS DATOS JUSTO ANTES DE MOSTRARLOS
        df_actual = obtener_datos_reales()
        total = len(df_actual)

        # 2. BOTÓN DE SORTEO: Usa los datos de arriba para evitar errores
        if st.sidebar.button("🎰 REALIZAR SORTEO", use_container_width=True):
            if total > 0:
                # Elige un ganador de la lista que estamos viendo
                ganador = df_actual.sample(n=1).iloc[0]
                st.balloons()
                st.title(f"🏆 ¡EL GANADOR ES! 🏆")
                st.header(f"✨ {ganador['Nombre'].upper()} {ganador['Apellido'].upper()} ✨")
                st.subheader(f"🎮 ID: {ganador.get('ID', 'N/A')} | User: {ganador.get('User', 'N/A')}")
            else:
                st.error("No hay participantes cargados en este momento.")

        # PROGRESO Y LISTA
        st.progress(min(total / meta, 1.0))
        st.write(f"### 📊 Registrados en Vivo: {total} / {meta}")
        
        if not df_actual.empty:
            for idx, row in df_actual.iterrows():
                st.write(f"**{idx + 1}.** {row['Nombre']} {row['Apellido']} — ✅")
        else:
            st.warning("La lista en Google Sheets parece estar vacía o no ha actualizado aún.")

        if st.sidebar.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()
