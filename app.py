import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN ---
st.set_page_config(page_title="Rifa Tony AFK", layout="wide")

# SUSTITUYE ESTO POR TU ENLACE DE "PUBLICAR EN LA WEB" (EL QUE TERMINA EN .csv)
LINK_CSV = "https://docs.google.com/spreadsheets/d/e/2PACX-1vSx5dTlNFD_aegJHRA_MTKHp3S6JAkgCQdUQaiLKlJpvdI5HpMqNZDDWHMlUvjPPHFqUzbSTy1xNpxg/pub?output=csv"
ID_SHEET = "1zBwqiaFjT3RfnAA19BBE37AHFGaz6oQZM2C3aVJC2uE"
CLAVE_ADMIN = "tonyjm20"
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl"

# --- 2. CONEXIÓN PARA ESCRITURA ---
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_datos():
    try:
        # VÍA RÁPIDA: Lee el CSV público (Evita el error 401)
        # Añadimos un parámetro aleatorio para saltar el caché de Google
        url_final = f"{LINK_CSV}&cache={random.randint(1,99999)}"
        df = pd.read_csv(url_final)
        # Limpiar espacios en nombres de columnas
        df.columns = [c.strip() for c in df.columns]
        return df
    except Exception as e:
        # Si falla el link público, intenta la conexión interna
        try:
            return conn.read(worksheet="Hoja1", ttl=0)
        except:
            return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

def registrar_pago(n, ape, u, i, em):
    try:
        # Leemos el estado actual
        df_actual = leer_datos()
        nueva_fila = pd.DataFrame([{
            "Nombre": n, "Apellido": ape, "User": u, 
            "ID": i, "Email": em, "Fecha": time.strftime("%d/%m/%Y %H:%M:%S")
        }])
        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
        # Escribimos usando la conexión oficial (Requiere que los Secrets estén bien)
        conn.update(worksheet="Hoja1", data=df_final)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# --- 3. LÓGICA DE NAVEGACIÓN ---
if 'config' not in st.session_state:
    st.session_state.config = {"meta": 50, "precio": "10.00", "premio": "Premio Especial"}

params = st.query_params
es_seguidor = params.get("view") == "registro"

# ==========================================
# VISTA SEGUIDOR (PAGO)
# ==========================================
if es_seguidor:
    st.title(f"🎟️ Sorteo: {st.session_state.config['premio']}")
    precio = st.session_state.config['precio']
    
    with st.form("registro"):
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre")
            ap = st.text_input("Apellido")
            cor = st.text_input("Email")
        with c2:
            usr = st.text_input("User del Juego")
            idx = st.text_input("ID del Juego")
        validar = st.form_submit_button("Confirmar Datos")

    if validar or (nom and idx):
        st.info(f"Paga ${precio} USD para completar tu inscripción:")
        paypal_html = f"""
        <div id="paypal-button-container"></div>
        <script src="https://www.paypal.com/sdk/js?client-id={CLIENT_ID_PAYPAL}&currency=USD"></script>
        <script>
            paypal.Buttons({{
                createOrder: function(data, actions) {{
                    return actions.order.create({{ purchase_units: [{{ amount: {{ value: '{precio}' }} }}] }});
                }},
                onApprove: function(data, actions) {{
                    return actions.order.capture().then(function(details) {{
                        const url = new URL(window.location.href);
                        url.searchParams.set('pago', 'ok');
                        url.searchParams.set('n', '{nom}'); url.searchParams.set('ape', '{ap}');
                        url.searchParams.set('u', '{usr}'); url.searchParams.set('id', '{idx}');
                        url.searchParams.set('em', '{cor}');
                        window.location.href = url.href;
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_html, height=500)

        if params.get("pago") == "ok":
            with st.spinner("Registrando..."):
                if registrar_pago(params.get("n"), params.get("ape"), params.get("u"), params.get("id"), params.get("em")):
                    st.balloons()
                    st.success("¡LISTO! Ya estás en la lista.")
                    time.sleep(3)
                    st.query_params.clear()
                    st.query_params.update({"view": "registro"})

# ==========================================
# VISTA TONY (STREAM)
# ==========================================
else:
    st.sidebar.title("🔐 Admin")
    if st.sidebar.text_input("Clave", type="password") == CLAVE_ADMIN:
        mode = st.sidebar.radio("Modo", ["📺 Stream", "⚙️ Ajustes"])
        
        if mode == "📺 Stream":
            st.header(f"🏆 Rifa: {st.session_state.config['premio']}")
            df = leer_datos()
            total = len(df)
            meta = st.session_state.config['meta']
            
            c1, c2 = st.columns(2)
            c1.metric("Participantes", f"{total} / {meta}")
            c2.progress(min(total/meta, 1.0) if meta > 0 else 0)
            
            st.divider()
            
            if not df.empty:
                st.subheader("Lista de Participantes")
                
                # --- AQUÍ ESTÁ EL TRUCO PARA EL NOMBRE Y EL NÚMERO ---
                # Creamos una lista limpia para mostrar en el Stream
                lineas_participantes = []
                
                # Recorremos el DataFrame (el Excel) fila por fila
                for index, row in df.iterrows():
                    numero_llegada = index + 1
                    nombre_completo = f"{row['Nombre']} {row['Apellido']}"
                    # Formato: "1. Tony Jimenez - ¡Está participando!"
                    linea = f"### **{numero_llegada}. {nombre_completo}** — *¡Está participando!* ✅"
                    lineas_participantes.append(linea)
                
                # Invertimos la lista para que el último que llegó salga arriba (opcional)
                # Si prefieres que el 1 salga arriba, quita el [::-1]
                for p in lineas_participantes[::-1]:
                    st.markdown(p)
            
            else:
                st.write("Esperando al primer valiente... 🔎")
            
            if st.button("🎰 SORTEAR"):
                if total > 0:
                    ganador = random.choice(df['Nombre'].tolist())
                    st.header(f"🎊 ¡GANADOR: {ganador.upper()}! 🎊")
                    st.balloons()
