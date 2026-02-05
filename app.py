import re
import logging
from dataclasses import dataclass

import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration

# ---------------------------------------------------
# CONFIGURACIÓN GLOBAL
# ---------------------------------------------------

st.set_page_config(
    page_title="Llamada privada",
    layout="centered",
    initial_sidebar_state="collapsed",
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ---------------------------------------------------
# CONFIG RTC (STUN + preparado para TURN)
# ---------------------------------------------------

@dataclass(frozen=True)
class WebRTCConfig:
    stun_urls: list
    turn_urls: list | None = None
    username: str | None = None
    credential: str | None = None

    def build(self) -> RTCConfiguration:
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
    # 🔥 Aquí podrás poner tu TURN real cuando lo tengas
    # turn_urls=["turn:your.turn.server:3478"],
    # username="user",
    # credential="pass",
).build()

# ---------------------------------------------------
# UTILIDADES
# ---------------------------------------------------

ROOM_ID_REGEX = re.compile(r"^[a-zA-Z0-9_-]{4,32}$")


def validate_room_id(room_id: str) -> bool:
    """Valida formato seguro del Room ID."""
    return bool(ROOM_ID_REGEX.match(room_id))


def get_room_id() -> str | None:
    """Obtiene y valida el Room ID desde UI."""
    room_id = st.text_input(
        "Ingresa el Room ID",
        type="password",
        help="Debe tener entre 4 y 32 caracteres (letras, números, _ y -)",
    )

    if not room_id:
        st.info("Ambas personas deben usar exactamente el mismo Room ID.")
        return None

    if not validate_room_id(room_id):
        st.error("Room ID inválido. Usa solo letras, números, _ o - (4–32 chars).")
        return None

    return room_id


# ---------------------------------------------------
# UI
# ---------------------------------------------------

st.title("🔒 Llamada privada por Room ID")
st.caption("Conexión WebRTC P2P cifrada, sin servidor intermedio.")

room_id = get_room_id()
if not room_id:
    st.stop()

st.success("Room ID válido. Inicializando conexión...")

# ---------------------------------------------------
# WEBRTC STREAMER
# ---------------------------------------------------

webrtc_ctx = webrtc_streamer(
    key=f"audio-call-{room_id}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={
        "video": False,
        "audio": True,
    },
    async_processing=True,
)

# ---------------------------------------------------
# ESTADO DE CONEXIÓN
# ---------------------------------------------------

if webrtc_ctx.state.playing:
    st.success("🎙️ Conectado. Audio activo.")
else:
    st.warning("Esperando a que la otra persona se conecte...")

# ---------------------------------------------------
# INSTRUCCIONES
# ---------------------------------------------------

with st.expander("📌 Instrucciones"):
    st.markdown(
        """
        1. Ambos abren esta aplicación.
        2. Escriben exactamente el mismo **Room ID**.
        3. Permiten el acceso al micrófono.
        4. La conexión es directa P2P y cifrada.
        """
    )
