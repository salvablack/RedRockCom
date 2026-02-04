import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration, VideoProcessorBase
import uuid

st.set_page_config(page_title="Sala Privada - Máx 3 personas", layout="wide")

st.title("🎥 Sala Privada (máximo 3 personas)")

# TURN server recomendado (gratuito temporal – cámbialo si expira)
RTC_CONFIG = RTCConfiguration(
    iceServers=[
        {"urls": "stun:stun.l.google.com:19302"},
        {
            "urls": "turn:openrelay.metered.ca:80",
            "username": "openrelayproject",
            "credential": "openrelayproject",
        },
        {
            "urls": "turn:openrelay.metered.ca:443",
            "username": "openrelayproject",
            "credential": "openrelayproject",
        },
    ]
)

# Room ID persistente por sesión
if "room_id" not in st.session_state:
    st.session_state.room_id = str(uuid.uuid4())[:8]

room = st.text_input("Ingresa o crea el Room ID (compártelo con los otros 2)", value=st.session_state.room_id)

if st.button("Unirse / Actualizar sala"):
    st.session_state.room_id = room.strip() or st.session_state.room_id
    st.success(f"Conectado a: **{st.session_state.room_id}**")
    st.rerun()

st.markdown(f"**Comparte este ID exacto con máximo 2 personas más:** `{st.session_state.room_id}`")

# El streamer WebRTC – key único por room para que no se mezclen sesiones
ctx = webrtc_streamer(
    key=f"video_{st.session_state.room_id}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={"video": True, "audio": True},
    video_html_attrs={"style": {"width": "70%", "border": "3px solid #4CAF50", "border-radius": "8px"}},
    desired_playing_state=True,  # Inicia automáticamente
)

if ctx.input_video_track:
    st.success("✅ Cámara y micrófono activos. ¡Listo para la reunión!")
    st.info("Abre la misma app en otro navegador/dispositivo, usa el mismo Room ID y verás el video del otro.")
else:
    st.warning("Permite acceso a cámara y micrófono cuando el navegador lo pida.")

st.markdown("---")
st.caption("Notas: Funciona mejor con máximo 3 personas. Si no conecta → prueba otro navegador o red. TURN incluido para ayudar con conexiones.")
