import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import uuid

st.set_page_config(page_title="Sala Audio - Fix Sonido Móvil", layout="centered")

st.title("🎙️ Sala de Audio Privada")
st.caption("Conectados pero sin sonido → toca 'Activar Sonido' en celular")

st.info("""
Si ves 🟢 pero no oyes nada:
- En celular: toca la pantalla o el botón 'Activar Sonido' primero
- Usa auriculares (cable o Bluetooth)
- Habla fuerte en el otro dispositivo después de activar
""")

RTC_CONFIG = RTCConfiguration(
    iceServers=[
        {"urls": "stun:stun.l.google.com:19302"},
        {"urls": "stun:stun1.l.google.com:19302"},
        {
            "urls": ["turn:openrelay.metered.ca:80", "turn:openrelay.metered.ca:443?transport=tcp"],
            "username": "openrelayproject",
            "credential": "openrelayproject"
        },
        {"urls": "turn:numb.viagenie.ca", "username": "webrtc@live.com", "credential": "muazkh"}
    ]
)

if "room_id" not in st.session_state:
    st.session_state.room_id = str(uuid.uuid4())[:8]

room = st.text_input("Room ID", value=st.session_state.room_id)

if st.button("Unirse / Refrescar"):
    st.session_state.room_id = room.strip() or str(uuid.uuid4())[:8]
    st.rerun()

st.markdown(f"**Room ID:** `{st.session_state.room_id}`")

audio_constraints = {
    "echoCancellation": True,
    "noiseSuppression": True,
    "autoGainControl": True,
    "channelCount": 1,
    "sampleRate": 16000
}

ctx = webrtc_streamer(
    key=f"audio_mobile_fix_{st.session_state.room_id}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={"audio": audio_constraints, "video": False},
    desired_playing_state=True,
    audio_html_attrs={"controls": False, "style": {"width": "100%"}}
)

if ctx.input_audio_track:
    st.success("✅ Micrófono enviando")
else:
    st.error("❌ Micrófono no activo")

if ctx.state.playing:
    st.success("🟢 Conectado → audio debería reproducirse")
    st.button("🔊 Activar / Desbloquear Sonido (toca aquí en celular si silencioso)", use_container_width=True)
    st.info("Después de tocar → habla en el otro lado. Esto ayuda en móvil donde autoplay falla.")
else:
    st.warning("🔴 Aún no reproduciendo audio recibido")

st.markdown("---")
st.caption("Prueba: Toca el botón grande arriba en celular → habla en PC → escucha en auriculares del celular.")
