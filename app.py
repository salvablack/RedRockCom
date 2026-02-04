import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
import uuid

st.set_page_config(
    page_title="Sala de Audio Privada – Optimizado Móvil",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.title("🎙️ Sala de Audio Privada")
st.caption("Solo audio · Máximo 3 personas · Optimizado para celular 2026")

st.markdown("""
### Instrucciones importantes (especialmente si falla en celular)
1. **En celular**: usa **Chrome** (Android) o **Safari actualizado** (iPhone)
2. Permite el micrófono cuando aparezca el aviso
3. Prueba **cambiando de red**:
   - WiFi → datos móviles 4G/5G
   - Datos móviles → WiFi diferente
4. Usa **auriculares** (con o sin cable) → elimina eco y mejora conexión
5. Si se queda en "Esperando conexión...":
   - Refresca la página 2–3 veces
   - Crea un Room ID nuevo
   - Prueba en otro celular o PC al mismo tiempo
""")

# ──────────────────────────────────────────────────────────────
# Configuración ICE – más servidores TURN para móviles / redes difíciles
# ──────────────────────────────────────────────────────────────
RTC_CONFIG = RTCConfiguration(
    iceServers=[
        # Google STUN (siempre incluir)
        {"urls": "stun:stun.l.google.com:19302"},
        {"urls": "stun:stun1.l.google.com:19302"},
        {"urls": "stun:stun2.l.google.com:19302"},
        
        # OpenRelay – el más usado y gratuito
        {
            "urls": [
                "turn:openrelay.metered.ca:80",
                "turn:openrelay.metered.ca:443?transport=tcp",
                "turn:openrelay.metered.ca:443?transport=udp"
            ],
            "username": "openrelayproject",
            "credential": "openrelayproject"
        },
        
        # Alternativas adicionales si openrelay está saturado
        {
            "urls": "turn:numb.viagenie.ca",
            "username": "webrtc@live.com",
            "credential": "muazkh"
        },
        {
            "urls": "turn:turn.anyfirewall.com:443?transport=tcp",
            "username": "webrtc",
            "credential": "webrtc"
        },
        {
            "urls": "turn:relay.webwormhole.io:3478?transport=udp",
            "username": "anonymous",
            "credential": "anonymous"
        }
    ]
)

# ──────────────────────────────────────────────────────────────
# Room ID
# ──────────────────────────────────────────────────────────────
if "room_id" not in st.session_state:
    st.session_state.room_id = str(uuid.uuid4())[:8]

room_input = st.text_input(
    "Room ID (compártelo exactamente igual)",
    value=st.session_state.room_id,
    max_chars=20
)

if st.button("Unirse / Crear sala nueva"):
    cleaned = room_input.strip()
    if cleaned:
        st.session_state.room_id = cleaned
    else:
        st.session_state.room_id = str(uuid.uuid4())[:8]
    st.rerun()

st.markdown(f"**Room ID actual para compartir:**  `{st.session_state.room_id}`")

# ──────────────────────────────────────────────────────────────
# Audio constraints – optimizadas para móviles (bajo consumo)
# ──────────────────────────────────────────────────────────────
audio_constraints = {
    "echoCancellation": True,
    "echoCancellationType": "system",   # prueba "browser" si falla
    "noiseSuppression": True,
    "autoGainControl": True,
    "channelCount": 1,                  # mono → menos datos
    "sampleRate": 16000,                # 16 kHz → buena calidad + bajo ancho de banda
    "googEchoCancellation": True,
    "googNoiseSuppression": True
}

# ──────────────────────────────────────────────────────────────
# WebRTC streamer
# ──────────────────────────────────────────────────────────────
ctx = webrtc_streamer(
    key=f"audio_only_{st.session_state.room_id}",
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

# ──────────────────────────────────────────────────────────────
# Diagnóstico claro
# ──────────────────────────────────────────────────────────────
if ctx.input_audio_track:
    st.success("✅ Micrófono activo → tu voz se envía")
else:
    st.error("❌ No detecta micrófono")
    st.markdown("→ Verifica permisos en el navegador y ajustes del celular")

if ctx.state.playing:
    st.success("🟢 Reproduciendo audio recibido → deberías escuchar al otro")
    st.info("Con auriculares: solo deberías oír la voz del otro (sin eco)")
else:
    st.warning("🔴 Esperando conexión... (ICE checking o failed)")
    st.markdown("""
    **Qué hacer ahora mismo:**
    - Cambia de WiFi a datos móviles (o viceversa)
    - Refresca la página varias veces
    - Prueba en Chrome (Android) o Safari (iPhone)
    - Abre la misma sala en PC y celular al mismo tiempo
    """)

st.markdown("---")
st.caption("""
Si sigue sin conectar en celular pero sí en PC:
→ Es casi seguro problema de red móvil / NAT / TURN saturado
Dime: Android o iOS / WiFi o datos / qué navegador / qué pasa exactamente (carga eterna, negro, etc.)
""")
