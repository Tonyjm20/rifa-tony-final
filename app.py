import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(page_title="Rifa Tony AFK", layout="wide")

# --- 2. CONEXIÓN A GOOGLE SHEETS ---
# Conexión configurada para leer en tiempo real (ttl=0)
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 1. DEFINIR EL LINK PÚBLICO (Copia esto tal cual) ---
# Este link convierte tu Excel en un archivo que Python lee al instante
ID_HOJA = "1zBwqiaFjT3RfnAA19BBE37AHFGaz6oQZM2C3aVJC2uE"
URL_LECTURA = f"https://docs.google.com/spreadsheets/d/{ID_HOJA}/gviz/tq?tqx=out:csv&sheet=Hoja1"

# --- 2. LA FUNCIÓN DE LECTURA CORREGIDA ---
def leer_datos():
    try:
        # Intentamos leer por la vía rápida (Link Público)
        # index_col=False evita errores de columnas movidas
        df = pd.read_csv(URL_LECTURA, index_col=False)
        
        # Si el Excel está vacío, creamos las columnas para que no de error
        if df.empty:
            return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])
            
        return df
    except Exception as e:
        # Si falla la vía rápida, intentamos con la conexión oficial
        try:
            return conn.read(worksheet="Hoja1", ttl=0)
        except:
            st.error(f"Error crítico de base de datos: {e}")
            return pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"])

def registrar_en_sheets(nombre, apellido, user_game, id_game, email):
    try:
        df_actual = leer_datos()
        # Estructura exacta de tu Excel
        nueva_fila = pd.DataFrame([{
            "Nombre": nombre,
            "Apellido": apellido,
            "User": user_game,
            "ID": id_game,
            "Email": email,
            "Fecha": time.strftime("%d/%m/%Y %H:%M:%S")
        }])
        # Concatenamos y subimos
        df_final = pd.concat([df_actual, nueva_fila], ignore_index=True)
        conn.update(worksheet="Hoja 1", data=df_final)
        st.cache_data.clear() # Limpieza total de caché
        return True
    except Exception as e:
        st.error(f"Error al guardar: {e}")
        return False

# --- 3. CONFIGURACIÓN DEL SORTEO ---
if 'config' not in st.session_state:
    st.session_state.config = {"meta": 25, "precio": "1.00", "premio": "Insecto Especial"}

# REEMPLAZA ESTO CON TU CLIENT ID DE PAYPAL
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl"
CLAVE_ADMIN = "tonyjm20"

# --- 4. SISTEMA DE NAVEGACIÓN ---
params = st.query_params
es_seguidor = params.get("view") == "registro"

# ==========================================
# VISTA SEGUIDOR (REGISTRO + BOTÓN PAYPAL)
# ==========================================
if es_seguidor:
    st.title(f"🎟️ Participa por: {st.session_state.config['premio']}")
    precio_str = str(st.session_state.config['precio']).strip()
    
    st.info(f"Valor del cupo: **${precio_str} USD**")

    # Formulario de registro
    with st.form("form_registro"):
        c1, c2 = st.columns(2)
        with c1:
            n = st.text_input("Nombre")
            a = st.text_input("Apellido")
            em = st.text_input("Correo electrónico")
        with c2:
            u = st.text_input("Usuario (Nick)")
            i = st.text_input("ID del Juego")
        
        validar = st.form_submit_button("1. Validar Datos")

    if validar or (n and i):
        st.success("✅ Datos listos. Procede al pago para registrarte:")
        
        # Script de PayPal con redirección de datos
        paypal_code = f"""
        <div id="paypal-button-container"></div>
        <script src="https://www.paypal.com/sdk/js?client-id={CLIENT_ID_PAYPAL}&currency=USD"></script>
        <script>
            paypal.Buttons({{
                createOrder: function(data, actions) {{
                    return actions.order.create({{
                        purchase_units: [{{ amount: {{ value: '{precio_str}' }} }}]
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
                        url.searchParams.set('em', '{em}');
                        window.location.href = url.href;
                    }});
                }}
            }}).render('#paypal-button-container');
        </script>
        """
        components.html(paypal_code, height=550)

        # Captura tras el pago exitoso
        if params.get("pago") == "ok":
            with st.spinner("Registrando cupo..."):
                exito = registrar_en_sheets(
                    params.get("n"), params.get("ape"), 
                    params.get("u"), params.get("id"), params.get("em")
                )
                if exito:
                    st.balloons()
                    st.success("¡REGISTRO COMPLETADO EXITOSAMENTE!")
                    time.sleep(4)
                    st.query_params.clear()
                    st.query_params.update({"view": "registro"})

# ==========================================
# VISTA TONY (CONTROL Y STREAM)
# ==========================================
else:
    st.sidebar.title("🔐 Panel Admin")
    password = st.sidebar.text_input("Contraseña", type="password")
    
    if password == CLAVE_ADMIN:
        opcion = st.sidebar.radio("Navegar", ["📺 Vista OBS", "⚙️ Configuración"])

        if opcion == "📺 Vista OBS":
            st.header(f"🏆 Sorteo: {st.session_state.config['premio']}")
            
            # Datos en tiempo real desde Sheets
            df_display = leer_datos()
            total_inscritos = len(df_display)
            meta_rifa = st.session_state.config['meta']
            
            col_a, col_b = st.columns(2)
            col_a.metric("Participantes", f"{total_inscritos} / {meta_rifa}")
            col_b.progress(min(total_inscritos/meta_rifa, 1.0) if meta_rifa > 0 else 0)

            st.divider()
            st.subheader("Lista de Entrada")
            # Mostramos Nombre y User (el público no necesita ver el Email ni ID)
            if not df_display.empty:
                st.dataframe(df_display[["Nombre", "User", "Fecha"]].iloc[::-1], use_container_width=True)
            else:
                st.write("Esperando participantes...")

            if st.button("🎰 SORTEAR AHORA"):
                if total_inscritos > 0:
                    ganador = random.choice(df_display['Nombre'].tolist())
                    st.balloons()
                    st.success(f"🎊 ¡EL GANADOR ES: {ganador.upper()}! 🎊")

        elif opcion == "⚙️ Configuración":
            st.title("Ajustes Técnicos")
            st.session_state.config['premio'] = st.text_input("Nombre del Premio", value=st.session_state.config['premio'])
            st.session_state.config['meta'] = st.number_input("Meta de Cupos", value=st.session_state.config['meta'])
            st.session_state.config['precio'] = st.text_input("Precio del Cupo ($)", value=st.session_state.config['precio'])
            
            st.info("💡 Link para seguidores: Agrega `/?view=registro` al final de tu URL.")
            
            if st.button("🔴 REINICIAR TODA LA RIFA"):
                conn.update(worksheet="Hoja 1", data=pd.DataFrame(columns=["Nombre", "Apellido", "User", "ID", "Email", "Fecha"]))
                st.rerun()
    else:
        st.warning("Panel bloqueado. Ingresa la contraseña en el lateral.")
