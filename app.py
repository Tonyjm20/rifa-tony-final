import streamlit as st
import pandas as pd
import random
import time
import streamlit.components.v1 as components

# --- 1. CONFIGURACIÓN E INTERFAZ ---
st.set_page_config(page_title="Rifa Oficial TonyJM20", layout="wide", initial_sidebar_state="collapsed")

# Persistencia de datos
if 'participantes' not in st.session_state:
    st.session_state.participantes = []
if 'rifa_activa' not in st.session_state:
    st.session_state.rifa_activa = False
if 'ganador' not in st.session_state:
    st.session_state.ganador = None

# --- CONFIGURACIÓN TÉCNICA (EDITA ESTO) ---
CLIENT_ID_PAYPAL = "Aet4fqbdIlo68fTo3U7WcXax3B9UpCQI8QupSmw3IFBAw-OKF1A4XCcRvBS19VIh7e7MeQyicvqjCIQl" 
CLAVE_MAESTRO = "tonyjm20" 

if 'config' not in st.session_state:
    st.session_state.config = {
        "meta": 50, 
        "precio": "10.00", 
        "premio": "Insecto Especial - The Ants"
    }

# --- 2. LÓGICA DE RUTEO ---
params = st.query_params
es_publico = params.get("modo") == "registro"

if es_publico:
    menu = "🎟️ Registro"
else:
    st.sidebar.title("🎮 Panel Maestro")
    menu = st.sidebar.radio("Navegar:", ["📺 Pantalla Stream", "🔐 Admin", "🎟️ Registro"])

# ==========================================
# VISTA 1: REGISTRO (Seguidores)
# ==========================================
if menu == "🎟️ Registro":
    if not st.session_state.rifa_activa and es_publico:
        st.warning("⚠️ El sorteo aún no ha sido activado. ¡Vuelve pronto!")
    else:
        st.title(f"🎟️ Sorteo: {st.session_state.config['premio']}")
        st.info(f"Costo del boleto: ${st.session_state.config['precio']} USD")
        
        st.subheader("1. Completa tus datos")
        c1, c2 = st.columns(2)
        with c1:
            nom = st.text_input("Nombre")
            ape = st.text_input("Apellido")
        with c2:
            u_g = st.text_input("Usuario en The Ants")
            id_g = st.text_input("ID de Cuenta")
        
        mail = st.text_input("Email de contacto")

        st.divider()

        st.subheader("2. Realizar Pago")
        if CLIENT_ID_PAYPAL == "AQUÍ_PEGA_TU_CLIENT_ID_DE_PAYPAL":
            st.error("Error: Client ID de PayPal no configurado.")
        else:
            paypal_code = f"""
            <div id="paypal-button-container" style="display: flex; justify-content: center;"></div>
            <script src="https://www.paypal.com/sdk/js?client-id={CLIENT_ID_PAYPAL}&currency=USD&components=buttons"></script>
            <script>
                paypal.Buttons({{
                    style: {{ layout: 'vertical', color: 'gold', shape: 'rect' }},
                    createOrder: function(data, actions) {{
                        return actions.order.create({{
                            purchase_units: [{{ amount: {{ value: '{st.session_state.config['precio']}' }} }}]
                        }});
                    }},
                    onApprove: function(data, actions) {{
                        return actions.order.capture().then(function(d) {{
                            alert('¡Pago exitoso! Pulsa el botón verde para terminar.');
                        }});
                    }}
                }}).render('#paypal-button-container');
            </script>
            """
            components.html(paypal_code, height=500)

        if st.button("✅ FINALIZAR REGISTRO", use_container_width=True):
            if nom and id_g and mail:
                st.session_state.participantes.append({
                    "Nombre": nom, "Apellido": ape, "User": u_g, "ID": id_g, "Email": mail, "Hora": time.strftime("%H:%M")
                })
                st.success("¡Registrado! Revisa el Stream.")
            else:
                st.error("Por favor, llena todos los campos.")

# ==========================================
# VISTA 2: PANTALLA STREAM (OBS)
# ==========================================
elif menu == "📺 Pantalla Stream":
    st.title(f"🏆 Rifa: {st.session_state.config['premio']}")
    total = len(st.session_state.participantes)
    meta = st.session_state.config['meta']
    
    col_a, col_b = st.columns(2)
    col_a.metric("Vendidos", f"{total} / {meta}")
    col_b.progress(min(total/meta, 1.0) if meta > 0 else 0)
    
    st.divider()
    
    c_list, c_win = st.columns([2, 1])
    with c_list:
        st.subheader("👥 Participantes")
        if st.session_state.participantes:
            df = pd.DataFrame(st.session_state.participantes)
            st.table(df[["Nombre", "Apellido", "Hora"]].iloc[::-1].head(12))
    
    with c_win:
        st.subheader("🎲 Sorteo")
        if st.button("🎰 ¡GIRAR RULETA!", use_container_width=True):
            if total > 0:
                with st.spinner("Sorteando..."):
                    time.sleep(3)
                    st.session_state.ganador = random.choice(st.session_state.participantes)
                    st.balloons()
        
        if st.session_state.ganador:
            st.success(f"GANADOR: {st.session_state.ganador['Nombre']} {st.session_state.ganador['Apellido']}")

# ==========================================
# VISTA 3: ADMIN (Con botón de Copiar Link)
# ==========================================
elif menu == "🔐 Admin":
    st.title("Panel Maestro")
    intento_clave = st.text_input("Contraseña", type="password")
    
    if intento_clave == CLAVE_MAESTRO:
        st.subheader("Configuración")
        st.session_state.config['meta'] = st.number_input("Meta de Boletos", value=st.session_state.config['meta'])
        st.session_state.config['precio'] = st.text_input("Precio ($)", value=st.session_state.config['precio'])
        st.session_state.config['premio'] = st.text_input("Premio", value=st.session_state.config['premio'])

        st.divider()
        
        if not st.session_state.rifa_activa:
            if st.button("🚀 ACTIVAR RIFA PARA EL PÚBLICO"):
                st.session_state.rifa_activa = True
                st.rerun()
        else:
            st.success("✅ La rifa está ACTIVA.")
            
            # --- GENERADOR DE BOTÓN DE COPIAR ---
            # Intentamos obtener la URL actual automáticamente
            try:
                url_base = "https://rifa-tony-final.streamlit.app/" # Reemplázala por tu URL real si es diferente
                link_publico = f"{url_base}?modo=registro"
                
                st.write(f"Link actual: `{link_publico}`")
                
                # Componente HTML para botón de copiar
                copy_code = f"""
                <button onclick="copyToClipboard()" style="padding: 10px 20px; background-color: #4CAF50; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    📋 Copiar Link para Seguidores
                </button>
                <p id="msg" style="color: green; font-size: 12px;"></p>

                <script>
                function copyToClipboard() {{
                    const el = document.createElement('textarea');
                    el.value = '{link_publico}';
                    document.body.appendChild(el);
                    el.select();
                    document.execCommand('copy');
                    document.body.removeChild(el);
                    document.getElementById('msg').innerHTML = '¡Copiado al portapapeles!';
                }}
                </script>
                """
                components.html(copy_code, height=100)
            except:
                st.error("No se pudo generar el botón de copiar.")

            if st.button("🛑 DESACTIVAR RIFA"):
                st.session_state.rifa_activa = False
                st.rerun()

        if st.button("🗑️ Resetear Datos"):
            st.session_state.participantes = []
            st.session_state.ganador = None
            st.rerun()
