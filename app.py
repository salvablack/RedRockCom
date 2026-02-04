import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import uuid

st.set_page_config(page_title="Sala de Audio Privada - Máx 3", layout="wide")

st.title("🎙️ Sala de Audio Privada (solo voz, máximo 3 personas)")

st.info("""
Esta versión es **solo audio** para que conecte más fácil.  
- Permite micrófono cuando el navegador pregunte.  
- Comparte el Room ID con 1 o 2 personas más.  
- Prueba primero con 2 personas (abre en dos pestañas o dispositivos).
""")

# Más STUN + TURN públicos gratuitos (2026 – probados en foros recientes)
RTC_CONFIG = RTCConfiguration(
    iceServers=[
        # STUN de Google (siempre bueno)
        {"urls": "stun:stun.l.google.com:19302"},
        {"urls": "stun:stun1.l.google.com:19302"},
        {"urls": "stun:stun2.l.google.com:19302"},
        
        # TURN gratuitos abiertos (pueden saturarse, pero rotan bien)
        {
            "urls": "turn:openrelay.metered.ca:80",
            "username": "openrelayproject",
            "credential": "openrelayproject",
        },
        {
            "urls": "turn:openrelay.metered.ca:443?transport=tcp",
            "username": "openrelayproject",
            "credential": "openrelayproject",
        },
        {
            "urls": "turn:numb.viagenie.ca",
            "username": "webrtc@live.com",
            "credential": "muazkh",
        },
        # Otro TURN alternativo (si los de arriba fallan)
        {
            "urls": "turn:turn.anyfirewall.com:443?transport=tcp",
            "username": "webrtc",
            "credential": "webrtc",
        },
    ]
)

# Room ID
if "room_id" not in st.session_state:
    st.session_state.room_id = str(uuid.uuid4())[:8]

room = st.text_input(
    "Ingresa o crea el Room ID (compártelo exactamente igual)",
    value=st.session_state.room_id
)

if st.button("Unirse / Refrescar sala"):
    new_room = room.strip()
    if new_room:
        st.session_state.room_id = new_room
    st.success(f"Conectado a sala: **{st.session_state.room_id}**")
    st.rerun()

st.markdown(f"**Room ID para compartir (máx 2 amigos más):**  `{st.session_state.room_id}`")

# Solo audio – sin video para simplificar y reducir fallos
ctx = webrtc_streamer(
    key=f"audio_only_{st.session_state.room_id}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={
        "audio": True,
        "video": False   # ← clave: desactiva video
    },
    desired_playing_state=True,  # Inicia automáticamente
    video_html_attrs=None,       # No mostramos video local/remoto
)

if ctx.input_audio_track:
    st.success("✅ Micrófono activo. ¡Habla y escucha a los demás!")
    st.markdown("**Estado:** Audio enviado/recibido. Abre la misma app en otro dispositivo con el mismo Room ID.")
else:
    st.warning("""
    No se detecta audio todavía.  
    1. Permite el micrófono en el navegador (arriba a la izquierda suele aparecer el icono).  
    2. Prueba en Chrome o Edge (Firefox a veces falla más con WebRTC).  
    3. Si sigue sin ir → cambia de red (WiFi → datos móviles o viceversa).  
    4. Refresca la página o crea un Room ID nuevo.
    """)

st.caption("Si aún no conecta después de probar 2 pestañas → dime qué navegador usas y qué ves exactamente (pantalla negra, error en consola, etc.) para ajustar más.")
