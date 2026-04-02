import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Rifa Tony AFK", layout="wide", initial_sidebar_state="collapsed")

# --- 2. CONEXIÓN A GOOGLE SHEETS (TIEMPO REAL) ---
conn = st.connection("gsheets", type=GSheetsConnection)

def leer_datos():
    # ttl=0 obliga a Streamlit a leer el Excel real en cada refresco
    return conn.read(worksheet="Hoja 1", ttl=0)

def registrar_en_sheets(nombre, apellido, user_game, id_game, email):
    try:
        df_actual = leer_datos()
        nueva_fila = pd.DataFrame([{
            "Nombre": nombre,
            "Apellido": apellido,
            "User": user_game,
            "ID": id_game,
            "Email": email,
            "Fecha": time.strftime("%d/%m/%Y %H:%M:%S")
        }])
        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
        conn.update(worksheet="Hoja 1", data=df_final)
        st.cache_data.clear()
        return True
    except Exception as e:
        st.error(f"Error de conexión con Sheets: {e}")
        return False

# --- 3. VARIABLES DE SESIÓN ---
if 'config' not in st.session_state:
    st.session_state.config = {"meta": 50, "precio": "10.00", "premio": "Insecto Especial"}

# Reemplaza con tu Client ID real
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl" 
CLAVE_MAESTRO = "tonyjm20"

# --- 4. DETECTOR DE VISTAS ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

# ==========================================
# VISTA SEGUIDOR (REGISTRO Y PAGO)
# ==========================================
if es_seguidor:
    st.title(f"🎟️ Participa por: {st.session_state.config['premio']}")
    p_actual = str(st.session_state.config['precio']).strip()
    st.write(f"### Costo: **${p_actual} USD**")

    with st.form("form_pago"):
        col1, col2 = st.columns(2)
        with col1:
            n = st.text_input("Nombre")
            a = st.text_input("Apellido")
            e = st.text_input("Email")
        with col2:
            u = st.text_input("User del Juego")
            i = st.text_input("ID del Juego")
        
        confirmar = st.form_submit_button("1. Validar Datos")

    if confirmar or (n and i):
        st.success("✅ Datos validados. Ahora procede al pago:")
        
        paypal_html = f"""
        <div id="paypal-button-container"></div>
        <script src="https://www.paypal.com/sdk/js?client-id={CLIENT_ID_PAYPAL}&currency=USD"></script>
        <script>
            paypal.Buttons({{
                style: {{ layout: 'vertical', color: 'gold', shape: 'rect' }},
                createOrder: function(data, actions) {{
                    return actions.order.create({{
                        purchase_units: [{{ amount: {{ value: '{p_actual}' }} }}]
                    }});
                }},
                onApprove: function(data, actions) {{
                    return actions.order.capture().then(function(details) {{
                        const url = new URL(window.location.href);
                        url.searchParams.set('pago', 'ok');
                        url.searchParams.set('n', '{n}');
                        url.searchParams.set('ape', '{a}');
                        url.searchParams.set('u', '{u}');
                        url.searchParams.set('id', '{i}');
                        url.searchParams.set('em', '{e}');
                        window.location.href = url.href;
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_html, height=600)

        if params.get("pago") == "ok":
            with st.spinner("Guardando en la lista oficial..."):
                registrar_en_sheets(
                    params.get("n"), params.get("ape"), 
                    params.get("u"), params.get("id"), params.get("em")
                )
                st.balloons()
                st.success("¡ESTÁS DENTRO! Revisa la pantalla del stream.")
                time.sleep(3)
                st.query_params.clear()
                st.query_params.update({"view": "registro"})

# ==========================================
# VISTA TONY (STREAM Y ADMIN)
# ==========================================
else:
    st.sidebar.title("🔐 Panel Maestro")
    acceso = st.sidebar.text_input("Contraseña", type="password")
    
    if acceso == CLAVE_MAESTRO:
        menu = st.sidebar.radio("Ir a:", ["📺 Pantalla Stream", "⚙️ Ajustes"])

        if menu == "📺 Pantalla Stream":
            st.title(f"🏆 Gran Rifa: {st.session_state.config['premio']}")
            
            # Leer desde Google Sheets
            df = leer_datos()
            total = len(df)
            meta = st.session_state.config['meta']
            
            c1, c2 = st.columns(2)
            c1.metric("Participantes", f"{total} / {meta}")
            c2.progress(min(total/meta, 1.0) if meta > 0 else 0)

            st.divider()
            if not df.empty:
                # Mostrar solo Nombre y User para el público
                st.table(df[["Nombre", "User", "Fecha"]].iloc[::-1])
            
            if st.button("🎰 GIRAR RULETA (SORTEAR)"):
                if total > 0:
                    ganador = random.choice(df['Nombre'].tolist())
                    st.header(f"🎊 ¡GANADOR: {ganador}! 🎊")
                    st.balloons()

        elif menu == "⚙️ Ajustes":
            st.title("Configuración")
            st.session_state.config['premio'] = st.text_input("Premio", value=st.session_state.config['premio'])
            st.session_state.config['meta'] = st.number_input("Meta de boletos", value=st.session_state.config['meta'])
            st.session_state.config['precio'] = st.text_input("Precio ($)", value=st.session_state.config['precio'])
            
            st.divider()
            st.subheader("🔗 Link para el Chat")
            st.code("https://rifa-tony-final-n6sp2uzx2pwyrnx4gkkn8r.streamlit.app?view=registro")
            
            if st.button("🗑️ Borrar toda la lista"):
                conn.update(worksheet="Hoja 1", data=pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"]))
                st.rerun()
    else:
        st.info("Ingresa la clave para ver el Panel de Control.")
