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
# CONFIG GENERAL
# ---------------------------------------------------

st.set_page_config(page_title="Llamada privada", layout="centered")

# ---------------------------------------------------
# RTC CONFIG (preparado para TURN)
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
# AUDIO PROCESSOR (mute + nivel de voz SIN romper audio)
# ---------------------------------------------------

class AudioLevelProcessor(AudioProcessorBase):
    def __init__(self):
        self.audio_level = 0.0
        self.muted = False

    def recv(self, frame):
        audio = frame.to_ndarray()
        self.audio_level = float(np.abs(audio).mean())

        if self.muted:
            audio = np.zeros_like(audio)

        new_frame = frame.from_ndarray(audio, layout=frame.layout)
        new_frame.sample_rate = frame.sample_rate

        return new_frame


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
# WEBRTC
# ---------------------------------------------------

webrtc_ctx = webrtc_streamer(
    key=f"room-{room_id}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={
        "video": False,
        "audio": True,
    },
    audio_processor_factory=AudioLevelProcessor,
    async_processing=True,
)

# ---------------------------------------------------
# ESTADO + NIVEL DE VOZ
# ---------------------------------------------------

status = st.empty()
voice = st.empty()

if webrtc_ctx.state.playing:
    status.success("🟢 Conectado")

    if webrtc_ctx.audio_processor:
        webrtc_ctx.audio_processor.muted = st.session_state.muted
        level = webrtc_ctx.audio_processor.audio_level

        if level > 200:
            voice.success("🎤 Hablando")
        elif level > 20:
            voice.info("🔊 Audio detectado")
        else:
            voice.warning("🔇 Silencio")
else:
    status.warning("🟡 Esperando a la otra persona...")

# ---------------------------------------------------
# INSTRUCCIONES
# ---------------------------------------------------

with st.expander("📌 Cómo usar"):
    st.markdown(
        """
        1. Ambos abren esta app.
        2. Escriben el mismo **Room ID**.
        3. Permiten el micrófono.
        4. La conexión es directa y cifrada (P2P).
        """
    )

