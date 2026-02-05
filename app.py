import re
import time
import logging
from dataclasses import dataclass

import streamlit as st
from streamlit_webrtc import (
    webrtc_streamer,
    WebRtcMode,
    RTCConfiguration,
)

# ---------------------------------------------------
# CONFIG GENERAL
# ---------------------------------------------------

st.set_page_config(page_title="Llamada privada", layout="centered")
logging.basicConfig(level=logging.INFO)

# ---------------------------------------------------
# CONFIG RTC (LISTO PARA TURN)
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
# VALIDACIÓN ROOM
# ---------------------------------------------------

ROOM_REGEX = re.compile(r"^[a-zA-Z0-9_-]{4,32}$")


def get_room_id():
    room = st.text_input("Room ID (definido por ti)", type="password")

    if not room:
        st.info("Ambas personas deben usar exactamente el mismo Room ID")
        return None

    if not ROOM_REGEX.match(room):
        st.error("Solo letras, números, _ y - (4–32 chars)")
        return None

    return room


# ---------------------------------------------------
# UI
# ---------------------------------------------------

st.title("🔒 RedRock Com")

room_id = get_room_id()
if not room_id:
    st.stop()

# ---------------------------------------------------
# CONTROL DE MUTE EN SESSION STATE
# ---------------------------------------------------

if "muted" not in st.session_state:
    st.session_state.muted = False

def toggle_mute():
    st.session_state.muted = not st.session_state.muted


col1, col2 = st.columns(2)
with col1:
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
        "audio": {
            "echoCancellation": True,
            "noiseSuppression": True,
            "autoGainControl": True,
        },
    },
    async_processing=True,
)

# ---------------------------------------------------
# ESTADO DE CONEXIÓN
# ---------------------------------------------------

status_placeholder = st.empty()
stats_placeholder = st.empty()

if webrtc_ctx.state.playing:
    status_placeholder.success("🟢 Conectado")

    # Aplicar mute dinámico
    if webrtc_ctx.audio_processor:
        webrtc_ctx.audio_processor.muted = st.session_state.muted

    # ---------------------------------------------------
    # MONITOREO DE STATS (latencia y calidad)
    # ---------------------------------------------------
    for _ in range(5):  # refresca stats unos segundos
        stats = webrtc_ctx.get_stats()
        rtt = None
        bitrate = None

        for report in stats.values():
            if report.type == "candidate-pair" and report.state == "succeeded":
                rtt = report.currentRoundTripTime

            if report.type == "outbound-rtp" and report.kind == "audio":
                bitrate = report.bytesSent

        stats_placeholder.markdown(
            f"""
            **Latencia (RTT):** {round(rtt*1000,2) if rtt else 'N/A'} ms  
            **Audio enviado:** {bitrate if bitrate else 'N/A'} bytes
            """
        )
        time.sleep(1)

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
        3. Permiten micrófono.
        4. La conexión es directa, cifrada y sin servidor intermedio.
        """
    )
