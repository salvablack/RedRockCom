import re
from dataclasses import dataclass

import numpy as np
import streamlit as st
from streamlit_webrtc import (
    webrtc_streamer,
    WebRtcMode,
    RTCConfiguration,
    AudioProcessorBase,
)

# ---------------------------------------------------
# CONFIGURACIÓN GENERAL
# ---------------------------------------------------

st.set_page_config(page_title="Llamada privada", layout="centered")

# ---------------------------------------------------
# CONFIG RTC (PREPARADO PARA TURN)
# ---------------------------------------------------

@dataclass(frozen=True)
class WebRTCConfig:
    stun_urls: list
    turn_urls: list | None = None
    username: str | None = None
    credential: str | None = None

    def build(self):
        ice_servers = [{"urls": self.stun_urls}]
        if self.turn_urls:
            ice_servers.append(
                {
                    "urls": self.turn_urls,
                    "username": self.username,
                    "credential": self.credential,
                }
            )
        return RTCConfiguration({"iceServers": ice_servers})


RTC_CONFIG = WebRTCConfig(
    stun_urls=["stun:stun.l.google.com:19302"],
).build()

# ---------------------------------------------------
# AUDIO PROCESSOR (mute + nivel de voz)
# ---------------------------------------------------

class AudioLevelProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_level = 0.0
        self.muted = False

    def recv(self, frame):
        audio = frame.to_ndarray()
        self.audio_level = float(np.abs(audio).mean())

        if self.muted:
            audio[:] = 0

        return frame.from_ndarray(audio, layout=frame.layout)


# ---------------------------------------------------
# VALIDACIÓN ROOM ID
# ---------------------------------------------------

ROOM_REGEX = re.compile(r"^[a-zA-Z0-9_-]{4,32}$")


def get_room_id():
    room = st.text_input("Room ID (lo eliges tú)", type="password")

    if not room:
        st.info("Ambas personas deben usar exactamente el mismo Room ID")
        return None

    if not ROOM_REGEX.match(room):
        st.error("Solo letras, números, _ y - (4–32 caracteres)")
        return None

    return room


# ---------------------------------------------------
# UI
# ---------------------------------------------------

st.title("🔒 Llamada privada P2P por Room ID")

room_id = get_room_id()
if not room_id:
    st.stop()

# ---------------------------------------------------
# MUTE STATE
# ---------------------------------------------------

if "muted" not in st.session_state:
    st.session_state.muted = False


def toggle_mute():
    st.session_state.muted = not st.session_state.muted


st.button(
    "🔇 Mute" if not st.session_state.muted else "🔊 Unmute",
    on_click=toggle_mute,
)

# ---------------------------------------------------
# WEBRTC STREAMER
# ---------------------------------------------------

webrtc_ctx = webrtc_streamer(
    key=f"room-{room_id}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={
        "video": False,
        "audio": {
            "echoCancellation": True,
            "noiseSuppression": True,
            "autoGainControl": True,
        },
    },
    audio_processor_factory=AudioLevelProcessor,
    async_processing=True,
)

# ---------------------------------------------------
# ESTADO DE CONEXIÓN + NIVEL DE AUDIO
# ---------------------------------------------------

status_placeholder = st.empty()
audio_placeholder = st.empty()

if webrtc_ctx.state.playing:
    status_placeholder.success("🟢 Conectado")

    if webrtc_ctx.audio_processor:
        webrtc_ctx.audio_processor.muted = st.session_state.muted
        level = webrtc_ctx.audio_processor.audio_level

        if level > 200:
            audio_placeholder.success("🎤 Hablando")
        elif level > 20:
            audio_placeholder.info("🔊 Audio detectado")
        else:
            audio_placeholder.warning("🔇 Silencio")
else:
    status_placeholder.warning("🟡 Esperando a la otra persona...")

# ---------------------------------------------------
# INSTRUCCIONES
# ---------------------------------------------------

with st.expander("📌 Cómo usar"):
    st.markdown(
        """
        1. Ambos abren esta app.
        2. Escriben el mismo **Room ID**.
        3. Permiten el acceso al micrófono.
        4. La conexión es directa P2P y cifrada.
        """
    )

