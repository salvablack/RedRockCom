import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

st.set_page_config(page_title="Llamada privada", layout="centered")

st.title("🔒 Llamada privada por Room ID")

room_id = st.text_input("Ingresa el Room ID", type="password")

if not room_id:
    st.info("Ambas personas deben usar el MISMO Room ID")
    st.stop()

RTC_CONFIGURATION = RTCConfiguration(
    {"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
)

webrtc_streamer(
    key=f"audio-call-{room_id}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIGURATION,
    media_stream_constraints={
        "video": False,
        "audio": True
    },
    async_processing=True,
)

st.markdown("""
### 📌 Instrucciones
- Ambos abren esta app
- Escriben exactamente el mismo **Room ID**
- Permiten el micrófono
- ¡Listo! 🎙️
""")

