import streamlit as st
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Sorteo Tony AFK - Oficial", layout="wide")

LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
CLAVE_ADMIN = "tonyjm20"
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl"

# --- 2. FUNCIÓN DE LECTURA SIN CACHÉ (PARA EVITAR DATOS VIEJOS) ---
def obtener_datos_frescos():
    st.cache_data.clear() # Limpia la memoria de Streamlit
    try:
        # Token de tiempo para obligar a Google a soltar el archivo nuevo
        token = int(time.time() * 1000)
        url_final = f"{LINK_CSV}&nocache={token}"
        
        df = pd.read_csv(url_final)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

# --- 3. MANEJO DE SESIÓN ---
if 'autenticado' not in st.session_state:
    st.session_state['autenticado'] = False

# --- 4. LÓGICA DE NAVEGACIÓN ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

if es_seguidor:
    # --- VISTA SEGUIDOR ---
    st.title("🎟️ Registro para el Sorteo ($20.00)")
    with st.form("registro_pago"):
        st.subheader("1. Ingresa tus datos")
        c1, c2 = st.columns(2)
        with c1:
            n = st.text_input("Nombre")
            a = st.text_input("Apellido")
            e = st.text_input("Email")
        with c2:
            u = st.text_input("User del Juego")
            i = st.text_input("ID del Juego")
        
        if st.form_submit_button("Confirmar Datos"):
            if n and i and e:
                st.session_state['temp_user'] = {"n":n,"a":a,"u":u,"i":i,"e":e}
                st.success("✅ Datos listos. Realiza el pago abajo.")
            else:
                st.error("❌ Por favor completa los campos obligatorios.")
    
    if 'temp_user' in st.session_state:
        st.divider()
        st.subheader("2. Pago Seguro vía PayPal ($20.00)")
        # BOTÓN DE PAYPAL AJUSTADO A $20.00
        paypal_html = f"""
        <script src="https://www.paypal.com/sdk/js?client-id={CLIENT_ID_PAYPAL}&currency=USD"></script>
        <div id="paypal-button-container"></div>
        <script>
            paypal.Buttons({{
                createOrder: function(data, actions) {{
                    return actions.order.create({{
                        purchase_units: [{{ amount: {{ value: '20.00' }} }}]
                    }});
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
        st.success("¡Pago confirmado! Estás participando en la rifa.")

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
        st.title("📺 Panel de Transmisión - Sorteo en Vivo")
        
        # BARRA LATERAL
        st.sidebar.header("⚙️ Ajustes")
        # META AJUSTADA A 25 PERSONAS
        meta = st.sidebar.number_input("Meta de Participantes", min_value=1, value=25)
        
        if st.sidebar.button("🔄 REFRESCAR LISTA", type="primary", use_container_width=True):
            st.cache_data.clear()
            st.rerun()

        st.sidebar.divider()
        btn_sorteo = st.sidebar.button("🎰 REALIZAR SORTEO", use_container_width=True)

        # MOSTRAR DATOS
        df = obtener_datos_frescos()
        total = len(df)
        
        # PROGRESO
        st.progress(min(total / meta, 1.0))
        st.write(f"### 📊 Participantes: {total} / {meta}")
        
        st.divider()
        
        if not df.empty:
            # Lista de nombres
            for idx, row in df.iterrows():
                st.write(f"**{idx + 1}.** {row['Nombre']} {row['Apellido']} — ✅")
            
            # Lógica de Sorteo
            if btn_sorteo:
                with st.spinner("¡Buscando ganador en la lista real!"):
                    # Una última lectura forzada antes de elegir
                    df_final = obtener_datos_frescos()
                    ganador_index = random.randint(0, len(df_final) - 1)
                    ganador = df_final.iloc[ganador_index]
                    
                    st.balloons()
                    st.title(f"🏆 ¡EL GANADOR ES! 🏆")
                    st.header(f"✨ {ganador['Nombre'].upper()} {ganador['Apellido'].upper()} ✨")
                    st.subheader(f"🎮 User: {ganador.get('User', 'N/A')} | ID: {ganador.get('ID', 'N/A')}")
        else:
            st.info("Esperando participantes... Refresca cuando alguien haya pagado.")

        if st.sidebar.button("Cerrar Sesión"):
            st.session_state['autenticado'] = False
            st.rerun()
