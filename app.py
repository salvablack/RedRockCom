import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import uuid

st.set_page_config(
    page_title="Llamada de Audio Privada",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("📞 Llamada de Audio Privada")
st.caption("1 a 1 (o máximo 3) – Solo audio – Usa auriculares")

st.markdown("""
### Guía rápida para que funcione
1. **Usa auriculares** (imprescindible para no oírte a ti mismo).
2. Permite micrófono cuando el navegador lo pida.
3. Crea o ingresa un **Room ID** y compártelo con la otra persona.
4. Ambos dan clic en **"Unirse y activar llamada"**.
5. En **celular**: después de conectar, toca **"Desbloquear Sonido"** si no oyes nada.
6. Prueba cambiar red (WiFi ↔ datos móviles) si se queda "Esperando...".
""")

# TURN + STUN robustos (más opciones para conexiones difíciles)
RTC_CONFIG = RTCConfiguration(
    iceServers=[
        {"urls": "stun:stun.l.google.com:19302"},
        {"urls": "stun:stun1.l.google.com:19302"},
        {"urls": "stun:stun.stunprotocol.org:3478"},
        {
            "urls": [
                "turn:openrelay.metered.ca:80",
                "turn:openrelay.metered.ca:443?transport=tcp",
                "turn:openrelay.metered.ca:443?transport=udp"
            ],
            "username": "openrelayproject",
            "credential": "openrelayproject"
        },
        {
            "urls": "turn:numb.viagenie.ca",
            "username": "webrtc@live.com",
            "credential": "muazkh"
        }
    ]
)

# Room ID persistente
if "room_id" not in st.session_state:
    st.session_state.room_id = str(uuid.uuid4())[:8]

room_input = st.text_input(
    "Room ID (compártelo exactamente con la otra persona)",
    value=st.session_state.room_id,
    max_chars=20
)

if st.button("Unirse y activar llamada"):
    cleaned = room_input.strip()
    if cleaned:
        st.session_state.room_id = cleaned
    st.rerun()

st.markdown(f"**Room ID para compartir:** `{st.session_state.room_id}`")

# Constraints audio: anti-eco, bajo consumo para móvil
audio_constraints = {
    "echoCancellation": True,
    "echoCancellationType": "system",  # o "browser" si falla
    "noiseSuppression": True,
    "autoGainControl": True,
    "channelCount": 1,  # mono
    "sampleRate": 16000  # 16kHz para menos ancho de banda
}

ctx = webrtc_streamer(
    key=f"llamada_audio_{st.session_state.room_id}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={
        "audio": audio_constraints,
        "video": False
    },
    desired_playing_state=True,
    audio_html_attrs={
        "controls": False,
        "style": {"width": "100%", "margin": "10px 0"}
    }
)

# Estado
if ctx.input_audio_track:
    st.success("✅ Tu micrófono está enviando voz")
else:
    st.error("❌ Micrófono no detectado – permite acceso")

if ctx.state.playing:
    st.success("🟢 Conexión establecida – audio debería reproducirse")
    if st.button("🔊 Desbloquear / Activar Sonido (toca aquí si silencioso)", use_container_width=True):
        st.info("Clic hecho → habla ahora en el otro dispositivo. Esto desbloquea el audio en móviles.")
else:
    st.warning("🔴 Esperando conexión... (prueba cambiar red o refrescar)")

st.markdown("---")
st.caption("""
Notas importantes:
- Solo 1 a 1 estable (para 3 se necesita signaling avanzado que no soporta bien este componente).
- Si conecta pero no suena: toca la pantalla o el botón de arriba en el celular.
- Si falla en celular pero funciona en PC: es común por NAT/red móvil – prueba WiFi diferente.
- Auriculares evitan oír tu propia voz.
""")
