import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import uuid

st.set_page_config(
    page_title="Sala de Audio Privada - Optimizado Móvil",
    layout="centered",          # Mejor para celulares
    initial_sidebar_state="collapsed"  # Oculta sidebar por defecto
)

st.title("🎙️ Sala de Audio Privada")
st.caption("Optimizado para celular - Solo audio - Máximo 3 personas")

# Mensajes claros para móvil
st.info("""
**Consejos para celular:**
1. Usa **Chrome** o **Safari** actualizado
2. Permite micrófono (arriba aparece icono de permiso)
3. Prueba con **auriculares Bluetooth** o con cable (reduce eco al máximo)
4. Usa **WiFi estable** o 4G/5G bueno
5. Si se queda cargando → refresca o cambia Room ID
""")

# TURN servers más robustos (incluye opciones móviles comunes en 2026)
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
            "urls": "turn:turn:3478?transport=udp",
            "username": "webrtc",
            "credential": "webrtc"
        }
    ]
)

# Room ID simple
if "room_id" not in st.session_state:
    st.session_state.room_id = str(uuid.uuid4())[:8]

room_input = st.text_input(
    "Room ID (compártelo exactamente con los demás)",
    value=st.session_state.room_id,
    max_chars=20
)

if st.button("Unirse / Crear sala nueva"):
    st.session_state.room_id = room_input.strip() or str(uuid.uuid4())[:8]
    st.rerun()

st.markdown(f"**Tu Room ID:** `{st.session_state.room_id}`")

# Audio constraints optimizadas para móviles (baja latencia, echo fuerte)
audio_constraints = {
    "echoCancellation": True,
    "echoCancellationType": "system",  # Mejor en móviles modernos
    "noiseSuppression": True,
    "autoGainControl": True,
    "channelCount": 1,                 # Mono → menos consumo en móvil
    "sampleRate": 16000,               # 16kHz → buena calidad + bajo ancho de banda
    "googEchoCancellation": True,
    "googNoiseSuppression": True
}

ctx = webrtc_streamer(
    key=f"mobile_audio_{st.session_state.room_id}",
    mode=WebRtcMode.SENDRECV,
    rtc_configuration=RTC_CONFIG,
    media_stream_constraints={
        "audio": audio_constraints,
        "video": False
    },
    desired_playing_state=True,
    audio_html_attrs={
        "controls": False,             # Oculta controles por defecto en móvil
        "style": {"width": "100%", "margin": "10px 0"}
    }
)

# Diagnóstico móvil-friendly
if ctx.input_audio_track:
    st.success("✅ Micrófono activo → tu voz se envía")
else:
    st.error("❌ No accede al micrófono")
    st.markdown("- Verifica permisos en ajustes del navegador/celular")
    st.markdown("- Prueba permitir siempre para este sitio")

if ctx.state.playing:
    st.success("🟢 Reproduciendo audio del otro → habla y escucha")
    st.info("Con auriculares: deberías oír SOLO al otro (sin tu eco)")
else:
    st.warning("🔴 Esperando conexión... prueba refrescar o cambiar red")

st.markdown("---")
st.caption("""
Si sigue fallando en celular:
- Copia errores de consola (en Chrome móvil: chrome://inspect → conecta USB o usa "remote debugging")
- Dime si es Android o iOS, y qué pasa exactamente (carga eterna, negro, permiso denegado, etc.)
""")
