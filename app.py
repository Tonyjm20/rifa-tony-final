import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Rifa Automática Tony AFK", layout="wide")

# Tus credenciales exactas
LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
CLAVE_ADMIN = "tonyjm20"
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl"

# Conexión para escritura (Usa los Secrets de Streamlit)
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_datos():
    try:
        # Lectura rápida por CSV para el OBS
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
        # Intento de escritura en la Hoja1
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
    st.title("🎟️ Registro y Pago del Sorteo")
    
    # 1. CAPTURA DE DATOS (Se guardan temporalmente en la sesión)
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
            # Guardamos en la memoria del navegador para el siguiente paso
            st.session_state['datos_pago'] = {
                "n": nombre, "a": apellido, "u": usuario, "i": id_juego, "e": correo
            }
            st.success("✅ Datos listos. Ahora realiza el pago abajo.")
        else:
            st.warning("⚠️ Por favor, completa los campos obligatorios (Nombre, ID y Email).")

    # 2. BOTÓN DE PAYPAL (Solo aparece si ya confirmó datos)
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
                    return actions.order.create({{
                        purchase_units: [{{ amount: {{ value: '10.00' }} }}]
                    }});
                }},
                onApprove: function(data, actions) {{
                    return actions.order.capture().then(function(details) {{
                        // Redirigimos pasando los datos en la URL para el registro final
                        const url = window.location.origin + "/?view=registro&pago=exito" +
                                    "&n={d['n']}&a={d['a']}&u={d['u']}&i={d['i']}&em={d['e']}";
                        window.location.href = url;
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_html, height=500)

    # 3. PROCESAMIENTO AUTOMÁTICO TRAS EL PAGO
    if params.get("pago") == "exito":
        st.balloons()
        with st.spinner("Registrando tu participación..."):
            # Extraemos los datos de la URL
            n_final = params.get("n")
            a_final = params.get("a")
            u_final = params.get("u")
            i_final = params.get("i")
            em_final = params.get("em")
            
            # Ejecutamos la escritura en el Excel
            exito = registrar_en_sheets(n_final, a_final, u_final, i_final, em_final)
            
            if exito:
                st.success(f"¡Excelente {n_final}! Ya estás en la lista. ¡Mucha suerte!")
            else:
                st.error("El pago se realizó, pero hubo un error al anotar tu nombre en el Excel.")
                st.info("No te preocupes, Tony tiene tu comprobante y te anotará manualmente.")

else:
    # VISTA ADMIN (PANEL PARA EL STREAM)
    st.sidebar.title("🔐 Admin")
    if st.sidebar.text_input("Clave", type="password") == CLAVE_ADMIN:
        st.title("📺 Panel de Transmisión")
        df = leer_datos()
        
        if not df.empty:
            st.metric("Participantes", len(df))
            for index, row in df.iterrows():
                st.markdown(f"### **{index + 1}. {row['Nombre']} {row['Apellido']}** — ✅ *Participando*")
            
            if st.button("🎰 REALIZAR SORTEO", type="primary"):
                ganador = random.choice(df['Nombre'].tolist())
                st.header(f"🎊 ¡GANADOR: {ganador.upper()}! 🎊")
                st.balloons()
        else:
            st.write("Esperando registros...")
