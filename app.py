import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Rifa Automática Tony AFK", layout="wide")

LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
CLAVE_ADMIN = "tonyjm20"
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl"

# Conexión para escritura
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_datos():
    try:
        url_fresca = f"{LINK_CSV}&t={int(time.time())}"
        df = pd.read_csv(url_fresca)
        df.columns = [c.strip() for c in df.columns]
        return df
    except:
        return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

def registrar_en_sheets(n, ape, u, i, em):
    try:
        df_actual = leer_datos()
        nueva_fila = pd.DataFrame([{
            "Nombre": n, "Apellido": ape, "User": u, 
            "ID": i, "Email": em, "Fecha": time.strftime("%d/%m/%Y %H:%M:%S")
        }])
        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
        conn.update(worksheet="Hoja1", data=df_final)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error al guardar en Google Sheets: {e}")
        return False

# --- LÓGICA DE NAVEGACIÓN ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

if es_seguidor:
    # --- VISTA DEL SEGUIDOR (REGISTRO + PAGO) ---
    st.title("🎟️ Registro y Pago del Sorteo")
    
    with st.form("formulario_pago"):
        st.subheader("Paso 1: Ingresa tus datos")
        c1, c2 = st.columns(2)
        with c1:
            nombre = st.text_input("Nombre")
            apellido = st.text_input("Apellido")
            correo = st.text_input("Email")
        with c2:
            usuario = st.text_input("User del Juego")
            id_juego = st.text_input("ID del Juego")
        btn_confirmar = st.form_submit_button("Confirmar Datos para Pagar")

    if btn_confirmar:
        if nombre and id_juego and correo:
            st.session_state['datos_pago'] = {"n": nombre, "a": apellido, "u": usuario, "i": id_juego, "e": correo}
            st.success("✅ Datos listos. Procede al pago abajo.")

    if 'datos_pago' in st.session_state:
        st.divider()
        st.subheader("Paso 2: Realizar Pago ($10.00)")
        d = st.session_state['datos_pago']
        paypal_html = f"""
        <script src="https://www.paypal.com/sdk/js?client-id={CLIENT_ID_PAYPAL}&currency=USD"></script>
        <div id="paypal-button-container"></div>
        <script>
            paypal.Buttons({{
                createOrder: function(data, actions) {{
                    return actions.order.create({{ purchase_units: [{{ amount: {{ value: '10.00' }} }}] }});
                }},
                onApprove: function(data, actions) {{
                    return actions.order.capture().then(function(details) {{
                        const url = window.location.origin + "/?view=registro&pago=exito" +
                                    "&n={d['n']}&a={d['a']}&u={d['u']}&i={d['i']}&em={d['e']}";
                        window.location.href = url;
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_html, height=500)

    if params.get("pago") == "exito":
        st.balloons()
        with st.spinner("Registrando participación..."):
            registrar_en_sheets(params.get("n"), params.get("a"), params.get("u"), params.get("i"), params.get("em"))
            st.success(f"¡Listo {params.get('n')}! Ya estás en la lista.")

else:
    # --- VISTA ADMIN (STREAM + BARRA DE PROGRESO) ---
    st.sidebar.title("🔐 Admin")
    if st.sidebar.text_input("Clave", type="password") == CLAVE_ADMIN:
        st.title("📺 Panel de Transmisión")
        
        # Configuración de la Meta
        meta = st.sidebar.number_input("Meta de participantes", min_value=1, value=50)
        
        df = leer_datos()
        total = len(df)
        
        # --- AQUÍ ESTÁ LA BARRA DE PROGRESO ---
        porcentaje = min(total / meta, 1.0)
        st.subheader(f"📊 Progreso: {total} de {meta} participantes")
        st.progress(porcentaje)
        
        c1, c2 = st.columns(2)
        c1.metric("Registrados", f"{total}")
        c2.metric("Faltan", max(0, meta - total))
        
        st.divider()
        
        if not df.empty:
            for index, row in df.iterrows():
                st.markdown(f"### **{index + 1}. {row['Nombre']} {row['Apellido']}** — ✅ *Participando*")
            
            if st.button("🎰 REALIZAR SORTEO", type="primary"):
                ganador = random.choice(df['Nombre'].tolist())
                st.header(f"🎊 ¡GANADOR: {ganador.upper()}! 🎊")
                st.balloons()
